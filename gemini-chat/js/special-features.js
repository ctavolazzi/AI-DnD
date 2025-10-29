/* ============================================
   🎲 GEMINI CHAT - SPECIAL FEATURES
   Fun interactive features like coin flips
   ============================================ */

import { log } from './logging.js';

/**
 * Check if message is a coin flip request (no regex!)
 * @param {string} message - User message to check
 * @returns {boolean} True if coin flip detected
 */
export function isCoinFlipRequest(message) {
    const lower = message.toLowerCase().trim();

    // List of coin flip phrases (no regex needed!)
    const coinFlipPhrases = [
        'flip a coin',
        'flip coin',
        'coin flip',
        'heads or tails',
        'yes or no',
        'decide for me',
        'make a decision',
        'pick yes or no',
        'should i',
        'yes no maybe'
    ];

    // Check if any phrase is in the message using simple string methods
    for (const phrase of coinFlipPhrases) {
        if (lower.includes(phrase)) {
            log.system(`🎲 Coin flip detected: "${phrase}"`);
            return true;
        }
    }

    // Also check for question marks + short messages (likely yes/no questions)
    if (lower.includes('?') && lower.split(' ').length <= 8) {
        const yesNoWords = ['yes', 'no', 'should', 'can', 'will', 'would', 'could'];
        for (const word of yesNoWords) {
            if (lower.includes(word)) {
                log.system(`🎲 Yes/No question detected`);
                return true;
            }
        }
    }

    return false;
}

/**
 * Fetch coin flip result from YesNo API
 * @returns {Promise<Object>} API response with answer and image
 */
export async function flipCoin() {
    console.group('🎲 Coin Flip');
    console.time('⏱️ API Response Time');

    try {
        log.system('Fetching from https://yesno.wtf/api');

        const response = await fetch('https://yesno.wtf/api');
        const data = await response.json();

        console.timeEnd('⏱️ API Response Time');

        console.log('API Response:', data);
        log.system(`Result: ${data.answer.toUpperCase()}`);
        log.system(`Image: ${data.image}`);

        console.groupEnd();

        return data;
    } catch (error) {
        console.timeEnd('⏱️ API Response Time');
        log.error('Coin flip API failed', error);
        console.groupEnd();
        throw error;
    }
}

/**
 * Create coin flip result HTML with GIF
 * @param {Object} result - YesNo API result
 * @param {string} originalQuestion - User's original question
 * @returns {string} HTML string
 */
export function createCoinFlipHTML(result, originalQuestion) {
    const { answer, image } = result;

    // Fun emojis for each answer
    const emojis = {
        'yes': '✅',
        'no': '❌',
        'maybe': '🤔'
    };

    const emoji = emojis[answer] || '🎲';

    // Create beautiful HTML with the GIF
    const html = `
        <div class="coin-flip-result">
            <div class="coin-flip-header">
                <span class="coin-flip-emoji">${emoji}</span>
                <h3 class="coin-flip-answer">The answer is: ${answer.toUpperCase()}!</h3>
            </div>
            <div class="coin-flip-question">
                <em>"${originalQuestion}"</em>
            </div>
            <div class="coin-flip-image">
                <img src="${image}" alt="${answer}" />
            </div>
            <div class="coin-flip-footer">
                <small>🎲 Powered by <a href="https://yesno.wtf" target="_blank">yesno.wtf</a></small>
            </div>
        </div>
    `;

    log.system('Coin flip HTML created');
    return html;
}

/**
 * Inject styles for coin flip display
 */
export function injectCoinFlipStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* Coin Flip Result Styles */
        .coin-flip-result {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 24px;
            margin: 8px 0;
            text-align: center;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            animation: coinFlipAppear 0.5s ease-out;
        }

        @keyframes coinFlipAppear {
            from {
                opacity: 0;
                transform: scale(0.9) rotateY(90deg);
            }
            to {
                opacity: 1;
                transform: scale(1) rotateY(0deg);
            }
        }

        .coin-flip-header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 16px;
        }

        .coin-flip-emoji {
            font-size: 36px;
            animation: bounce 1s ease-in-out infinite;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .coin-flip-answer {
            color: white;
            margin: 0;
            font-size: 28px;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .coin-flip-question {
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            margin: 0 0 20px 0;
            font-style: italic;
        }

        .coin-flip-image {
            background: white;
            border-radius: 12px;
            padding: 8px;
            margin: 16px auto;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .coin-flip-image img {
            width: 100%;
            height: auto;
            border-radius: 8px;
            display: block;
        }

        .coin-flip-footer {
            margin-top: 16px;
            color: rgba(255, 255, 255, 0.8);
        }

        .coin-flip-footer a {
            color: white;
            text-decoration: none;
            font-weight: 600;
        }

        .coin-flip-footer a:hover {
            text-decoration: underline;
        }

        /* Dark theme adjustments */
        [data-theme="dark"] .coin-flip-result {
            background: linear-gradient(135deg, #4776E6 0%, #8E54E9 100%);
        }
    `;
    document.head.appendChild(style);
    log.system('🎲 Coin flip styles injected');
}

// Initialize styles when module loads
injectCoinFlipStyles();

