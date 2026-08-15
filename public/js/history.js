/**
 * PromptBridge Local History Manager
 */
const PromptHistory = (() => {
  const STORAGE_KEY = 'promptbridge_saved_history_v1';
  let historyCache = [];

  const load = () => {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      historyCache = data ? JSON.parse(data) : [];
    } catch (e) {
      console.warn("Could not load history from localStorage", e);
      historyCache = [];
    }
    updateBadge();
    return historyCache;
  };

  const save = (entry) => {
    const item = {
      id: 'pb_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5),
      timestamp: new Date().toISOString(),
      rawInput: entry.rawInput,
      detectedLanguage: entry.detectedLanguage || 'Multilingual',
      category: entry.category || 'general',
      understoodIntent: entry.understoodIntent || '',
      optimizedPrompt: entry.optimizedPrompt || '',
      recommendedTool: entry.recommendedTool || { name: 'ChatGPT', id: 'chatgpt' },
      isFavorite: false
    };

    historyCache.unshift(item);
    if (historyCache.length > 50) historyCache.pop(); // Keep last 50 items

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(historyCache));
    } catch (e) {
      console.warn("Could not save history item to localStorage", e);
    }

    updateBadge();
    return item;
  };

  const getAll = () => historyCache;

  const getById = (id) => historyCache.find(item => item.id === id);

  const toggleFavorite = (id) => {
    const item = historyCache.find(i => i.id === id);
    if (item) {
      item.isFavorite = !item.isFavorite;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(historyCache));
      return item.isFavorite;
    }
    return false;
  };

  const clearAll = () => {
    historyCache = [];
    localStorage.removeItem(STORAGE_KEY);
    updateBadge();
  };

  const exportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(historyCache, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `promptbridge_history_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const updateBadge = () => {
    const badge = document.getElementById('history-count-badge');
    if (!badge) return;
    if (historyCache.length > 0) {
      badge.textContent = historyCache.length;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  };

  // Initialize on load
  load();

  return {
    load,
    save,
    getAll,
    getById,
    toggleFavorite,
    clearAll,
    exportJSON,
    updateBadge
  };
})();
