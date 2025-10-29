/* ============================================
   🎨 GEMINI CHAT - MAIN APPLICATION
   Core chat functionality and API integration
   ============================================ */

import { GoogleGenAI } from 'https://esm.run/@google/genai';
import { log, logSessionStats, logMemoryUsage, initializeLogging } from './logging.js';
import { toggleThemeMenu, setTheme, initializeThemes } from './themes.js';
import { renderMarkdown } from './markdown-renderer.js';
import { streamResponse } from './streaming.js';
import { initializeShortcuts, showShortcutsModal, showCommandPalette } from './shortcuts.js';
import { calculateCost, trackMessage, showAnalytics } from './analytics.js';
import { isCoinFlipRequest, flipCoin, createCoinFlipHTML } from './special-features.js';

// Application state
let client = null;
let conversationHistory = [];
let sessionStats = {
    messagesCount: 0,
    totalTokens: 0,
    cachedTokens: 0,
    inputTokens: 0,
    outputTokens: 0,
    startTime: Date.now(),
    apiCalls: 0,
    errors: 0
};

// ============================================
// INITIALIZATION
// ============================================

function initialize() {
    // Initialize logging system
    initializeLogging();

    // Initialize theme system
    initializeThemes();

    // Initialize keyboard shortcuts
    initializeShortcuts({
        openCommandPalette: showCommandPalette,
        showShortcuts: showShortcutsModal,
        clearChat: () => window.clearHistory && window.clearHistory(),
        exportConversation: () => window.exportConversation && window.exportConversation(),
        toggleTheme: toggleThemeMenu,
        toggleDarkMode: () => setTheme('dark'),
        showStats: () => window.getSessionStats && window.getSessionStats(),
        showMemory: logMemoryUsage,
        closeModal: () => {
            document.querySelectorAll('.show').forEach(el => el.classList.remove('show'));
        },
        sendMessage: sendMessage
    });

    log.system('✨ ALL ADVANCED FEATURES LOADED!');
    console.log('%c🚀 NEW FEATURES UNLOCKED!', 'font-size: 16px; font-weight: bold; color: #51cf66;');
    console.log('%c📝 Markdown rendering with syntax highlighting', 'color: #888;');
    console.log('%c🌊 Real-time streaming responses', 'color: #888;');
    console.log('%c⌨️  Keyboard shortcuts (Cmd+/ to see all)', 'color: #888;');
    console.log('%c📊 Analytics dashboard (Cmd+. for stats)', 'color: #888;');
    console.log('%c💰 Token cost tracking', 'color: #888;');
    console.log('%c🎲 Coin flip feature (try "flip a coin" or "yes or no?")', 'color: #888;');

    // Make functions available globally
    window.setApiKey = setApiKey;
    window.sendMessage = sendMessage;
    window.handleKeyDown = handleKeyDown;
    window.toggleThemeMenu = toggleThemeMenu;
    window.setTheme = setTheme;
    window.showAnalytics = showAnalytics;

    // Add debug helpers to window
    window.getSessionStats = () => {
        logSessionStats(sessionStats);
        return sessionStats;
    };
    window.getConversationHistory = () => {
        console.log('%c📝 Conversation History', 'font-size: 16px; font-weight: bold;');
        console.table(conversationHistory.map((msg, i) => ({
            index: i,
            role: msg.role,
            text: msg.parts[0].text.substring(0, 50) + '...',
            length: msg.parts[0].text.length
        })));
        return conversationHistory;
    };
    window.clearHistory = () => {
        conversationHistory = [];
        log.system('Conversation history cleared');
    };
    window.showMemory = logMemoryUsage;
    window.clearApiKey = function() {
        console.warn('🧹 Clearing API key from localStorage');
        localStorage.removeItem('GEMINI_API_KEY');
        log.system('API key cleared');
        console.log('Reloading page...');
        location.reload();
    };
    window.exportConversation = function() {
        const data = {
            timestamp: new Date().toISOString(),
            stats: sessionStats,
            conversation: conversationHistory
        };
        console.log('📤 Conversation Export:');
        console.log(JSON.stringify(data, null, 2));
        return data;
    };
    window.startProfiling = function() {
        console.profile('Gemini Chat Performance');
        log.perf('Profiling started');
    };
    window.stopProfiling = function() {
        console.profileEnd('Gemini Chat Performance');
        log.perf('Profiling stopped');
    };

    log.system('Application initialized');
    console.log('%c💡 TIP: Type getSessionStats() to see statistics', 'color: #888; font-style: italic;');
    console.log('%c💡 TIP: Type getConversationHistory() to see chat history', 'color: #888; font-style: italic;');
    console.log('%c💡 TIP: Type showMemory() to check memory usage', 'color: #888; font-style: italic;');

    // Try to get API key from environment
    const envApiKey = localStorage.getItem('GEMINI_API_KEY');
    if (envApiKey) {
        log.system('Found API key in localStorage');
        initializeClient(envApiKey);
    } else {
        log.system('No API key found, awaiting user input');
    }

    // Start periodic logging
    startPeriodicLogging();
}

