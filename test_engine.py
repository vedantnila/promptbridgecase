"""
Verification tests for PromptBridge Multilingual Intent Engine and AI Matchmaker.
"""
import sys

# Ensure UTF-8 output encoding on Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from intent_engine import process_prompt_request, detect_language, categorize_request
from ai_tools_db import get_recommendations_for_category, build_launch_url, AI_TOOLS

def run_tests():
    print("==================================================")
    print("  Running PromptBridge Automated Verification Tests")
    print("==================================================")

    # Test 1: User's primary Marathi example
    marathi_input = "mala college sathi easy arduino project pahije low cost madhe"
    res1 = process_prompt_request(marathi_input)
    
    print("\n[Test 1] Marathi Input:", marathi_input)
    print("Detected Language:", res1["detectedLanguage"])
    print("Category:", res1["category"])
    print("Understood Intent:", res1["understoodIntent"])
    print("Primary Recommended Tool:", res1["recommendedTool"]["name"])
    print("Launch Rationale:", res1["recommendationReason"])
    assert "Marathi" in res1["detectedLanguage"]
    assert res1["category"] == "hardware_engineering"
    assert res1["recommendedTool"]["id"] == "chatgpt"
    assert "Arduino" in res1["optimizedPrompt"]
    assert "Bill of Materials" in res1["optimizedPrompt"] or "Component" in res1["optimizedPrompt"]
    print("[PASS] Test 1 Passed!")

    # Test 2: Hinglish Workplace Email
    hinglish_input = "boss ko fever ke liye leave email likh do professional 2 days"
    res2 = process_prompt_request(hinglish_input)
    print("\n[Test 2] Hinglish Input:", hinglish_input)
    print("Detected Language:", res2["detectedLanguage"])
    print("Category:", res2["category"])
    print("Primary Recommended Tool:", res2["recommendedTool"]["name"])
    assert res2["category"] == "email_communication"
    assert res2["recommendedTool"]["id"] == "claude"
    assert "Subject Line" in res2["optimizedPrompt"]
    print("[PASS] Test 2 Passed!")

    # Test 3: Coding & Scraping
    code_input = "python script to scrape amazon prices to excel"
    res3 = process_prompt_request(code_input)
    print("\n[Test 3] Coding Input:", code_input)
    print("Category:", res3["category"])
    print("Primary Recommended Tool:", res3["recommendedTool"]["name"])
    assert res3["category"] == "coding"
    assert res3["recommendedTool"]["id"] == "chatgpt"
    print("[PASS] Test 3 Passed!")

    # Test 4: Launch URL builder with prefill query
    launch_chatgpt = build_launch_url("chatgpt", "Explain quantum physics simply")
    print("\n[Test 4] ChatGPT Launch Info:", launch_chatgpt)
    assert launch_chatgpt["prefilled"] == True
    assert "https://chatgpt.com/?q=" in launch_chatgpt["url"]

    launch_claude = build_launch_url("claude", "Draft an essay")
    print("Claude Launch Info:", launch_claude)
    assert launch_claude["prefilled"] == False
    assert launch_claude["url"] == "https://claude.ai/new"
    print("[PASS] Test 4 Passed!")

    # Test 5: Visual Art & Midjourney/Ideogram
    image_input = "make 90s vintage anime aesthetic cyber girl portrait wallpaper"
    res5 = process_prompt_request(image_input)
    print("\n[Test 5] Visual Art Input:", image_input)
    print("Category:", res5["category"])
    print("Primary Tool:", res5["recommendedTool"]["name"])
    assert res5["category"] == "image_generation"
    assert res5["recommendedTool"]["id"] == "ideogram"
    print("[PASS] Test 5 Passed!")

    print("\n==================================================")
    print("  ALL 5 VERIFICATION TESTS PASSED SUCCESSFULLY!   ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
