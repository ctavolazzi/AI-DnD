export class TurnManager {
  constructor() { this.turn = 0; }
  next() { this.turn += 1; return this.turn; }
  current() { return this.turn; }
}
