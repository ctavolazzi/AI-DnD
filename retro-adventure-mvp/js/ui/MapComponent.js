import { LOCATIONS } from '../data/locations.js';

export class MapComponent {
  constructor(onClick) { this.onClick = onClick; }
  render(currentLocation = 'tavern') {
    const grid = [
      [null, 'tavern', 'town_square'],
      [null, 'mine_entrance', 'mine_level1'],
      [null, 'mine_level2', 'boss_chamber']
    ];
    const html = `
      <div id="map-grid" style="height:180px;background:#fff7;display:grid;grid-template-columns:repeat(3,1fr);gap:6px">
        ${grid.flatMap((row)=>row).map((id)=>{
          if (!id) return `<div style="aspect-ratio:1;border:1px solid #654321;opacity:.3"></div>`;
          const isCurrent = id === currentLocation;
          const style = `aspect-ratio:1;border:2px solid ${isCurrent?'#DAA520':'#654321'};display:grid;place-items:center;cursor:pointer;`;
          const icon = LOCATIONS[id]?.icon || '❓';
          const title = LOCATIONS[id]?.name || id;
          return `<div class="map-cell" data-id="${id}" title="${title}" style="${style}">${isCurrent?'📍':icon}</div>`;
        }).join('')}
      </div>`;
    return html;
  }
  bindInteractions(container, available=[]) {
    const cells = container.querySelectorAll('.map-cell');
    cells.forEach(cell => {
      const id = cell.getAttribute('data-id');
      const isAvailable = available.includes(id);
      if (!isAvailable) {
        cell.style.opacity = '.5';
        cell.style.cursor = 'not-allowed';
        return;
      }
      cell.addEventListener('click', () => this.onClick && this.onClick(id));
    });
  }
}
