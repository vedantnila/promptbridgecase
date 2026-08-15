"""
PromptBridge HTTP & REST API Server.
Zero-dependency, multi-threaded server serving frontend assets and AI generation endpoints.
"""

import os
import sys

# Ensure UTF-8 output encoding on Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
import mimetypes
from http.server import HTTPServer, ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Import our modular engines
from gemini_service import generate_optimized_prompt, call_gemini_api
from intent_engine import process_prompt_request
from ai_tools_db import AI_TOOLS, CATEGORY_AI_MAPPING, build_launch_url

# Load .env file if it exists
def load_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

load_env()

PORT = int(os.environ.get("PORT", 3000))
PUBLIC_DIR = Path(__file__).parent / "public"

class PromptBridgeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def _send_json(self, data: dict, status_code: int = 200):
        """Helper to send JSON responses."""
        res_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(res_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(res_bytes)

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            has_env_key = bool(os.environ.get("GEMINI_API_KEY", "").strip())
            self._send_json({
                "status": "ready",
                "app": "PromptBridge",
                "version": "1.0.0",
                "hasServerApiKey": has_env_key,
                "defaultModel": os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
            })
            return

        if path == "/api/tools":
            self._send_json({
                "tools": AI_TOOLS,
                "categories": CATEGORY_AI_MAPPING
            })
            return

        # Serve frontend index.html for root path or single page routes
        if path == "/" or not (PUBLIC_DIR / path.lstrip("/")).exists():
            index_file = PUBLIC_DIR / "index.html"
            if index_file.exists():
                with open(index_file, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        # Serve static assets
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        
        try:
            req_data = json.loads(post_body)
        except Exception:
            req_data = {}

        if path == "/api/generate":
            user_input = req_data.get("input", "").strip()
            if not user_input:
                self._send_json({"error": "Please provide your request in the input box."}, status_code=400)
                return

            tone = req_data.get("tone", "Detailed")
            audience = req_data.get("audience", "Standard")
            api_key = req_data.get("apiKey", "").strip()
            model = req_data.get("model", "gemini-1.5-flash")

            result = generate_optimized_prompt(
                user_input=user_input,
                custom_api_key=api_key if api_key else None,
                model=model,
                tone=tone,
                audience=audience
            )
            self._send_json(result)
            return

        if path == "/api/test-key":
            test_key = req_data.get("apiKey", "").strip()
            if not test_key:
                self._send_json({"valid": False, "error": "No API key provided."}, status_code=400)
                return
                
            test_result = call_gemini_api(
                user_input="test hello world",
                api_key=test_key,
                model="gemini-1.5-flash"
            )
            if test_result:
                self._send_json({"valid": True, "message": "API key verified successfully!"})
            else:
                self._send_json({"valid": False, "error": "API key verification failed. Please check the key."})
            return

        if path == "/api/launch-url":
            tool_id = req_data.get("toolId", "chatgpt")
            prompt = req_data.get("prompt", "")
            launch_info = build_launch_url(tool_id, prompt)
            self._send_json(launch_info)
            return

        self._send_json({"error": "Endpoint not found"}, status_code=404)

def run_server():
    server_address = ("", PORT)
    httpd = ThreadingHTTPServer(server_address, PromptBridgeHandler)
    print("=====================================================")
    print(f"  [PromptBridge Server Running] at: http://localhost:{PORT}")
    print("  Tagline: 'You don't need to know how to prompt AI.'")
    print("=====================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down PromptBridge server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
