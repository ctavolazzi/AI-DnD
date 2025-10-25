export const LOCATIONS = {
  tavern: { id: 'tavern', name: 'Starting Tavern', icon: '🍺', discovered: true, adjacent: ['town_square'] },
  town_square: { id: 'town_square', name: 'Town Square', icon: '🏛️', discovered: false, adjacent: ['tavern', 'mine_entrance'] },
  mine_entrance: { id: 'mine_entrance', name: 'Mine Entrance', icon: '⛏️', discovered: false, adjacent: ['town_square', 'mine_level1'] },
  mine_level1: { id: 'mine_level1', name: 'Mine Level 1', icon: '🪨', discovered: false, adjacent: ['mine_entrance', 'mine_level2'] },
  mine_level2: { id: 'mine_level2', name: 'Mine Level 2', icon: '💎', discovered: false, adjacent: ['mine_level1', 'boss_chamber'] },
  boss_chamber: { id: 'boss_chamber', name: 'Rune Guardian Lair', icon: '🗿', discovered: false, adjacent: ['mine_level2'] },
  crystal_cavern: { id: 'crystal_cavern', name: 'Crystal Cavern', icon: '🔷', discovered: false, adjacent: [] }
};
