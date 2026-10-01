#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, tarfile
from pathlib import PurePosixPath

CKPT_INDEX_RE = re.compile(r"(?P<base>(?P<iter>\d+)_Step-\d+)\.ckpt\.index$")


def validate(path, max_expanded_mb=600):
    with tarfile.open(path, "r:gz") as tf:
        members = tf.getmembers()
        if len(members) > 100:
            raise ValueError("compact bundle contains too many entries")
        files = set()
        total = 0
        for m in members:
            p = PurePosixPath(m.name)
            if p.is_absolute() or ".." in p.parts:
                raise ValueError(f"unsafe path: {m.name}")
            if not (m.isfile() or m.isdir()):
                raise ValueError(f"unsupported special archive entry: {m.name}")
            if m.isfile():
                total += m.size
                if total > max_expanded_mb * 1024 * 1024:
                    raise ValueError(f"archive expands beyond {max_expanded_mb} MB")
                files.add(m.name.lstrip("./"))

        required = {"model/model_metadata.json", "model/deepracer_checkpoints.json", "model/.coach_checkpoint", "model/.ready"}
        missing = required - files
        if missing:
            raise ValueError("missing required file(s): " + ", ".join(sorted(missing)))

        indexes = [x for x in files if x.startswith("model/") and x.endswith(".ckpt.index")]
        if len(indexes) != 1:
            raise ValueError(f"expected exactly one checkpoint index, found {len(indexes)}")
        m = CKPT_INDEX_RE.search(indexes[0].split("/",1)[1])
        if not m:
            raise ValueError("checkpoint index has unexpected name")
        base = m.group("base")
        iteration = m.group("iter")
        peers = {
            f"model/{base}.ckpt.meta",
            f"model/model_{iteration}.pb",
        }
        for peer in peers:
            if peer not in files:
                raise ValueError(f"missing matching checkpoint artifact: {peer}")
        data = [x for x in files if x.startswith(f"model/{base}.ckpt.data-")]
        if len(data) != 1:
            raise ValueError("expected exactly one matching checkpoint data shard")

        meta = None
        if "cedc_submission_manifest.json" in files:
            f = tf.extractfile("cedc_submission_manifest.json")
            if f:
                meta = json.load(f)
                if meta.get("format") != "cedc-deepracer-compact-v1":
                    raise ValueError("unknown CEDC bundle format")
                if meta.get("selected_checkpoint") != base:
                    raise ValueError("CEDC manifest checkpoint does not match bundle files")
        return {"checkpoint": base, "iteration": int(iteration), "expanded_bytes": total, "metadata": meta}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("archive")
    ap.add_argument("--max-expanded-mb", type=int, default=600)
    a=ap.parse_args()
    info=validate(a.archive, a.max_expanded_mb)
    print(json.dumps({"ok": True, **info}, indent=2))

if __name__ == "__main__": main()
