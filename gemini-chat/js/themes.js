/* ============================================
   🎨 GEMINI CHAT - THEME SYSTEM
   Theme management and switching
   ============================================ */

import { log } from './logging.js';

// Toggle theme menu visibility
export function toggleThemeMenu() {
    const menu = document.getElementById('themeMenu');
    menu.classList.toggle('show');
    log.system('Theme menu toggled');
}

// Set active theme
export function setTheme(themeName) {
    console.group('🎨 Theme Change');
    log.system(`Changing theme to: ${themeName}`);

    const body = document.body;
    const currentTheme = body.getAttribute('data-theme') || 'default';

    if (themeName === 'default') {
        body.removeAttribute('data-theme');
    } else {
        body.setAttribute('data-theme', themeName);
    }

    // Save to localStorage
    localStorage.setItem('preferred-theme', themeName);
    log.system(`Theme saved to localStorage: ${themeName}`);

    // Update active state in menu
    document.querySelectorAll('.theme-option').forEach(option => {
        option.classList.remove('active');
        if (option.getAttribute('data-theme') === themeName) {
            option.classList.add('active');
        }
    });

    // Close menu
    toggleThemeMenu();

    console.log('Theme applied:', {
        previous: currentTheme,
        current: themeName,
        timestamp: new Date().toISOString()
    });
    console.groupEnd();
}

// Load saved theme on startup
export function loadSavedTheme() {
    const savedTheme = localStorage.getItem('preferred-theme');
    if (savedTheme && savedTheme !== 'default') {
        log.system(`Loading saved theme: ${savedTheme}`);
        document.body.setAttribute('data-theme', savedTheme);

        // Update active state in menu
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.remove('active');
            if (option.getAttribute('data-theme') === savedTheme) {
                option.classList.add('active');
            }
        });
    }
}

// Initialize theme system
export function initializeThemes() {
    // Load saved theme
    loadSavedTheme();

    // Close theme menu when clicking outside
    document.addEventListener('click', (e) => {
        const menu = document.getElementById('themeMenu');
        const button = document.querySelector('.theme-button');
        if (menu && !menu.contains(e.target) && !button.contains(e.target)) {
            menu.classList.remove('show');
        }
    });
}