// ============================================
// API KEY MANAGEMENT
// ============================================

async function setApiKey() {
    console.group('🔑 API Key Configuration');
    console.time('⏱️ API Key Setup Duration');

    const apiKey = document.getElementById('apiKeyInput').value.trim();

    console.assert(apiKey.length > 0, 'API key cannot be empty');

    if (!apiKey) {
        log.error('No API key provided');
        console.trace('Stack trace for missing API key');
        addMessage('error', 'Please enter a valid API key');
        console.timeEnd('⏱️ API Key Setup Duration');
        console.groupEnd();
        return;
    }

    log.user('API key entered', `Length: ${apiKey.length} characters`);
    console.log('Masked API key:', apiKey.substring(0, 8) + '...' + apiKey.substring(apiKey.length - 4));

    try {
        // Save to localStorage for persistence
        localStorage.setItem('GEMINI_API_KEY', apiKey);
        log.system('API key saved to localStorage');
        console.dir({ storage: 'localStorage', key: 'GEMINI_API_KEY', saved: true });

        initializeClient(apiKey);
        console.timeEnd('⏱️ API Key Setup Duration');
    } catch (error) {
        sessionStats.errors++;
        log.error('Failed to initialize client', error);
        console.error('Full error object:', error);
        console.trace();
        addMessage('error', 'Failed to initialize client: ' + error.message);
        console.timeEnd('⏱️ API Key Setup Duration');
    }

    console.groupEnd();
}

