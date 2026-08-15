/**
 * PromptBridge Main Application Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  // --- State ---
  let currentResult = null;
  let isEditingPrompt = false;
  let isListeningVoice = false;
  let speechRecognizer = null;

  // --- DOM Elements ---
  const promptInput = document.getElementById('user-prompt-input');
  const charCounter = document.getElementById('char-counter');
  const btnClearInput = document.getElementById('btn-clear-input');
  const btnVoiceInput = document.getElementById('btn-voice-input');
  const selectTone = document.getElementById('select-tone');
  const selectAudience = document.getElementById('select-audience');
  const btnGenerate = document.getElementById('btn-generate');
  const starterChips = document.querySelectorAll('.chip-item');

  // Results elements
  const resultsSection = document.getElementById('results-section');
  const badgeDetectedLang = document.getElementById('badge-detected-lang');
  const badgeCategory = document.getElementById('badge-category');
  const intentDescription = document.getElementById('intent-description');
  const intentHighlightsList = document.getElementById('intent-highlights-list');

  const promptOutputText = document.getElementById('prompt-output-text');
  const promptWordCount = document.getElementById('prompt-word-count');
  const promptCharCount = document.getElementById('prompt-char-count');
  const promptDisplayView = document.getElementById('prompt-display-view');
  const promptEditView = document.getElementById('prompt-edit-view');
  const promptEditableTextarea = document.getElementById('prompt-editable-textarea');

  const btnCopyPrompt = document.getElementById('btn-copy-prompt');
  const copyBtnText = document.getElementById('copy-btn-text');
  const btnToggleEdit = document.getElementById('btn-toggle-edit');
  const btnSaveEdit = document.getElementById('btn-save-edit');
  const btnCancelEdit = document.getElementById('btn-cancel-edit');
  const btnRegenerate = document.getElementById('btn-regenerate');
  const btnListenPrompt = document.getElementById('btn-listen-prompt');
  const btnSaveFavorite = document.getElementById('btn-save-favorite');

  // AI Recommendation elements
  const primaryAiName = document.getElementById('primary-ai-name');
  const primaryAiBadge = document.getElementById('primary-ai-badge');
  const primaryAiDev = document.getElementById('primary-ai-dev');
  const primaryAiIcon = document.getElementById('primary-ai-icon');
  const primaryAiReason = document.getElementById('primary-ai-reason');
  const primaryAiStrengths = document.getElementById('primary-ai-strengths');
  const btnLaunchPrimary = document.getElementById('btn-launch-primary');
  const launchPrimaryLabel = document.getElementById('launch-primary-label');
  const alternativesGrid = document.getElementById('alternatives-grid');

  // Drawers & Modals
  const historyDrawer = document.getElementById('history-drawer');
  const historyDrawerOverlay = document.getElementById('history-drawer-overlay');
  const btnOpenHistory = document.getElementById('btn-open-history');
  const btnCloseHistory = document.getElementById('btn-close-history');
  const historySearchInput = document.getElementById('history-search-input');
  const historyListContainer = document.getElementById('history-list-container');
  const btnExportHistory = document.getElementById('btn-export-history');
  const btnClearHistory = document.getElementById('btn-clear-history');

  const settingsModal = document.getElementById('settings-modal');
  const btnOpenSettings = document.getElementById('btn-open-settings');
  const btnCloseSettings = document.getElementById('btn-close-settings');
  const geminiKeyInput = document.getElementById('gemini-key-input');
  const modelSelect = document.getElementById('model-select');
  const btnTestKey = document.getElementById('btn-test-key');
  const btnSaveSettings = document.getElementById('btn-save-settings');
  const keyTestStatus = document.getElementById('key-test-status');

  const howModal = document.getElementById('how-modal');
  const btnHowItWorks = document.getElementById('btn-how-it-works');
  const btnCloseHow = document.getElementById('btn-close-how');
  const btnGotIt = document.getElementById('btn-got-it');

  const btnThemeToggle = document.getElementById('btn-theme-toggle');

  // --- Theme Management ---
  const initTheme = () => {
    const savedTheme = localStorage.getItem('promptbridge_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
  };

  btnThemeToggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('promptbridge_theme', next);
    Toast.info(`Switched to ${next} theme`);
  });

  initTheme();

  // --- Input Management ---
  const updateInputState = () => {
    const val = promptInput.value;
    const len = val.length;
    charCounter.textContent = `${len} / 1500`;
    btnClearInput.style.display = len > 0 ? 'inline-flex' : 'none';
  };

  promptInput.addEventListener('input', updateInputState);

  btnClearInput.addEventListener('click', () => {
    promptInput.value = '';
    updateInputState();
    promptInput.focus();
  });

  // Shortcut: Ctrl + Enter / Cmd + Enter
  promptInput.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleGenerate();
    }
  });

  // Starter Chips click
  starterChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const text = chip.getAttribute('data-text');
      promptInput.value = text;
      updateInputState();
      promptInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
      promptInput.focus();
      handleGenerate();
    });
  });

  // --- Speech-to-Text Recognition ---
  const initSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      btnVoiceInput.style.display = 'none';
      return;
    }

    speechRecognizer = new SpeechRecognition();
    speechRecognizer.continuous = false;
    speechRecognizer.interimResults = false;
    speechRecognizer.lang = 'en-IN'; // Supports Indian English, Hinglish, Marathi accents

    speechRecognizer.onstart = () => {
      isListeningVoice = true;
      btnVoiceInput.classList.add('listening');
      btnVoiceInput.querySelector('.voice-text').textContent = 'Listening...';
      Toast.info('Listening... Speak naturally in Marathi, Hindi, or English');
    };

    speechRecognizer.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (promptInput.value.trim().length > 0) {
        promptInput.value += ' ' + transcript;
      } else {
        promptInput.value = transcript;
      }
      updateInputState();
      Toast.success('Voice captured!');
    };

    speechRecognizer.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      Toast.error('Speech recognition stopped. You can type directly.');
      stopListening();
    };

    speechRecognizer.onend = () => {
      stopListening();
    };
  };

  const stopListening = () => {
    isListeningVoice = false;
    btnVoiceInput.classList.remove('listening');
    btnVoiceInput.querySelector('.voice-text').textContent = 'Voice';
  };

  btnVoiceInput.addEventListener('click', () => {
    if (!speechRecognizer) return;
    if (isListeningVoice) {
      speechRecognizer.stop();
      stopListening();
    } else {
      try {
        speechRecognizer.start();
      } catch (err) {
        console.warn(err);
      }
    }
  });

  initSpeechRecognition();

  // --- API / Generation Handler ---
  const handleGenerate = async () => {
    const rawInput = promptInput.value.trim();
    if (!rawInput) {
      Toast.error('Please enter what you want AI to do in the box above.');
      promptInput.focus();
      return;
    }

    // Set Loading State
    btnGenerate.classList.add('loading');
    btnGenerate.disabled = true;

    const tone = selectTone.value;
    const audience = selectAudience.value;
    const customApiKey = localStorage.getItem('promptbridge_gemini_key') || '';
    const selectedModel = localStorage.getItem('promptbridge_model') || 'gemini-1.5-flash';

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: rawInput,
          tone: tone,
          audience: audience,
          apiKey: customApiKey,
          model: selectedModel
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      currentResult = {
        ...data,
        rawInput: rawInput
      };

      // Render Results
      renderResults(currentResult);

      // Save to History
      PromptHistory.save(currentResult);

      Toast.success('Optimized prompt & recommendations generated!');

    } catch (err) {
      console.error('Generation error:', err);
      Toast.error('Error generating prompt. Please try again.');
    } finally {
      btnGenerate.classList.remove('loading');
      btnGenerate.disabled = false;
    }
  };

  btnGenerate.addEventListener('click', handleGenerate);

  // --- Render Results UI ---
  const renderResults = (data) => {
    resultsSection.style.display = 'flex';

    // 1. Intent Breakdown
    badgeDetectedLang.textContent = `Language: ${data.detectedLanguage || 'Multilingual'}`;
    
    const formattedCat = (data.category || 'General').replace('_', ' ').toUpperCase();
    badgeCategory.textContent = formattedCat;
    
    intentDescription.textContent = data.understoodIntent || 'We understood your core objective.';

    // Highlights
    intentHighlightsList.innerHTML = '';
    const highlights = data.highlights || ['Intent extracted', 'Context bounded', 'Structured output format'];
    highlights.forEach(hl => {
      const span = document.createElement('span');
      span.className = 'highlight-tag';
      span.innerHTML = `✓ ${hl}`;
      intentHighlightsList.appendChild(span);
    });

    // 2. Optimized Prompt
    promptOutputText.textContent = data.optimizedPrompt || '';
    promptEditableTextarea.value = data.optimizedPrompt || '';
    
    updatePromptMetrics(data.optimizedPrompt || '');

    // Reset edit state
    setEditMode(false);

    // 3. Primary AI Recommendation
    const primaryTool = data.recommendedTool || CLIENT_AI_TOOLS['chatgpt'];
    primaryAiName.textContent = primaryTool.name;
    primaryAiBadge.textContent = primaryTool.badge || '🥇 Best for Your Task';
    primaryAiDev.textContent = `By ${primaryTool.developer || 'AI'}`;
    primaryAiIcon.textContent = primaryTool.icon || '🤖';
    primaryAiReason.innerHTML = `<strong>Why it's best:</strong> ${data.recommendationReason || primaryTool.bestFor}`;
    
    // Strengths
    primaryAiStrengths.innerHTML = '';
    const strengths = primaryTool.keyStrengths || [
      'Deep domain logic & reasoning',
      'Fast iterative follow-ups',
      'High accuracy step-by-step guidance'
    ];
    strengths.forEach(st => {
      const div = document.createElement('div');
      div.className = 'strength-item';
      div.innerHTML = `<span class="strength-check">✓</span> <span>${st}</span>`;
      primaryAiStrengths.appendChild(div);
    });

    // Launch Primary Button
    launchPrimaryLabel.textContent = `Open ${primaryTool.name}`;
    btnLaunchPrimary.onclick = () => {
      launchAITool(primaryTool.id, promptOutputText.textContent);
    };

    // 4. Alternatives Grid
    alternativesGrid.innerHTML = '';
    const alternatives = data.alternativeTools || [];
    alternatives.forEach(tool => {
      const altCard = document.createElement('div');
      altCard.className = 'alt-card';
      altCard.innerHTML = `
        <div class="alt-card-header">
          <span class="alt-card-icon">${tool.icon || '✨'}</span>
          <span class="alt-card-name">${tool.name}</span>
        </div>
        <p class="alt-card-desc">${tool.bestFor || 'Great alternative for this task.'}</p>
        <button type="button" class="btn-launch-alt" data-tool-id="${tool.id}">
          <span>Open ${tool.name}</span>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/></svg>
        </button>
      `;

      const launchBtn = altCard.querySelector('.btn-launch-alt');
      launchBtn.addEventListener('click', () => {
        launchAITool(tool.id, promptOutputText.textContent);
      });

      alternativesGrid.appendChild(altCard);
    });

    // Scroll smoothly to results
    setTimeout(() => {
      resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  };

  const updatePromptMetrics = (text) => {
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const chars = text.length;
    promptWordCount.textContent = `${words} words`;
    promptCharCount.textContent = `${chars} chars`;
  };

  // --- Copy Prompt Action ---
  btnCopyPrompt.addEventListener('click', async () => {
    const textToCopy = promptOutputText.textContent;
    if (!textToCopy) return;

    try {
      await navigator.clipboard.writeText(textToCopy);
      
      // Visual feedback
      btnCopyPrompt.classList.add('copied');
      btnCopyPrompt.querySelector('.copy-icon').style.display = 'none';
      btnCopyPrompt.querySelector('.check-icon').style.display = 'inline-block';
      copyBtnText.textContent = 'Copied!';

      Toast.success('Prompt copied to clipboard! Ready to paste.');

      setTimeout(() => {
        btnCopyPrompt.classList.remove('copied');
        btnCopyPrompt.querySelector('.copy-icon').style.display = 'inline-block';
        btnCopyPrompt.querySelector('.check-icon').style.display = 'none';
        copyBtnText.textContent = 'Copy Prompt';
      }, 2500);
    } catch (err) {
      console.warn('Clipboard write error:', err);
      Toast.error('Could not auto-copy. Please select and copy manually.');
    }
  });

  // --- Edit Prompt Mode ---
  const setEditMode = (editing) => {
    isEditingPrompt = editing;
    if (editing) {
      promptDisplayView.style.display = 'none';
      promptEditView.style.display = 'block';
      promptEditableTextarea.value = promptOutputText.textContent;
      promptEditableTextarea.focus();
      btnToggleEdit.style.display = 'none';
    } else {
      promptDisplayView.style.display = 'block';
      promptEditView.style.display = 'none';
      btnToggleEdit.style.display = 'inline-flex';
    }
  };

  btnToggleEdit.addEventListener('click', () => setEditMode(true));

  btnSaveEdit.addEventListener('click', () => {
    const newText = promptEditableTextarea.value.trim();
    if (newText) {
      promptOutputText.textContent = newText;
      updatePromptMetrics(newText);
      if (currentResult) {
        currentResult.optimizedPrompt = newText;
      }
      Toast.success('Prompt changes saved!');
    }
    setEditMode(false);
  });

  btnCancelEdit.addEventListener('click', () => {
    setEditMode(false);
  });

  // --- Regenerate Action ---
  btnRegenerate.addEventListener('click', () => {
    handleGenerate();
  });

  // --- Listen to Prompt (TTS) ---
  btnListenPrompt.addEventListener('click', () => {
    if (!('speechSynthesis' in window)) {
      Toast.error('Speech audio is not supported in this browser.');
      return;
    }

    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      Toast.info('Audio paused.');
      return;
    }

    const textToRead = promptOutputText.textContent;
    if (!textToRead) return;

    const utterance = new SpeechSynthesisUtterance(textToRead);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    
    window.speechSynthesis.speak(utterance);
    Toast.info('Reading prompt aloud...');
  });

  // --- Save to Favorite Action ---
  btnSaveFavorite.addEventListener('click', () => {
    btnSaveFavorite.classList.toggle('active');
    if (btnSaveFavorite.classList.contains('active')) {
      Toast.success('Saved to favorite prompts!');
    } else {
      Toast.info('Removed from favorites.');
    }
  });

  // --- History Drawer Handlers ---
  const renderHistoryList = (filterText = '') => {
    const items = PromptHistory.getAll();
    historyListContainer.innerHTML = '';

    const filtered = items.filter(item => {
      if (!filterText) return true;
      const lower = filterText.toLowerCase();
      return (item.rawInput || '').toLowerCase().includes(lower) ||
             (item.optimizedPrompt || '').toLowerCase().includes(lower);
    });

    if (filtered.length === 0) {
      historyListContainer.innerHTML = `
        <div style="text-align:center; padding: 2rem 1rem; color: var(--text-muted);">
          <p>No saved prompts found.</p>
          <small>Generated prompts will automatically appear here.</small>
        </div>
      `;
      return;
    }

    filtered.forEach(item => {
      const card = document.createElement('div');
      card.className = 'history-item-card';
      const timeFormatted = new Date(item.timestamp).toLocaleDateString(undefined, {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
      });

      card.innerHTML = `
        <div class="history-item-meta">
          <span>${item.detectedLanguage} • ${item.category}</span>
          <span>${timeFormatted}</span>
        </div>
        <div class="history-input-preview">"${item.rawInput}"</div>
        <div class="history-prompt-preview">${item.optimizedPrompt}</div>
      `;

      card.addEventListener('click', () => {
        promptInput.value = item.rawInput;
        updateInputState();
        renderResults(item);
        closeHistoryDrawer();
        Toast.info('Loaded prompt from history!');
      });

      historyListContainer.appendChild(card);
    });
  };

  const openHistoryDrawer = () => {
    renderHistoryList();
    historyDrawer.classList.add('active');
    historyDrawerOverlay.classList.add('active');
  };

  const closeHistoryDrawer = () => {
    historyDrawer.classList.remove('active');
    historyDrawerOverlay.classList.remove('active');
  };

  btnOpenHistory.addEventListener('click', openHistoryDrawer);
  btnCloseHistory.addEventListener('click', closeHistoryDrawer);
  historyDrawerOverlay.addEventListener('click', closeHistoryDrawer);

  historySearchInput.addEventListener('input', (e) => {
    renderHistoryList(e.target.value.trim());
  });

  btnExportHistory.addEventListener('click', () => {
    PromptHistory.exportJSON();
    Toast.success('Exported history as JSON file.');
  });

  btnClearHistory.addEventListener('click', () => {
    if (confirm('Are you sure you want to clear your saved prompt history?')) {
      PromptHistory.clearAll();
      renderHistoryList();
      Toast.info('Prompt history cleared.');
    }
  });

  // --- Settings Modal Handlers ---
  const loadSavedSettings = () => {
    const savedKey = localStorage.getItem('promptbridge_gemini_key') || '';
    const savedModel = localStorage.getItem('promptbridge_model') || 'gemini-1.5-flash';
    geminiKeyInput.value = savedKey;
    modelSelect.value = savedModel;
  };

  const openSettingsModal = () => {
    loadSavedSettings();
    keyTestStatus.style.display = 'none';
    settingsModal.style.display = 'flex';
  };

  const closeSettingsModal = () => {
    settingsModal.style.display = 'none';
  };

  btnOpenSettings.addEventListener('click', openSettingsModal);
  btnCloseSettings.addEventListener('click', closeSettingsModal);
  settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) closeSettingsModal();
  });

  btnTestKey.addEventListener('click', async () => {
    const key = geminiKeyInput.value.trim();
    if (!key) {
      keyTestStatus.className = 'key-test-status error';
      keyTestStatus.textContent = 'Please enter an API key to test.';
      keyTestStatus.style.display = 'block';
      return;
    }

    btnTestKey.textContent = 'Testing...';
    btnTestKey.disabled = true;

    try {
      const res = await fetch('/api/test-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey: key })
      });
      const data = await res.json();
      if (data.valid) {
        keyTestStatus.className = 'key-test-status success';
        keyTestStatus.textContent = '✓ Valid Google Gemini API key! Ready for live LLM generation.';
      } else {
        keyTestStatus.className = 'key-test-status error';
        keyTestStatus.textContent = `✗ Verification failed: ${data.error || 'Invalid key'}`;
      }
      keyTestStatus.style.display = 'block';
    } catch (e) {
      keyTestStatus.className = 'key-test-status error';
      keyTestStatus.textContent = '✗ Connection error during testing.';
      keyTestStatus.style.display = 'block';
    } finally {
      btnTestKey.textContent = 'Test Key';
      btnTestKey.disabled = false;
    }
  });

  btnSaveSettings.addEventListener('click', () => {
    const key = geminiKeyInput.value.trim();
    const model = modelSelect.value;
    localStorage.setItem('promptbridge_gemini_key', key);
    localStorage.setItem('promptbridge_model', model);
    closeSettingsModal();
    Toast.success('Settings saved successfully!');
  });

  // --- How It Works Modal ---
  btnHowItWorks.addEventListener('click', () => {
    howModal.style.display = 'flex';
  });
  btnCloseHow.addEventListener('click', () => {
    howModal.style.display = 'none';
  });
  btnGotIt.addEventListener('click', () => {
    howModal.style.display = 'none';
    promptInput.focus();
  });
  howModal.addEventListener('click', (e) => {
    if (e.target === howModal) howModal.style.display = 'none';
  });

  // Check backend server status
  fetch('/api/status')
    .then(res => res.json())
    .then(data => {
      const footerStatus = document.getElementById('footer-engine-status');
      if (footerStatus) {
        if (data.hasServerApiKey) {
          footerStatus.textContent = '⚡ Gemini Live LLM + Multilingual Engine Active';
        } else {
          footerStatus.textContent = '⚡ Multilingual Intent Engine Active (Offline Ready)';
        }
      }
    })
    .catch(() => {});
});
