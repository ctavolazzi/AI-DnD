# Naming

The rules, then the decisions. Read the rules first; they are what make future
names decidable instead of improvised.

> **Status: decided, mostly NOT applied.** The tables below read "Was / Now",
> which is misleading, so read this first. Only the `UNIT_* -> SOLDIER_*`
> constant renames exist in the code. `world`, `playerUnits`, `orderedTarget`,
> `canReach` and the rest are decisions, not identifiers you can grep for. Each
> table row is marked. Applying the remainder is one deliberate pass that has to
> update the test harness in the same commit, since the harness reaches into
> these names directly.

## Rules

1. **Symmetric things get symmetric names.** If `playerUnits` exists, its
   counterpart is `enemyUnits`, never `enemies`.
2. **A name says what a thing is, not what stage it is at.** `mvp`, `new`,
   `v2`, `temp` and `final` all expire. Names should not.
3. **One word, one meaning, project-wide.** If `target` means the thing a unit
   was ordered to attack, nothing else may be called a target.
4. **No abbreviation that is not universal.** `hp` and `id` stay. `sel`,
   `dest`, `pbase` and `S` go.
5. **A shared prefix must be genuinely shared.** `UNIT_HP` may only mean
   something true of all units. If it means the soldier's hp, it is
   `SOLDIER_HP`.
6. **Argument order reads left to right as a sentence.** `nearestTo(point,
   candidates)`, not `nearest(list, from)`.
7. **Avoid words the industry has worn out.** `config`, `data`, `manager`,
   `handler`, `util`. They describe the shape of a filing cabinet, not its
   contents.

## Decisions: the world

*None of these are applied. The code still uses `S`, `S.units`, `S.enemies`.*

| Was | Now | Why |
| --- | --- | --- |
| `S` | `world` | A single capital letter is not a name |
| `S.units` | `world.playerUnits` | It meant "mine", which the name did not say |
| `S.enemies` | `world.enemyUnits` | Enemies are units; the pair is now symmetric |
| `S.pbase` | `world.playerBase` | Abbreviation, and asymmetric with the units above |
| `S.ebase` | `world.enemyBase` | Same |
| `S.status` | `world.outcome` | Status is rule-7 vague |
| `'playing' / 'won' / 'lost'` | `'playing' / 'victory' / 'defeat'` | Mixed present and past tense; now all nouns |
| `S.drag` | `world.selectionBox` | Drag is the gesture, the box is the thing |

## Decisions: a unit

*None of these are applied. The code still uses `side`, `kind`, `sel`, `foe`.*

| Was | Now | Why |
| --- | --- | --- |
| `side: 'p' \| 'e'` | `team: 'player' \| 'enemy'` | Single-letter codes force a lookup every read |
| `kind` | `type` | `type` is the word used everywhere else for this |
| `max` | `maxHp` | Max what? |
| `sel` | `selected` | Rule 4 |
| `dest` | `moveTo` | It is a destination point, and the verb form reads at the call site |
| `foe` | `orderedTarget` | It is specifically what the player ordered, which `foe` never conveyed |
| local `locked` | `currentTarget` | `foe` and `locked` were two names for overlapping ideas, violating rule 3 |

## Decisions: constants

| Was | Now | Applied? | Why |
| --- | --- | --- | --- |
| `UNIT_COST/HP/SPEED/DPS` | `SOLDIER_*` | **yes** | Rule 5. These are one unit type's stats, not all units' |
| `RADIUS` | `UNIT_RADIUS` | no | Radius of what |
| `SPACING` | `MIN_SEPARATION` | no | Spacing is ambiguous between a gap and a layout |
| `STEP` | `TICK_SECONDS` | no | Step of what, in what unit |
| `ENEMY_AGGRO` | `AGGRO_RANGE` | no | It is a distance, and it is not enemy-specific in principle |
| `HARVEST_RATE` | `GOLD_PER_SECOND` | no | Rate of what, per what |
| `BASE_R` | `BASE_RADIUS` | no | Rule 4 |

## Decisions: functions

*None of these are applied. The code still uses `unit()`, `separate()`,
`nearest()`, `inRange()`, `standoff()`, `buy()`.*

| Was | Now | Why |
| --- | --- | --- |
| `unit(...)` | `makeUnit(...)` | A noun that returns a thing should say it makes it |
| `base(...)` | `makeBase(...)` | Same |
| `separate(all)` | `pushApart(bodies)` | Says what it does to them |
| `nearest(list, from)` | `nearestTo(point, candidates)` | Rule 6 |
| `inRange(u, t)` | `canReach(attacker, target)` | In range of what, and from whose side |
| `standoff(t)` | `stopDistance(target)` | Standoff is jargon with two meanings |
| `buy(kind, cost)` | `buyUnit(type)` | Cost was derivable; passing both invited a mismatch |

## Decisions: stored data

The words for the two kinds of stored data, which is where the previous naming
was vaguest.

| Term | Means | Lives in | Written by |
| --- | --- | --- | --- |
| **design data** | Authored numbers that define the game: unit stats, map layout | `design/` as text, in git | a human, in a commit |
| **match records** | Generated facts about games that were played | a database, gitignored | the server, at runtime |

The word `config` is retired. It was being used for both of the above and for
the browser's runtime copy, which is three meanings for one word.

Note the properties differ, which is why they are named apart rather than
lumped: design data is authored, versioned, diffable, read-only at runtime.
Match records are generated, append-only, never hand-edited, and worthless in a
diff.

## Open: the project has no name

`rts-mvp` violates rule 2. It is a status, not a thing, and every document
under it inherits the problem.

Until told otherwise the working name is **Ironline**: short, pronounceable,
unclaimed in this workspace, and it says nothing about scope so it cannot
expire. The folder rename is deliberately not done yet, because it breaks every
path in every document written so far and should happen in one deliberate pass
rather than as a side effect of a naming cleanup.
