/* ============================================
   🌊 GEMINI CHAT - STREAMING RESPONSES
   Real-time streaming AI responses
   ============================================ */

import { log } from './logging.js';
import { renderMarkdown } from './markdown-renderer.js';

/**
 * Stream a response from Gemini API with real-time updates
 * @param {GoogleGenAI} client - The Gemini client
 * @param {Array} history - Conversation history
 * @param {HTMLElement} messageElement - The message element to update
 * @param {Object} sessionStats - Session statistics object
 * @returns {Promise<Object>} Response metadata
 */
export async function streamResponse(client, history, messageElement, sessionStats) {
    console.group('🌊 Streaming Response');
    console.time('⏱️ Stream Duration');

    const startTime = performance.now();
    let fullText = '';
    let tokenCount = 0;

    log.api('🌊 Starting stream from Gemini API...');

    try {
        if (typeof client?.models?.generateContentStream !== 'function') {
            throw new Error('Streaming not supported by this @google/genai client');
        }

        const responseStream = await client.models.generateContentStream({
            model: 'gemini-2.5-flash',
            contents: history
        });

        log.system('Stream established');
        let chunkCount = 0;

        const partsToText = (parts = []) => parts.map(part => part.text || '').join('');

        // Process each chunk as it arrives from the async iterator
        for await (const chunk of responseStream.stream) {
            chunkCount++;

            // Extract text from chunk (Gemini API returns text in candidates)
            const candidates = chunk.candidates || [];
            if (candidates.length > 0 && candidates[0].content && candidates[0].content.parts) {
                const text = partsToText(candidates[0].content.parts);

                if (text) {
                    fullText += text;
                    tokenCount += Math.ceil(text.length / 4);

                    // Update the message in real-time
                    const html = renderMarkdown(fullText);
                    messageElement.innerHTML = html;

                    // Scroll to bottom
                    const container = document.getElementById('messagesContainer');
                    container.scrollTop = container.scrollHeight;

                    // Log chunk details (collapsed)
                    console.groupCollapsed(`📦 Chunk ${chunkCount}`);
                    console.log('Text length:', text.length);
                    console.log('Cumulative length:', fullText.length);
                    console.log('Estimated tokens:', tokenCount);
                    console.dir(chunk);
                    console.groupEnd();
                }
            }
        }

        const finalResponse = await responseStream.response;

        // If chunks yielded no text (e.g., empty baseline), fall back to final aggregated response
        if (!fullText) {
            const finalCandidates = finalResponse?.candidates || [];
            if (finalCandidates.length > 0 && finalCandidates[0].content && finalCandidates[0].content.parts) {
                fullText = partsToText(finalCandidates[0].content.parts);
            }
        }

        // Prefer actual token counts when available
        const usageMetadata = finalResponse?.usageMetadata || finalResponse?.usage_metadata;
        if (usageMetadata && usageMetadata.candidatesTokenCount) {
            tokenCount = usageMetadata.candidatesTokenCount;
        } else if (!tokenCount && fullText) {
            tokenCount = Math.ceil(fullText.length / 4);
        }

        const endTime = performance.now();
        const duration = (endTime - startTime).toFixed(2);

        console.timeEnd('⏱️ Stream Duration');
        log.perf(`Stream completed in ${duration}ms`);
        log.system(`Received ${chunkCount} chunks`);

        console.log('Stream Statistics:', {
            'Total Chunks': chunkCount,
            'Total Characters': fullText.length,
            'Duration (ms)': duration,
            'Chars/sec': (fullText.length / (duration / 1000)).toFixed(0),
            'Chunks/sec': (chunkCount / (duration / 1000)).toFixed(2)
        });

        console.groupEnd();

        return {
            text: fullText,
            duration: duration,
            chunks: chunkCount,
            tokens: tokenCount
        };

    } catch (error) {
        sessionStats.errors++;
        log.error('Streaming failed', error);
        console.error('Stream error details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        console.groupEnd();
        throw error;
    }
}

/**
 * Create a typing indicator animation
 * @param {HTMLElement} element - Element to animate
 */
export function startTypingAnimation(element) {
    element.classList.add('typing');
    element.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
    log.system('Typing animation started');
}

/**
 * Stop typing animation
 * @param {HTMLElement} element - Element to clear
 */
export function stopTypingAnimation(element) {
    element.classList.remove('typing');
    log.system('Typing animation stopped');
}

/**
 * Add streaming-specific styles
 */
export function injectStreamingStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* Streaming Indicator */
        .message-content.streaming {
            position: relative;
        }

        .message-content.streaming::after {
            content: '▊';
            animation: blink 1s infinite;
            margin-left: 2px;
            opacity: 0.7;
        }

        @keyframes blink {
            0%, 50% { opacity: 0.7; }
            51%, 100% { opacity: 0; }
        }

        /* Typing Dots */
        .typing {
            display: flex;
            gap: 4px;
            padding: 12px 16px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: var(--button-primary);
            border-radius: 50%;
            animation: typing-bounce 1.4s infinite ease-in-out both;
        }

        .typing-dot:nth-child(1) {
            animation-delay: -0.32s;
        }

        .typing-dot:nth-child(2) {
            animation-delay: -0.16s;
        }

        @keyframes typing-bounce {
            0%, 80%, 100% {
                transform: scale(0);
            }
            40% {
                transform: scale(1);
            }
        }

        /* Smooth text appearance */
        .message-content.markdown {
            animation: fadeIn 0.3s ease-out;
        }

        @keyframes fadeIn {
            from {
                opacity: 0.8;
            }
            to {
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    log.system('🌊 Streaming styles injected');
}

// Initialize styles when module loads
injectStreamingStyles();

