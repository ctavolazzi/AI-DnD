/**
 * Main entry point for the Browser D&D Game
 * Initializes the game engine and starts the application
 */

// Global game instance
let gameEngine = null;
let startScreen = null;

/**
 * Initialize the game when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    try {
        console.log('🎮 Initializing Browser D&D Game...');

        // Initialize game engine
        gameEngine = new GameEngine();

        // Wait for engine to be ready
        if (gameEngine.isReady()) {
            console.log('✅ Game engine initialized successfully');

            // Initialize start screen
            startScreen = new StartScreen(
                gameEngine.getEventBus(),
                gameEngine.getStateManager(),
                gameEngine.getSaveManager()
            );

            // Set up global references for debugging
            window.gameEngine = gameEngine;
            window.startScreen = startScreen;

            // Enable debug mode in development
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                gameEngine.setDebug(true);
                startScreen.setDebug(true);
                console.log('🐛 Debug mode enabled');
            }

            // Set up error handling
            setupErrorHandling();

            // Set up keyboard shortcuts
            setupKeyboardShortcuts();

            console.log('🎯 Game ready! Press F1 for help');

        } else {
            throw new Error('Game engine failed to initialize');
        }

    } catch (error) {
        console.error('❌ Failed to initialize game:', error);
        showError('Failed to initialize game. Please refresh the page.');
    }
});

/**
 * Set up error handling
 */
function setupErrorHandling() {
    // Global error handler
    window.addEventListener('error', (event) => {
        console.error('Global error:', event.error);
        showError('An unexpected error occurred. Check the console for details.');
    });

    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
        showError('An unexpected error occurred. Check the console for details.');
    });
}

/**
 * Set up keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (event) => {
        // F1 - Show help
        if (event.key === 'F1') {
            event.preventDefault();
            showHelp();
        }

        // Escape - Go back to main menu
        if (event.key === 'Escape') {
            event.preventDefault();
            if (gameEngine && gameEngine.getState().ui.currentScreen === 'game') {
                gameEngine.showStartScreen();
            }
        }

        // Ctrl+S - Quick save
        if (event.ctrlKey && event.key === 's') {
            event.preventDefault();
            if (gameEngine && gameEngine.getState().ui.currentScreen === 'game') {
                gameEngine.getSaveManager().saveGame('quicksave');
            }
        }

        // Ctrl+L - Quick load
        if (event.ctrlKey && event.key === 'l') {
            event.preventDefault();
            if (gameEngine && gameEngine.getState().ui.currentScreen === 'start') {
                startScreen.showSaveList();
            }
        }
    });
}

/**
 * Show error message
 * @param {string} message - Error message
 */
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #f44336;
        color: white;
        padding: 20px;
        border-radius: 8px;
        font-family: 'Press Start 2P', monospace;
        font-size: 12px;
        z-index: 10000;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.5);
    `;
    errorDiv.textContent = message;

    document.body.appendChild(errorDiv);

    // Remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

/**
 * Show help information
 */
function showHelp() {
    const helpDiv = document.createElement('div');
    helpDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--panel-parchment);
        color: var(--text-dark);
        padding: 30px;
        border: 3px solid var(--border-wood);
        border-radius: 8px;
        font-family: 'Press Start 2P', monospace;
        font-size: 10px;
        z-index: 10000;
        text-align: left;
        box-shadow: var(--shadow-lg);
        max-width: 500px;
        line-height: 1.8;
    `;

    helpDiv.innerHTML = `
        <h3 style="text-align: center; margin-bottom: 20px; color: var(--accent-brown);">Keyboard Shortcuts</h3>
        <div style="margin-bottom: 15px;">
            <strong>F1</strong> - Show this help<br>
            <strong>Escape</strong> - Return to main menu<br>
            <strong>Ctrl+S</strong> - Quick save (in game)<br>
            <strong>Ctrl+L</strong> - Quick load (from menu)
        </div>
        <div style="margin-bottom: 15px;">
            <strong>Mouse:</strong><br>
            • Click buttons to navigate<br>
            • Click save slots to load games<br>
            • Use form inputs for character creation
        </div>
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="this.parentElement.parentElement.remove()"
                    style="padding: 10px 20px; font-family: inherit; font-size: 10px;
                           background: var(--primary-gold); border: 2px solid var(--border-wood);
                           cursor: pointer; color: var(--text-dark);">
                Close
            </button>
        </div>
    `;

    document.body.appendChild(helpDiv);

    // Close on escape
    const closeHandler = (event) => {
        if (event.key === 'Escape') {
            helpDiv.remove();
            document.removeEventListener('keydown', closeHandler);
        }
    };
    document.addEventListener('keydown', closeHandler);
}

/**
 * Get game engine instance
 * @returns {GameEngine|null} Game engine instance
 */
function getGameEngine() {
    return gameEngine;
}

/**
 * Get start screen instance
 * @returns {StartScreen|null} Start screen instance
 */
function getStartScreen() {
    return startScreen;
}

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

console.log('📜 Main script loaded');
