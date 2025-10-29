/* ============================================
   📝 GEMINI CHAT - MARKDOWN RENDERER
   Beautiful markdown rendering with syntax highlighting
   ============================================ */

import { log } from './logging.js';

// Initialize marked.js for markdown parsing
const markedScript = document.createElement('script');
markedScript.src = 'https://cdn.jsdelivr.net/npm/marked@11.0.0/marked.min.js';
document.head.appendChild(markedScript);

// Initialize highlight.js for code syntax highlighting
const highlightScript = document.createElement('script');
highlightScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js';
document.head.appendChild(highlightScript);

const highlightStyles = document.createElement('link');
highlightStyles.rel = 'stylesheet';
highlightStyles.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css';
document.head.appendChild(highlightStyles);

// Wait for libraries to load
let librariesLoaded = false;

window.addEventListener('load', () => {
    setTimeout(() => {
        if (typeof marked !== 'undefined' && typeof hljs !== 'undefined') {
            // Configure marked to use highlight.js
            marked.setOptions({
                highlight: function(code, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        return hljs.highlight(code, { language: lang }).value;
                    }
                    return hljs.highlightAuto(code).value;
                },
                breaks: true,
                gfm: true
            });
            librariesLoaded = true;
            log.system('✨ Markdown renderer initialized');
        }
    }, 500);
});

/**
 * Render markdown text to HTML
 * @param {string} text - Markdown text to render
 * @returns {string} HTML string
 */
export function renderMarkdown(text) {
    if (!librariesLoaded || typeof marked === 'undefined') {
        // Fallback: basic formatting
        return text
            .replace(/\n/g, '<br>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>');
    }

    try {
        const html = marked.parse(text);

        // Post-process to add copy buttons to code blocks
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;

        const codeBlocks = tempDiv.querySelectorAll('pre code');
        codeBlocks.forEach((block, index) => {
            const pre = block.parentElement;
            const wrapper = document.createElement('div');
            wrapper.className = 'code-block-wrapper';

            const toolbar = document.createElement('div');
            toolbar.className = 'code-toolbar';

            const lang = block.className.replace('language-', '') || 'text';
            const langLabel = document.createElement('span');
            langLabel.className = 'code-language';
            langLabel.textContent = lang;

            const copyBtn = document.createElement('button');
            copyBtn.className = 'code-copy-btn';
            copyBtn.innerHTML = '📋 Copy';
            copyBtn.onclick = () => copyCode(block.textContent, copyBtn);

            toolbar.appendChild(langLabel);
            toolbar.appendChild(copyBtn);

            pre.parentNode.insertBefore(wrapper, pre);
            wrapper.appendChild(toolbar);
            wrapper.appendChild(pre);
        });

        return tempDiv.innerHTML;
    } catch (error) {
        log.error('Markdown rendering failed', error);
        return text.replace(/\n/g, '<br>');
    }
}

/**
 * Copy code to clipboard
 * @param {string} code - Code to copy
 * @param {HTMLElement} button - Button that triggered the copy
 */
function copyCode(code, button) {
    navigator.clipboard.writeText(code).then(() => {
        const originalText = button.innerHTML;
        button.innerHTML = '✅ Copied!';
        button.classList.add('copied');

        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('copied');
        }, 2000);

        log.system('Code copied to clipboard');
    }).catch(err => {
        log.error('Failed to copy code', err);
        button.innerHTML = '❌ Failed';
        setTimeout(() => {
            button.innerHTML = '📋 Copy';
        }, 2000);
    });
}

/**
 * Add markdown styles to the document
 */
export function injectMarkdownStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* Markdown Content Styles */
        .message-content.markdown {
            line-height: 1.6;
        }

        .message-content.markdown h1,
        .message-content.markdown h2,
        .message-content.markdown h3 {
            margin-top: 16px;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .message-content.markdown h1 { font-size: 1.5em; }
        .message-content.markdown h2 { font-size: 1.3em; }
        .message-content.markdown h3 { font-size: 1.1em; }

        .message-content.markdown p {
            margin: 8px 0;
        }

        .message-content.markdown code {
            background: rgba(0, 0, 0, 0.1);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
        }

        .message-content.markdown pre {
            background: #1e1e1e;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 12px 0;
        }

        .message-content.markdown pre code {
            background: none;
            padding: 0;
            color: #d4d4d4;
            display: block;
        }

        .message-content.markdown ul,
        .message-content.markdown ol {
            margin: 8px 0;
            padding-left: 24px;
        }

        .message-content.markdown li {
            margin: 4px 0;
        }

        .message-content.markdown blockquote {
            border-left: 4px solid var(--accent-color);
            margin: 12px 0;
            padding-left: 16px;
            color: var(--text-secondary);
            font-style: italic;
        }

        .message-content.markdown a {
            color: var(--accent-color);
            text-decoration: none;
        }

        .message-content.markdown a:hover {
            text-decoration: underline;
        }

        .message-content.markdown table {
            border-collapse: collapse;
            width: 100%;
            margin: 12px 0;
        }

        .message-content.markdown th,
        .message-content.markdown td {
            border: 1px solid var(--input-border);
            padding: 8px 12px;
            text-align: left;
        }

        .message-content.markdown th {
            background: var(--input-bg);
            font-weight: 600;
        }

        .message-content.markdown hr {
            border: none;
            border-top: 2px solid var(--input-border);
            margin: 16px 0;
        }

        /* Code Block Wrapper */
        .code-block-wrapper {
            position: relative;
            margin: 12px 0;
        }

        .code-toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #2d2d2d;
            padding: 8px 12px;
            border-radius: 8px 8px 0 0;
            font-size: 12px;
        }

        .code-language {
            color: #888;
            text-transform: uppercase;
            font-weight: 600;
        }

        .code-copy-btn {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: #fff;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.2s;
        }

        .code-copy-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .code-copy-btn.copied {
            background: #51cf66;
        }

        .code-block-wrapper pre {
            margin: 0;
            border-radius: 0 0 8px 8px;
        }
    `;
    document.head.appendChild(style);
    log.system('📝 Markdown styles injected');
}

// Initialize styles when module loads
injectMarkdownStyles();

