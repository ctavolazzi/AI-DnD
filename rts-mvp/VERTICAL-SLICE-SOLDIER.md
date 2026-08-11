# Vertical slice: the soldier

One unit, specified through every layer, from the row it is authored in to the
pixels that move on screen. Naming follows `NAMING.md`. Nothing here is built
yet; this is the specification the build follows.

The soldier is chosen because it is the cheapest, most common unit, so every
mistake in this slice will be visible immediately and often.

```
  design/units/soldier.json        authored by a human, in git
          |
          v  seed / migrate
  unit_type row                    one row, the definition
          |
          v  GET /api/unit-types   read-only, published only
  UnitTypeCache (client)           immutable after load
          |
          v  spawn command
  Unit instance                    many, on the map, per match
          |
          v  effective stats       base + modifiers, recomputed on change
  simulation tick                  movement, combat, separation
          |
          v  render (never back)
  sprite + animation state
```

---

## Layer 0. Where the definition lives

**One authored file: `design/units/soldier.json`.** Text, in git, diffable,
reviewed in a pull request like code.

```json
{
  "id": "soldier",
  "displayName": "Soldier",
  "costGold": 5,
  "baseHp": 40,
  "baseSpeed": 70,
  "baseDps": 20,
  "attackRange": 26,
  "bodyRadius": 8,
  "buildSeconds": 0,
  "spriteSheet": "soldier.png",
  "published": true
}
```

`id` is a **stable slug**. It is never renamed and never reused, because match
records will reference it for as long as those records exist. `displayName` is
the only thing users see, and it may change freely.

On server start, `design/units/*.json` is loaded into the `unit_type` table.
The table is a cache of the files, not a second source of truth. If they
disagree, the files win, and the loader says so loudly rather than merging.

---

## Layer 1. Lookup

Two access patterns, and they want different things.

**By id, one at a time.** `getUnitType("soldier")`. Hot path, called on every
spawn. Backed by a `Map` built once at load. Never a query per call.

**All published types.** `listUnitTypes()`. Cold path, called once per client
session to populate the client cache.

Cache invalidation is deliberately crude: the whole map is rebuilt on server
start or on an explicit reload. Design data changes at the speed of a commit,
not the speed of gameplay, so anything more clever is unearned complexity.

A miss on `getUnitType` is a **hard error, never a default**. A silent fallback
to a generic unit is how a typo ships a 0-cost invincible soldier.

---

## Layer 2. Transformations, the modifier pipeline

The definition holds *base* stats. What the simulation reads are *effective*
stats. Between them sits one pipeline, and its order is fixed forever because
changing it silently rebalances the entire game.

```
effective = clamp( round( (base + sumOfFlat) * (1 + sumOfPercent) ), min, max )
```

Flat before percent. Percent modifiers sum with each other, they do not
multiply, so two +50% effects give +100% and not +125%. This is chosen because
it is the rule players can do in their heads.

Four modifier sources, all producing the same `{stat, flat, percent, source}`
shape:

| Source | Scope | Lifetime | Example |
| --- | --- | --- | --- |
| upgrade | whole team | rest of match, once bought | +20% soldier dps |
| veterancy | one unit | rest of that unit's life | +10% hp per rank |
| aura | units inside a radius | while in radius | nearby officer, +15% speed |
| terrain | units on a tile | while standing there | high ground, +1 range |

**Recomputation rule.** Effective stats are cached on the unit and recomputed
only when `unit.modifierVersion !== team.modifierVersion`, or when the unit
enters or leaves an aura or terrain zone. Not every tick. A soldier standing
still with no upgrades recomputes zero times.

**Ordering rule for equal stats.** Modifiers are sorted by `source` using a
fixed enum order before summing, so floating point addition happens in the same
sequence on every machine. This exists purely to protect determinism, and it is
the kind of detail that causes an out-of-sync three weeks later if skipped.

---

## Layer 3. CRUD, and who is allowed to do what

The important answer: **the game client can never write a unit type.** Design
data is authored in git and served read-only. This is not a permissions
oversight to fix later, it is the design.

| Actor | Create | Read | Update | Delete |
| --- | --- | --- | --- | --- |
| Game client (anonymous) | no | published only | no | no |
| Designer, via pull request | yes | yes | yes | tombstone only |
| Admin API, bearer token | no | including drafts | draft rows only | no |
| Server, at runtime | no | yes | no | no |

**Validation, applied at load and rejected loudly:**

- `id` matches `^[a-z][a-z0-9-]{1,31}$`. Lowercase slug, no surprises in URLs.
- Every numeric field is finite and within a declared range. `baseHp` in
  `[1, 100000]`, `baseSpeed` in `[0, 1000]`, `costGold` in `[0, 100000]`.
- `costGold` of 0 is legal but must carry an explicit `"free": true` so it
  cannot happen by an omitted field.
- Unknown keys are an error, not ignored. A typo in `baseDsp` must fail rather
  than silently apply zero damage.

**Deletion is a tombstone, never a delete.** Set `retiredAt`. Match records
reference `unit_type.id` and those references must stay resolvable for as long
as any replay exists. A hard delete turns old replays into corrupt data.

**Authorization for the admin path**, when it exists: bearer token in an
`Authorization` header, compared in constant time, never in a query string
where it lands in access logs. Write endpoints are rate limited and every write
is appended to an audit row with actor, timestamp, before and after. Draft rows
are invisible to `GET /api/unit-types` unless the token is present.

