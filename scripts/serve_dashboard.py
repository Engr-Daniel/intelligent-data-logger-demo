"""Local-only dashboard. Run: python scripts/serve_dashboard.py"""
from __future__ import annotations

import argparse
import json
import secrets
import sys
import threading
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# Support this workspace's local dependency installation without changing global Python.
local = ROOT / ".venv/Lib/site-packages"
if local.exists():
    sys.path.insert(0, str(local))

from src.interface.web_service import Conversation, dashboard

STATIC = ROOT / "src/interface/static"


class Handler(BaseHTTPRequestHandler):
    sessions = {}
    sessions_lock = threading.Lock()

    def log_message(self, *_):
        pass  # Questions and credentials never enter access logs.

    def send(self, body, content_type="application/json", code=200, cookie=None):
        try:
            self._send(body, content_type, code, cookie)
        except ConnectionError:
            pass  # A closed browser tab does not need an error response or traceback.

    def _send(self, body, content_type="application/json", code=200, cookie=None):
        if not isinstance(body, bytes):
            body = json.dumps(body, allow_nan=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
        if cookie:
            self.send_header("Set-Cookie", f"logger_session={cookie}; HttpOnly; SameSite=Strict; Path=/")
        self.end_headers()
        self.wfile.write(body)

    def valid_origin(self):
        expected = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        origin = self.headers.get("Origin")
        return (self.headers.get("Host") in expected and
                (origin is None or origin in {"http://" + h for h in expected}))

    def session(self):
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        sid = cookie["logger_session"].value if "logger_session" in cookie else None
        with self.sessions_lock:
            if sid not in self.sessions:
                if len(self.sessions) >= 100:
                    raise ValueError("Session limit reached. Restart the local server.")
                sid = secrets.token_urlsafe(24)
                self.sessions[sid] = (Conversation(), threading.Lock())
            return sid, self.sessions[sid]

    def do_GET(self):
        if not self.valid_origin():
            return self.send({"error": "Local access only."}, code=403)
        parts = urlsplit(self.path)
        files = {"/": ("index.html", "text/html; charset=utf-8"),
                 "/app.css": ("app.css", "text/css"), "/app.js": ("app.js", "text/javascript")}
        try:
            if parts.path in files:
                name, mime = files[parts.path]
                return self.send((STATIC / name).read_bytes(), mime)
            if parts.path == "/api/dashboard":
                return self.send(dashboard(parse_qs(parts.query).get("day", [None])[0]))
            if parts.path in ("/api/session", "/api/export"):
                sid, (conversation, lock) = self.session()
                with lock:
                    result = conversation.export() if parts.path.endswith("export") else {
                        "turns": conversation.turns, "mode": conversation.mode}
                return self.send(result, cookie=sid)
            self.send({"error": "Not found"}, code=404)
        except ValueError as exc:
            self.send({"error": str(exc)}, code=400)
        except Exception:
            self.send({"error": "Unable to load telemetry. Check that the demo dataset has been generated."}, code=500)

    def do_POST(self):
        if not self.valid_origin() or self.headers.get("Content-Type") != "application/json":
            return self.send({"error": "Invalid local request."}, code=403)
        try:
            length = int(self.headers.get("Content-Length", 0))
            if not 0 < length <= 12000:
                raise ValueError("Request is too large or empty.")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("Expected a JSON object.")
            sid, (conversation, lock) = self.session()
            if not lock.acquire(blocking=False):
                return self.send({"error": "An analysis is already running."}, code=409)
            try:
                if self.path == "/api/ask":
                    result = conversation.ask(payload.get("question"), payload.get("mode", "offline"))
                elif self.path == "/api/reset":
                    conversation.__init__()
                    result = {"ok": True}
                else:
                    return self.send({"error": "Not found"}, code=404)
            finally:
                lock.release()
            self.send(result, cookie=sid)
        except (ValueError, json.JSONDecodeError) as exc:
            self.send({"error": str(exc)}, code=400)
        except Exception:
            self.send({"error": "The request could not complete. Please retry."}, code=500)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Intelligent Data Logger: http://127.0.0.1:{args.port} (synthetic demo; offline by default)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
