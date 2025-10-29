/**
 * StartScreen - Handles the start screen UI and interactions
 * Based on learnings from the existing project's UI patterns
 */
class StartScreen {
    constructor(eventBus, stateManager, saveManager) {
        this.eventBus = eventBus;
        this.stateManager = stateManager;
        this.saveManager = saveManager;
        this.debug = false;

        this.initialize();
    }

    /**
     * Initialize the start screen
     */
    initialize() {
        this.setupEventListeners();
        this.setupUI();
        this.loadSaveList();

        if (this.debug) {
            console.log('StartScreen: Initialized');
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // New Game button
        const newGameBtn = document.getElementById('new-game-btn');
        if (newGameBtn) {
            newGameBtn.addEventListener('click', () => {
                this.handleNewGame();
            });
        }

        // Load Game button
        const loadGameBtn = document.getElementById('load-game-btn');
        if (loadGameBtn) {
            loadGameBtn.addEventListener('click', () => {
                this.handleLoadGame();
            });
        }

        // Settings button
        const settingsBtn = document.getElementById('settings-btn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => {
                this.handleSettings();
            });
        }

        // Back to menu buttons
        const backToMenuBtn = document.getElementById('back-to-menu');
        if (backToMenuBtn) {
            backToMenuBtn.addEventListener('click', () => {
                this.showMainMenu();
            });
        }

        const backToMenuCharBtn = document.getElementById('back-to-menu-char');
        if (backToMenuCharBtn) {
            backToMenuCharBtn.addEventListener('click', () => {
                this.showMainMenu();
            });
        }

        // Start Adventure button
        const startAdventureBtn = document.getElementById('start-adventure');
        if (startAdventureBtn) {
            startAdventureBtn.addEventListener('click', () => {
                this.handleStartAdventure();
            });
        }

        // Character form inputs
        const charNameInput = document.getElementById('char-name');
        if (charNameInput) {
            charNameInput.addEventListener('input', () => {
                this.updateCharacterPreview();
            });
        }

        const charClassSelect = document.getElementById('char-class');
        if (charClassSelect) {
            charClassSelect.addEventListener('change', () => {
                this.updateCharacterPreview();
            });
        }

        const charRaceSelect = document.getElementById('char-race');
        if (charRaceSelect) {
            charRaceSelect.addEventListener('change', () => {
                this.updateCharacterPreview();
            });
        }

        // Listen for engine events
        this.eventBus.on('newGameStarted', () => {
            this.showCharacterCreation();
        });

