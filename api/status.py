import os
import sys
import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        has_env_key = bool(os.environ.get("GEMINI_API_KEY", "").strip())
        data = {
            "status": "ready",
            "app": "PromptBridge",
            "version": "1.0.0",
            "hasServerApiKey": has_env_key,
            "defaultModel": os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        }
        res_bytes = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(res_bytes)
