import os
import sys
import json
from http.server import BaseHTTPRequestHandler

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai_tools_db import build_launch_url

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else '{}'
        
        try:
            req_data = json.loads(post_body)
        except Exception:
            req_data = {}

        tool_id = req_data.get('toolId', 'chatgpt')
        prompt = req_data.get('prompt', '')
        launch_info = build_launch_url(tool_id, prompt)

        res_bytes = json.dumps(launch_info).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(res_bytes)
