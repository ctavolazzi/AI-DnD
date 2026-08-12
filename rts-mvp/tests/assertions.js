// Test harness for index.html. Appended to a copy of the game by tests/run.sh,
// never shipped inside the game itself.
//
// How it works: the game declares its state and functions at the top level of a
// classic <script>, so those bindings are reachable from a later <script> in the
// same document. This block stubs requestAnimationFrame to stop the render loop,
// then calls the real update() in a tight loop to run minutes of game time in
// milliseconds. Nothing here is mocked. It drives production code.

window.requestAnimationFrame = () => 0;
const out = [];
const ok = (n, cond, d) => out.push((cond ? 'PASS' : 'FAIL') + ' :: ' + n + (d ? ' :: ' + d : ''));
const sim = (secs, dt = STEP) => { for (let t = 0; t < secs; t += dt) update(dt); };
const key = k => window.dispatchEvent(new KeyboardEvent('keydown', { key: k }));

reset(); S.units[0].x = MINE.x; S.units[0].y = MINE.y; sim(10);
ok('unit on mine accrues gold', S.gold >= 15, 'gold=' + S.gold.toFixed(1));

reset(); S.gold = 20; key('s');
const sol = S.units[S.units.length - 1];
ok('S buys a soldier at full bar', sol.kind === 'soldier' && sol.hp === sol.max && S.gold === 15, 'gold=' + S.gold);

reset(); S.gold = 20; key('d');
const hv = S.units[S.units.length - 1];
ok('D buys a heavy at full bar', hv.kind === 'heavy' && hv.hp === HEAVY_HP && hv.hp / hv.max === 1 && S.gold === 8, 'gold=' + S.gold);

reset(); S.gold = 5; key('d');
ok('D refused when gold is short', S.units.length === 2 && S.gold === 5, 'gold=' + S.gold);

reset(); S.enemies = [S.enemies[0]];
S.enemies[0].x = 300; S.enemies[0].y = 300; S.enemies[0].hp = 1000;
S.units = [unit(310, 300, 'p', 'heavy')]; S.units[0].hp = 1000;
sim(1);
const dealt = 1000 - S.enemies[0].hp;
ok('heavy out-damages a soldier', dealt > 28 && dealt < 36, 'dealt=' + dealt.toFixed(1) + '/sec');

reset(); S.enemies = []; S.gold = 200;
for (let i = 0; i < 8; i++) key('d');
for (const u of S.units) u.foe = S.ebase;
sim(60);
ok('army razes the enemy base -> VICTORY', S.status === 'won' && S.ebase.hp <= 0, 'status=' + S.status);

reset(); S.units = []; S.gold = 100; sim(20);
ok('undefended base gets marched on -> DEFEAT', S.status === 'lost' && S.pbase.hp <= 0, 'status=' + S.status);

reset(); S.units = []; S.gold = 0; sim(0.1);
ok('no army and no gold -> DEFEAT (stall guard)', S.status === 'lost', 'status=' + S.status);

reset(); S.units = []; S.gold = 50; sim(0.1);
ok('no army but gold left keeps playing', S.status === 'playing', 'status=' + S.status);

reset(); S.units = [S.units[0]];
S.units[0].x = 300; S.units[0].y = 300; S.units[0].hp = 1000;
S.enemies = [S.enemies[0], S.enemies[1]];
const decoy = S.enemies[0], target = S.enemies[1];
decoy.x = 300; decoy.y = 290; target.x = 300; target.y = 320;
S.units[0].foe = target; sim(1.9);
ok('focus fire hits the ordered target', target.hp < 10 && decoy.hp === SOLDIER_HP,
   'target=' + target.hp.toFixed(1) + ' decoy=' + decoy.hp.toFixed(1));

reset(); S.units[0].x = 300; S.units[0].y = 300; S.units[1].x = 300; S.units[1].y = 300;
sim(1);
const gap = Math.hypot(S.units[0].x - S.units[1].x, S.units[0].y - S.units[1].y);
ok('stacked units push apart', gap >= SPACING - 0.5, 'gap=' + gap.toFixed(2));

reset(); S.enemies = [];
S.units = [unit(S.ebase.x - 45, S.ebase.y, 'p')]; sim(2);
ok('auto-attacks the enemy base with no order given', S.ebase.hp < BASE_HP, 'ebase=' + S.ebase.hp.toFixed(1));

// ---- determinism ----------------------------------------------------------
// The gold rate here is load bearing. An earlier version added 0.05/tick, so
// every scripted purchase was refused, so the PRNG was never called, so this
// assertion passed even with Math.random restored. It was vacuous and only the
// negative control revealed it. Do not lower this number.
function scripted(seed) {
  reset(seed);
  const marks = [];
  for (let t = 0; t < 600; t++) {
    if (t === 30 || t === 90) key('s');
    if (t === 150) key('d');
    if (t === 200 && S.enemies.length) for (const u of S.units) u.foe = S.enemies[0];
    S.gold += 0.5;
    update(STEP);
    if (t % 120 === 0) marks.push(checksum());
  }
  return marks.join(',');
}
const runA = scripted(12345), runB = scripted(12345), runC = scripted(999);
ok('same seed reproduces identical checksums', runA === runB, runA.slice(0, 34) + '...');
ok('a different seed diverges', runA !== runC, 'seed999=' + runC.slice(0, 22) + '...');

reset(1); S.gold = 50; key('s'); const spawn1 = S.units[S.units.length - 1].x;
reset(1); S.gold = 50; key('s'); const spawn2 = S.units[S.units.length - 1].x;
ok('spawn jitter is seeded, not Math.random', spawn1 === spawn2,
   'x1=' + spawn1.toFixed(4) + ' x2=' + spawn2.toFixed(4));

// ---- fixed timestep -------------------------------------------------------
// Drives the real frame() with controlled wall-clock values. `last` and
// `accumulator` are top-level let bindings in index.html, so they are writable
// from here.
const realUpdate = update;
let ticks = 0;
update = dt => { ticks++; realUpdate(dt); };

reset(); last = 0; accumulator = 0; ticks = 0; frame(200);
ok('200ms of wall clock produces exactly 12 ticks', ticks === 12, 'ticks=' + ticks);

reset(); last = 0; accumulator = 0; ticks = 0; frame(5000);
ok('a 5s stall is clamped to 15 ticks, no death spiral', ticks === 15, 'ticks=' + ticks);

update = realUpdate;
document.body.innerHTML = '<pre>' + out.join('\n') + '</pre>';
