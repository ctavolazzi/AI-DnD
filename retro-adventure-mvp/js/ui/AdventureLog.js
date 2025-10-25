export class AdventureLog {
  constructor() { this.node = null; }
  mount(el) { this.node = el; }
  add(message) {
    if (!this.node) return;
    this.node.textContent += (this.node.textContent ? '\n' : '') + message;
    this.node.scrollTop = this.node.scrollHeight;
  }
}
