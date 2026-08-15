"""
Multilingual Intent Parser and Prompt Engineering Synthesis Engine for PromptBridge.
Provides offline intent extraction for Marathi, Hindi, Hinglish, English, and broken sentences.
"""

import re
from typing import Dict, Any, List, Tuple
from ai_tools_db import get_recommendations_for_category, AI_TOOLS

# Linguistic patterns for language detection
MARATHI_INDICATORS = [
    r"\bmala\b", r"\bsathi\b", r"\bpahije\b", r"\bmadhe\b", r"\bkasa\b", r"\bkay\b", 
    r"\bkaraicha\b", r"\bkarnar\b", r"\bsoppa\b", r"\bsope\b", r"\bswastat\b", r"\bkamit\b",
    r"\bkami\b", r"\bhawa\b", r"\bhavi\b", r"\bshikaicha\b", r"\bbolaycha\b", r"\btumhi\b",
    r"\bmajha\b", r"\bmajhi\b", r"\bahe\b", r"\bahot\b", r"\bnavin\b", r"\bkaay\b"
]

HINDI_HINGLISH_INDICATORS = [
    r"\bchahiye\b", r"\bkarna hai\b", r"\bkaise\b", r"\bke liye\b", r"\bbatao\b", 
    r"\bsasta\b", r"\blikh do\b", r"\bsamjha do\b", r"\bseekhna hai\b", r"\bchutti\b",
    r"\bnaukri\b", r"\bbanao\b", r"\bkare\b", r"\bmujhe\b", r"\bmera\b", r"\bmeri\b",
    r"\bhoga\b", r"\bhai\b", r"\bkaro\b", r"\bmadat\b", r"\bjaldi\b", r"\bacha\b", r"\bachha\b"
]

def detect_language(text: str) -> str:
    """Detect natural language used in text."""
    lower = text.lower()
    
    # Check Devanagari script
    if re.search(r"[\u0900-\u097F]", text):
        # Look for Marathi specific Devanagari markers
        if any(w in text for w in ["मला", "पाहिजे", "साठी", "मध्ये", "कसा", "करायचा", "सोपा"]):
            return "Marathi (मराठी Script)"
        return "Hindi / Marathi (Devanagari Script)"
    
    marathi_matches = sum(1 for p in MARATHI_INDICATORS if re.search(p, lower))
    hindi_matches = sum(1 for p in HINDI_HINGLISH_INDICATORS if re.search(p, lower))
    
    if marathi_matches > 0 and marathi_matches >= hindi_matches:
        return "Marathi (Latin / Roman script)"
    elif hindi_matches > 0:
        return "Hinglish (Hindi + English)"
    elif any(c in lower for c in ["plz", "pls", "wat", "bcoz", "ur", "u", "thnx", "pic", "make"]):
        return "Informal English / Mixed"
    return "English"

