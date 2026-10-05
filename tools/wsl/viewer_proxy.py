"""Fixed address for the training simulator's live video: http://localhost:18080/ (from Windows too).

DRfC (compose mode) publishes the simulator's web video server on any free port in 8080-8089, and
it moves when the simulator restarts. This forwards each connection to wherever it is right now.
usage: python3 tools/wsl/viewer_proxy.py [listen-port=18080] [container=deepracer-0-robomaker-1]
"""
import asyncio
import subprocess
import sys

LISTEN = int(sys.argv[1]) if len(sys.argv) > 1 else 18080
CONTAINER = sys.argv[2] if len(sys.argv) > 2 else "deepracer-0-robomaker-1"


def current_port():
    """The given container, else any running simulator (training or evaluation)."""
    names = [CONTAINER] + sorted(subprocess.run(["docker", "ps", "--filter", "name=robomaker", "--format", "{{.Names}}"],
                                                capture_output=True, text=True).stdout.split())
    for name in names:
        out = subprocess.run(["docker", "port", name, "8080/tcp"], capture_output=True, text=True).stdout
        if out:
            return int(out.split("\n")[0].rsplit(":", 1)[1])
    return None


async def pipe(reader, writer):
    try:
        while data := await reader.read(65536):
            writer.write(data)
            await writer.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass
    finally:
        writer.close()


async def handle(client_r, client_w):
    port = current_port()
    if port is None:
        client_w.write(b"HTTP/1.0 503 Service Unavailable\r\n\r\nsimulator not running (restarting?) - retry in a minute\n")
        client_w.close()
        return
    try:
        sim_r, sim_w = await asyncio.open_connection("127.0.0.1", port)
    except OSError:
        client_w.close()
        return
    await asyncio.gather(pipe(client_r, sim_w), pipe(sim_r, client_w))


async def main():
    server = await asyncio.start_server(handle, "0.0.0.0", LISTEN)
    print(f"viewer on http://localhost:{LISTEN}/")
    async with server:
        await server.serve_forever()


asyncio.run(main())
