"""
Google Gemini API integration service for PromptBridge.
Provides LLM-powered prompt generation with automatic fallback.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from ai_tools_db import AI_TOOLS, CATEGORY_AI_MAPPING, get_recommendations_for_category
from intent_engine import process_prompt_request

SYSTEM_PROMPT = """
You are PromptBridge's Intent-to-Prompt Engine.
Your mission is to help people who don't know how to prompt AI. Users type in their own simple words, including Marathi, Hindi, Hinglish, mixed dialects, broken English, spelling/grammar mistakes, or short sentences.

IMPORTANT RULES:
1. NEVER just correct grammar. Extract the TRUE INTENT and real-world goal behind what the user wants.
   For example: "mala college sathi easy arduino project pahije low cost madhe" means:
   - Language: Marathi (Roman script)
   - Category: hardware_engineering
   - Intent: The user is a college student needing beginner-friendly, affordable Arduino engineering project ideas.
   - Optimized Prompt: A comprehensive prompt specifying Role (Embedded Systems Mentor), Objective, Constraints (low budget, accessible components), Detailed Output Requirements (BOM, Pinout, Code, Viva questions, Future upgrades).

2. Return ONLY a valid JSON object (no markdown code blocks, no backticks, just raw JSON) matching this schema:
{
  "detectedLanguage": "Marathi / Hinglish / Hindi / English / etc.",
  "category": "hardware_engineering | coding | email_communication | presentation_design | image_generation | content_writing | research_academic | travel_lifestyle | general",
  "understoodIntent": "1-2 sentence friendly summary of what the user wants in clear English",
  "optimizedPrompt": "The complete, highly structured, precision prompt formatted with markdown headers and sections (Role, Objective, Context, Constraints, Deliverables)",
  "recommendedToolKey": "chatgpt | claude | perplexity | gemini | gamma | ideogram | canva | cursor",
  "alternativeToolKeys": ["claude", "perplexity"],
  "taskMatchReason": "Clear reason why this AI tool is best suited for this task",
  "highlights": ["Role framing applied", "Contextual constraints added", "Structured output schema enforced", "Viva/troubleshooting steps included"]
}
"""

def call_gemini_api(user_input: str, api_key: str, model: str = "gemini-1.5-flash", tone: str = "Detailed", audience: str = "Standard") -> Optional[Dict[str, Any]]:
    """Call Gemini REST API to generate prompt and intent."""
    if not api_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    user_message = f"User Request: \"{user_input}\"\nTone Preference: {tone}\nTarget Audience: {audience}\n\nPlease analyze intent, synthesize the optimized prompt, and recommend the best AI tools."

    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_message}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "response_mime_type": "application/json"
        }
    }

    try:
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            
            candidates = res_json.get("candidates", [])
            if not candidates:
                return None
                
            content_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            # Clean up response text if enclosed in backticks
            clean_text = content_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            parsed_data = json.loads(clean_text)
            
            # Enrich with tool objects from AI_TOOLS
            primary_key = parsed_data.get("recommendedToolKey", "chatgpt").lower()
            primary_tool = AI_TOOLS.get(primary_key, AI_TOOLS["chatgpt"])
            
            alt_keys = parsed_data.get("alternativeToolKeys", ["gemini", "claude"])
            alt_tools = [AI_TOOLS[k.lower()] for k in alt_keys if k.lower() in AI_TOOLS]
            if not alt_tools:
                alt_tools = [AI_TOOLS["claude"], AI_TOOLS["gemini"]]
                
            return {
                "detectedLanguage": parsed_data.get("detectedLanguage", "Multilingual"),
                "category": parsed_data.get("category", "general"),
                "understoodIntent": parsed_data.get("understoodIntent", "Understood user request"),
                "optimizedPrompt": parsed_data.get("optimizedPrompt", ""),
                "recommendedTool": primary_tool,
                "alternativeTools": alt_tools,
                "recommendationReason": parsed_data.get("taskMatchReason", primary_tool["bestFor"]),
                "highlights": parsed_data.get("highlights", ["Intent recognized", "Context expanded"]),
                "source": "Gemini Live LLM"
            }
    except Exception as e:
        print(f"[Gemini Service Warning] API call failed: {e}. Falling back to offline intent engine.")
        return None

def generate_optimized_prompt(user_input: str, custom_api_key: Optional[str] = None, model: str = "gemini-1.5-flash", tone: str = "Detailed", audience: str = "Standard") -> Dict[str, Any]:
    """
    Main generator function:
    Tries Gemini API first if key exists, then falls back seamlessly to Intent Engine.
    """
    api_key = custom_api_key or os.environ.get("GEMINI_API_KEY", "").strip()
    
    if api_key:
        llm_result = call_gemini_api(user_input, api_key, model=model, tone=tone, audience=audience)
        if llm_result:
            return llm_result

    # Fallback to smart offline multilingual intent engine
    return process_prompt_request(user_input, tone=tone, audience=audience)
