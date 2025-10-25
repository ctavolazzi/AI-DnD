import { LOCATIONS } from '../data/locations.js';

export class LocationSystem {
  constructor(stateManager) { this.state = stateManager; }
  getCurrent() { return this.state.get().location.current; }
  getLocation(id) { return LOCATIONS[id]; }
  getAvailableExits(id = this.getCurrent()) {
    const loc = LOCATIONS[id];
    return loc ? loc.adjacent : [];
  }
  canMoveTo(id) {
    const s = this.state.get();
    const exits = this.getAvailableExits(s.location.current);
    return exits.includes(id);
  }
  moveTo(id) {
    if (!this.canMoveTo(id)) return false;
    this.state.update(d => {
      d.location.current = id;
      if (!d.location.discovered.includes(id)) d.location.discovered.push(id);
      // refresh available based on map data
      d.location.available = this.getAvailableExits(id);
    });
    return true;
  }
}
