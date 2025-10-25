import { MapComponent } from './MapComponent.js';
import { AdventureLog } from './AdventureLog.js';
import { LOCATIONS } from '../data/locations.js';
import { logMovement } from '../utils/logger.js';

export class UIManager {
  constructor(root) { this.root = root; this.unsubscribe = null; }
  init(stateManager) {
    this.stateManager = stateManager;
    this.map = new MapComponent((toId) => {
      // delegate navigation intent via custom event on window
      const ev = new CustomEvent('ui:navigate', { detail: { to: toId } });
      window.dispatchEvent(ev);
    });
    this.log = new AdventureLog();
    this.unsubscribe = stateManager.subscribe(() => this.render());
    this.render();
  }
  dispose() { this.unsubscribe?.(); }
  render() {
    const s = this.stateManager.get();
    this.root.innerHTML = `
      <main style="max-width:960px;padding:20px">
        <h1 style="margin:0 0 12px">The Emberpeak Expedition — MVP</h1>
        <section style="border:2px solid #654321;padding:12px;margin-bottom:12px">
          <h2 style="margin:0 0 8px">Adventure Log</h2>
          <div id="log" style="min-height:120px;background:#fff7; padding:8px"></div>
        </section>
        <section style="display:grid;grid-template-columns:1fr 280px;gap:12px">
          <div>
            <div style="border:2px solid #654321;padding:12px;margin-bottom:12px">
              <h3 style="margin:0 0 6px">Scene Viewer</h3>
              <div>${s.location.current}</div>
            </div>
            <div style="border:2px solid #654321;padding:12px">
              <h3 style="margin:0 0 6px">Actions</h3>
              <button id="act-examine">Examine</button>
              <button id="act-talk">Talk</button>
              <button id="act-rest">Rest</button>
            </div>
          </div>
          <aside>
            <div style="border:2px solid #654321;padding:12px;margin-bottom:12px">
              <h3 style="margin:0 0 6px">Map (Interactive ⭐)</h3>
              ${this.map.render(s.location.current)}
            </div>
            <div style="border:2px solid #654321;padding:12px">
              <h3 style="margin:0 0 6px">Character</h3>
              <div>${s.player.name} (Lv ${s.player.level})</div>
              <div>HP: ${s.player.hp.current}/${s.player.hp.max}</div>
            </div>
          </aside>
        </section>
      </main>
    `;
    // Bind map interactivity with available exits
    const mapGrid = this.root.querySelector('#map-grid');
    if (mapGrid) {
      this.map.bindInteractions(mapGrid, s.location.available || []);
    }

    const log = document.getElementById('log');
    if (log && !log.dataset.init) {
      log.dataset.init = '1';
      this.log.mount(log);
      this.log.add('Welcome to Emberpeak MVP!');
    }

    const btnExamine = document.getElementById('act-examine');
    btnExamine?.addEventListener('click', () => {
      this.stateManager.update(d => {
        d.meta.playtime += 1;
      });
      this.log.add('You look around carefully...');
    });

    const btnTalk = document.getElementById('act-talk');
    if (btnTalk) {
      // Enable/disable based on location dialogue availability
      const hasDialogue = !!(LOCATIONS[s.location.current]);
      btnTalk.disabled = !hasDialogue;
      btnTalk.title = hasDialogue ? 'Talk to nearby NPCs' : 'No one to talk to here';
      btnTalk.addEventListener('click', () => {
        const loc = LOCATIONS[this.stateManager.get().location.current];
        if (!loc) return;
        const { DIALOGUE } = window.__dialogue || {};
        const lines = (DIALOGUE && DIALOGUE[loc.id]) || [
          'You speak aloud, but only echoes answer you.'
        ];
        lines.forEach(line => this.log.add(`💬 ${line}`));
      });
    }

    const btnRest = document.getElementById('act-rest');
    btnRest?.addEventListener('click', () => {
      this.stateManager.update(d => {
        d.player.hp.current = Math.min(d.player.hp.max, d.player.hp.current + 5);
      });
      this.log.add('You take a moment to rest.');
    });

    // Movement logging: capture navigation events to log transitions
    const navHandler = (e) => {
      const to = e.detail?.to;
      const from = s.location.current;
      if (!to || to === from) return;
      // defer log until after state updates on next microtask
      queueMicrotask(() => {
        const ns = this.stateManager.get();
        logMovement(this.log, from, ns.location.current, LOCATIONS);
      });
    };
    window.removeEventListener('ui:navigate', this.__navLogHandler);
    this.__navLogHandler = navHandler;
    window.addEventListener('ui:navigate', this.__navLogHandler);
  }
}
