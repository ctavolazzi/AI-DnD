// ===================================
//   RETRO ADVENTURE GAME - ENHANCED JS
// ===================================

// Game State
const gameState = {
    currentLocation: 'tavern',
    playerHP: 30,
    playerMaxHP: 50,
    inventory: ['sword', 'potion'],
    soundEnabled: true,
    animationsEnabled: true
};

// ===================================
// DOM READY
// ===================================
document.addEventListener('DOMContentLoaded', function() {
    initializeGame();
    setupEventListeners();
    setupKeyboardShortcuts();
});

// ===================================
// INITIALIZATION
// ===================================
function initializeGame() {
    console.log('🎮 Retro Adventure Game - Enhanced Edition');
    updateHPBar();
    setupTabSwitching();
}

// ===================================
// EVENT LISTENERS
// ===================================
function setupEventListeners() {
    // Action buttons
    const actionButtons = document.querySelectorAll('.action-btn:not(.disabled)');
    actionButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.dataset.action;
            handleAction(action);
        });
    });

    // Navigation buttons
    const navButtons = document.querySelectorAll('.compass-btn:not(.disabled):not(.compass-center)');
    navButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const direction = this.dataset.direction;
            handleNavigation(direction);
        });
    });

    // Look button
    const lookBtn = document.querySelector('.compass-center');
    if (lookBtn) {
        lookBtn.addEventListener('click', handleLook);
    }

    // Settings
    const soundCheckbox = document.getElementById('soundEffects');
    const animCheckbox = document.getElementById('animations');
    
    if (soundCheckbox) {
        soundCheckbox.addEventListener('change', function() {
            gameState.soundEnabled = this.checked;
            addLogEntry('🔊 Sound effects ' + (this.checked ? 'enabled' : 'disabled'), 'system');
        });
    }

    if (animCheckbox) {
        animCheckbox.addEventListener('change', function() {
            gameState.animationsEnabled = this.checked;
            document.body.style.setProperty('--animation-speed', this.checked ? '0.4s' : '0s');
            addLogEntry('✨ Animations ' + (this.checked ? 'enabled' : 'disabled'), 'system');
        });
    }
}

// ===================================
// KEYBOARD SHORTCUTS
// ===================================
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ignore if typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        const key = e.key.toLowerCase();

        switch(key) {
            case 'e':
                e.preventDefault();
                handleAction('examine');
                break;
            case 't':
                e.preventDefault();
                handleAction('talk');
                break;
            case 'a':
                e.preventDefault();
                handleAction('attack');
                break;
            case 'r':
                e.preventDefault();
                handleAction('rest');
                break;
            case 's':
                e.preventDefault();
                toggleSettings();
                break;
            case 'h':
                e.preventDefault();
                toggleHelp();
                break;
            case 'escape':
                closeSettings();
                closeHelp();
                break;
            case 'arrowup':
                e.preventDefault();
                handleNavigation('north');
                break;
            case 'arrowdown':
                e.preventDefault();
                handleNavigation('south');
                break;
            case 'arrowleft':
                e.preventDefault();
                handleNavigation('west');
                break;
            case 'arrowright':
                e.preventDefault();
                handleNavigation('east');
                break;
        }
    });
}

// ===================================
// TAB SWITCHING
// ===================================
function setupTabSwitching() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            switchTab(targetTab);
        });
    });
}

function switchTab(tabName) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    // Add active class to selected tab and content
    const selectedTab = document.querySelector(`.tab[data-tab="${tabName}"]`);
    const selectedContent = document.getElementById(tabName);

    if (selectedTab && selectedContent) {
        selectedTab.classList.add('active');
        selectedContent.classList.add('active');
        playSound('tab-switch');
    }
}

// ===================================
// ACTION HANDLERS
// ===================================
function handleAction(action) {
    playSound('button-click');

    switch(action) {
        case 'examine':
            addLogEntry('👁️ You carefully examine your surroundings...', 'action');
            setTimeout(() => {
                addLogEntry('The tavern is dimly lit with oak furniture and a crackling fireplace. Several patrons sit at the bar, speaking in hushed tones.', 'description');
            }, 500);
            break;

        case 'talk':
            addLogEntry('💬 You approach the adventurers at the bar...', 'action');
            setTimeout(() => {
                addLogEntry('"Greetings, traveler," the Rogue says with a sly smile. "Looking for adventure, or just a warm meal?"', 'dialogue');
            }, 800);
            break;

        case 'attack':
            if (isActionDisabled('attack')) {
                addLogEntry('⚠️ There are no enemies to attack here.', 'warning');
                return;
            }
            addLogEntry('⚔️ You draw your weapon!', 'action');
            break;

        case 'rest':
            addLogEntry('💤 You find a quiet corner to rest...', 'action');
            setTimeout(() => {
                const healAmount = 10;
                gameState.playerHP = Math.min(gameState.playerHP + healAmount, gameState.playerMaxHP);
                updateHPBar();
                addLogEntry(`✨ You recover ${healAmount} HP! Current HP: ${gameState.playerHP}/${gameState.playerMaxHP}`, 'success');
            }, 1000);
            break;
    }

    // Animate button
    animateButton(event.target);
}

function handleNavigation(direction) {
    if (isDirectionBlocked(direction)) {
        addLogEntry(`⚠️ You cannot go ${direction}. The path is blocked.`, 'warning');
        playSound('error');
        return;
    }

    playSound('footsteps');
    addLogEntry(`🚶 You head ${direction}...`, 'navigation');

    // Simulate travel
    setTimeout(() => {
        addLogEntry('You arrive at a new location.', 'narrative');
    }, 1000);
}

