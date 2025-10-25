import { StateManager } from './StateManager.js';
import { SaveManager } from './SaveManager.js';
import { TurnManager } from './TurnManager.js';
import { LocationSystem } from '../systems/LocationSystem.js';

export class GameEngine {
  constructor(initialState) {
    this.stateManager = new StateManager(initialState);
    this.saveManager = new SaveManager();
    this.turnManager = new TurnManager();
    this.locationSystem = new LocationSystem(this.stateManager);

    const saved = this.saveManager.load();
    if (saved) {
      this.stateManager.state = saved;
    }

    this.unsub = this.stateManager.subscribe((s) => {
      this.saveManager.save(s);
    });
  }

  start() {
    // initialize available exits for current location
    const current = this.stateManager.get().location.current;
    this.stateManager.update(d => { d.location.available = this.locationSystem.getAvailableExits(current); });
  }
}
