# rts-mvp

The smallest thing that is still a complete RTS loop, in one file. No build step,
no dependencies, no server. Open `index.html` in a browser.

## The loop

    mine gold  ->  buy a unit  ->  kill the three enemies  ->  VICTORY
                                       (or lose everyone)  ->  DEFEAT  ->  R restarts

## Controls

| Input | Action |
|---|---|
| left-click | select one unit |
| left-drag | box-select units |
| right-click | order selected units to a point |
| `S` | spend 5 gold, spawn a unit at the base |
| `R` | restart |

Units auto-attack any enemy inside 26px and auto-harvest while standing on the
gold circle. Enemies idle until a unit comes within 100px, then chase and fight.

## What is deliberately not here

Pathfinding, unit collision, buildings you can construct, fog of war, multiple
unit types, sound, sprites, saving, AI opponent, camera scrolling. Every one of
those is a separate decision, and none of them are needed for the loop to close.

## Verified

Headless Chrome drives the real `update()` and asserts: harvesting accrues gold,
`S` debits gold and spawns, an army reaches VICTORY, a lone unit reaches DEFEAT,
and reset returns a fresh game. The suite was negative-controlled by removing
player damage, which turns the VICTORY assertion red.
