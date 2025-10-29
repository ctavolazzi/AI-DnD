/**
 * SaveManager - Handles game save/load operations
 * Based on learnings from the existing project's save system
 */
class SaveManager {
    constructor(stateManager, eventBus) {
        this.stateManager = stateManager;
        this.eventBus = eventBus;
        this.storageKey = 'browser_dnd_saves';
        this.autoSaveKey = 'browser_dnd_autosave';
        this.debug = false;

        // Auto-save settings
        this.autoSaveInterval = 30000; // 30 seconds
        this.autoSaveTimer = null;
        this.lastAutoSave = null;

        this.initialize();
    }

    /**
     * Initialize save manager
     */
    initialize() {
        // Listen for state changes to trigger auto-save
        this.eventBus.on('stateChanged', () => {
            if (this.stateManager.getStateValue('settings.autoSave')) {
                this.scheduleAutoSave();
            }
        });

        if (this.debug) {
            console.log('SaveManager: Initialized');
        }
    }

    /**
     * Save game to localStorage
     * @param {string} saveName - Name for the save
     * @param {boolean} isAutoSave - Is this an auto-save
     * @returns {boolean} Success status
     */
    saveGame(saveName = null, isAutoSave = false) {
        try {
            const state = this.stateManager.getState();
            const saveData = this.prepareSaveData(state, saveName, isAutoSave);

            if (isAutoSave) {
                localStorage.setItem(this.autoSaveKey, JSON.stringify(saveData));
                this.lastAutoSave = new Date().toISOString();
            } else {
                const saves = this.getAllSaves();
                saves[saveName] = saveData;
                localStorage.setItem(this.storageKey, JSON.stringify(saves));
            }

            this.eventBus.emit('gameSaved', {
                saveName: isAutoSave ? 'autosave' : saveName,
                timestamp: saveData.metadata.timestamp,
                isAutoSave
            });

            if (this.debug) {
                console.log('SaveManager: Game saved', { saveName, isAutoSave });
            }

            return true;
        } catch (error) {
            console.error('SaveManager: Save failed', error);
            this.eventBus.emit('saveError', { error: error.message, operation: 'save' });
            return false;
        }
    }

    /**
     * Load game from localStorage
     * @param {string} saveName - Name of the save to load
     * @returns {boolean} Success status
     */
    loadGame(saveName) {
        try {
            let saveData;

            if (saveName === 'autosave') {
                const autoSaveData = localStorage.getItem(this.autoSaveKey);
                if (!autoSaveData) {
                    throw new Error('No autosave found');
                }
                saveData = JSON.parse(autoSaveData);
            } else {
                const saves = this.getAllSaves();
                if (!saves[saveName]) {
                    throw new Error(`Save "${saveName}" not found`);
                }
                saveData = saves[saveName];
            }

            // Validate save data
            if (!this.validateSaveData(saveData)) {
                throw new Error('Invalid save data');
            }

            // Load state
            this.stateManager.loadState(saveData);

            this.eventBus.emit('gameLoaded', {
                saveName,
                timestamp: saveData.metadata.timestamp
            });

            if (this.debug) {
                console.log('SaveManager: Game loaded', { saveName });
            }

            return true;
        } catch (error) {
            console.error('SaveManager: Load failed', error);
            this.eventBus.emit('loadError', { error: error.message, operation: 'load' });
            return false;
        }
    }

    /**
     * Get all available saves
     * @returns {Object} Object of save names and metadata
     */
    getAllSaves() {
        try {
            const savesData = localStorage.getItem(this.storageKey);
            return savesData ? JSON.parse(savesData) : {};
        } catch (error) {
            console.error('SaveManager: Failed to get saves', error);
            return {};
        }
    }

    /**
     * Get save metadata
     * @param {string} saveName - Name of the save
     * @returns {Object|null} Save metadata or null
     */
    getSaveMetadata(saveName) {
        if (saveName === 'autosave') {
            const autoSaveData = localStorage.getItem(this.autoSaveKey);
            if (!autoSaveData) return null;
            const saveData = JSON.parse(autoSaveData);
            return saveData.metadata;
        }

        const saves = this.getAllSaves();
        return saves[saveName] ? saves[saveName].metadata : null;
    }

    /**
     * Delete a save
     * @param {string} saveName - Name of the save to delete
     * @returns {boolean} Success status
     */
    deleteSave(saveName) {
        try {
            if (saveName === 'autosave') {
                localStorage.removeItem(this.autoSaveKey);
            } else {
                const saves = this.getAllSaves();
                if (saves[saveName]) {
                    delete saves[saveName];
                    localStorage.setItem(this.storageKey, JSON.stringify(saves));
                }
            }

            this.eventBus.emit('saveDeleted', { saveName });

            if (this.debug) {
                console.log('SaveManager: Save deleted', { saveName });
            }

            return true;
        } catch (error) {
            console.error('SaveManager: Delete failed', error);
            return false;
        }
    }

