"""Training dashboard in the browser: live video + per-iteration progress, http://localhost:18081/

The video is relayed from the simulator's web video server (its port moves on every restart, see
tools/wsl/viewer_proxy.py), the table comes from tools/progress.py.
usage: python3 tools/dashboard.py [run-prefix=current run's base] [port=18081]
"""
import html
import re
import subprocess
import sys
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from progress import report  # noqa: E402

PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 18081
RUN_ENV = Path.home() / "deepracer-for-cloud" / "run.env"


def base() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    m = re.search(r"^DR_LOCAL_S3_MODEL_PREFIX=(.*)$", RUN_ENV.read_text(), re.M)
    # cedc-m11-jason-vegas1-2 -> cedc-m11-jason (every leg of the rotation)
    return re.sub(r"-[a-z]+\d+(-\d+)?$", "", m[1].strip()) if m else "cedc-"


def sim_port():
    """Host port of the running simulator's video server: training (deepracer-0-robomaker-*) or
    evaluation (deepracer-eval-0-robomaker-*), whichever is up."""
    names = subprocess.run(["docker", "ps", "--filter", "name=robomaker", "--format", "{{.Names}}"],
                           capture_output=True, text=True).stdout.split()
    for name in sorted(names):
        out = subprocess.run(["docker", "port", name, "8080/tcp"], capture_output=True, text=True).stdout
        if out:
            return out.split("\n")[0].rsplit(":", 1)[1]
    return None


def status() -> str:
    try:
        return subprocess.run(["bash", "/tmp/simstatus.sh"], capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return f"status unavailable: {e}"


PAGE = """<title>DeepRacer training</title>
<style>
body{margin:0;padding:16px;background:#111;color:#ddd;font:14px system-ui,sans-serif}
h1{font-size:18px;margin:0 0 12px} .row{display:flex;gap:16px;flex-wrap:wrap}
.cam{flex:1 1 420px;max-width:640px} .cam img{width:100%;background:#000;border:1px solid #333;min-height:200px}
pre{flex:1 1 420px;margin:0;overflow-x:auto;background:#000;padding:12px;border:1px solid #333;font-size:12px}
.small{color:#888;font-size:12px}
</style>
<h1>DeepRacer training</h1>
<div class=row>
 <div class=cam>
  <img id=v alt="video: simulator restarting or viewer_proxy.py not running">
  <div class=small>Live race view (no reward overlay). Goes blank while the simulator restarts or an evaluation switches track; reloads itself.</div>
  <img id=c alt="">
  <div class=small>Car camera: what the model sees (domain randomization changes lighting/colours).</div>
 </div>
 <pre id=t>loading…</pre>
</div>
<script>
const cam = t => `/stream?topic=${t}&width=480&height=360&quality=60&t=${Date.now()}`;
const v = document.getElementById('v'), c = document.getElementById('c');
// raw camera topics: published in training and evaluation (the kvs/main_camera_stream overlays are training-only)
function video(){ v.src = cam('/racecar/main_camera/zed/rgb/image_rect_color'); c.src = cam('/racecar/camera/zed/rgb/image_rect_color'); }
v.onerror = c.onerror = () => setTimeout(video, 15000);
video(); setInterval(video, 300000);  // reconnect every 5 min (simulator restarts drop the stream)
async function table(){ try { document.getElementById('t').textContent = await (await fetch('/text')).text(); } catch(e) {} }
table(); setInterval(table, 30000);
</script>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/stream"):
            return self.relay()
        if self.path.startswith("/text"):
            body = f"{status()}\n\n{report(base())}\n\n(table updates every ~2 min, when the supervisor saves logs)"
            ctype = "text/plain; charset=utf-8"
        else:
            body, ctype = PAGE, "text/html; charset=utf-8"
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def relay(self):  # copy the simulator's MJPEG stream through (same origin and port as the page)
        port = sim_port()
        try:
            src = urllib.request.urlopen(f"http://127.0.0.1:{port}{self.path}", timeout=10) if port else None
        except OSError:
            src = None
        if src is None:
            self.send_error(503, "simulator not running (restarting?)")
            return
        self.send_response(200)
        self.send_header("Content-Type", src.headers.get("Content-Type", "multipart/x-mixed-replace"))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            while chunk := src.read1(65536):
                self.wfile.write(chunk)
        except (OSError, ConnectionError):
            pass
        finally:
            src.close()

    def log_message(self, *args):
        pass


print(f"dashboard on http://localhost:{PORT}/ ({time.strftime('%H:%M')})", flush=True)
ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
