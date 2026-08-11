# rts-mvp: architecture and execution plan

Written 2026-08-11. This plan is grounded in two things: measurements taken
against the code in this folder, and published architecture from shipped RTS
games and maintained open source libraries. Every claim about our own code below
was verified by running something, and the command is given so you can re-run it.

---

## 1. What exists today, measured

One file, `index.html`, about 300 lines. Canvas 2D, no build step, no
dependencies, no server.

Measured facts, not estimates:

| Question | Answer | How it was measured |
| --- | --- | --- |
| Is it winnable? | Yes, ~28s | Scripted playthrough driving real `update()` |
| Winnable both ways? | Yes: soldier spam 27.5s, heavy save 28.7s | Same harness, two strategies |
| What if you do nothing? | Lose at exactly 10.0s | Same harness, zero input |
| Does the suite discriminate? | Yes, 12 green, sabotage turns exactly 2 red | Sed-sabotaged copies |
| Is the sim deterministic? | Yes, except two spots | `grep -nE 'Math\.random\|Date\.now\|performance\.now'` |

That last row is the important one.

### The determinism audit

    grep -nE 'Math\.random|Date\.now|performance\.now|new Date' index.html

No line numbers are quoted here on purpose. An earlier draft of this document
cited three, and all three were wrong one commit later. Run the command.

When first run, it found `Math.random()` twice inside `buy()` jittering the
spawn position, and `performance.now()` in the frame loop producing a variable
`dt`. `update()` itself contained none of them, so the simulation was already a
pure function of `(state, dt)`. That was not planned. It fell out of splitting
`update` from `draw` so the headless harness could run the simulation without
rendering.

That accident is the single most valuable asset in this codebase, because it is
the precondition for the architecture the genre actually uses. **Phase 1 below
is now done**, so the command should today report only the `performance.now()`
call that drives the render clock, which is correct and must stay.

---

## 2. What the field does

### Deterministic lockstep, from Age of Empires

Terrano and Bettner's *1500 Archers on a 28.8* is the foundational reference.
Their problem was synchronising 1500 entities for 8 players over a 28.8kbit
modem. Their calculation: shipping just x, y, status, action, facing and damage
per unit capped them at roughly 250 moving units.

So they did not send state. They sent **commands**, and ran the identical
simulation on every machine.

Concrete mechanics worth copying:

- A **communications turn** of about 200ms, decoupled from the render frame
  rate. Rendering can stutter without touching simulation correctness.
- Commands issued during turn N are **scheduled to execute on turn N+2**. Three
  states coexist: executing now, received for next, sent for the turn after.
  Nothing ever blocks on a network round trip.
- **Adaptive turn length**: the host measures each client's achievable frame
  rate and pings for round-trip latency, then broadcasts a turn length that the
  slowest machine can hold. It rises fast under congestion and settles back
  slowly.
- **Checksums** per turn detect divergence. Their hard-won lesson: a subtle
  difference, such as misaligned random terrain generation, compounds silently
  until the game declares out-of-sync with no traceable cause.

Bandwidth scales with **player count, not world complexity**. Eight players at
30Hz and ~50 bytes of input is roughly 12KB/s per client whether the map holds
1,000 units or 10,000.

### Server-authoritative replication, from Colyseus