function initializeClient(apiKey) {
    console.groupCollapsed('🚀 Client Initialization');
    console.time('⏱️ Client Init Duration');

    try {
        log.system('Creating GoogleGenAI client instance');
        client = new GoogleGenAI({ apiKey });

        console.dir(client, { depth: 2 });
        log.system('✅ Client instance created successfully');

        // Hide API key setup and enable chat
        document.getElementById('apiKeySetup').classList.add('hidden');
        document.getElementById('messageInput').disabled = false;
        document.getElementById('sendButton').disabled = false;
        document.getElementById('statusIndicator').classList.remove('disconnected');
        document.getElementById('statusIndicator').classList.add('connected');

        log.system('UI updated: Chat enabled');
        console.log('UI State:', {
            apiKeySetup: 'hidden',
            messageInput: 'enabled',
            sendButton: 'enabled',
            statusIndicator: 'connected'
        });

        // Clear welcome message
        document.getElementById('messagesContainer').innerHTML = '';

        addMessage('assistant', 'Hi! I\'m Gemini 2.5 Flash. How can I help you today?');
        log.ai('Initial greeting sent');

        console.timeEnd('⏱️ Client Init Duration');
        console.count('✅ Successful Initializations');

    } catch (error) {
        sessionStats.errors++;
        log.error('Failed to initialize client', error);
        console.error('Initialization error details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        console.trace();
        addMessage('error', 'Failed to initialize: ' + error.message);
        console.timeEnd('⏱️ Client Init Duration');
        console.count('❌ Failed Initializations');
    }

    console.groupEnd();
}

// ============================================
// MESSAGE HANDLING
// ============================================

async function sendMessage() {
    console.group('%c💬 Message Send Operation', 'font-size: 14px; font-weight: bold; color: #667eea;');
    console.time('⏱️ Total Request Duration');
    console.time('⏱️ API Response Time');

    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    const messageId = Date.now();

    console.log('Message ID:', messageId);
    log.user('New message', `"${message}"`);
    console.log('Message length:', message.length, 'characters');
    console.log('Estimated tokens:', Math.ceil(message.length / 4));

    if (!message) {
        log.error('Empty message submitted');
        console.groupEnd();
        return;
    }

    // Check for special features (coin flip) BEFORE API call
    if (isCoinFlipRequest(message)) {
        log.system('🎲 Processing coin flip request instead of AI');

        sessionStats.messagesCount++;
        console.count('📨 Messages Sent');

        // Add user message
        addMessage('user', message);
        input.value = '';

        // Show loading
        input.disabled = true;
        document.getElementById('sendButton').disabled = true;
        const loadingId = addLoadingIndicator();

        try {
            // Flip the coin!
            const result = await flipCoin();

            // Remove loading
            removeLoadingIndicator(loadingId);

            // Create and add coin flip result
            const html = createCoinFlipHTML(result, message);
            const container = document.getElementById('messagesContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message assistant';
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content coin-flip';
            contentDiv.innerHTML = html;
            messageDiv.appendChild(contentDiv);
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;

            log.system('✨ Coin flip displayed');

        } catch (error) {
            removeLoadingIndicator(loadingId);
            addMessage('error', 'Coin flip failed! Try again.');
            log.error('Coin flip error', error);
        } finally {
            input.disabled = false;
            document.getElementById('sendButton').disabled = false;
            input.focus();
        }

        console.groupEnd();
        return; // Don't send to AI
    }

    if (!client) {
        log.error('Client not initialized');
        console.assert(client !== null, 'Client must be initialized before sending messages');
        addMessage('error', 'Please set your API key first');
        console.groupEnd();
        return;
    }

    sessionStats.messagesCount++;
    console.count('📨 Messages Sent');

    // Add user message
    addMessage('user', message);
    input.value = '';

    // Disable input while processing
    input.disabled = true;
    document.getElementById('sendButton').disabled = true;
    log.system('Input disabled during API call');

    // Show loading indicator
    const loadingId = addLoadingIndicator();
    log.system('Loading indicator displayed');

    try {
        // Add to conversation history
        conversationHistory.push({
            role: 'user',
            parts: [{ text: message }]
        });

        log.system('Message added to conversation history');
        console.log('Conversation history length:', conversationHistory.length);
        console.table(conversationHistory.map((msg, i) => ({
            index: i,
            role: msg.role,
            preview: msg.parts[0].text.substring(0, 30) + '...'
        })));

        // Generate response
        log.api('🚀 Sending request to Gemini API...');
        console.log('Model:', 'gemini-2.5-flash');
        console.log('History items:', conversationHistory.length);

        sessionStats.apiCalls++;
        console.count('🌐 API Calls Made');

        const requestStartTime = performance.now();

        // Create a message element for response rendering
        const messageDiv = document.querySelector(`#${loadingId}`);
        const contentDiv = messageDiv.querySelector('.message-content');
        contentDiv.classList.remove('loading');
        contentDiv.classList.add('markdown');
        contentDiv.innerHTML = '';

        const supportsStreaming = typeof client?.models?.generateContentStream === 'function';
        let streamResult = null;
        let usedStreaming = false;

        if (supportsStreaming) {
            try {
                contentDiv.classList.add('streaming');
                log.api('🌊 Using streaming mode for real-time response');
                streamResult = await streamResponse(client, conversationHistory, contentDiv, sessionStats);
                usedStreaming = true;
            } catch (streamError) {
                log.system('⚠️ Streaming unavailable, falling back to non-streaming response');
                console.warn('Streaming failed, falling back to generateContent()', streamError);
                streamResult = null;
            } finally {
                contentDiv.classList.remove('streaming');
            }
        } else {
            log.system('Streaming API not available, using generateContent()');
        }

        if (!streamResult) {
            const response = await client.models.generateContent({
                model: 'gemini-2.5-flash',
                contents: conversationHistory
            });

            const candidates = response.candidates || [];
            const parts = (candidates[0] && candidates[0].content && candidates[0].content.parts) || [];
            const responseText = parts.map(part => part.text || '').join('');

            const estimatedTokens = Math.ceil(responseText.length / 4);
            const html = renderMarkdown(responseText);
            contentDiv.innerHTML = html;
            const container = document.getElementById('messagesContainer');
            container.scrollTop = container.scrollHeight;

            streamResult = {
                text: responseText,
                duration: (performance.now() - requestStartTime).toFixed(2),
                chunks: 1,
                tokens: estimatedTokens,
                mode: 'fallback'
            };

            log.system('✅ Fallback response rendered');
        } else {
            streamResult.mode = usedStreaming ? 'streaming' : streamResult.mode;
        }

        const requestEndTime = performance.now();
        const requestDuration = (requestEndTime - requestStartTime).toFixed(2);

        console.timeEnd('⏱️ API Response Time');
        log.perf(`API responded in ${requestDuration}ms`);
        log.perf(`Received ${streamResult.chunks} chunks`);

        // Track token usage for user message
        trackMessage('user', Math.ceil(message.length / 4), 0, 0);

        // ==========================================
        // 🎯 DETAILED RESPONSE ANALYSIS
        // ==========================================
        console.groupCollapsed('📦 Stream Response Details');
        console.log('Stream metadata:', streamResult);

        // Note: Token usage metadata not available in streaming mode
        // We'll use estimated tokens instead
        const usage = null; // Streaming doesn't provide usage metadata

        if (false) { // Skip this section for streaming

            console.group('🎯 Token Usage Analysis');
            log.token('Token breakdown received');

            const tokenData = {
                'Prompt Tokens': usage.promptTokenCount || usage.prompt_token_count || 0,
                'Cached Tokens': usage.cachedContentTokenCount || usage.cached_content_token_count || 0,
                'Candidates Tokens': usage.candidatesTokenCount || usage.candidates_token_count || 0,
                'Total Tokens': usage.totalTokenCount || usage.total_token_count || 0
            };

            console.table(tokenData);

            // Update session stats
            sessionStats.inputTokens += tokenData['Prompt Tokens'];
            sessionStats.outputTokens += tokenData['Candidates Tokens'];
            sessionStats.cachedTokens += tokenData['Cached Tokens'];
            sessionStats.totalTokens += tokenData['Total Tokens'];

            // Cache efficiency
            const cacheHitRate = tokenData['Total Tokens'] > 0
                ? (tokenData['Cached Tokens'] / tokenData['Total Tokens'] * 100).toFixed(2)
                : 0;

            log.cache(`Cache hit rate: ${cacheHitRate}%`);

            if (tokenData['Cached Tokens'] > 0) {
                log.cache(`💚 ${tokenData['Cached Tokens']} tokens served from cache!`);
                console.log('Cache savings:', {
                    'Tokens from cache': tokenData['Cached Tokens'],
                    'Percentage': cacheHitRate + '%',
                    'Cost savings': 'Significant!'
                });
            }

            // Visual token breakdown
            const total = tokenData['Total Tokens'];
            const cached = tokenData['Cached Tokens'];
            const prompt = tokenData['Prompt Tokens'] - cached;
            const output = tokenData['Candidates Tokens'];

            const barLength = 50;
            const cachedBar = Math.round((cached / total) * barLength);
            const promptBar = Math.round((prompt / total) * barLength);
            const outputBar = barLength - cachedBar - promptBar;

            console.log('Token Distribution:');
            console.log('[' +
                '█'.repeat(cachedBar) +
                '▓'.repeat(promptBar) +
                '░'.repeat(outputBar) +
                ']'
            );
            console.log('█ = Cached | ▓ = Prompt | ░ = Output');

            console.groupEnd();
        }

        // Response text analysis
        const responseText = streamResult.text;
        const estimatedTokens = streamResult.tokens;

        log.ai('Response received', `Length: ${responseText.length} chars`);
        console.log('Response preview:', responseText.substring(0, 100) + '...');
        console.log('Response stats:', {
            'Characters': responseText.length,
            'Words': responseText.split(/\s+/).length,
            'Lines': responseText.split('\n').length,
            'Chunks received': streamResult.chunks,
            'Estimated tokens': estimatedTokens
        });

        // Performance metrics
        console.log('Performance Metrics:', {
            'Stream Duration': requestDuration + 'ms',
            'Chunks Received': streamResult.chunks,
            'Characters per second': (responseText.length / (requestDuration / 1000)).toFixed(0),
            'Tokens per second': (estimatedTokens / (requestDuration / 1000)).toFixed(0),
            'Chunks per second': (streamResult.chunks / (requestDuration / 1000)).toFixed(2)
        });

        // Calculate and log cost
        const cost = calculateCost(estimatedTokens, estimatedTokens, 0);
        log.token(`💰 Estimated cost: ${cost.formatted}`);
        console.log('Cost breakdown:', cost);

        // Track in analytics
        trackMessage('assistant', estimatedTokens, 0, cost.totalCost);

        console.groupEnd(); // End Stream Response Details

        // Message already added by streaming (no need to add again)

        // Add to conversation history
        conversationHistory.push({
            role: 'model',
            parts: [{ text: responseText }]
        });

        log.system('Response added to conversation history');

        // Memory check after response
        if (conversationHistory.length % 5 === 0) {
            logMemoryUsage();
        }

    } catch (error) {
        sessionStats.errors++;

        // Remove loading indicator and restore to normal state
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) {
            // Check if it's still a loading indicator or was converted to message
            const contentDiv = loadingEl.querySelector('.message-content');
            if (contentDiv && (contentDiv.classList.contains('loading') || contentDiv.classList.contains('streaming'))) {
                removeLoadingIndicator(loadingId);
            }
        }

        console.group('❌ ERROR DETAILS');
        log.error('API request failed', error);
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        console.table({
            'Error Type': error.name,
            'Message': error.message,
            'When': new Date().toISOString()
        });
        console.trace();
        console.groupEnd();

        addMessage('error', 'Error: ' + error.message);
        console.count('❌ Failed Requests');
    } finally {
        // Re-enable input
        input.disabled = false;
        document.getElementById('sendButton').disabled = false;
        input.focus();
        log.system('Input re-enabled');

        console.timeEnd('⏱️ Total Request Duration');

        // Show updated session stats
        logSessionStats(sessionStats);

        console.groupEnd(); // End Message Send Operation
    }
}

// ============================================
// UI HELPERS
// ============================================

function addMessage(type, content) {
    console.groupCollapsed(`💬 ${type.toUpperCase()} Message Added`);

    const container = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Use markdown rendering for assistant messages
    if (type === 'assistant') {
        contentDiv.classList.add('markdown');
        contentDiv.innerHTML = renderMarkdown(content);
    } else {
        contentDiv.textContent = content;
    }

    messageDiv.appendChild(contentDiv);
    container.appendChild(messageDiv);

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;

    console.log('Message type:', type);
    console.log('Content length:', content.length);
    console.log('Content preview:', content.substring(0, 50) + '...');
    console.log('DOM element created:', messageDiv);
    console.log('Container scroll position:', container.scrollTop);

    console.groupEnd();
}

function addLoadingIndicator() {
    const container = document.getElementById('messagesContainer');
    const loadingDiv = document.createElement('div');
    const loadingId = 'loading-' + Date.now();
    loadingDiv.id = loadingId;
    loadingDiv.className = 'message assistant';
    loadingDiv.innerHTML = `
        <div class="message-content loading">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        </div>
    `;
    container.appendChild(loadingDiv);
    container.scrollTop = container.scrollHeight;

    log.system('Loading indicator added', loadingId);
    console.count('⏳ Loading Indicators Created');

    return loadingId;
}

function removeLoadingIndicator(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
        log.system('Loading indicator removed', loadingId);
        console.count('✅ Loading Indicators Removed');
    } else {
        log.error('Loading indicator not found', loadingId);
    }
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        log.user('Enter key pressed - sending message');
        console.log('Keyboard shortcut:', 'Enter (without Shift)');
        sendMessage();
    } else if (event.key === 'Enter' && event.shiftKey) {
        console.log('Keyboard shortcut:', 'Shift+Enter (new line)');
    }
}

// ============================================
// PERIODIC LOGGING
// ============================================

function startPeriodicLogging() {
    // Log memory usage every 30 seconds
    setInterval(() => {
        if (client && conversationHistory.length > 0) {
            console.groupCollapsed('⏰ Periodic Memory Check');
            logMemoryUsage();
            console.log('Current time:', new Date().toLocaleTimeString());
            console.groupEnd();
        }
    }, 30000);

    // Log session stats every minute
    setInterval(() => {
        if (client && sessionStats.messagesCount > 0) {
            console.groupCollapsed('⏰ Periodic Stats Update');
            logSessionStats(sessionStats);
            console.log('Current time:', new Date().toLocaleTimeString());
            console.groupEnd();
        }
    }, 60000);
}

// ============================================
// START APPLICATION
// ============================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

