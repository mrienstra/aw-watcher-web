#!/usr/bin/env python3
"""
Tiny local log sink for the #252 vs #260 A/B test (see README.md).

Test builds POST one line per console message to http://127.0.0.1:5699/log;
each line is appended to ab-test/focus-logs/focus-<date>.log (local date).
Listens on 127.0.0.1 only.

Start:  nohup python3 ab-test/log-sink.py >/dev/null 2>&1 &
Stop:   pkill -f ab-test/log-sink.py
"""

from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

LOG_DIR = Path(__file__).resolve().parent / "focus-logs"
LOG_DIR.mkdir(exist_ok=True)
lock = Lock()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        line = self.rfile.read(length).decode("utf-8", "replace").replace("\n", "\\n")
        path = LOG_DIR / f"focus-{datetime.now():%Y-%m-%d}.log"
        with lock, path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        self.send_response(204)
        self.end_headers()

    def log_message(self, *args):
        pass  # no per-request access logging


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 5699), Handler).serve_forever()
