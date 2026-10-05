"""Serve and inspect the actual production bundle without provider or database calls."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from threading import Thread
import httpx


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "frontend/dist"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    assert (DIST / "index.html").is_file(), "Run npm run build first."
    rules = json.loads((ROOT / "frontend/vercel.json").read_text())["rewrites"]
    source = next(r["source"] for r in rules if r["destination"] == "/index.html")
    files = list((DIST / "assets").glob("*.js")) + list((DIST / "assets").glob("*.css"))
    assert files and any("AssistantWidget" in p.name for p in files)
    scripts = "\n".join(p.read_text(encoding="utf-8") for p in files if p.suffix == ".js")
    assert "pr-robot" in scripts and "codex-clipboard" not in scripts
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(DIST)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with httpx.Client(base_url=base) as client:
            assert client.get("/").status_code == 200
            for path in files:
                route = "/" + path.relative_to(DIST).as_posix()
                assert not re.fullmatch(source, route), f"Vercel would rewrite asset {route}"
                response = client.get(route)
                assert response.status_code == 200 and not response.headers["content-type"].startswith("text/html")
                assert response.content == path.read_bytes()
        print(f"PASS: {len(files)} production JS/CSS assets served unchanged; widget lazy chunk and inline SVG present; /assets/ excluded from SPA rewrite.")
        print("Local production-bundle verification only; Vercel deployment not claimed.")
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    main()
