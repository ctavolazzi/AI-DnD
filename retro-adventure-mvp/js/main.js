import { GameEngine } from './engine/GameEngine.js';
import { UIManager } from './ui/UIManager.js';
import { DIALOGUE } from './data/dialogues.js';

const engine = new GameEngine();
const ui = new UIManager(document.getElementById('app-root'));

ui.init(engine.stateManager);
engine.start();

// Hook up UI map navigation to LocationSystem
window.addEventListener('ui:navigate', (e) => {
  const to = e.detail?.to;
  if (!to) return;
  const ok = engine.locationSystem.moveTo(to);
  if (ok) {
    // Optionally log movement
    const s = engine.stateManager.get();
    // nothing else required; UI will re-render via state subscription
  }
});

// Expose dialogue data to UIManager without adding tight coupling
window.__dialogue = { DIALOGUE };