    /**
     * Check if autosave exists
     * @returns {boolean} Has autosave
     */
    hasAutoSave() {
        return localStorage.getItem(this.autoSaveKey) !== null;
    }

    /**
     * Get autosave metadata
     * @returns {Object|null} Autosave metadata
     */
    getAutoSaveMetadata() {
        return this.getSaveMetadata('autosave');
    }

    /**
     * Prepare save data for storage
     * @param {Object} state - Current game state
     * @param {string} saveName - Name for the save
     * @param {boolean} isAutoSave - Is this an auto-save
     * @returns {Object} Prepared save data
     */
    prepareSaveData(state, saveName, isAutoSave) {
        const timestamp = new Date().toISOString();

        return {
            metadata: {
                ...state.metadata,
                saveName: isAutoSave ? 'autosave' : saveName,
                timestamp,
                version: '1.0.0',
                isAutoSave
            },
            state: {
                player: state.player,
                world: state.world,
                quests: state.quests,
                settings: state.settings
            }
        };
    }

    /**
     * Validate save data structure
     * @param {Object} saveData - Save data to validate
     * @returns {boolean} Is valid
     */
    validateSaveData(saveData) {
        if (!saveData || typeof saveData !== 'object') return false;
        if (!saveData.metadata || !saveData.state) return false;

        const requiredMetadata = ['version', 'timestamp'];
        const requiredState = ['player', 'world', 'quests'];

        return requiredMetadata.every(key => saveData.metadata.hasOwnProperty(key)) &&
               requiredState.every(key => saveData.state.hasOwnProperty(key));
    }

    /**
     * Schedule auto-save
     */
    scheduleAutoSave() {
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
        }

        this.autoSaveTimer = setTimeout(() => {
            this.saveGame(null, true);
        }, this.autoSaveInterval);
    }

    /**
     * Cancel auto-save
     */
    cancelAutoSave() {
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }
    }

    /**
     * Export save data as JSON string
     * @param {string} saveName - Name of the save to export
     * @returns {string|null} JSON string or null
     */
    exportSave(saveName) {
        try {
            let saveData;

            if (saveName === 'autosave') {
                const autoSaveData = localStorage.getItem(this.autoSaveKey);
                if (!autoSaveData) return null;
                saveData = JSON.parse(autoSaveData);
            } else {
                const saves = this.getAllSaves();
                if (!saves[saveName]) return null;
                saveData = saves[saveName];
            }

            return JSON.stringify(saveData, null, 2);
        } catch (error) {
            console.error('SaveManager: Export failed', error);
            return null;
        }
    }

    /**
     * Import save data from JSON string
     * @param {string} jsonData - JSON string
     * @param {string} saveName - Name for the imported save
     * @returns {boolean} Success status
     */
    importSave(jsonData, saveName) {
        try {
            const saveData = JSON.parse(jsonData);

            if (!this.validateSaveData(saveData)) {
                throw new Error('Invalid save data format');
            }

            const saves = this.getAllSaves();
            saves[saveName] = saveData;
            localStorage.setItem(this.storageKey, JSON.stringify(saves));

            this.eventBus.emit('saveImported', { saveName });

            if (this.debug) {
                console.log('SaveManager: Save imported', { saveName });
            }

            return true;
        } catch (error) {
            console.error('SaveManager: Import failed', error);
            this.eventBus.emit('importError', { error: error.message });
            return false;
        }
    }

    /**
     * Clear all saves
     */
    clearAllSaves() {
        localStorage.removeItem(this.storageKey);
        localStorage.removeItem(this.autoSaveKey);
        this.cancelAutoSave();

        this.eventBus.emit('allSavesCleared');

        if (this.debug) {
            console.log('SaveManager: All saves cleared');
        }
    }

    /**
     * Get storage usage info
     * @returns {Object} Storage usage information
     */
    getStorageInfo() {
        const saves = this.getAllSaves();
        const autoSave = localStorage.getItem(this.autoSaveKey);

        return {
            totalSaves: Object.keys(saves).length,
            hasAutoSave: !!autoSave,
            lastAutoSave: this.lastAutoSave,
            storageUsed: this.estimateStorageUsage()
        };
    }

    /**
     * Estimate storage usage
     * @returns {number} Estimated bytes used
     */
    estimateStorageUsage() {
        let total = 0;

        // Count manual saves
        const saves = this.getAllSaves();
        Object.values(saves).forEach(save => {
            total += JSON.stringify(save).length;
        });

        // Count autosave
        const autoSave = localStorage.getItem(this.autoSaveKey);
        if (autoSave) {
            total += autoSave.length;
        }

        return total;
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
window.SaveManager = SaveManager;
