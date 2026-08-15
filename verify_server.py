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

def post(path, body):
    req = urllib.request.Request(
        f"http://localhost:3000{path}",
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
    res = urllib.request.urlopen("http://localhost:3000/", timeout=5)
    html_content = res.read().decode("utf-8")
    assert res.status == 200
    assert "PromptBridge" in html_content
    assert "You don't need to know how to prompt AI." in html_content
    print("[PASS] 1. Root HTML Serving Verified!")

    # 2. Test Marathi User Flow
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
    print("[PASS] 2. Marathi Request Flow Verified!")

    # 3. Test Short/Broken Intent: "make project on arduino cheap"
    short_res = post("/api/generate", {
        "input": "make project on arduino cheap"
    })
    print("\n[Short / Broken Intent Flow]")
    print("Understood Intent:", short_res["understoodIntent"])
    assert "Arduino" in short_res["optimizedPrompt"]
    assert short_res["category"] == "hardware_engineering"
    print("[PASS] 3. Short / Broken Sentence Intent Extraction Verified!")

    # 4. Test Hinglish Workplace Email
    email_res = post("/api/generate", {
        "input": "boss ko fever ke liye leave email likh do professional 2 din ke liye"
    })
    print("\n[Hinglish Email Flow]")
    print("Understood Intent:", email_res["understoodIntent"])
    print("Top Recommended AI:", email_res["recommendedTool"]["name"])
    assert email_res["category"] == "email_communication"
    assert email_res["recommendedTool"]["id"] == "claude"
    print("[PASS] 4. Hinglish Workplace Communication Flow Verified!")

    # 5. Test AI Tool Launch URLs (Prefill vs Standard)
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

    launch_perp = post("/api/launch-url", {
        "toolId": "perplexity",
        "prompt": "Current stock market trends"
    })
    assert launch_perp["prefilled"] == True
    assert "https://www.perplexity.ai/search?q=" in launch_perp["url"]

    print("[PASS] 5. Tool Launch URLs & Prefill Builders Verified!")

    print("\n==================================================")
    print("  ALL END-TO-END SERVER VERIFICATIONS PASSED!     ")
    print("==================================================")

if __name__ == "__main__":
    main()
