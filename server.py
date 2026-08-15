"""
PromptBridge HTTP & REST API Server.
Zero-dependency, multi-threaded server serving frontend assets and AI generation endpoints.
Compatible with local development and Vercel Serverless runtime.
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
import traceback
import mimetypes
from http.server import HTTPServer, ThreadingHTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
os.chdir(str(ROOT_DIR))

# Import our modular engines
from gemini_service import generate_optimized_prompt, call_gemini_api
from intent_engine import process_prompt_request
from ai_tools_db import AI_TOOLS, CATEGORY_AI_MAPPING, build_launch_url

# Load .env file if it exists
def load_env():
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

load_env()

PORT = int(os.environ.get("PORT", 3000))

class PromptBridgeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        if "directory" not in kwargs:
            kwargs["directory"] = str(ROOT_DIR)
        super().__init__(*args, **kwargs)

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
        try:
            self.wfile.flush()
        except Exception:
            pass

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        try:
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

            # Explicit root serving
            if path in ["/", "/index.html"]:
                index_path = ROOT_DIR / "index.html"
                if not index_path.exists():
                    index_path = ROOT_DIR / "public" / "index.html"
                with open(index_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                try:
                    self.wfile.flush()
                except Exception:
                    pass
                return

            # Serve static assets
            super().do_GET()
        except Exception as e:
            print(f"[Error in do_GET]: {e}")
            traceback.print_exc()

    def do_POST(self):
        try:
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

            if path in ["/api/test-key", "/api/test_key"]:
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

            if path in ["/api/launch-url", "/api/launch_url"]:
                tool_id = req_data.get("toolId", "chatgpt")
                prompt = req_data.get("prompt", "")
                launch_info = build_launch_url(tool_id, prompt)
                self._send_json(launch_info)
                return

            self._send_json({"error": "Endpoint not found"}, status_code=404)
        except Exception as e:
            print(f"[Error in do_POST]: {e}")
            traceback.print_exc()

# Top-level exports for Vercel Serverless Entrypoint detection
handler = PromptBridgeHandler
app = PromptBridgeHandler
application = PromptBridgeHandler

def run_server():
    server_address = ("127.0.0.1", PORT)
    httpd = ThreadingHTTPServer(server_address, PromptBridgeHandler)
    print("=====================================================", flush=True)
    print(f"  [PromptBridge Server Running] at: http://127.0.0.1:{PORT}", flush=True)
    print("  Tagline: 'You don't need to know how to prompt AI.'", flush=True)
    print("=====================================================", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down PromptBridge server...", flush=True)
        httpd.server_close()

if __name__ == "__main__":
    run_server()
