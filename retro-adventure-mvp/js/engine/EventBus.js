export class EventBus {
  constructor() { this.listeners = new Map(); }
  on(event, handler) {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event).add(handler);
    return () => this.off(event, handler);
  }
  off(event, handler) { this.listeners.get(event)?.delete(handler); }
  emit(event, payload) { this.listeners.get(event)?.forEach(h => h(payload)); }
}
