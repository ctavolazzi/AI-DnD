export function logMovement(adventureLog, fromId, toId, locations) {
  const fromName = locations[fromId]?.name || fromId;
  const toName = locations[toId]?.name || toId;
  const icon = locations[toId]?.icon || '🧭';
  adventureLog?.add(`${icon} You travel from ${fromName} to ${toName}.`);
}
