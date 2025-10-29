/* ============================================
   🎨 GEMINI CHAT - LOGGING SYSTEM
   Advanced console logging utilities
   ============================================ */

// Print ASCII art banner
export const banner = `
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ██████╗ ███████╗███╗   ███╗██╗███╗   ██╗██╗          ║
║  ██╔════╝ ██╔════╝████╗ ████║██║████╗  ██║██║          ║
║  ██║  ███╗█████╗  ██╔████╔██║██║██╔██╗ ██║██║          ║
║  ██║   ██║██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██║          ║
║  ╚██████╔╝███████╗██║ ╚═╝ ██║██║██║ ╚████║██║          ║
║   ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝          ║
║                                                          ║
║          🚀 Advanced Chat Interface v1.0 🚀              ║
║          💬 Powered by Gemini 2.5 Flash                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        `;

// Styled console log helpers
export const log = {
    system: (msg, data) => {
        console.log(
            '%c🔧 SYSTEM %c' + msg,
            'background: #667eea; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
            'color: #667eea; font-weight: bold;',
            data || ''
        );
    },
    api: (msg, data) => {
        console.log(
            '%c🌐 API %c' + msg,
            'background: #51cf66; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
            'color: #51cf66; font-weight: bold;',
            data || ''
        );
    },
    user: (msg, data) => {
        console.log(
            '%c👤 USER %c' + msg,
            'background: #764ba2; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
            'color: #764ba2; font-weight: bold;',
            data || ''
        );
    },
    ai: (msg, data) => {
        console.log(
            '%c🤖 AI %c' + msg,
            'background: #ff6b6b; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
            'color: #ff6b6b; font-weight: bold;',
            data || ''
        );
    },
    token: (msg, data) => {
        console.log(
            '%c🎯 TOKEN %c' + msg,
            'background: #ffd93d; color: black; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
            'color: #ffd93d; font-weight: bold;',
            data || ''
        );
    },
    cache: (msg, data) => {
        console.log(
            '%c💾 CACHE %c' + msg,
            'background: #6bcf7f; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
            'color: #6bcf7f; font-weight: bold;',
            data || ''
        );
    },
    perf: (msg, data) => {
        console.log(
            '%c⚡ PERF %c' + msg,
            'background: #ff9f1c; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
            'color: #ff9f1c; font-weight: bold;',
            data || ''
        );
    },
    error: (msg, error) => {
        console.log(
            '%c❌ ERROR %c' + msg,
            'background: #d32f2f; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;',
            'color: #d32f2f; font-weight: bold;',
            error || ''
        );
    }
};

// Display session stats as a table
export function logSessionStats(sessionStats) {
    console.groupCollapsed('📊 Session Statistics');
    console.table({
        'Messages Sent': sessionStats.messagesCount,
        'API Calls': sessionStats.apiCalls,
        'Total Tokens': sessionStats.totalTokens,
        'Cached Tokens': sessionStats.cachedTokens,
        'Input Tokens': sessionStats.inputTokens,
        'Output Tokens': sessionStats.outputTokens,
        'Errors': sessionStats.errors,
        'Uptime (seconds)': ((Date.now() - sessionStats.startTime) / 1000).toFixed(2),
        'Cache Hit Rate': sessionStats.totalTokens > 0
            ? ((sessionStats.cachedTokens / sessionStats.totalTokens * 100).toFixed(2) + '%')
            : '0%'
    });
    console.groupEnd();
}

// Memory usage logging
export function logMemoryUsage() {
    if (performance.memory) {
        console.groupCollapsed('💾 Memory Usage');
        const used = (performance.memory.usedJSHeapSize / 1048576).toFixed(2);
        const total = (performance.memory.totalJSHeapSize / 1048576).toFixed(2);
        const limit = (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2);

        console.log(`Used: ${used} MB / ${total} MB (Limit: ${limit} MB)`);
        console.log(`Usage: ${((used / limit) * 100).toFixed(2)}%`);

        // Visual bar
        const barLength = 50;
        const filledLength = Math.round((used / limit) * barLength);
        const bar = '█'.repeat(filledLength) + '░'.repeat(barLength - filledLength);
        console.log(`[${bar}]`);
        console.groupEnd();
    }
}

// Initialize logging system
export function initializeLogging() {
    console.log('%c' + banner, 'color: #667eea; font-weight: bold;');
    console.count('🔄 App Initialization');

    console.log('%c' + '═'.repeat(60), 'color: #667eea;');
    console.log('%c✨ Console Logging System Initialized ✨', 'font-size: 16px; font-weight: bold; color: #51cf66;');
    console.log('%c' + '═'.repeat(60), 'color: #667eea;');
    console.log('');
    console.log('%c📚 Available Commands:', 'font-weight: bold; font-size: 14px;');
    console.log('');
    console.table({
        'getSessionStats()': 'View current session statistics',
        'getConversationHistory()': 'View conversation history',
        'showMemory()': 'Check memory usage',
        'clearHistory()': 'Clear conversation history',
        'clearApiKey()': 'Clear API key and reload',
        'exportConversation()': 'Export conversation to JSON',
        'startProfiling()': 'Start performance profiling',
        'stopProfiling()': 'Stop performance profiling'
    });
    console.log('');
    console.log('%c🎨 Console Features Used:', 'font-weight: bold; font-size: 14px;');
    console.log('✓ Styled logs with CSS');
    console.log('✓ console.table() for data visualization');
    console.log('✓ console.group() / console.groupCollapsed()');
    console.log('✓ console.time() / console.timeEnd()');
    console.log('✓ console.count()');
    console.log('✓ console.trace()');
    console.log('✓ console.assert()');
    console.log('✓ console.dir() for object inspection');
    console.log('✓ console.profile() for performance');
    console.log('✓ performance.memory for memory tracking');
    console.log('✓ ASCII art banners');
    console.log('✓ Visual progress bars');
    console.log('✓ Automatic periodic logging');
    console.log('');
    console.log('%c🚀 Ready to chat! Type your message above.', 'color: #667eea; font-weight: bold; font-size: 14px;');
    console.log('');
}

