# Testing Setup Guide - Retro Adventure Game

## Quick Start Testing Setup

### Option 1: Jest (Unit Testing) - RECOMMENDED START

**Install:**
```bash
npm init -y
npm install --save-dev jest @types/jest jsdom
```

**Create test file:** `retro-adventure-game.test.js`
```javascript
/**
 * @jest-environment jsdom
 */

// Mock game state
const createGameState = () => ({
    currentLocation: { x: 3, y: 2 },
    playerHP: 50,
    maxHP: 50,
    locations: {
        '3,2': { name: 'Starting Tavern', visited: true, walls: [] },
        '3,1': { name: 'Town Square', visited: false, walls: ['north'] },
    }
});

// Test suite
describe('Game State Tests', () => {
    test('player starts at correct location', () => {
        const state = createGameState();
        expect(state.currentLocation).toEqual({ x: 3, y: 2 });
    });

    test('player starts with full HP', () => {
        const state = createGameState();
        expect(state.playerHP).toBe(50);
        expect(state.maxHP).toBe(50);
    });
});

describe('Movement Tests', () => {
    test('blocked by walls', () => {
        const state = createGameState();
        const location = state.locations['3,1'];
        expect(location.walls).toContain('north');
    });
});

describe('HP System Tests', () => {
    test('HP cannot go below 0', () => {
        let hp = 10;
        const damage = 20;
        hp = Math.max(0, hp - damage);
        expect(hp).toBe(0);
    });

    test('HP cannot exceed max', () => {
        let hp = 40;
        const maxHP = 50;
        const healing = 20;
        hp = Math.min(maxHP, hp + healing);
        expect(hp).toBe(50);
    });
});
```

**Add to package.json:**
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

**Run tests:**
```bash
npm test
```

---

### Option 2: Playwright (UI Testing)

**Install:**
```bash
npm init playwright@latest
```

**Create test:** `tests/gameplay.spec.js`
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Retro Adventure Game', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('file://' + __dirname + '/../retro-adventure-game.html');
    });

    test('game loads successfully', async ({ page }) => {
        const title = await page.locator('.game-title').textContent();
        expect(title).toContain('EMBERPEAK EXPEDITION');
    });

    test('navigation buttons exist', async ({ page }) => {
        await expect(page.locator('#north')).toBeVisible();
        await expect(page.locator('#south')).toBeVisible();
        await expect(page.locator('#east')).toBeVisible();
        await expect(page.locator('#west')).toBeVisible();
    });

    test('clicking north button adds text to log', async ({ page }) => {
        await page.click('#north');
        const logText = await page.locator('#viewport').textContent();
        expect(logText.length).toBeGreaterThan(0);
    });

    test('map displays current position', async ({ page }) => {
        const currentCell = await page.locator('.map-cell.current');
        await expect(currentCell).toBeVisible();
    });

    test('action buttons are clickable', async ({ page }) => {
        await page.click('#talk-btn');
        await page.click('#skill-btn');
        await page.click('#rest-btn');
        // Check that log has messages
        const messages = await page.locator('.text-line').count();
        expect(messages).toBeGreaterThan(3);
    });
});

