#!/usr/bin/env python3
"""
Minimal server for FN Bulovka calendar.
Serves static files + stores event notes in notes.json and drive links in drives.json.
"""

import json, os, http.server, socketserver

PORT = 50895
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_FILE = os.path.join(BASE_DIR, "notes.json")
DRIVES_FILE = os.path.join(BASE_DIR, "drives.json")

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _json_response(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _handle_get_store(self, filepath):
        self._json_response(load_json(filepath))

    def _handle_post_store(self, filepath):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        key = body.get("key", "")
        value = body.get("value", "")
        store = load_json(filepath)
        if value:
            store[key] = value
        else:
            store.pop(key, None)
        save_json(filepath, store)
        self._json_response({"ok": True})

    def do_GET(self):
        if self.path == "/api/notes":
            self._handle_get_store(NOTES_FILE)
        elif self.path == "/api/drives":
            self._handle_get_store(DRIVES_FILE)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/notes":
            self._handle_post_store(NOTES_FILE)
        elif self.path == "/api/drives":
            self._handle_post_store(DRIVES_FILE)
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        if "/api/" in (args[0] if args else ""):
            super().log_message(format, *args)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"FN Bulovka server running on http://localhost:{PORT}")
        httpd.serve_forever()
