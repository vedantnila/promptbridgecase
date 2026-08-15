import os
import sys
import json
from http.server import BaseHTTPRequestHandler

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gemini_service import call_gemini_api

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

        test_key = req_data.get('apiKey', '').strip()
        if not test_key:
            res_bytes = json.dumps({"valid": False, "error": "No API key provided."}).encode('utf-8')
            self.send_response(400)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(res_bytes)
            return

        test_result = call_gemini_api(
            user_input="test hello world",
            api_key=test_key,
            model="gemini-1.5-flash"
        )

        if test_result:
            res_bytes = json.dumps({"valid": True, "message": "API key verified successfully!"}).encode('utf-8')
        else:
            res_bytes = json.dumps({"valid": False, "error": "API key verification failed. Please check the key."}).encode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(res_bytes)