function handleLook() {
    playSound('button-click');
    addLogEntry('👀 You take a moment to look around carefully...', 'action');
    setTimeout(() => {
        addLogEntry('You notice exits to the NORTH, WEST, and EAST. The south exit appears to be blocked.', 'description');
    }, 600);
}

// ===================================
// LOG MANAGEMENT
// ===================================
function addLogEntry(text, type = 'narrative') {
    const log = document.querySelector('.adventure-log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = text;
    
    log.appendChild(entry);
    
    // Auto-scroll to bottom
    setTimeout(() => {
        log.scrollTop = log.scrollHeight;
    }, 100);

    // Remove "new" badge if it exists
    const newBadge = log.querySelector('.new-message');
    if (newBadge) {
        newBadge.remove();
    }
}

function scrollLogToTop() {
    const log = document.querySelector('.adventure-log');
    log.scrollTo({ top: 0, behavior: 'smooth' });
}

function scrollLogToBottom() {
    const log = document.querySelector('.adventure-log');
    log.scrollTo({ top: log.scrollHeight, behavior: 'smooth' });
}

// ===================================
// HP BAR
// ===================================
function updateHPBar() {
    const hpFill = document.querySelector('.hp-fill');
    const hpValue = document.querySelector('.hp-value');
    
    if (hpFill && hpValue) {
        const percentage = (gameState.playerHP / gameState.playerMaxHP) * 100;
        hpFill.style.width = percentage + '%';
        hpValue.textContent = `${gameState.playerHP} / ${gameState.playerMaxHP}`;

        // Change color based on HP percentage
        if (percentage > 60) {
            hpFill.style.background = 'linear-gradient(to right, var(--hp-green), var(--hp-yellow))';
        } else if (percentage > 30) {
            hpFill.style.background = 'linear-gradient(to right, var(--hp-yellow), orange)';
        } else {
            hpFill.style.background = 'linear-gradient(to right, orange, var(--hp-red))';
        }
    }
}

// ===================================
// SETTINGS & HELP
// ===================================
function openSettings() {
    const menu = document.getElementById('settingsMenu');
    if (menu) {
        menu.classList.remove('hidden');
        playSound('menu-open');
    }
}

function closeSettings() {
    const menu = document.getElementById('settingsMenu');
    if (menu) {
        menu.classList.add('hidden');
        playSound('menu-close');
    }
}

function toggleSettings() {
    const menu = document.getElementById('settingsMenu');
    if (menu) {
        if (menu.classList.contains('hidden')) {
            openSettings();
        } else {
            closeSettings();
        }
    }
}

function toggleHelp() {
    const overlay = document.getElementById('helpOverlay');
    if (overlay) {
        overlay.classList.toggle('hidden');
        playSound(overlay.classList.contains('hidden') ? 'menu-close' : 'menu-open');
    }
}

function closeHelp() {
    const overlay = document.getElementById('helpOverlay');
    if (overlay && !overlay.classList.contains('hidden')) {
        overlay.classList.add('hidden');
        playSound('menu-close');
    }
}

// ===================================
// UTILITY FUNCTIONS
// ===================================
function isActionDisabled(action) {
    const btn = document.querySelector(`.action-btn[data-action="${action}"]`);
    return btn ? btn.classList.contains('disabled') : true;
}

function isDirectionBlocked(direction) {
    const btn = document.querySelector(`.compass-btn[data-direction="${direction}"]`);
    return btn ? btn.classList.contains('disabled') : true;
}

function animateButton(button) {
    if (!gameState.animationsEnabled || !button) return;
    
    button.style.transform = 'scale(0.95)';
    setTimeout(() => {
        button.style.transform = '';
    }, 100);
}

function playSound(soundName) {
    if (!gameState.soundEnabled) return;
    
    // In a real implementation, you would play actual sound files here
    console.log(`🔊 Playing sound: ${soundName}`);
}

// ===================================
// DEMO FUNCTIONS (for testing)
// ===================================
function simulateDialogue() {
    const dialogues = [
        '"The mines of Emberpeak have been sealed for weeks," the Fighter says gravely.',
        '"Strange sounds echo from below," the Rogue adds. "And no one who\'s gone down has come back."',
        '"We need someone brave enough to investigate. Are you that person?"'
    ];

    dialogues.forEach((dialogue, index) => {
        setTimeout(() => {
            addLogEntry(dialogue, 'dialogue');
        }, index * 2000);
    });
}

function takeDamage(amount) {
    gameState.playerHP = Math.max(0, gameState.playerHP - amount);
    updateHPBar();
    addLogEntry(`💔 You take ${amount} damage! Current HP: ${gameState.playerHP}/${gameState.playerMaxHP}`, 'combat');
    
    if (gameState.playerHP === 0) {
        setTimeout(() => {
            addLogEntry('💀 You have been defeated...', 'death');
        }, 500);
    }
}

function heal(amount) {
    const oldHP = gameState.playerHP;
    gameState.playerHP = Math.min(gameState.playerMaxHP, gameState.playerHP + amount);
    const actualHeal = gameState.playerHP - oldHP;
    updateHPBar();
    addLogEntry(`✨ You restore ${actualHeal} HP! Current HP: ${gameState.playerHP}/${gameState.playerMaxHP}`, 'success');
}

// ===================================
// EXPORT FOR CONSOLE DEBUGGING
// ===================================
window.gameDebug = {
    addLog: addLogEntry,
    takeDamage: takeDamage,
    heal: heal,
    simulateDialogue: simulateDialogue,
    state: gameState
};

console.log('💡 Debug commands available via window.gameDebug');
console.log('Example: gameDebug.takeDamage(10)');
