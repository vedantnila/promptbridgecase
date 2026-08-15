"""
AI Tools Database and Matchmaker logic for PromptBridge.
Provides tool metadata, strengths, prefill URL builders, and categorization.
"""

from typing import Dict, Any, List

AI_TOOLS: Dict[str, Dict[str, Any]] = {
    "chatgpt": {
        "id": "chatgpt",
        "name": "ChatGPT",
        "developer": "OpenAI",
        "badge": "🥇 Best for General & Coding",
        "icon": "🤖",
        "primaryColor": "#10a37f",
        "bestFor": "General questions, coding, debugging, step-by-step explanations, and interactive brainstorming",
        "keyStrengths": [
            "World-class coding and hardware prototyping assistance",
            "Deep logical reasoning and structured problem solving",
            "Fast conversational iteration and clarification"
        ],
        "baseUrl": "https://chatgpt.com/",
        "prefillParam": "q",  # ChatGPT supports ?q=prompt
        "supportsPrefill": True,
        "categories": ["coding", "hardware_engineering", "general", "content_writing", "email_communication", "travel_lifestyle"]
    },
    "claude": {
        "id": "claude",
        "name": "Claude",
        "developer": "Anthropic",
        "badge": "🥇 Best for Nuanced Writing & Logic",
        "icon": "🎭",
        "primaryColor": "#d97706",
        "bestFor": "Long-form writing, natural human tone, deep code analysis, complex document synthesis, and Artifacts preview",
        "keyStrengths": [
            "Exceptionally natural, human-sounding prose without robotic clichés",
            "Massive context window for long texts and research papers",
            "Interactive Artifacts for live code, HTML, and SVG preview"
        ],
        "baseUrl": "https://claude.ai/new",
        "prefillParam": "q",
        "supportsPrefill": False, # Will open claude.ai/new and copy prompt to clipboard
        "categories": ["content_writing", "email_communication", "coding", "research_academic"]
    },
    "perplexity": {
        "id": "perplexity",
        "name": "Perplexity AI",
        "developer": "Perplexity",
        "badge": "🥇 Best for Live Web Research",
        "icon": "🔍",
        "primaryColor": "#20808D",
        "bestFor": "Real-time web research, fact checking, finding up-to-date sources, citations, and travel / market data",
        "keyStrengths": [
            "Live web browsing with cited, verified references",
            "Direct answers with source links instead of outdated information",
            "Excellent for price comparisons, specs, and recent developments"
        ],
        "baseUrl": "https://www.perplexity.ai/search",
        "prefillParam": "q",
        "supportsPrefill": True, # Supports ?q=prompt
        "categories": ["research_academic", "travel_lifestyle", "general"]
    },
    "gemini": {
        "id": "gemini",
        "name": "Google Gemini",
        "developer": "Google",
        "badge": "🥇 Best for Multimodal & Google Ecosystem",
        "icon": "✨",
        "primaryColor": "#3b82f6",
        "bestFor": "Multimodal analysis (text, images, audio), Google Docs/Drive integration, fast summarization, and live search",
        "keyStrengths": [
            "Extremely fast responses and massive multi-million token context",
            "Deep integration with Google Workspace and YouTube",
            "Strong multilingual translation and regional language comprehension"
        ],
        "baseUrl": "https://gemini.google.com/app",
        "prefillParam": "",
        "supportsPrefill": False,
        "categories": ["general", "research_academic", "content_writing", "hardware_engineering"]
    },
    "gamma": {
        "id": "gamma",
        "name": "Gamma App",
        "developer": "Gamma",
        "badge": "🥇 Best for AI Presentations & Decks",
        "icon": "📊",
        "primaryColor": "#9333ea",
        "bestFor": "Creating stunning presentation slides, interactive pitch decks, documents, and web pages from text prompts",
        "keyStrengths": [
            "Turns structured prompt outlines into polished slide decks in 30 seconds",
            "Beautiful typography, cards, and automatic image layout",
            "Export directly to PowerPoint (PPTX) or PDF"
        ],
        "baseUrl": "https://gamma.app",
        "prefillParam": "",
        "supportsPrefill": False,
        "categories": ["presentation_design"]
    },
    "ideogram": {
        "id": "ideogram",
        "name": "Ideogram AI",
        "developer": "Ideogram",
        "badge": "🥇 Best for Typography & Photorealistic Images",
        "icon": "🎨",
        "primaryColor": "#e11d48",
        "bestFor": "Generating visual art, posters, character designs, logos, typography graphic design, and wallpaper renders",
        "keyStrengths": [
            "Flawless text and typography rendering inside generated images",
            "Photorealistic lighting, cinematic anime, and vintage aesthetics",
            "Instant aspect ratio and style selection"
        ],
        "baseUrl": "https://ideogram.ai",
        "prefillParam": "",
        "supportsPrefill": False,
        "categories": ["image_generation"]
    },
    "canva": {
        "id": "canva",
        "name": "Canva Magic Studio",
        "developer": "Canva",
        "badge": "🥈 Best for Social Graphics & Templates",
        "icon": "🪄",
        "primaryColor": "#06b6d4",
        "bestFor": "Quick social media templates, posters, banners, flyers, and collaborative visual editing",
        "keyStrengths": [
            "Thousands of customizable layouts and typography presets",
            "Drag and drop editing with brand asset integration",
            "Instant export for Instagram, LinkedIn, and print"
        ],
        "baseUrl": "https://www.canva.com",
        "prefillParam": "",
        "supportsPrefill": False,
        "categories": ["presentation_design", "image_generation"]
    },
    "cursor": {
        "id": "cursor",
        "name": "Cursor / v0",
        "developer": "Anysphere / Vercel",
        "badge": "🥈 Best for Full Project Code",
        "icon": "⚡",
        "primaryColor": "#0284c7",
        "bestFor": "Full-stack code generation, UI component prototyping, and repository-wide refactoring",
        "keyStrengths": [
            "Direct code execution and React component sandbox preview",
            "Contextual repo-aware AI pair programmer",
            "Instant git integration"
        ],
        "baseUrl": "https://v0.dev",
        "prefillParam": "q",
        "supportsPrefill": True,
        "categories": ["coding"]
    }
}

