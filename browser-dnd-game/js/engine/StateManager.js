/**
 * StateManager - Centralized game state management
 * Based on learnings from the existing project's save system
 */
class StateManager {
    constructor(eventBus) {
        this.eventBus = eventBus;
        this.state = this.getInitialState();
        this.history = [];
        this.maxHistorySize = 50;
        this.debug = false;
    }

    /**
     * Get initial game state
     * @returns {Object} Initial state object
     */
    getInitialState() {
        return {
            // Game metadata
            metadata: {
                version: '1.0.0',
                gameId: null,
                startTime: null,
                lastSaved: null,
                currentTurn: 0,
                maxTurns: 100
            },

            // Player data
            player: {
                name: '',
                class: '',
                race: '',
                level: 1,
                hp: 100,
                maxHp: 100,
                attack: 10,
                defense: 8,
                experience: 0,
                inventory: [],
                equipment: {
                    weapon: null,
                    armor: null,
                    accessory: null
                },
                spells: [],
                statusEffects: []
            },

            // Game world
            world: {
                currentLocation: 'start',
                discoveredLocations: ['start'],
                visitedLocations: ['start'],
                questFlags: {},
                npcs: {},
                enemies: []
            },

            // Quest system
            quests: {
                active: [],
                completed: [],
                available: []
            },

            // UI state
            ui: {
                currentScreen: 'start',
                selectedTab: 'adventure',
                notifications: [],
                modal: null
            },

            // Game settings
            settings: {
                soundEnabled: true,
                musicEnabled: true,
                autoSave: true,
                difficulty: 'normal'
            }
        };
    }

    /**
     * Get current state
     * @returns {Object} Current state (immutable copy)
     */
    getState() {
        return JSON.parse(JSON.stringify(this.state));
    }

    /**
     * Get specific state section
     * @param {string} path - Dot notation path (e.g., 'player.name')
     * @returns {*} State value
     */
    getStateValue(path) {
        return this.getNestedValue(this.state, path);
    }

    /**
     * Update state
     * @param {string|Object} path - Path to update or state object
     * @param {*} value - New value (if path is string)
     */
    setState(path, value = undefined) {
        const oldState = this.getState();

        if (typeof path === 'object') {
            // Merge entire state object
            this.state = this.deepMerge(this.state, path);
        } else {
            // Update specific path
            this.setNestedValue(this.state, path, value);
        }

        // Save to history
        this.saveToHistory(oldState);

        // Emit state change event
        this.eventBus.emit('stateChanged', {
            oldState,
            newState: this.getState(),
            path: typeof path === 'string' ? path : 'full'
        });

        if (this.debug) {
            console.log('StateManager: State updated', { path, value });
        }
    }

    /**
     * Reset state to initial values
     */
    reset() {
        const oldState = this.getState();
        this.state = this.getInitialState();
        this.history = [];

        this.eventBus.emit('stateReset', {
            oldState,
            newState: this.getState()
        });

        if (this.debug) {
            console.log('StateManager: State reset');
        }
    }

    /**
     * Load state from save data
     * @param {Object} saveData - Save data object
     */
    loadState(saveData) {
        const oldState = this.getState();

        // Validate save data structure
        if (!this.validateSaveData(saveData)) {
            throw new Error('Invalid save data structure');
        }

        // Merge save data with current state
        this.state = this.deepMerge(this.state, saveData);

        // Update metadata
        this.state.metadata.lastLoaded = new Date().toISOString();

        this.eventBus.emit('stateLoaded', {
            oldState,
            newState: this.getState(),
            saveData
        });

        if (this.debug) {
            console.log('StateManager: State loaded from save data');
        }
    }

    /**
     * Get nested value from object using dot notation
     * @param {Object} obj - Object to search
     * @param {string} path - Dot notation path
     * @returns {*} Value or undefined
     */
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => {
            return current && current[key] !== undefined ? current[key] : undefined;
        }, obj);
    }

    /**
     * Set nested value in object using dot notation
     * @param {Object} obj - Object to modify
     * @param {string} path - Dot notation path
     * @param {*} value - Value to set
     */
    setNestedValue(obj, path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        const target = keys.reduce((current, key) => {
            if (!current[key] || typeof current[key] !== 'object') {
                current[key] = {};
            }
            return current[key];
        }, obj);
        target[lastKey] = value;
    }

    /**
     * Deep merge two objects
     * @param {Object} target - Target object
     * @param {Object} source - Source object
     * @returns {Object} Merged object
     */
    deepMerge(target, source) {
        const result = { ...target };

        for (const key in source) {
            if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                result[key] = this.deepMerge(target[key] || {}, source[key]);
            } else {
                result[key] = source[key];
            }
        }

        return result;
    }

    /**
     * Save current state to history
     * @param {Object} state - State to save
     */
    saveToHistory(state) {
        this.history.push({
            state: JSON.parse(JSON.stringify(state)),
            timestamp: new Date().toISOString()
        });

        // Limit history size
        if (this.history.length > this.maxHistorySize) {
            this.history.shift();
        }
    }

    /**
     * Validate save data structure
     * @param {Object} saveData - Save data to validate
     * @returns {boolean} Is valid
     */
    validateSaveData(saveData) {
        // Basic structure validation
        const requiredKeys = ['metadata', 'player', 'world', 'quests'];
        return requiredKeys.every(key => saveData.hasOwnProperty(key));
    }

    /**
     * Get state history
     * @returns {Array} History array
     */
    getHistory() {
        return [...this.history];
    }

    /**
     * Clear state history
     */
    clearHistory() {
        this.history = [];
        if (this.debug) {
            console.log('StateManager: History cleared');
        }
    }

    /**
     * Enable/disable debug mode
     * @param {boolean} enabled - Debug enabled
     */
    setDebug(enabled) {
        this.debug = enabled;
    }
}

// Export for use in other modules
window.StateManager = StateManager;