---

## Layer 4. What references a soldier

Every inbound reference is by `id`, never by row number, and this is what makes
the tombstone rule enforceable.

| Referrer | Field | Breaks if the soldier disappears |
| --- | --- | --- |
| Spawn command | `unitTypeId` | replay becomes unplayable |
| Match record | `unitsBuilt[].unitTypeId` | historical stats become wrong |
| Upgrade | `appliesTo: ["soldier"]` | upgrade silently affects nothing |
| Production menu | `offers: ["soldier"]` | button vanishes, no error |
| Sprite manifest | `spriteSheet` | unit renders as a missing-texture box |

A startup integrity check resolves every reference and refuses to boot on a
dangling one. Finding this at boot is cheap. Finding it when a player clicks
buy is not.

---

## Layer 5. Getting to the client

`GET /api/unit-types` returns published definitions only, with an `ETag` so a
returning client gets a 304 rather than the payload.

The client stores them in a frozen map, `UnitTypeCache`, and never mutates it.
Runtime instances hold `unitTypeId` and read through the cache. Copying stats
onto each instance at spawn would fork the definition into N silent copies,
which is the same single-source-of-truth failure the naming pass found in the
documentation.

**Offline behaviour.** If the fetch fails, the client uses a generated fallback
bundle baked into the page at export time, stamped `GENERATED, DO NOT EDIT`. It
is a derived artifact, not a second source.

---

## Layer 6. The runtime instance

```js
{
  id,              // unique within the match, assigned by the simulation
  unitTypeId,      // "soldier", the only link to the definition
  team,            // "player" | "enemy"
  x, y,            // position in world pixels
  hp,              // current, absolute
  moveTo,          // {x, y} or null
  orderedTarget,   // unit or base the player told it to attack, or null
  selected,        // client-side only, never affects simulation
  modifiers,       // array, sorted by source enum
  statsCache,      // effective stats, plus the version it was computed at
  animState        // client-side only
}
```

Two fields are marked client-side only and that marking is load bearing.
`selected` and `animState` must never be read by `update()`. If selection could
change simulation, two players with different selections would desync
immediately.

---

## Layer 7. Movement

Five stages, in this order, every tick:

1. **Order resolution.** If `orderedTarget` is alive, `moveTo` is set to its
   position. This is what makes a chase follow a moving target.
2. **Desired direction.** Normalized vector to `moveTo`, or zero.
3. **Step.** Advance by `effectiveSpeed * TICK_SECONDS`, stopping short by
   `stopDistance(target)` so the unit parks inside its own attack range instead
   of oscillating on the boundary.
4. **Separation.** After all units have moved, overlapping bodies are pushed
   apart at `MIN_SEPARATION`. A correction pass, not physics.
5. **Clamp.** Into map bounds.

Pathfinding is deliberately absent at this stage. When it arrives it slots in
at stage 2, replacing "normalized vector to `moveTo`" with "flow field lookup at
my cell". Nothing else in the pipeline changes, which is the point of writing
the stages down now.

---

## Layer 8. Animation

**The rule that matters: animation reads simulation state and never writes it.**
Frame timing uses real elapsed wall time. Simulation uses fixed ticks. They are
never the same clock. Violating this makes the game desync on machines with
different frame rates, which is exactly the failure mode Age of Empires
documented.

State machine, derived fresh each frame from simulation state:

| State | Entered when | Frames | Loop |
| --- | --- | --- | --- |
| `idle` | no `moveTo`, no target in reach | 2 | yes, 0.6s |
| `move` | position changed this tick | 4 | yes, 0.4s |
| `attack` | target within reach | 3 | yes, matches 1 attack cycle |
| `hurt` | hp dropped since last frame | 1 | no, 0.12s, overrides move |
| `die` | hp reached 0 | 4 | no, then the instance is removed |

`die` is the one case where rendering outlives simulation. The instance leaves
the simulation arrays on the tick it dies, and a separate client-only corpse
list holds it for the length of the death animation. The simulation must not
know corpses exist.

Facing is 8-directional, derived from the movement vector, and it is purely
cosmetic. It is never an input to combat, because a facing requirement would
mean turn-to-face time, which would mean simulation state.

---

## Layer 9. Controls

| Input | Produces | Notes |
| --- | --- | --- |
| left click on a unit | select that unit | client-only state change |
| left drag | select all own units in box | client-only |
| right click on ground | `{type: "move", unitIds, x, y}` | a command, not a mutation |
| right click on a hostile | `{type: "attack", unitIds, targetId}` | a command |
| `S` | `{type: "buy", unitTypeId: "soldier"}` | a command |

**The rule: input emits commands, it never mutates the world.** Commands are
queued with the tick they execute on. This is what makes replays, networking,
and testing the input layer all possible, and it is why the current code, where
handlers mutate state directly, has no test coverage of the mouse.

Command validation happens in the simulation, not the handler. A buy command
with insufficient gold is dropped by `update()`, not prevented by a disabled
button, because the button is on one machine and the simulation is on all of
them.

---

## What this slice deliberately leaves out

Formations, stances such as hold-ground or aggressive, patrol, waypoint queues,
attack-move as distinct from attack-target, veterancy accrual rules, and unit
production time. Each is a real feature. Each slots into a stage named above
rather than requiring the pipeline to change shape, which is the test of whether
this specification was worth writing.
