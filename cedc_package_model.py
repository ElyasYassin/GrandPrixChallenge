#!/usr/bin/env python3
"""Create a compact CEDC DeepRacer simulator submission from a DRfC model/ directory.

The output contains exactly one complete checkpoint plus its matching frozen .pb model,
model metadata, a normalized checkpoint manifest, and Coach marker files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CKPT_RE = re.compile(r"(?P<iter>\d+)_Step-(?P<step>\d+)(?:\.ckpt)?")
MODEL_RE = re.compile(r"model_(?P<iter>\d+)\.pb$")

@dataclass(frozen=True)
class Candidate:
    iteration: int
    step: int
    base: str  # e.g. 50_Step-370870
    data: Path
    index: Path
    meta: Path
    frozen: Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def discover_candidates(model_dir: Path) -> dict[int, Candidate]:
    result: dict[int, Candidate] = {}
    for index in model_dir.glob("*_Step-*.ckpt.index"):
        stem = index.name[: -len(".ckpt.index")]
        m = CKPT_RE.fullmatch(stem)
        if not m:
            continue
        iteration = int(m.group("iter"))
        step = int(m.group("step"))
        data_matches = list(model_dir.glob(stem + ".ckpt.data-*"))
        meta = model_dir / (stem + ".ckpt.meta")
        frozen = model_dir / f"model_{iteration}.pb"
        if len(data_matches) != 1 or not meta.is_file() or not frozen.is_file():
            continue
        result[iteration] = Candidate(iteration, step, stem, data_matches[0], index, meta, frozen)
    return result


def walk_string_refs(obj: Any, path: tuple[str, ...] = ()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_string_refs(v, path + (str(k),))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_string_refs(v, path + (str(i),))
    elif isinstance(obj, str):
        m = CKPT_RE.search(obj)
        if m:
            yield path, obj, int(m.group("iter")), int(m.group("step"))


def pick_candidate(manifest: Any, candidates: dict[int, Candidate], selector: str) -> tuple[Candidate, str]:
    if not candidates:
        raise SystemExit("No complete simulator checkpoints found (checkpoint triplet + matching model_N.pb).")

    if selector.isdigit():
        n = int(selector)
        if n not in candidates:
            raise SystemExit(f"Checkpoint iteration {n} is not complete. Available: {sorted(candidates)}")
        return candidates[n], f"explicit iteration {n}"

    m = CKPT_RE.search(selector)
    if m:
        n = int(m.group("iter"))
        c = candidates.get(n)
        if not c or c.step != int(m.group("step")):
            raise SystemExit(f"Requested checkpoint {selector!r} not found as a complete checkpoint.")
        return c, f"explicit checkpoint {c.base}"

    if selector == "latest":
        n = max(candidates)
        return candidates[n], "highest complete iteration"

    refs = list(walk_string_refs(manifest))
    if selector in {"auto", "best"}:
        best_refs = [r for r in refs if any("best" in p.lower() for p in r[0])]
        for _path, _text, n, step in best_refs:
            c = candidates.get(n)
            if c and c.step == step:
                return c, "best checkpoint referenced by deepracer_checkpoints.json"
        if selector == "best":
            raise SystemExit("Could not identify a complete best checkpoint from deepracer_checkpoints.json. Use --checkpoint latest or an iteration number.")

    if selector == "auto":
        last_refs = [r for r in refs if any("last" in p.lower() for p in r[0])]
        for _path, _text, n, step in last_refs:
            c = candidates.get(n)
            if c and c.step == step:
                return c, "last checkpoint referenced by deepracer_checkpoints.json"
        # Any manifest reference is safer than inventing one.
        for _path, _text, n, step in refs:
            c = candidates.get(n)
            if c and c.step == step:
                return c, "checkpoint referenced by deepracer_checkpoints.json"
        n = max(candidates)
        return candidates[n], "highest complete iteration (manifest selector not identifiable)"

    raise SystemExit("--checkpoint must be auto, best, latest, an iteration number, or a checkpoint basename")


def rewrite_checkpoint_string(text: str, selected: Candidate) -> str:
    return CKPT_RE.sub(selected.base, text)


def normalize_manifest(obj: Any, selected: Candidate, path: tuple[str, ...] = ()) -> tuple[Any, int]:
    """Conservatively update selector-like checkpoint strings.

    We rewrite strings only when their JSON key path includes checkpoint/best/last/name.
    Historical metric arrays are otherwise left intact.
    """
    changed = 0
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            nv, c = normalize_manifest(v, selected, path + (str(k),))
            out[k] = nv
            changed += c
        return out, changed
    if isinstance(obj, list):
        out = []
        for i, v in enumerate(obj):
            nv, c = normalize_manifest(v, selected, path + (str(i),))
            out.append(nv)
            changed += c
        return out, changed
    if isinstance(obj, str) and CKPT_RE.search(obj):
        key_context = " ".join(path).lower()
        if any(token in key_context for token in ("checkpoint", "best", "last")):
            new = rewrite_checkpoint_string(obj, selected)
            return new, int(new != obj)
    return obj, 0


def normalize_coach_checkpoint(source: Path, selected: Candidate) -> str:
    if source.is_file():
        text = source.read_text(errors="replace")
        if CKPT_RE.search(text):
            return rewrite_checkpoint_string(text, selected)
    return selected.base + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a compact CEDC DeepRacer competition submission")
    ap.add_argument("model_dir", type=Path, help="DRfC model/ directory")
    ap.add_argument("output", type=Path, help="Output .tar.gz")
    ap.add_argument("--checkpoint", default="auto", help="auto (default), best, latest, iteration number, or checkpoint basename")
    ap.add_argument("--max-upload-mb", type=int, default=90, help="Fail if compressed archive exceeds this size (default: 90)")
    args = ap.parse_args()

    model_dir = args.model_dir.resolve()
    if not model_dir.is_dir():
        raise SystemExit(f"Not a directory: {model_dir}")
    metadata = model_dir / "model_metadata.json"
    manifest_path = model_dir / "deepracer_checkpoints.json"
    if not metadata.is_file() or not manifest_path.is_file():
        raise SystemExit("model_dir must contain model_metadata.json and deepracer_checkpoints.json")

    try:
        manifest = json.loads(manifest_path.read_text())
    except Exception as exc:
        raise SystemExit(f"Could not parse deepracer_checkpoints.json: {exc}")

    candidates = discover_candidates(model_dir)
    selected, reason = pick_candidate(manifest, candidates, args.checkpoint)
    normalized_manifest, changed = normalize_manifest(manifest, selected)

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cedc-model-") as tmp:
        root = Path(tmp)
        dest = root / "model"
        dest.mkdir()
        for src in (metadata, selected.data, selected.index, selected.meta, selected.frozen):
            shutil.copy2(src, dest / src.name)

        (dest / "deepracer_checkpoints.json").write_text(json.dumps(normalized_manifest, indent=2, sort_keys=True) + "\n")
        (dest / ".coach_checkpoint").write_text(normalize_coach_checkpoint(model_dir / ".coach_checkpoint", selected))
        (dest / ".ready").touch()

        bundle_meta = {
            "format": "cedc-deepracer-compact-v1",
            "selected_checkpoint": selected.base,
            "iteration": selected.iteration,
            "step": selected.step,
            "selection_reason": reason,
            "manifest_checkpoint_strings_rewritten": changed,
            "files": {p.name: {"size": p.stat().st_size, "sha256": sha256(p)} for p in sorted(dest.iterdir()) if p.is_file()},
        }
        (root / "cedc_submission_manifest.json").write_text(json.dumps(bundle_meta, indent=2, sort_keys=True) + "\n")

        with tarfile.open(output, "w:gz", compresslevel=9) as tf:
            tf.add(dest, arcname="model", recursive=True)
            tf.add(root / "cedc_submission_manifest.json", arcname="cedc_submission_manifest.json")

    size_mb = output.stat().st_size / (1024 * 1024)
    print(f"Selected: {selected.base} ({reason})")
    print(f"Manifest selector strings rewritten: {changed}")
    print(f"Created: {output}")
    print(f"Compressed size: {size_mb:.1f} MB")
    if size_mb > args.max_upload_mb:
        output.unlink(missing_ok=True)
        raise SystemExit(f"Archive exceeds {args.max_upload_mb} MB safety limit for portal/Cloudflare upload.")


if __name__ == "__main__":
    main()