# Category to primary AI mapping
CATEGORY_AI_MAPPING = {
    "hardware_engineering": {
        "primary": "chatgpt",
        "alternatives": ["claude", "gemini", "perplexity"],
        "reason": "ChatGPT provides precise pinout configurations, Arduino C++ boilerplate code, circuit schematics, and component cost approximations."
    },
    "coding": {
        "primary": "chatgpt",
        "alternatives": ["claude", "cursor", "gemini"],
        "reason": "ChatGPT & Claude excel at clean code architecture, bug diagnosis, step-by-step comments, and library setup."
    },
    "email_communication": {
        "primary": "claude",
        "alternatives": ["chatgpt", "gemini"],
        "reason": "Claude specializes in polished, empathetic, and professional workplace communication without sounding robotic."
    },
    "content_writing": {
        "primary": "claude",
        "alternatives": ["chatgpt", "gemini"],
        "reason": "Claude produces engaging, organic narrative flows with exceptional vocabulary control and natural tone."
    },
    "research_academic": {
        "primary": "perplexity",
        "alternatives": ["gemini", "claude", "chatgpt"],
        "reason": "Perplexity provides live web-connected answers with clickable source citations and academic rigor."
    },
    "presentation_design": {
        "primary": "gamma",
        "alternatives": ["canva", "chatgpt"],
        "reason": "Gamma turns structured prompt outlines directly into interactive, beautifully designed slide decks."
    },
    "image_generation": {
        "primary": "ideogram",
        "alternatives": ["canva", "chatgpt"],
        "reason": "Ideogram translates descriptive visual prompts into stunning, photorealistic imagery with perfect text in the artwork."
    },
    "travel_lifestyle": {
        "primary": "perplexity",
        "alternatives": ["chatgpt", "gemini"],
        "reason": "Perplexity checks real-time travel costs, hotel options, local attractions, and itinerary feasibility."
    },
    "general": {
        "primary": "chatgpt",
        "alternatives": ["gemini", "claude", "perplexity"],
        "reason": "ChatGPT is the most versatile general-purpose AI for broad explanations, brainstorming, and structuring ideas."
    }
}

def get_recommendations_for_category(category: str) -> Dict[str, Any]:
    """Retrieve primary and alternative tools with rationale for a category."""
    mapping = CATEGORY_AI_MAPPING.get(category, CATEGORY_AI_MAPPING["general"])
    primary_id = mapping["primary"]
    alt_ids = mapping["alternatives"]
    
    primary_tool = AI_TOOLS.get(primary_id, AI_TOOLS["chatgpt"])
    alt_tools = [AI_TOOLS[tid] for tid in alt_ids if tid in AI_TOOLS]
    
    return {
        "primary": primary_tool,
        "alternatives": alt_tools,
        "reason": mapping["reason"]
    }

def build_launch_url(tool_id: str, prompt: str) -> Dict[str, Any]:
    """Generate launch URL with prefill query if supported."""
    import urllib.parse
    tool = AI_TOOLS.get(tool_id, AI_TOOLS["chatgpt"])
    base_url = tool["baseUrl"]
    supports_prefill = tool.get("supportsPrefill", False)
    param = tool.get("prefillParam", "")
    
    if supports_prefill and param:
        encoded_prompt = urllib.parse.quote(prompt)
        separator = "&" if "?" in base_url else "?"
        full_url = f"{base_url}{separator}{param}={encoded_prompt}"
        return {
            "url": full_url,
            "prefilled": True,
            "message": f"Opening {tool['name']} with your prompt prefilled (also copied to clipboard!)."
        }
    else:
        return {
            "url": base_url,
            "prefilled": False,
            "message": f"Opening {tool['name']}. Your prompt is copied to clipboard — simply press Ctrl+V / Cmd+V to paste!"
        }
