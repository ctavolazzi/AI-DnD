import { EventBus } from './EventBus.js';

export class StateManager {
  constructor(initial) {
    this.bus = new EventBus();
    this.state = initial || {
      meta: { version: '1.0.0', saveTimestamp: null, playtime: 0 },
      player: {
        name: 'Hero', class: 'Rogue', level: 1, xp: 0, xpToNext: 100,
        stats: { str: 10, dex: 12, con: 10 },
        hp: { current: 20, max: 20 },
        equipped: { weapon: null, armor: null }
      },
      inventory: { items: [], capacity: 20 },
      location: { current: 'tavern', discovered: ['tavern'], available: [] },
      quests: { active: null, completed: [], objectives: [] },
      combat: { active: false, enemy: null, turn: 'player', log: [] },
      flags: {}
    };
  }
  get() { return this.state; }
  subscribe(handler) { return this.bus.on('state', handler); }
  update(mutator) {
    const draft = structuredClone(this.state);
    mutator(draft);
    this.state = draft;
    this.bus.emit('state', this.state);
  }
}
