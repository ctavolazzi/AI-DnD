/**
 * GameEngine - Main game engine coordinator
 * Based on learnings from the existing project
 */
class GameEngine {
    constructor() {
        this.eventBus = new EventBus();
        this.stateManager = new StateManager(this.eventBus);
        this.saveManager = new SaveManager(this.stateManager, this.eventBus);
        this.startScreen = null;
        this.gameScreen = null;
        this.isInitialized = false;
        this.debug = false;

        this.initialize();
    }

    /**
     * Initialize the game engine
     */
    initialize() {
        try {
            // Set up event listeners
            this.setupEventListeners();

            // Initialize UI components
            this.initializeUI();

            // Set up auto-save
            this.setupAutoSave();

            this.isInitialized = true;

            if (this.debug) {
                console.log('GameEngine: Initialized successfully');
            }

            this.eventBus.emit('engineInitialized');
        } catch (error) {
            console.error('GameEngine: Initialization failed', error);
            this.eventBus.emit('engineError', { error: error.message });
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Game state events
        this.eventBus.on('stateChanged', (data) => {
            if (this.debug) {
                console.log('GameEngine: State changed', data.path);
            }
        });

        // Save/Load events
        this.eventBus.on('gameSaved', (data) => {
            this.showNotification(`Game saved: ${data.saveName}`, 'success');
        });

        this.eventBus.on('gameLoaded', (data) => {
            this.showNotification(`Game loaded: ${data.saveName}`, 'success');
            this.transitionToGame();
        });

        this.eventBus.on('saveError', (data) => {
            this.showNotification(`Save failed: ${data.error}`, 'error');
        });

        this.eventBus.on('loadError', (data) => {
            this.showNotification(`Load failed: ${data.error}`, 'error');
        });

        // Screen transition events
        this.eventBus.on('startNewGame', () => {
            this.startNewGame();
        });

        this.eventBus.on('loadGame', (data) => {
            this.loadGame(data.saveName);
        });

        this.eventBus.on('showStartScreen', () => {
            this.showStartScreen();
        });

        this.eventBus.on('showGameScreen', () => {
            this.transitionToGame();
        });
    }

    /**
     * Initialize UI components
     */
    initializeUI() {
        // Initialize start screen
        this.startScreen = new StartScreen(this.eventBus, this.stateManager, this.saveManager);

        // Get game screen element
        this.gameScreen = document.getElementById('game-screen');

        if (!this.gameScreen) {
            throw new Error('Game screen element not found');
        }
    }

    /**
     * Set up auto-save functionality
     */
    setupAutoSave() {
        // Auto-save every 30 seconds if enabled
        setInterval(() => {
            if (this.stateManager.getStateValue('settings.autoSave') &&
                this.stateManager.getStateValue('ui.currentScreen') === 'game') {
                this.saveManager.saveGame(null, true);
            }
        }, 30000);
    }

    /**
     * Start a new game
     */
    startNewGame() {
        try {
            // Reset state
            this.stateManager.reset();

            // Generate new game ID
            const gameId = this.generateGameId();
            this.stateManager.setState('metadata.gameId', gameId);
            this.stateManager.setState('metadata.startTime', new Date().toISOString());
            this.stateManager.setState('ui.currentScreen', 'character-creation');

            if (this.debug) {
                console.log('GameEngine: New game started', { gameId });
            }

            this.eventBus.emit('newGameStarted', { gameId });
        } catch (error) {
            console.error('GameEngine: Failed to start new game', error);
            this.eventBus.emit('engineError', { error: error.message });
        }
    }

    /**
     * Load a game
     * @param {string} saveName - Name of the save to load
     */
    loadGame(saveName) {
        try {
            const success = this.saveManager.loadGame(saveName);

            if (success) {
                this.stateManager.setState('ui.currentScreen', 'game');
                this.eventBus.emit('gameLoaded', { saveName });
            }
        } catch (error) {
            console.error('GameEngine: Failed to load game', error);
            this.eventBus.emit('loadError', { error: error.message });
        }
    }

    /**
     * Transition to game screen
     */
    transitionToGame() {
        try {
            // Hide start screen
            const startScreen = document.getElementById('start-screen');
            if (startScreen) {
                startScreen.classList.remove('active');
            }

            // Show game screen
            if (this.gameScreen) {
                this.gameScreen.classList.add('active');
            }

            // Update state
            this.stateManager.setState('ui.currentScreen', 'game');

            if (this.debug) {
                console.log('GameEngine: Transitioned to game screen');
            }

            this.eventBus.emit('gameScreenShown');
        } catch (error) {
            console.error('GameEngine: Failed to transition to game', error);
            this.eventBus.emit('engineError', { error: error.message });
        }
    }

    /**
     * Show start screen
     */
    showStartScreen() {
        try {
            // Hide game screen
            if (this.gameScreen) {
                this.gameScreen.classList.remove('active');
            }

            // Show start screen
            const startScreen = document.getElementById('start-screen');
            if (startScreen) {
                startScreen.classList.add('active');
            }

            // Update state
            this.stateManager.setState('ui.currentScreen', 'start');

            if (this.debug) {
                console.log('GameEngine: Showing start screen');
            }

            this.eventBus.emit('startScreenShown');
        } catch (error) {
            console.error('GameEngine: Failed to show start screen', error);
            this.eventBus.emit('engineError', { error: error.message });
        }
    }

    /**
     * Show notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, info)
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
            color: white;
            border-radius: 4px;
            z-index: 1000;
            font-family: 'Press Start 2P', monospace;
            font-size: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease;
        `;

        // Add to page
        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    /**
     * Generate unique game ID
     * @returns {string} Game ID
     */
    generateGameId() {
        return `game_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Get current game state
     * @returns {Object} Current state
     */
    getState() {
        return this.stateManager.getState();
    }

    /**
     * Get save manager
     * @returns {SaveManager} Save manager instance
     */
    getSaveManager() {
        return this.saveManager;
    }

    /**
     * Get state manager
     * @returns {StateManager} State manager instance
     */
    getStateManager() {
        return this.stateManager;
    }

    /**
     * Get event bus
     * @returns {EventBus} Event bus instance
     */
    getEventBus() {
        return this.eventBus;
    }

    /**
     * Enable/disable debug mode
     * @param {boolean} enabled - Debug enabled
     */
    setDebug(enabled) {
        this.debug = enabled;
        this.stateManager.setDebug(enabled);
        this.saveManager.setDebug(enabled);
    }

    /**
     * Check if engine is initialized
     * @returns {boolean} Is initialized
     */
    isReady() {
        return this.isInitialized;
    }
}

// Export for use in other modules
window.GameEngine = GameEngine;