def categorize_request(text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Categorize user request and extract key entities/constraints.
    """
    lower = text.lower()
    meta: Dict[str, Any] = {
        "is_budget_conscious": False,
        "is_beginner": False,
        "target_entity": "",
        "detected_topics": []
    }
    
    if any(k in lower for k in ["cheap", "low cost", "budget", "swastat", "kami", "sasta", "under 500", "under 1000", "free", "kam kharcha"]):
        meta["is_budget_conscious"] = True
        
    if any(k in lower for k in ["easy", "soppa", "sope", "beginner", "simple", "basic", "starter", "starting"]):
        meta["is_beginner"] = True
        
    if "college" in lower or "school" in lower or "student" in lower or "engineering" in lower:
        meta["audience"] = "College / Student"
    else:
        meta["audience"] = "General / Professional"

    # Hardware & Embedded Systems
    if any(k in lower for k in ["arduino", "esp32", "esp8266", "raspberry pi", "iot", "sensor", "circuit", "microcontroller", "robot", "robotics", "breadboard"]):
        meta["detected_topics"].append("Hardware / Arduino")
        return "hardware_engineering", meta

    # Web Scraping & Coding
    if any(k in lower for k in ["scrape", "scraping", "python", "script", "code", "javascript", "react", "html", "css", "sql", "database", "api", "bug", "algorithm", "github", "pandas", "excel"]):
        meta["detected_topics"].append("Coding / Software")
        return "coding", meta

    # Professional Workplace Emails & Letters
    if any(k in lower for k in ["email", "mail", "leave", "fever", "boss", "resignation", "sick", "chutti", "application", "client", "apology", "manager", "hr"]):
        meta["detected_topics"].append("Workplace Communication")
        return "email_communication", meta

    # Presentations & Slides
    if any(k in lower for k in ["ppt", "presentation", "slide", "slides", "pitch deck", "gamma", "canva", "powerpoint"]):
        meta["detected_topics"].append("Presentation / Slides")
        return "presentation_design", meta

    # Image & Visual Prompts
    if any(k in lower for k in ["image", "photo", "picture", "draw", "portrait", "vintage", "anime", "wallpaper", "logo", "banner", "photorealistic", "illustration", "3d render", "midjourney", "aesthetic"]):
        meta["detected_topics"].append("Visual / Image Generation")
        return "image_generation", meta

    # Content Writing & Social Media
    if any(k in lower for k in ["blog", "article", "post", "linkedin", "tweet", "twitter", "thread", "essay", "caption", "bio", "story", "poem", "content"]):
        meta["detected_topics"].append("Content Creation")
        return "content_writing", meta

    # Research & Academic
    if any(k in lower for k in ["research", "study", "paper", "literature", "thesis", "summary", "fact", "cite", "history", "compare", "difference"]):
        meta["detected_topics"].append("Academic Research")
        return "research_academic", meta

    # Travel & Lifestyle
    if any(k in lower for k in ["travel", "trip", "tour", "goa", "vacation", "itinerary", "hotel", "flight", "workout", "gym", "diet", "weight loss", "meal plan"]):
        meta["detected_topics"].append("Travel & Lifestyle")
        return "travel_lifestyle", meta

    return "general", meta

def synthesize_prompt(user_input: str, category: str, meta: Dict[str, Any], tone: str = "Detailed", audience: str = "Standard") -> Dict[str, Any]:
    """
    Synthesize an optimized, precision-crafted prompt adhering to prompt engineering best practices.
    """
    clean_input = user_input.strip()
    detected_lang = detect_language(clean_input)
    is_budget = meta.get("is_budget_conscious", False)
    is_beginner = meta.get("is_beginner", False)
    
    # 1. Hardware Engineering (e.g., Arduino college projects)
    if category == "hardware_engineering":
        understood = (
            "You are looking for beginner-friendly, budget-conscious Arduino and microcontroller project ideas "
            "suitable for a college engineering submission or hobby build."
        )
        if "arduino" in clean_input.lower():
            optimized = (
                "Act as an expert Embedded Systems Engineer and University Mentor.\n\n"
                "### Objective:\n"
                f"Suggest 3 to 5 practical, beginner-friendly, and cost-effective Arduino project ideas specifically tailored for a college student.\n\n"
                "### Key Constraints & Requirements:\n"
                "- **Budget**: Keep individual project cost under low/moderate component price limits.\n"
                "- **Difficulty Level**: Easy to Moderate (achievable with standard sensors and basic breadboard wiring).\n"
                "- **Components**: Prioritize readily available parts (e.g., Arduino Uno/Nano, Ultrasonic Sensor HC-SR04, DHT11, I2C 16x2 LCD, Servo, Buzzer).\n\n"
                "### Structure the output for EACH project with:\n"
                "1. **Project Title & 1-Sentence Working Principle**\n"
                "2. **Bill of Materials (BOM)** with approximate cost in INR / USD\n"
                "3. **Circuit & Pinout Overview** (Key pin-to-pin connections)\n"
                "4. **Complete, Cleanly Commented Arduino C++ Code** (Ready to copy-paste into Arduino IDE)\n"
                "5. **Viva / Submission Questions & Answers** (3 crucial technical questions an examiner might ask)\n"
                "6. **Bonus / Future Upgrade Suggestions** (e.g., adding IoT / Bluetooth control)"
            )
        else:
            optimized = (
                "Act as an experienced Hardware and IoT Systems Architect.\n\n"
                "### Objective:\n"
                f"Provide a comprehensive, step-by-step implementation guide for the following hardware project requirement:\n"
                f"> \"{clean_input}\"\n\n"
                "### Requirements & Output Format:\n"
                "1. **System Architecture**: Block diagram explanation and microcontrollers required (ESP32/Arduino/Raspberry Pi).\n"
                "2. **Component Checklist**: All required sensors, power supplies, and actuators with estimated budget.\n"
                "3. **Wiring Pinout Table**: Clear pin connection mapping.\n"
                "4. **Working Firmware / Code**: Well-commented, robust code handling sensor calibration and error states.\n"
                "5. **Testing & Troubleshooting**: Common wiring pitfalls and verification steps."
            )

    # 2. Coding & Web Scraping
    elif category == "coding":
        understood = (
            "You need production-ready code with step-by-step instructions, dependency setup, and proper error handling."
        )
        if "scrape" in clean_input.lower() or "price" in clean_input.lower():
            optimized = (
                "Act as a Senior Python Automation and Data Engineer.\n\n"
                "### Objective:\n"
                "Write a modular, clean, and robust Python script to extract product pricing and details, and export the structured dataset.\n\n"
                "### Requirements:\n"
                "- **Libraries**: Use modern libraries (`requests`, `BeautifulSoup4` or `playwright`, and `pandas`).\n"
                "- **Headers & Anti-Bot**: Include realistic User-Agent request headers to prevent immediate IP rate limiting.\n"
                "- **Error Handling**: Handle missing elements, connection timeouts, and HTTP status codes gracefully.\n"
                "- **Output**: Export cleaned records into an Excel file (`.xlsx`) or CSV with columns: `Product_Title`, `Current_Price`, `Rating`, `Timestamp`.\n\n"
                "### Deliverables:\n"
                "1. Dependency installation command (`pip install ...`)\n"
                "2. Fully functional, heavily commented Python source code\n"
                "3. Step-by-step execution guide and compliance/best practice notes on request throttling"
            )
        else:
            optimized = (
                "Act as a Principal Software Engineer and Technical Educator.\n\n"
                "### Objective:\n"
                f"Develop a clean, production-grade solution for the following programming requirement:\n"
                f"> \"{clean_input}\"\n\n"
                "### Code Quality Standards:\n"
                "- **Language & Paradigm**: Modern best practices, type safety / type hints, and PEP8 / idiomatic patterns.\n"
                "- **Robustness**: Include input validation, edge case coverage, and comprehensive error handling.\n"
                "- **Efficiency**: Optimize algorithmic time and space complexity.\n\n"
                "### Output Structure:\n"
                "1. Architecture overview and approach rationale\n"
                "2. Complete, self-contained code snippet\n"
                "3. Example input/output test cases\n"
                "4. Setup and run instructions"
            )

    # 3. Email & Workplace Communication
    elif category == "email_communication":
        understood = (
            "You need a polite, professional, and well-structured workplace communication suitable for sending to your manager or team."
        )
        optimized = (
            "Act as an Executive Business Communications Specialist.\n\n"
            "### Objective:\n"
            f"Draft 2 polished variations of a professional email based on this situation:\n"
            f"> \"{clean_input}\"\n\n"
            "### Provide Two Options:\n"
            "1. **Option A: Concise & Direct** (Ideal for busy managers and fast approvals)\n"
            "2. **Option B: Formal & Detailed** (Includes handoff coverage, contact availability, and formal closing)\n\n"
            "### Email Structure for each:\n"
            "- **Clear Subject Line** (e.g., `Sick Leave Request: [Your Name] – [Date Range]`)\n"
            "- **Salutation**: Professional greeting\n"
            "- **Context & Dates**: Unambiguous dates, reason, and expected return\n"
            "- **Workflow Coverage**: Brief mention of task delegation or emergency reachable contact\n"
            "- **Sign-off**: Professional signature placeholders `[Your Full Name]`, `[Employee ID]`, `[Designation]`"
        )

    # 4. Presentation & Slides
    elif category == "presentation_design":
        understood = (
            "You need an engaging, slide-by-slide presentation outline with visual layout notes and talking points ready for Gamma or Canva."
        )
        optimized = (
            "Act as a World-Class Keynote Designer and Presentation Strategist.\n\n"
            "### Objective:\n"
            f"Create a high-impact, 7 to 10 slide presentation deck outline for:\n"
            f"> \"{clean_input}\"\n\n"
            "### For EACH Slide, provide:\n"
            "1. **Slide Number & Catchy Headline**\n"
            "2. **Visual Concept & Layout**: Exact layout suggestion (e.g., 3-column feature cards, split screen, big metric callout)\n"
            "3. **On-Slide Bullet Points**: Concise, impactful text (maximum 3-4 bullet points per slide)\n"
            "4. **Speaker Notes**: 2-3 sentences of spoken commentary to guide the presenter\n\n"
            "### Tone & Style:\n"
            "- Professional, modern, and data-driven\n"
            "- Formatted in markdown so it can be directly imported into AI presentation builders like **Gamma.app**"
        )

    # 5. Image Generation
    elif category == "image_generation":
        understood = (
            "You need a rich, descriptive visual art prompt optimized for Midjourney, Ideogram, or DALL-E."
        )
        optimized = (
            "Generate a series of high-detail image synthesis prompts for Midjourney v6 and Ideogram based on:\n"
            f"> \"{clean_input}\"\n\n"
            "### Primary Image Prompt:\n"
            f"A masterwork visual composition of {clean_input}, captured with 35mm cinematic lens, intricate textures, dramatic volumetric lighting, 8k resolution, photorealistic rendering, soft depth of field, color graded in warm cinematic tones, Unreal Engine 5 render style --ar 16:9 --v 6.0 --style raw\n\n"
            "### Alternative Styles Provided:\n"
            "1. **Cinematic Photorealism**: (Lighting, camera angle, aperture, shutter speed)\n"
            "2. **Stylized 90s Vintage / Anime Aesthetic**: (Retro film grain, cel-shaded highlights, vibrant pastel palette)\n"
            "3. **Minimalist Vector / Graphic Design**: (Clean flat contours, bold typography, iconic silhouette)\n\n"
            "### Recommended Negative Prompt:\n"
            "`blurry, distorted hands, extra limbs, low resolution, deformed anatomy, watermark, text noise, artifacts`"
        )

    # 6. Content Writing
    elif category == "content_writing":
        understood = (
            "You need compelling, high-converting content with a strong hook, structured readability, and clear call-to-action."
        )
        optimized = (
            "Act as an Award-Winning Copywriter and Content Strategist.\n\n"
            "### Objective:\n"
            f"Write high-engagement content based on the following topic:\n"
            f"> \"{clean_input}\"\n\n"
            "### Key Structural Guidelines:\n"
            "- **The Hook**: An irresistible opening line that immediately grabs attention.\n"
            "- **Body Structure**: Use short, punchy paragraphs, bullet points, and subheaders for scannability.\n"
            "- **Voice & Tone**: Authentic, insightful, and conversational (avoid generic AI buzzwords like 'game-changer', 'delve', or 'tapestry').\n"
            "- **Call To Action (CTA)**: A provocative closing question or next step that encourages comments and shares."
        )

    # 7. Research & Academic
    elif category == "research_academic":
        understood = (
            "You need an in-depth, well-researched synthesis with factual evidence, structured comparisons, and verified sources."
        )
        optimized = (
            "Act as a Senior Research Fellow and Academic Analyst.\n\n"
            "### Objective:\n"
            f"Provide a rigorous, unbiased, and comprehensive breakdown of the following subject:\n"
            f"> \"{clean_input}\"\n\n"
            "### Required Sections:\n"
            "1. **Executive Summary**: Core thesis and key takeaways in 3 concise points.\n"
            "2. **Detailed Analytical Breakdown**: Deep-dive into fundamental mechanisms, historical context, and current developments.\n"
            "3. **Comparative Analysis Table**: Side-by-side comparison of leading methodologies, pros, cons, and trade-offs.\n"
            "4. **Key Debates & Open Challenges**: Emerging controversies, limitations, or future trajectories.\n"
            "5. **Recommended Reading & Reference Directions**"
        )

    # 8. Travel & Lifestyle
    elif category == "travel_lifestyle":
        understood = (
            "You need a realistic, day-by-day plan with cost breakdowns, local tips, and time-managed logistics."
        )
        optimized = (
            "Act as a Seasoned Local Travel Guide and Itinerary Planner.\n\n"
            "### Objective:\n"
            f"Design a realistic, budget-friendly day-by-day itinerary for:\n"
            f"> \"{clean_input}\"\n\n"
            "### Details to Include for EACH Day:\n"
            "- **Morning / Afternoon / Evening Breakdown**: Well-paced activities without exhausting travel times.\n"
            "- **Transportation Advice**: Most cost-effective ways to commute (scooter rental, metro, local cabs).\n"
            "- **Food & Dining Recommendations**: Must-try local culinary spots for budget and authentic meals.\n"
            "- **Estimated Expense Table**: Approximate breakdown for Stay, Food, Transport, and Entry Tickets.\n"
            "- **Safety & Insider Pro-Tips**: Best times to avoid crowds and money-saving hacks."
        )

    # 9. General / Brainstorming
    else:
        understood = (
            f"You want a clear, well-structured explanation and actionable guidance for: '{clean_input}'."
        )
        optimized = (
            "Act as an expert Advisor and Master Communicator.\n\n"
            "### Goal:\n"
            f"Provide a structured, easy-to-follow, and deeply informative response for:\n"
            f"> \"{clean_input}\"\n\n"
            "### Instructions:\n"
            "- Break down the concept into intuitive, step-by-step explanations.\n"
            "- Provide concrete real-world examples and analogies.\n"
            "- Highlight practical tips, potential pitfalls to avoid, and immediate next steps.\n"
            "- Use clear formatting with headers, bullet points, and bold text for key takeaways."
        )

    # Fetch AI Recommendations
    rec = get_recommendations_for_category(category)
    
    highlights = [
        "Identified underlying intent & domain context",
        f"Detected language: {detected_lang}",
        "Assigned targeted expert persona & role",
        "Applied structured output schema & constraints"
    ]
    
    return {
        "detectedLanguage": detected_lang,
        "category": category,
        "understoodIntent": understood,
        "optimizedPrompt": optimized,
        "recommendedTool": rec["primary"],
        "alternativeTools": rec["alternatives"],
        "recommendationReason": rec["reason"],
        "highlights": highlights,
        "source": "Multilingual Intent Engine"
    }

def process_prompt_request(raw_text: str, tone: str = "Detailed", audience: str = "Standard") -> Dict[str, Any]:
    """Top-level handler for offline generation."""
    category, meta = categorize_request(raw_text)
    return synthesize_prompt(raw_text, category, meta, tone=tone, audience=audience)
