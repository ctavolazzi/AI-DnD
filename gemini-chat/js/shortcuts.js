/* ============================================
   ⌨️ GEMINI CHAT - KEYBOARD SHORTCUTS
   Power user keyboard shortcuts and command palette
   ============================================ */

import { log } from './logging.js';

const shortcuts = {
    'cmd+k': { action: 'openCommandPalette', description: 'Open command palette', category: 'Navigation' },
    'cmd+/': { action: 'showShortcuts', description: 'Show keyboard shortcuts', category: 'Help' },
    'cmd+l': { action: 'clearChat', description: 'Clear conversation', category: 'Actions' },
    'cmd+s': { action: 'exportConversation', description: 'Export conversation', category: 'Actions' },
    'cmd+t': { action: 'toggleTheme', description: 'Toggle theme menu', category: 'Appearance' },
    'cmd+d': { action: 'toggleDarkMode', description: 'Toggle dark mode', category: 'Appearance' },
    'cmd+.': { action: 'showStats', description: 'Show session stats', category: 'Debug' },
    'cmd+m': { action: 'showMemory', description: 'Show memory usage', category: 'Debug' },
    'esc': { action: 'closeModal', description: 'Close modal/menu', category: 'Navigation' },
    'cmd+enter': { action: 'sendMessage', description: 'Send message', category: 'Chat' }
};

let commandPaletteOpen = false;
let shortcutsModalOpen = false;

/**
 * Initialize keyboard shortcuts system
 * @param {Object} handlers - Action handlers
 */
export function initializeShortcuts(handlers) {
    document.addEventListener('keydown', (e) => {
        const key = getKeyCombo(e);

        if (shortcuts[key]) {
            const shortcut = shortcuts[key];

            // Don't prevent default for text inputs unless it's a special combo
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                if (!['cmd+k', 'cmd+/', 'esc'].includes(key)) {
                    return;
                }
            }

            e.preventDefault();
            log.system(`Keyboard shortcut: ${key} → ${shortcut.description}`);

            if (handlers[shortcut.action]) {
                handlers[shortcut.action]();
            }
        }
    });

    // Inject shortcuts UI
    injectShortcutsUI();
    injectCommandPalette();

    log.system('⌨️ Keyboard shortcuts initialized');
    console.log('Available shortcuts:', shortcuts);
}

/**
 * Get key combination string
 */
function getKeyCombo(e) {
    const parts = [];

    if (e.metaKey || e.ctrlKey) parts.push('cmd');
    if (e.shiftKey) parts.push('shift');
    if (e.altKey) parts.push('alt');

    const key = e.key.toLowerCase();
    if (key !== 'meta' && key !== 'control' && key !== 'shift' && key !== 'alt') {
        parts.push(key === ' ' ? 'space' : key);
    }

    return parts.join('+');
}

/**
 * Show keyboard shortcuts modal
 */
export function showShortcutsModal() {
    if (shortcutsModalOpen) return;

    const modal = document.getElementById('shortcuts-modal');
    modal.classList.add('show');
    shortcutsModalOpen = true;
    log.system('Shortcuts modal opened');
}

/**
 * Hide keyboard shortcuts modal
 */
export function hideShortcutsModal() {
    const modal = document.getElementById('shortcuts-modal');
    modal.classList.remove('show');
    shortcutsModalOpen = false;
    log.system('Shortcuts modal closed');
}

/**
 * Show command palette
 */
export function showCommandPalette() {
    if (commandPaletteOpen) return;

    const palette = document.getElementById('command-palette');
    const input = document.getElementById('command-input');
    palette.classList.add('show');
    commandPaletteOpen = true;
    setTimeout(() => input.focus(), 100);
    log.system('Command palette opened');
}

/**
 * Hide command palette
 */
export function hideCommandPalette() {
    const palette = document.getElementById('command-palette');
    const input = document.getElementById('command-input');
    palette.classList.remove('show');
    input.value = '';
    commandPaletteOpen = false;
    filterCommands('');
    log.system('Command palette closed');
}

/**
 * Filter commands in palette
 */
function filterCommands(query) {
    const commands = document.querySelectorAll('.command-item');
    const lowerQuery = query.toLowerCase();

    commands.forEach(cmd => {
        const text = cmd.textContent.toLowerCase();
        if (text.includes(lowerQuery)) {
            cmd.style.display = 'flex';
        } else {
            cmd.style.display = 'none';
        }
    });
}

/**
 * Inject command palette UI
 */
function injectCommandPalette() {
    const palette = document.createElement('div');
    palette.id = 'command-palette';
    palette.className = 'command-palette';

    const commands = Object.entries(shortcuts).map(([key, shortcut]) => {
        return `
            <div class="command-item" data-action="${shortcut.action}">
                <div class="command-info">
                    <div class="command-name">${shortcut.description}</div>
                    <div class="command-category">${shortcut.category}</div>
                </div>
                <div class="command-key">${formatKey(key)}</div>
            </div>
        `;
    }).join('');

    palette.innerHTML = `
        <div class="command-content">
            <div class="command-header">
                <span>🚀</span>
                <input type="text" id="command-input" placeholder="Type a command..." />
                <span class="command-close" onclick="window.hideCommandPalette()">✕</span>
            </div>
            <div class="command-list">
                ${commands}
            </div>
        </div>
    `;

    document.body.appendChild(palette);

    // Setup command input filter
    const input = document.getElementById('command-input');
    input.addEventListener('input', (e) => filterCommands(e.target.value));

    // Setup command clicks
    palette.querySelectorAll('.command-item').forEach(item => {
        item.addEventListener('click', () => {
            const action = item.dataset.action;
            hideCommandPalette();
            if (window[action]) {
                window[action]();
            }
        });
    });

    // Close on backdrop click
    palette.addEventListener('click', (e) => {
        if (e.target === palette) {
            hideCommandPalette();
        }
    });
}

