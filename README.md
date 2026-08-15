# PromptBridge 🌉

> **"You don't need to know how to prompt AI. Just tell us what you want."**

PromptBridge transforms everyday natural language — including **Marathi**, **Hindi**, **Hinglish**, **broken English**, spelling/grammar mistakes, and incomplete thoughts — into precision-engineered prompts for modern AI models (ChatGPT, Claude, Gemini, Perplexity, Gamma, Ideogram, etc.).

---

## ✨ Features

- 🗣️ **Multilingual Intent Recognition**: Supports Marathi, Hindi, Hinglish, English, and mixed dialects.
- 💡 **Intent-Driven Prompt Synthesis**: Extracts true intent, sets professional personas, injects constraints, and formats structured outputs.
- 🎯 **AI Tool Matchmaker**: Recommends the #1 best AI model for the specific task category along with top alternatives.
- 🚀 **1-Click Auto-Copy & Launch**: Automatically copies the prompt to your clipboard and opens the AI tool with prefill links.
- ✏️ **Inline Prompt Editor**: Tweak and refine the prompt directly before copying.
- 🎚️ **Depth & Tone Controls**: Switch between Quick, Detailed, Step-by-Step, Academic, or Creative formats.
- 🎙️ **Voice Speech-to-Text**: Dictate your ideas in any supported language using Web Speech API.
- 📜 **Prompt History & Favorites**: Saves generated prompts locally with search, reload, and JSON export.
- ⚡ **Dual AI Engine**:
  - **Live LLM**: Direct integration with Google Gemini API (`GEMINI_API_KEY`) or OpenAI.
  - **Smart Offline Intent Engine**: Handles dozens of domains (embedded systems, coding, emails, creative, research, travel, marketing) with zero external dependencies.

---

## 🚀 Quick Start

### 1. Run the Application
```bash
python server.py
```
Open your browser at `http://localhost:3000`.

### 2. (Optional) Configure Gemini API Key
Create a `.env` file or enter your API key directly in the UI Settings:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=3000
```
*Note: If no API key is provided, PromptBridge automatically runs its built-in Multilingual Intent Engine.*