The opposite trade. [Colyseus](https://github.com/colyseus/colyseus) is a
maintained Node framework built on rooms: a `Server` holds many `Room`
instances, each an isolated session with its own state. Only the server mutates
state. Clients send messages requesting changes. The server diffs the schema,
binary-encodes only the changed properties, and pushes deltas at a configured
`patchRate`.

Bandwidth scales with **the number of objects changing**. You get cheat
resistance and instant local response without input delay, and you pay for it in
server cost and per-unit bandwidth.

### The rest of the stable toolchain

| Concern | Library | Why it is the safe pick |
| --- | --- | --- |
| Rendering at scale | [PixiJS v8](https://pixijs.com/8.x/guides/concepts/performance-tips) | WebGL/WebGPU, aggressive draw-call batching, thousands of sprites at 60fps. Batch limit is 16 textures per draw |
| Entity storage | [bitECS](https://github.com/NateTheGreatt/bitECS) | Data-oriented, struct-of-arrays. Benchmarked ~9.5ms for 15,000 entities against 131.6ms for an OOP baseline, roughly 14x |
| Entity ergonomics | [miniplex](https://github.com/hmans/miniplex) | Slower than bitECS but far pleasanter. The right pick only if entity counts stay low |
| Group movement | Flow fields | Cost field, then Dijkstra integration field, then per-cell vector to the lowest-cost neighbour of 8. One computation serves unlimited agents heading to one destination |

Flow field detail worth writing down now: agents bilinearly interpolate across
the 4 nearest cells so they do not visibly snap to the grid, and the field is
regenerated only when the destination or the map changes. The known weakness is
that only cardinal and 45 degree directions exist, so paths are slightly
suboptimal compared to per-unit A*. Production systems often run hierarchical A*
over tile portals first and request flow fields only for the tiles on that path.

---

## 3. The fork, and which way we go

**We go deterministic lockstep.**

Three reasons, in order of weight:

1. **The simulation is already pure.** Section 1 proved it. We are two small
   fixes from lockstep-capable, and an unknown number of weeks from a
   server-authoritative rewrite.
2. **The test harness is already a determinism rig.** It drives `update()`
   headlessly at a fixed step. Running two instances and comparing checksums is
   a small addition to something that already exists and already works.
3. **Commands are also replays.** A match becomes a seed plus a command log,
   which is kilobytes. State snapshots are megabytes. This pays off before any
   networking exists, which matters because it means phases 1 and 2 are useful
   even if multiplayer never ships.

What we accept by choosing this: clients can cheat by reading state they should
not see, and one slow client sets the pace for everyone. Both are acceptable for
a game this size. Neither is acceptable for a ranked competitive product, and if
that ever becomes the goal, Colyseus is the migration target and this plan
should be reread rather than followed.

---

## 4. Execution plan

Each phase ends in something verifiable. No phase depends on a later phase
existing. Verification is stated up front so it cannot be invented afterwards to
fit whatever happened.

### Phase 1: determinism hardening — DONE

Removed the two known nondeterminism sources.

**Evidence:** 17 headless assertions pass, including `same seed reproduces
identical checksums`, `a different seed diverges`, `spawn jitter is seeded, not
Math.random`, `200ms of wall clock produces exactly 12 ticks`, and `a 5s stall is
clamped to 15 ticks`. Negative-controlled: restoring `Math.random` and removing
the accumulator clamp turns exactly three of those red.

One thing that went wrong and is worth keeping. The first version of the
determinism test passed even with `Math.random` restored, because the scripted
run only accrued 0.05 gold per tick, so every purchase was refused and the PRNG
was never called. The test was vacuous and only the negative control revealed
it. A determinism assertion that never spends gold never tests randomness.

The original plan for this phase follows.

- Replace `Math.random()` in `buy()` with a seeded PRNG carried in `S`. A
  32-bit xorshift is sufficient and is four lines.
- Replace variable `dt` with a fixed simulation step of 1/60, driven by an
  accumulator. The render loop keeps using real elapsed time; the simulation
  only ever advances in whole fixed ticks.
- Add `checksum(S)`, a cheap integer hash over positions, hp and gold, quantised
  to avoid float noise.

**Verify:** run the same seed and the same command log twice, assert identical
checksums at every tick. Then change one input by one tick and assert the
checksums diverge. A determinism test that has never diverged proves nothing.

### Phase 2: the command layer

Input currently mutates `S` directly from event handlers. Interpose a queue.

- Handlers stop mutating and start emitting commands: `{tick, type, payload}`.
- `update()` takes the commands due this tick and applies them before stepping.
- Record every command to an in-memory log alongside the seed.

**Verify:** play a match, save the log, replay it into a fresh state, assert the
final checksum matches. This is the phase that makes replays exist, and replays
are what make every later bug reproducible.

### Phase 3: the stack

This is where the project stops being one file.

- `server.py`, Python standard library only, `http.server` plus `sqlite3`. No
  dependencies, consistent with the no-build-step constraint.
- `GET /api/config` serves balance numbers from `balance.json`. The twelve
  numbers that currently define all difficulty move out of the client, so
  tuning stops requiring a code edit.
- `POST /api/match` stores a finished match: seed, command log, result,
  duration, outcome. Because of phase 2 this is a few KB, not a state dump.
- `GET /api/replay/{id}` returns a log the client can play back.
- The client falls back to built-in defaults when the API is unreachable, so
  `file://` keeps working exactly as it does today.

**Verify:** real HTTP requests against a running server, asserting on status
codes and body shape. Then stop the server and confirm the game still boots and
plays from defaults.

### Phase 4: transport

Only now does networking appear, and it appears as a relay rather than an
authority.

- WebSocket server relaying commands, tagging each with its execution tick.
- Two-turn scheduling exactly as AoE described it.
- Adaptive turn length from measured client frame rate and RTT.
- Per-turn checksum exchange. On mismatch, stop and dump both states rather than
  drifting silently.

**Verify:** two headless clients, same seed, scripted divergent inputs, running
to completion with matching checksums every turn. Then deliberately desync one
client and assert the mismatch is caught on the turn it happens.

### Phase 5: scale, only if measured

Do not start this phase on speculation. Start it when a profile says to.

- Canvas 2D to PixiJS when draw time becomes the frame budget problem.
- Per-unit steering to flow fields when unit counts make the current separation
  pass look like a crowd crush.
- Plain object array to bitECS when iteration cost shows up in a profile.

**Verify:** a benchmark of the current renderer at increasing unit counts,
recorded before the swap, so the improvement is a number rather than a feeling.

---

## 5. What we deliberately do not build

Fog of war, constructible buildings, an opponent that makes decisions, terrain,
camera scrolling, sound, sprites, matchmaking, accounts, ranked play.

Each is a real feature. None is on the critical path to a networked
deterministic RTS, and every one of them is cheaper to add after the command
layer exists than before it.

---

## 6. Known gap, stated plainly

The mouse has never been tested. Every assertion in the suite drives `update()`
directly or dispatches synthetic keyboard events. Click, drag, box-select and
right-click targeting have zero coverage, and they are the only way a human
touches this game. Phase 2 makes this fixable, because once input emits commands
instead of mutating state, the input layer can be tested by asserting on the
commands it produces.

Until then, treat the input layer as unverified.

---

## How strong the sourcing in section 2 actually is

Stated plainly, because the tables above look more authoritative than the
evidence behind them warrants.

| Claim | What I actually read |
| --- | --- |
| AoE 200ms turns, N+2 scheduling, adaptive turn length, checksums | **Not the paper.** The PDF fetch failed. This is a summarising model's reading of a secondary article about the paper. The specifics are probably right and are widely repeated, but I did not verify them at the source |
| "8 players at 30Hz, ~50 bytes, ~12KB/s" | A search-result summary of a different blog, not Terrano and Bettner. It is placed in the AoE subsection above, which wrongly implies that attribution |
| bitECS "9.56ms vs 131.6ms, roughly 14x" | A search-result snippet. I never opened the benchmark or ran it |
| Colyseus rooms, schema deltas, patchRate | Official docs summary. Reasonably solid |
| Flow field three-stage algorithm | The howtorts article itself, fetched and read |

Nothing in section 3's decision depends on the weak rows. The decision rests on
section 1, which was measured locally. But if a number from section 2 is about
to drive a real choice, verify it first.

## Sources

- [1500 Archers on a 28.8: Network Programming in Age of Empires and Beyond](https://www.gamedeveloper.com/programming/1500-archers-on-a-28-8-network-programming-in-age-of-empires-and-beyond)
- [Colyseus multiplayer framework](https://github.com/colyseus/colyseus) and [state synchronization docs](https://docs.colyseus.io/state)
- [bitECS](https://github.com/NateTheGreatt/bitECS)
- [PixiJS v8 performance tips](https://pixijs.com/8.x/guides/concepts/performance-tips)
- [How to RTS: Basic Flow Fields](https://howtorts.github.io/2014/01/04/basic-flow-fields.html)
- [Crowd Pathfinding and Steering Using Flow Field Tiles, Game AI Pro ch.23](https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter23_Crowd_Pathfinding_and_Steering_Using_Flow_Field_Tiles.pdf)
