# rts-mvp

The smallest thing that is still a complete RTS loop, in one file. No build step,
no dependencies, no server. Open `index.html` in a browser.

## The loop

    mine gold  ->  buy soldiers and heavies  ->  raze the red base  ->  VICTORY
                            (or lose your own base)  ->  DEFEAT  ->  R restarts

You also lose if you have no units and not enough gold to buy one, since there is
no way back from there.

## Controls

| Input | Action |
| --- | --- |
| left-click | select one unit |
| left-drag | box-select units |
| right-click ground | order selected units to a point |
| right-click an enemy or the red base | focus fire that specific target |
| `S` | 5 gold, soldier: 40hp, 70px/s, 20dps, drawn as a circle |
| `D` | 12 gold, heavy: 120hp, 45px/s, 32dps, drawn as a square |
| `R` | restart |

With no focus target, units auto-attack the nearest hostile thing in range,
including the enemy base. They auto-harvest while standing on the gold circle.
Enemies fight anything within 100px and otherwise march on your base. Bodies push
each other apart at 17px; bases do not move and are not part of that.

Both bases have 300hp. A target's radius widens its reachable band, so a base is
hittable from its edge rather than only from its centre.

## What is deliberately not here

Pathfinding, buildings you can construct, fog of war, sound, sprites, saving, an
AI opponent that makes decisions, camera scrolling. Every one of those is a
separate decision, and none of them are needed for the loop to close.

## Verified

Headless Chrome drives the real `update()` across 12 assertions: harvesting,
both purchase types and their refusal when short on gold, heavy damage output,
victory by razing the enemy base, defeat by losing yours, the stall guard, focus
fire, separation, and auto-acquiring the base with no order given.

The suite is negative-controlled. Disabling the two new mechanisms at once, by
dropping the enemy base from the auto-target list and stopping enemies from
marching, turns exactly two assertions red and leaves the other ten green.

One gap this caught and closed: the victory test set `u.foe` explicitly, so it
only ever exercised the ordered-attack path. Auto-acquisition of the base had no
coverage at all and the sabotage sailed straight through it. The
`unit auto-attacks the enemy base with no order given` assertion exists because
of that miss.
