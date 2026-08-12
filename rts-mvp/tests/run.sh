#!/bin/bash
# Run the assertion suite against index.html in headless Chrome.
#
#   ./tests/run.sh              run the real build, expect 17 PASS
#   ./tests/run.sh --sabotage   break the code on purpose, expect specific FAILs
#
# A suite that has never gone red proves nothing. --sabotage exists so you can
# watch it go red before you trust a green run. Expected failures under sabotage:
#   spawn jitter is seeded              (Math.random restored)
#   same seed reproduces identical...   (Math.random restored)
#   a 5s stall is clamped to 15 ticks   (accumulator clamp removed)
# Everything else must stay green. If a sabotage turns MORE assertions red than
# listed, the sabotage was too broad and the run tells you nothing.

set -euo pipefail
cd "$(dirname "$0")/.."

CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME" ] || { echo "Chrome not found at: $CHROME  (set \$CHROME)" >&2; exit 1; }

BUILD=.test-build.html
PROFILE=$(mktemp -d)
trap 'rm -f "$BUILD"; rm -rf "$PROFILE"' EXIT

if [ "${1:-}" = "--sabotage" ]; then
  echo "=== SABOTAGED BUILD: determinism (three assertions must go red) ==="
  sed -e 's|+ rand() \* 12|+ Math.random() * 12|' \
      -e 's|(rand() - 0.5) \* 30|(Math.random() - 0.5) * 30|' \
      -e 's|Math.min(0.25, (now - last) / 1000)|((now - last) / 1000)|' index.html > "$BUILD"
elif [ "${1:-}" = "--sabotage-input" ]; then
  # Breaks three input mechanisms: the click-versus-drag threshold, hit detection
  # for right-click targeting, and the match-over guard. Expected red:
  #   click on a unit selects it and only it
  #   right-click an enemy sets it as the focus target
  #   right-click the enemy base targets the base
  #   input is ignored once the match is over
  echo "=== SABOTAGED BUILD: input (four assertions must go red) ==="
  sed -e 's|if (Math.hypot(x1 - x0, y1 - y0) < 5) {|if (false) {|' \
      -e 's|<= (t.r \|\| 12))|<= -1)|' \
      -e "s|if (S.status !== 'playing') return;|if (false) return;|" index.html > "$BUILD"
else
  echo "=== REAL BUILD ==="
  cat index.html > "$BUILD"
fi

{ echo '<script>'; cat tests/assertions.js; echo '</script>'; } >> "$BUILD"

# Chrome --dump-dom writes the DOM and then frequently does NOT exit, because the
# page keeps a live rAF chain. Do not run it in the foreground and expect a
# return. Capture to a file, give it a watchdog, kill it, then read the file.
# Do NOT pass --disable-gpu; it changes rendering behaviour.
RAW=$(mktemp)
trap 'rm -f "$BUILD" "$RAW"; rm -rf "$PROFILE"' EXIT

"$CHROME" --headless=new --dump-dom --virtual-time-budget=3000 \
  --user-data-dir="$PROFILE" "file://$PWD/$BUILD" > "$RAW" 2>/dev/null &
CHROME_PID=$!

for _ in $(seq 1 40); do
  grep -q 'PASS ::\|FAIL ::' "$RAW" 2>/dev/null && break
  kill -0 "$CHROME_PID" 2>/dev/null || break
  sleep 0.5
done
kill "$CHROME_PID" 2>/dev/null || true
wait "$CHROME_PID" 2>/dev/null || true

grep -oE '(PASS|FAIL) :: [^<]*' "$RAW" | sed 's/&gt;/>/g; s/&lt;/</g' > /tmp/rts-test-out.txt || true
cat /tmp/rts-test-out.txt

PASSED=$(grep -c '^PASS' /tmp/rts-test-out.txt || true)
FAILED=$(grep -c '^FAIL' /tmp/rts-test-out.txt || true)
echo "---"
echo "pass: $PASSED   fail: $FAILED"
[ "$PASSED" -eq 0 ] && { echo "NO ASSERTIONS RAN. The page probably threw before the suite. Open $BUILD in a browser and read the console." >&2; exit 2; }
exit 0