        this.eventBus.on('gameLoaded', () => {
            this.hideAllPanels();
        });
    }

    /**
     * Set up UI elements
     */
    setupUI() {
        // Hide all panels initially
        this.hideAllPanels();

        // Show main menu
        this.showMainMenu();
    }

    /**
     * Handle New Game button click
     */
    handleNewGame() {
        if (this.debug) {
            console.log('StartScreen: New game requested');
        }

        this.eventBus.emit('startNewGame');
    }

    /**
     * Handle Load Game button click
     */
    handleLoadGame() {
        if (this.debug) {
            console.log('StartScreen: Load game requested');
        }

        this.showSaveList();
    }

    /**
     * Handle Settings button click
     */
    handleSettings() {
        if (this.debug) {
            console.log('StartScreen: Settings requested');
        }

        // TODO: Implement settings panel
        alert('Settings panel coming soon!');
    }

    /**
     * Handle Start Adventure button click
     */
    handleStartAdventure() {
        const charName = document.getElementById('char-name').value.trim();
        const charClass = document.getElementById('char-class').value;
        const charRace = document.getElementById('char-race').value;

        if (!charName) {
            alert('Please enter a character name!');
            return;
        }

        // Update state with character data
        this.stateManager.setState('player.name', charName);
        this.stateManager.setState('player.class', charClass);
        this.stateManager.setState('player.race', charRace);

        // Set initial stats based on class
        this.setInitialStats(charClass);

        if (this.debug) {
            console.log('StartScreen: Character created', { charName, charClass, charRace });
        }

        this.eventBus.emit('characterCreated', {
            name: charName,
            class: charClass,
            race: charRace
        });

        this.eventBus.emit('showGameScreen');
    }

    /**
     * Set initial character stats based on class
     * @param {string} charClass - Character class
     */
    setInitialStats(charClass) {
        const stats = this.getBaseStats(charClass);

        this.stateManager.setState('player.hp', stats.hp);
        this.stateManager.setState('player.maxHp', stats.hp);
        this.stateManager.setState('player.attack', stats.attack);
        this.stateManager.setState('player.defense', stats.defense);
        this.stateManager.setState('player.level', 1);
        this.stateManager.setState('player.experience', 0);
    }

    /**
     * Get base stats for character class
     * @param {string} charClass - Character class
     * @returns {Object} Base stats
     */
    getBaseStats(charClass) {
        const stats = {
            warrior: { hp: 120, attack: 15, defense: 12 },
            mage: { hp: 80, attack: 20, defense: 6 },
            rogue: { hp: 100, attack: 18, defense: 10 },
            cleric: { hp: 110, attack: 12, defense: 14 }
        };

        return stats[charClass] || stats.warrior;
    }

    /**
     * Update character preview
     */
    updateCharacterPreview() {
        const charName = document.getElementById('char-name').value;
        const charClass = document.getElementById('char-class').value;
        const charRace = document.getElementById('char-race').value;

        // TODO: Update character preview display
        if (this.debug) {
            console.log('StartScreen: Character preview updated', { charName, charClass, charRace });
        }
    }

    /**
     * Show main menu
     */
    showMainMenu() {
        this.hideAllPanels();

        const mainMenu = document.querySelector('.main-menu');
        if (mainMenu) {
            mainMenu.style.display = 'flex';
        }
    }

    /**
     * Show character creation
     */
    showCharacterCreation() {
        this.hideAllPanels();

        const charCreation = document.getElementById('character-creation');
        if (charCreation) {
            charCreation.classList.remove('hidden');
        }

        // Focus on name input
        const charNameInput = document.getElementById('char-name');
        if (charNameInput) {
            charNameInput.focus();
        }
    }

    /**
     * Show save list
     */
    showSaveList() {
        this.hideAllPanels();

        const saveList = document.getElementById('save-list');
        if (saveList) {
            saveList.classList.remove('hidden');
        }

        this.loadSaveList();
    }

    /**
     * Hide all panels
     */
    hideAllPanels() {
        const panels = [
            document.querySelector('.main-menu'),
            document.getElementById('save-list'),
            document.getElementById('character-creation')
        ];

        panels.forEach(panel => {
            if (panel) {
                if (panel.id === 'save-list' || panel.id === 'character-creation') {
                    panel.classList.add('hidden');
                } else {
                    panel.style.display = 'none';
                }
            }
        });
    }

    /**
     * Load and display save list
     */
    loadSaveList() {
        const saveSlots = document.getElementById('save-slots');
        if (!saveSlots) return;

        const saves = this.saveManager.getAllSaves();
        const autoSave = this.saveManager.getAutoSaveMetadata();

        // Clear existing slots
        saveSlots.innerHTML = '';

        // Add autosave if available
        if (autoSave) {
            const autoSaveSlot = this.createSaveSlot('autosave', autoSave, true);
            saveSlots.appendChild(autoSaveSlot);
        }

        // Add manual saves
        Object.entries(saves).forEach(([saveName, saveData]) => {
            const saveSlot = this.createSaveSlot(saveName, saveData.metadata, false);
            saveSlots.appendChild(saveSlot);
        });

        // Add empty slot if no saves
        if (Object.keys(saves).length === 0 && !autoSave) {
            const emptySlot = this.createEmptySlot();
            saveSlots.appendChild(emptySlot);
        }
    }

    /**
     * Create save slot element
     * @param {string} saveName - Name of the save
     * @param {Object} metadata - Save metadata
     * @param {boolean} isAutoSave - Is autosave
     * @returns {HTMLElement} Save slot element
     */
    createSaveSlot(saveName, metadata, isAutoSave) {
        const slot = document.createElement('div');
        slot.className = 'save-slot';

        const date = new Date(metadata.timestamp);
        const dateStr = date.toLocaleDateString();
        const timeStr = date.toLocaleTimeString();

        slot.innerHTML = `
            <div class="save-info">
                <div class="save-name">${isAutoSave ? 'Auto Save' : saveName}</div>
                <div class="save-details">
                    ${dateStr} at ${timeStr} | Turn ${metadata.currentTurn || 0}
                </div>
            </div>
            <div class="save-actions">
                <button class="menu-btn primary" onclick="startScreen.loadSave('${saveName}')">
                    Load
                </button>
                ${!isAutoSave ? `<button class="menu-btn tertiary" onclick="startScreen.deleteSave('${saveName}')">Delete</button>` : ''}
            </div>
        `;

        return slot;
    }

    /**
     * Create empty slot element
     * @returns {HTMLElement} Empty slot element
     */
    createEmptySlot() {
        const slot = document.createElement('div');
        slot.className = 'save-slot empty';
        slot.innerHTML = `
            <div class="save-info">
                <div class="save-name">No saves available</div>
                <div class="save-details">Start a new game to create your first save</div>
            </div>
        `;
        return slot;
    }

    /**
     * Load a save game
     * @param {string} saveName - Name of the save to load
     */
    loadSave(saveName) {
        if (this.debug) {
            console.log('StartScreen: Loading save', saveName);
        }

        this.eventBus.emit('loadGame', { saveName });
    }

    /**
     * Delete a save game
     * @param {string} saveName - Name of the save to delete
     */
    deleteSave(saveName) {
        if (confirm(`Are you sure you want to delete "${saveName}"?`)) {
            const success = this.saveManager.deleteSave(saveName);
            if (success) {
                this.loadSaveList(); // Refresh the list
            }
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
window.StartScreen = StartScreen;
