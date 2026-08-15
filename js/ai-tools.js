/**
 * PromptBridge AI Tools & Launch Matchmaker
 */

const CLIENT_AI_TOOLS = {
  chatgpt: {
    id: "chatgpt",
    name: "ChatGPT",
    developer: "OpenAI",
    icon: "🤖",
    primaryColor: "#10a37f",
    badge: "🥇 Best for General & Coding",
    baseUrl: "https://chatgpt.com/",
    prefillParam: "q",
    supportsPrefill: true,
    bestFor: "General questions, coding, step-by-step explanations, and interactive debugging",
    keyStrengths: [
      "Precise coding and hardware prototyping assistance",
      "Fast conversational iteration and clarification",
      "Deep logical reasoning and structured problem solving"
    ]
  },
  claude: {
    id: "claude",
    name: "Claude",
    developer: "Anthropic",
    icon: "🎭",
    primaryColor: "#d97706",
    badge: "🥇 Best for Writing & Logic",
    baseUrl: "https://claude.ai/new",
    prefillParam: "",
    supportsPrefill: false,
    bestFor: "Long-form writing, natural human tone, nuanced emails, and Artifacts preview",
    keyStrengths: [
      "Exceptionally human, nuanced writing without robotic clichés",
      "Massive context window for long documents and complex briefs",
      "Interactive Artifacts to render code, web pages, and documents"
    ]
  },
  perplexity: {
    id: "perplexity",
    name: "Perplexity AI",
    developer: "Perplexity",
    icon: "🔍",
    primaryColor: "#20808D",
    badge: "🥇 Best for Live Web Research",
    baseUrl: "https://www.perplexity.ai/search",
    prefillParam: "q",
    supportsPrefill: true,
    bestFor: "Real-time web search, cited sources, facts, travel itineraries, and price data",
    keyStrengths: [
      "Live web browsing with up-to-date cited sources",
      "Instant fact-checking and comparative tables",
      "Fast answers to recent events and research questions"
    ]
  },
  gemini: {
    id: "gemini",
    name: "Google Gemini",
    developer: "Google",
    icon: "✨",
    primaryColor: "#3b82f6",
    badge: "🥇 Best for Multimodal & Google Workspace",
    baseUrl: "https://gemini.google.com/app",
    prefillParam: "",
    supportsPrefill: false,
    bestFor: "Multimodal tasks, Google Docs/YouTube integration, and fast multilingual comprehension",
    keyStrengths: [
      "Extremely fast responses and huge token context",
      "Seamless integration with Google Workspace and YouTube",
      "Strong Indian language translation and multilingual understanding"
    ]
  },
  gamma: {
    id: "gamma",
    name: "Gamma App",
    developer: "Gamma",
    icon: "📊",
    primaryColor: "#9333ea",
    badge: "🥇 Best for AI Presentations & Pitch Decks",
    baseUrl: "https://gamma.app",
    prefillParam: "",
    supportsPrefill: false,
    bestFor: "Creating stunning presentation slides, interactive pitch decks, and documents in seconds",
    keyStrengths: [
      "Converts structured markdown outlines directly into polished slide decks",
      "Clean typography and automated responsive card layouts",
      "Export ready for PowerPoint (PPTX) and PDF"
    ]
  },
  ideogram: {
    id: "ideogram",
    name: "Ideogram AI",
    developer: "Ideogram",
    icon: "🎨",
    primaryColor: "#e11d48",
    badge: "🥇 Best for Visual Art & Typography",
    baseUrl: "https://ideogram.ai",
    prefillParam: "",
    supportsPrefill: false,
    bestFor: "Generating visual art, posters, character designs, logos, typography, and wallpaper renders",
    keyStrengths: [
      "Flawless typography in generated artwork",
      "Photorealistic lighting and cinematic aesthetic presets",
      "Instant style and aspect ratio customization"
    ]
  },
  canva: {
    id: "canva",
    name: "Canva Magic Studio",
    developer: "Canva",
    icon: "🪄",
    primaryColor: "#06b6d4",
    badge: "🥈 Best for Social Graphics & Templates",
    baseUrl: "https://www.canva.com",
    prefillParam: "",
    supportsPrefill: false,
    bestFor: "Quick social media templates, posters, banners, and collaborative design",
    keyStrengths: [
      "Thousands of customizable layouts and presets",
      "Drag and drop editing with brand assets",
      "Direct social media publishing"
    ]
  },
  cursor: {
    id: "cursor",
    name: "v0 / Cursor",
    developer: "Vercel / Anysphere",
    icon: "⚡",
    primaryColor: "#0284c7",
    badge: "🥈 Best for UI & Full Code",
    baseUrl: "https://v0.dev",
    prefillParam: "q",
    supportsPrefill: true,
    bestFor: "Full-stack code generation, UI component prototyping, and live React preview",
    keyStrengths: [
      "Live React and Tailwind component sandbox",
      "Production-grade code architecture",
      "Instant code copy and export"
    ]
  }
};

/**
 * Copies prompt to clipboard and opens the chosen AI tool in a new tab.
 */
async function launchAITool(toolId, promptText) {
  const tool = CLIENT_AI_TOOLS[toolId] || CLIENT_AI_TOOLS['chatgpt'];
  
  // 1. Copy prompt to clipboard
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(promptText);
    }
  } catch (err) {
    console.warn("Clipboard auto-copy failed:", err);
  }

  // 2. Build target URL
  let targetUrl = tool.baseUrl;
  let prefillUsed = false;

  if (tool.supportsPrefill && tool.prefillParam) {
    const sep = tool.baseUrl.includes('?') ? '&' : '?';
    targetUrl = `${tool.baseUrl}${sep}${tool.prefillParam}=${encodeURIComponent(promptText)}`;
    prefillUsed = true;
  }

  // 3. Open in new tab
  window.open(targetUrl, '_blank', 'noopener,noreferrer');

  // 4. Show friendly toast notification
  if (prefillUsed) {
    Toast.success(`Opening ${tool.name} with your prompt! (Also copied to clipboard)`);
  } else {
    Toast.info(`Prompt copied! Opening ${tool.name} — press Ctrl+V / Cmd+V to paste.`);
  }
}
