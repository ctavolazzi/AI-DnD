export class SaveManager {
  constructor(key = 'emberpeak_mvp_save') { this.key = key; }
  save(state) {
    try {
      const payload = JSON.stringify(state);
      localStorage.setItem(this.key, payload);
      return true;
    } catch { return false; }
  }
  load() {
    try {
      const raw = localStorage.getItem(this.key);
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  }
  clear() { localStorage.removeItem(this.key); }
}
