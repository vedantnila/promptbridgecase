"""
Comprehensive End-to-End Server Verification for PromptBridge.
"""
import sys
import json
import urllib.request

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:3000"

def post(path, body):
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        return json.loads(res.read().decode("utf-8"))

def main():
    print("==================================================")
    print("  Testing PromptBridge Live HTTP Server Endpoints ")
    print("==================================================")

    # 1. Test HTML Page Serving
    res = urllib.request.urlopen(f"{BASE_URL}/", timeout=5)
    html_content = res.read().decode("utf-8")
    assert res.status == 200
    assert "PromptBridge" in html_content
    assert "You don't need to know how to prompt AI." in html_content
    print("[PASS] 1. Root HTML Serving Verified!")

    # 2. Test CSS and JS Serving
    css_res = urllib.request.urlopen(f"{BASE_URL}/css/style.css", timeout=5)
    assert css_res.status == 200
    assert len(css_res.read()) > 0
    print("[PASS] 2. CSS Asset Serving Verified!")

    js_res = urllib.request.urlopen(f"{BASE_URL}/js/app.js", timeout=5)
    assert js_res.status == 200
    assert len(js_res.read()) > 0
    print("[PASS] 3. JS Asset Serving Verified!")

    # 3. Test Marathi User Flow
    marathi_res = post("/api/generate", {
        "input": "mala college sathi easy arduino project pahije low cost madhe"
    })
    print("\n[Marathi Flow Response]")
    print("Language Detected:", marathi_res["detectedLanguage"])
    print("Understood Intent:", marathi_res["understoodIntent"])
    print("Top Recommended AI:", marathi_res["recommendedTool"]["name"])
    assert "Marathi" in marathi_res["detectedLanguage"]
    assert marathi_res["category"] == "hardware_engineering"
    assert marathi_res["recommendedTool"]["id"] == "chatgpt"
    print("[PASS] 4. Marathi Request Flow Verified!")

    # 4. Test Short/Broken Intent: "make project on arduino cheap"
    short_res = post("/api/generate", {
        "input": "make project on arduino cheap"
    })
    print("\n[Short / Broken Intent Flow]")
    print("Understood Intent:", short_res["understoodIntent"])
    assert "Arduino" in short_res["optimizedPrompt"]
    assert short_res["category"] == "hardware_engineering"
    print("[PASS] 5. Short / Broken Sentence Intent Extraction Verified!")

    # 5. Test Hinglish Workplace Email
    email_res = post("/api/generate", {
        "input": "boss ko fever ke liye leave email likh do professional 2 din ke liye"
    })
    print("\n[Hinglish Email Flow]")
    print("Understood Intent:", email_res["understoodIntent"])
    print("Top Recommended AI:", email_res["recommendedTool"]["name"])
    assert email_res["category"] == "email_communication"
    assert email_res["recommendedTool"]["id"] == "claude"
    print("[PASS] 6. Hinglish Workplace Communication Flow Verified!")

    # 6. Test AI Tool Launch URLs (Prefill vs Standard)
    launch_chatgpt = post("/api/launch-url", {
        "toolId": "chatgpt",
        "prompt": "Optimize Arduino Code"
    })
    assert launch_chatgpt["prefilled"] == True
    assert "https://chatgpt.com/?q=" in launch_chatgpt["url"]

    launch_claude = post("/api/launch-url", {
        "toolId": "claude",
        "prompt": "Review Essay"
    })
    assert launch_claude["prefilled"] == False
    assert launch_claude["url"] == "https://claude.ai/new"

    print("[PASS] 7. Tool Launch URLs & Prefill Builders Verified!")

    print("\n==================================================")
    print("  ALL END-TO-END SERVER VERIFICATIONS PASSED!     ")
    print("==================================================")

if __name__ == "__main__":
    main()
