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

> The unit stats in the table above are **hand-copied** from the constants in
> `index.html` and can drift. The hint line under the canvas is generated from
> those constants and cannot. Fixing this table properly needs the design-data
> layer described in `ARCHITECTURE-PLAN.md`.

## Determinism

The simulation is a pure function of state and a fixed 1/60s tick. It uses a
seeded xorshift32 rather than `Math.random`, so the same seed replays a match
exactly. Rendering runs on wall-clock time and never writes to simulation state.

## Verified

Headless Chrome drives the real `update()` across **17 assertions**: harvesting,
both purchase types and their refusal when short on gold, heavy damage output,
victory by razing the enemy base, defeat by losing yours, the stall guard, focus
fire, separation, auto-acquiring the base with no order given, seeded replay,
seed divergence, seeded spawn jitter, and two on the fixed timestep.

The suite is negative-controlled by three separate sabotages. Restoring
`Math.random`, removing the accumulator clamp, dropping the enemy base from the
auto-target list, and stopping enemies from marching each turn a specific
assertion red and leave the rest green.

Two gaps the negative controls caught, both of which would otherwise have
shipped as false confidence:

1. The victory test set `u.foe` explicitly, so it only exercised the
   ordered-attack path. Auto-acquisition of the base had no coverage at all.
2. The first determinism test passed even with `Math.random` restored, because
   the scripted run accrued too little gold for any purchase to succeed, so the
   PRNG was never called. The assertion was vacuous.

## Not verified

**The mouse.** Click, drag, box-select and right-click targeting have zero
coverage. Every assertion drives `update()` directly or dispatches synthetic
keyboard events. Nobody has clicked this game.