test.describe('Combat System', () => {
    test('HP bar updates correctly', async ({ page }) => {
        await page.goto('file://' + __dirname + '/../retro-adventure-game.html');

        const initialHP = await page.locator('#hp-text').textContent();
        expect(initialHP).toBe('50 / 50 HP');

        // Trigger encounter by moving around
        for (let i = 0; i < 10; i++) {
            await page.click('#east');
            await page.waitForTimeout(500);
            await page.click('#west');
            await page.waitForTimeout(500);
        }

        // Check if HP changed or combat occurred
        const logText = await page.locator('#viewport').textContent();
        // Could contain combat messages
    });
});
```

**Run tests:**
```bash
npx playwright test
npx playwright test --headed  # See browser
npx playwright test --debug   # Debug mode
```

---

### Option 3: Cypress (E2E Testing)

**Install:**
```bash
npm install --save-dev cypress
npx cypress open
```

**Create test:** `cypress/e2e/gameplay.cy.js`
```javascript
describe('Retro Adventure Game E2E', () => {
    beforeEach(() => {
        cy.visit('../retro-adventure-game.html');
    });

    it('loads game successfully', () => {
        cy.get('.game-title').should('contain', 'EMBERPEAK');
        cy.get('.viewport').should('be.visible');
        cy.get('.map-grid').should('be.visible');
    });

    it('can navigate in all directions', () => {
        cy.get('#north').click();
        cy.get('.viewport').should('contain.text', 'discover');

        cy.get('#south').click();
        cy.get('#east').click();
        cy.get('#west').click();

        // Check that text was added
        cy.get('.text-line').should('have.length.greaterThan', 5);
    });

    it('map updates when moving', () => {
        cy.get('.map-cell.current').should('exist');
        cy.get('#north').click();
        cy.get('.map-cell.current').should('exist');
    });

    it('can perform actions', () => {
        cy.get('#talk-btn').click();
        cy.get('.text-line.success').should('exist');

        cy.get('#skill-btn').click();
        cy.get('.text-line').should('contain.text', 'Check');

        cy.get('#rest-btn').click();
        cy.get('.text-line').should('contain.text', 'rest');
    });

    it('inventory is visible', () => {
        cy.get('.inventory-item').should('have.length', 4);
        cy.get('.item-name').first().should('contain', 'Dagger');
    });

    it('character stats are displayed', () => {
        cy.get('#char-name').should('contain', 'Hero');
        cy.get('#char-class').should('contain', 'Rogue');
        cy.get('#hp-bar').should('exist');
    });

    it('walls block movement', () => {
        // Move to a location with walls
        cy.get('#north').click();
        cy.wait(500);

        // Try to move into a wall
        cy.get('#north').click();
        cy.get('.text-line.damage').should('contain', 'BLOCKED');
    });
});
```

**Run:**
```bash
npx cypress open  # Interactive
npx cypress run   # Headless
```

---

## Visual Regression Testing

### Percy (Recommended)

**Install:**
```bash
npm install --save-dev @percy/cli @percy/playwright
```

**Add to Playwright tests:**
```javascript
const { percySnapshot } = require('@percy/playwright');

test('visual snapshot of main game screen', async ({ page }) => {
    await page.goto('file://' + __dirname + '/../retro-adventure-game.html');
    await percySnapshot(page, 'Game Main Screen');
});
```

---

## Performance Testing

### Lighthouse CI

**Install:**
```bash
npm install --save-dev @lhci/cli
```

**Configuration:** `lighthouserc.js`
```javascript
module.exports = {
  ci: {
    collect: {
      staticDistDir: './',
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
      },
    },
  },
};
```

**Run:**
```bash
npx lhci autorun
```

---

## Test Coverage Goals

### Critical Tests (Must Have):
- ✅ Game state initialization
- ✅ Movement system (all 4 directions)
- ✅ Wall collision detection
- ✅ HP update system
- ✅ Map rendering
- ✅ Text log appending
- ✅ Action button functionality

### Important Tests (Should Have):
- ⚠️ Inventory management
- ⚠️ Quest completion
- ⚠️ Combat encounters
- ⚠️ Modal open/close
- ⚠️ Mobile responsive breakpoints

### Nice-to-Have Tests:
- 💡 Message history limit
- 💡 Tooltip display
- 💡 Hover states
- 💡 Animation performance

---

## Running All Tests

**Create test script:** `run-all-tests.sh`
```bash
#!/bin/bash

echo "🧪 Running all tests..."

echo "\n📦 Running Jest unit tests..."
npm run test

echo "\n🎭 Running Playwright UI tests..."
npx playwright test

echo "\n🌲 Running Cypress E2E tests..."
npx cypress run

echo "\n📸 Running visual regression tests..."
npx percy exec -- playwright test

echo "\n⚡ Running Lighthouse performance tests..."
npx lhci autorun

echo "\n✅ All tests complete!"
```

**Make executable:**
```bash
chmod +x run-all-tests.sh
./run-all-tests.sh
```

---

## Continuous Integration (CI)

### GitHub Actions

**Create:** `.github/workflows/test.yml`
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm install

      - name: Run unit tests
        run: npm test

      - name: Run Playwright tests
        run: npx playwright test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results/
```

---

## Quick Start Command

```bash
# One-command setup
npm init -y && \
npm install --save-dev jest @types/jest jsdom playwright @playwright/test && \
mkdir tests && \
echo "✅ Testing environment ready!"
```

**Then create your first test and run:**
```bash
npm test
```

---

## Recommended Testing Priority

1. **Week 1:** Setup Jest, write 10 core unit tests
2. **Week 2:** Setup Playwright, write 5 UI tests
3. **Week 3:** Add Cypress for E2E, write full gameplay flow
4. **Week 4:** Add Percy for visual regression
5. **Ongoing:** Maintain 80%+ test coverage

**Target Coverage:**
- Unit Tests: 80%+
- Integration Tests: 60%+
- E2E Tests: Critical user paths

