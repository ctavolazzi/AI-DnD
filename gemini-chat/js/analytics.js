/* ============================================
   📊 GEMINI CHAT - ANALYTICS DASHBOARD
   Advanced analytics and cost tracking
   ============================================ */

import { log } from './logging.js';

// Gemini API Pricing (as of 2024)
const PRICING = {
    'gemini-2.5-flash': {
        input: 0.000000075,    // $0.075 per 1M tokens
        output: 0.0000003,     // $0.30 per 1M tokens
        cached: 0.0000000188   // $0.01875 per 1M tokens (cached)
    }
};

let analyticsData = {
    sessions: [],
    currentSession: {
        start: Date.now(),
        messages: [],
        totalCost: 0
    }
};

/**
 * Track a message in analytics
 */
export function trackMessage(type, tokens, cached, cost) {
    const message = {
        timestamp: Date.now(),
        type,
        tokens,
        cached,
        cost
    };

    analyticsData.currentSession.messages.push(message);
    analyticsData.currentSession.totalCost += cost;

    saveAnalytics();
}

/**
 * Calculate cost for a request
 */
export function calculateCost(promptTokens, outputTokens, cachedTokens) {
    const pricing = PRICING['gemini-2.5-flash'];

    const inputCost = (promptTokens - cachedTokens) * pricing.input;
    const cachedCost = cachedTokens * pricing.cached;
    const outputCost = outputTokens * pricing.output;

    const totalCost = inputCost + cachedCost + outputCost;

    return {
        inputCost,
        cachedCost,
        outputCost,
        totalCost,
        formatted: `$${totalCost.toFixed(6)}`
    };
}

/**
 * Show analytics dashboard
 */
export function showAnalytics() {
    const modal = document.getElementById('analytics-modal');
    if (!modal) {
        createAnalyticsModal();
    }

    updateAnalyticsDashboard();
    document.getElementById('analytics-modal').classList.add('show');
    log.system('📊 Analytics dashboard opened');
}

/**
 * Hide analytics dashboard
 */
export function hideAnalytics() {
    document.getElementById('analytics-modal').classList.remove('show');
    log.system('📊 Analytics dashboard closed');
}

/**
 * Update analytics dashboard with current data
 */
function updateAnalyticsDashboard() {
    const session = analyticsData.currentSession;
    const stats = calculateSessionStats(session);

    // Update summary cards
    document.getElementById('total-messages').textContent = stats.totalMessages;
    document.getElementById('total-tokens').textContent = stats.totalTokens.toLocaleString();
    document.getElementById('total-cost').textContent = stats.formattedCost;
    document.getElementById('cache-rate').textContent = stats.cacheRate + '%';

    // Update charts
    renderTokenChart(stats);
    renderCostChart(stats);
    renderMessageTimeline(session.messages);

    log.system('Analytics dashboard updated');
}

/**
 * Calculate statistics for current session
 */
function calculateSessionStats(session) {
    let totalTokens = 0;
    let cachedTokens = 0;
    let totalCost = 0;

    session.messages.forEach(msg => {
        totalTokens += msg.tokens;
        cachedTokens += msg.cached;
        totalCost += msg.cost;
    });

    const cacheRate = totalTokens > 0
        ? ((cachedTokens / totalTokens) * 100).toFixed(1)
        : 0;

    return {
        totalMessages: session.messages.length,
        totalTokens,
        cachedTokens,
        cacheRate,
        totalCost,
        formattedCost: `$${totalCost.toFixed(6)}`,
        duration: Date.now() - session.start
    };
}

/**
 * Render token distribution chart
 */
function renderTokenChart(stats) {
    const canvas = document.getElementById('token-chart');
    const ctx = canvas.getContext('2d');

    const cached = stats.cachedTokens;
    const regular = stats.totalTokens - stats.cachedTokens;
    const total = stats.totalTokens || 1;

    const cachedPercent = (cached / total);
    const regularPercent = (regular / total);

    // Simple bar chart
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    // Cached tokens (green)
    ctx.fillStyle = '#51cf66';
    ctx.fillRect(0, 0, width * cachedPercent, height);

    // Regular tokens (blue)
    ctx.fillStyle = '#667eea';
    ctx.fillRect(width * cachedPercent, 0, width * regularPercent, height);

    // Labels
    ctx.fillStyle = '#fff';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'center';

    if (cachedPercent > 0.1) {
        ctx.fillText('Cached', width * cachedPercent / 2, height / 2 + 4);
    }
    if (regularPercent > 0.1) {
        ctx.fillText('Regular', width * cachedPercent + (width * regularPercent / 2), height / 2 + 4);
    }
}

/**
 * Render cost breakdown chart
 */
function renderCostChart(stats) {
    const container = document.getElementById('cost-breakdown');

    const html = `
        <div class="cost-item">
            <span class="cost-label">💾 Cached Tokens</span>
            <span class="cost-value">${stats.cachedTokens.toLocaleString()}</span>
        </div>
        <div class="cost-item">
            <span class="cost-label">📝 Regular Tokens</span>
            <span class="cost-value">${(stats.totalTokens - stats.cachedTokens).toLocaleString()}</span>
        </div>
        <div class="cost-item">
            <span class="cost-label">💰 Total Cost</span>
            <span class="cost-value">${stats.formattedCost}</span>
        </div>
        <div class="cost-item">
            <span class="cost-label">⚡ Cache Efficiency</span>
            <span class="cost-value">${stats.cacheRate}%</span>
        </div>
    `;

    container.innerHTML = html;
}

