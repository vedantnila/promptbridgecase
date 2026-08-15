import os
import sys
import json
from http.server import BaseHTTPRequestHandler

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gemini_service import generate_optimized_prompt

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else '{}'
        
        try:
            req_data = json.loads(post_body)
        except Exception:
            req_data = {}

        user_input = req_data.get('input', '').strip()
        if not user_input:
            res_bytes = json.dumps({'error': 'Please provide your request in the input box.'}).encode('utf-8')
            self.send_response(400)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(res_bytes)
            return

        tone = req_data.get('tone', 'Detailed')
        audience = req_data.get('audience', 'Standard')
        api_key = req_data.get('apiKey', '').strip()
        model = req_data.get('model', 'gemini-1.5-flash')

        result = generate_optimized_prompt(
            user_input=user_input,
            custom_api_key=api_key if api_key else None,
            model=model,
            tone=tone,
            audience=audience
        )

        res_bytes = json.dumps(result, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(res_bytes)