/**
 * Inject shortcuts modal UI
 */
function injectShortcutsUI() {
    const modal = document.createElement('div');
    modal.id = 'shortcuts-modal';
    modal.className = 'shortcuts-modal';

    // Group shortcuts by category
    const categories = {};
    Object.entries(shortcuts).forEach(([key, shortcut]) => {
        if (!categories[shortcut.category]) {
            categories[shortcut.category] = [];
        }
        categories[shortcut.category].push({ key, ...shortcut });
    });

    const categoriesHTML = Object.entries(categories).map(([category, items]) => {
        const itemsHTML = items.map(item => `
            <div class="shortcut-item">
                <span class="shortcut-desc">${item.description}</span>
                <kbd class="shortcut-key">${formatKey(item.key)}</kbd>
            </div>
        `).join('');

        return `
            <div class="shortcut-category">
                <h3>${category}</h3>
                ${itemsHTML}
            </div>
        `;
    }).join('');

    modal.innerHTML = `
        <div class="shortcuts-content">
            <div class="shortcuts-header">
                <h2>⌨️ Keyboard Shortcuts</h2>
                <button class="shortcuts-close" onclick="window.hideShortcutsModal()">✕</button>
            </div>
            <div class="shortcuts-body">
                ${categoriesHTML}
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Close on backdrop click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            hideShortcutsModal();
        }
    });
}

/**
 * Format key combination for display
 */
function formatKey(key) {
    return key
        .replace('cmd', '⌘')
        .replace('shift', '⇧')
        .replace('alt', '⌥')
        .replace('enter', '↵')
        .replace('esc', 'Esc')
        .toUpperCase();
}

/**
 * Inject styles for shortcuts and command palette
 */
export function injectShortcutStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* Command Palette */
        .command-palette {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(4px);
            display: none;
            align-items: flex-start;
            justify-content: center;
            padding-top: 15vh;
            z-index: 10000;
        }

        .command-palette.show {
            display: flex;
            animation: fadeIn 0.2s;
        }

        .command-content {
            background: var(--container-bg);
            border-radius: 12px;
            width: 90%;
            max-width: 600px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }

        .command-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            border-bottom: 1px solid var(--input-border);
        }

        .command-header input {
            flex: 1;
            border: none;
            background: none;
            font-size: 16px;
            color: var(--text-primary);
            outline: none;
        }

        .command-close {
            cursor: pointer;
            font-size: 20px;
            color: var(--text-secondary);
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
        }

        .command-close:hover {
            background: var(--input-bg);
        }

        .command-list {
            max-height: 400px;
            overflow-y: auto;
            padding: 8px;
        }

        .command-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .command-item:hover {
            background: var(--input-bg);
        }

        .command-info {
            flex: 1;
        }

        .command-name {
            color: var(--text-primary);
            font-weight: 500;
        }

        .command-category {
            color: var(--text-secondary);
            font-size: 12px;
            margin-top: 2px;
        }

        .command-key {
            background: var(--input-bg);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
        }

        /* Shortcuts Modal */
        .shortcuts-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(4px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }

        .shortcuts-modal.show {
            display: flex;
            animation: fadeIn 0.2s;
        }

        .shortcuts-content {
            background: var(--container-bg);
            border-radius: 12px;
            width: 90%;
            max-width: 700px;
            max-height: 80vh;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-direction: column;
        }

        .shortcuts-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid var(--input-border);
        }

        .shortcuts-header h2 {
            margin: 0;
            color: var(--text-primary);
        }

        .shortcuts-close {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: var(--text-secondary);
            width: 32px;
            height: 32px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .shortcuts-close:hover {
            background: var(--input-bg);
        }

        .shortcuts-body {
            padding: 20px;
            overflow-y: auto;
        }

        .shortcut-category {
            margin-bottom: 24px;
        }

        .shortcut-category h3 {
            color: var(--text-primary);
            margin-bottom: 12px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .shortcut-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
        }

        .shortcut-desc {
            color: var(--text-primary);
        }

        .shortcut-key {
            background: var(--input-bg);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            border: 1px solid var(--input-border);
        }
    `;
    document.head.appendChild(style);
    log.system('⌨️ Shortcut styles injected');
}

// Make functions globally available
window.showShortcutsModal = showShortcutsModal;
window.hideShortcutsModal = hideShortcutsModal;
window.showCommandPalette = showCommandPalette;
window.hideCommandPalette = hideCommandPalette;

// Initialize styles
injectShortcutStyles();