/**
 * Render message timeline
 */
function renderMessageTimeline(messages) {
    const container = document.getElementById('message-timeline');

    const html = messages.slice(-10).reverse().map((msg, i) => {
        const time = new Date(msg.timestamp).toLocaleTimeString();
        const icon = msg.type === 'user' ? '👤' : '🤖';

        return `
            <div class="timeline-item">
                <span class="timeline-icon">${icon}</span>
                <span class="timeline-time">${time}</span>
                <span class="timeline-tokens">${msg.tokens} tokens</span>
                <span class="timeline-cost">$${msg.cost.toFixed(6)}</span>
            </div>
        `;
    }).join('');

    container.innerHTML = html || '<div class="timeline-empty">No messages yet</div>';
}

/**
 * Create analytics modal
 */
function createAnalyticsModal() {
    const modal = document.createElement('div');
    modal.id = 'analytics-modal';
    modal.className = 'analytics-modal';

    modal.innerHTML = `
        <div class="analytics-content">
            <div class="analytics-header">
                <h2>📊 Analytics Dashboard</h2>
                <button class="analytics-close" onclick="window.hideAnalytics()">✕</button>
            </div>

            <div class="analytics-body">
                <div class="analytics-summary">
                    <div class="summary-card">
                        <div class="summary-label">Messages</div>
                        <div class="summary-value" id="total-messages">0</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-label">Tokens</div>
                        <div class="summary-value" id="total-tokens">0</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-label">Cost</div>
                        <div class="summary-value" id="total-cost">$0.00</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-label">Cache Rate</div>
                        <div class="summary-value" id="cache-rate">0%</div>
                    </div>
                </div>

                <div class="analytics-section">
                    <h3>Token Distribution</h3>
                    <canvas id="token-chart" width="600" height="40"></canvas>
                    <div class="chart-legend">
                        <span><span class="legend-color" style="background: #51cf66;"></span> Cached (cheaper)</span>
                        <span><span class="legend-color" style="background: #667eea;"></span> Regular</span>
                    </div>
                </div>

                <div class="analytics-section">
                    <h3>Cost Breakdown</h3>
                    <div id="cost-breakdown"></div>
                </div>

                <div class="analytics-section">
                    <h3>Recent Messages</h3>
                    <div id="message-timeline"></div>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Close on backdrop click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            hideAnalytics();
        }
    });

    injectAnalyticsStyles();
}

/**
 * Inject analytics styles
 */
function injectAnalyticsStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .analytics-modal {
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

        .analytics-modal.show {
            display: flex;
            animation: fadeIn 0.2s;
        }

        .analytics-content {
            background: var(--container-bg);
            border-radius: 12px;
            width: 90%;
            max-width: 800px;
            max-height: 85vh;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-direction: column;
        }

        .analytics-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid var(--input-border);
        }

        .analytics-header h2 {
            margin: 0;
            color: var(--text-primary);
        }

        .analytics-close {
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

        .analytics-close:hover {
            background: var(--input-bg);
        }

        .analytics-body {
            padding: 20px;
            overflow-y: auto;
        }

        .analytics-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .summary-card {
            background: var(--input-bg);
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }

        .summary-label {
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .summary-value {
            color: var(--text-primary);
            font-size: 24px;
            font-weight: 600;
        }

        .analytics-section {
            margin-bottom: 24px;
        }

        .analytics-section h3 {
            color: var(--text-primary);
            margin-bottom: 12px;
            font-size: 16px;
        }

        #token-chart {
            width: 100%;
            height: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .chart-legend {
            display: flex;
            gap: 16px;
            margin-top: 8px;
            font-size: 12px;
            color: var(--text-secondary);
        }

        .legend-color {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 2px;
            margin-right: 4px;
        }

        .cost-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid var(--input-border);
        }

        .cost-item:last-child {
            border-bottom: none;
        }

        .cost-label {
            color: var(--text-secondary);
        }

        .cost-value {
            color: var(--text-primary);
            font-weight: 600;
        }

        .timeline-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px;
            border-bottom: 1px solid var(--input-border);
            font-size: 13px;
        }

        .timeline-icon {
            font-size: 16px;
        }

        .timeline-time {
            color: var(--text-secondary);
            min-width: 80px;
        }

        .timeline-tokens {
            color: var(--text-primary);
            flex: 1;
        }

        .timeline-cost {
            color: var(--accent-color);
            font-weight: 600;
        }

        .timeline-empty {
            text-align: center;
            color: var(--text-secondary);
            padding: 20px;
        }
    `;
    document.head.appendChild(style);
    log.system('📊 Analytics styles injected');
}

/**
 * Save analytics to localStorage
 */
function saveAnalytics() {
    try {
        localStorage.setItem('gemini-chat-analytics', JSON.stringify(analyticsData));
    } catch (e) {
        log.error('Failed to save analytics', e);
    }
}

/**
 * Load analytics from localStorage
 */
function loadAnalytics() {
    try {
        const saved = localStorage.getItem('gemini-chat-analytics');
        if (saved) {
            analyticsData = JSON.parse(saved);
            if (!analyticsData.currentSession) {
                analyticsData.currentSession = {
                    start: Date.now(),
                    messages: [],
                    totalCost: 0
                };
            }
        }
    } catch (e) {
        log.error('Failed to load analytics', e);
    }
}

// Make functions globally available
window.showAnalytics = showAnalytics;
window.hideAnalytics = hideAnalytics;

// Load saved analytics on module load
loadAnalytics();

export { analyticsData };

