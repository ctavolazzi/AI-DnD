# Quest System Walkthrough

## How to Complete All 4 Quests - Step by Step

### Quest 1: "Gather your party" ✅
**Location:** Starting Tavern (3,2)
**Actions Required:**
1. Click **💬 TALK** button
2. ✅ Quest automatically completes

**Current Status:** ✅ WORKS

---

### Quest 2: "Reach Emberpeak Mines" ✅
**Location:** Mine Entrance (3,5)
**Actions Required:**
1. From Tavern (3,2), click **⬇️ SOUTH** → City Gates (3,3)
2. Click **⬇️ SOUTH** → Forest Path (3,4)
3. Click **⬇️ SOUTH** → Mine Entrance (3,5)
4. ✅ Quest automatically completes when entering underground

**Current Status:** ✅ WORKS

---

### Quest 3: "Rescue the trapped miners" ✅
**Location:** Multiple steps in underground mines
**Actions Required:**

#### Part A: Find the Miner's Note
1. From Mine Entrance (3,5), navigate to Mining Camp (3,7):
   - **⬇️ SOUTH** → Shaft Junction (3,6)
   - **⬇️ SOUTH** → Mining Camp (3,7)
2. Click **💬 TALK** button
3. 📜 Receive: **Miner's Note** (automatically added to inventory)

#### Part B: Clear the Rubble
1. From Mining Camp (3,7), go **⬅️ WEST** → Collapsed Tunnel (2,7)
2. Click **💬 TALK** button
3. Game checks if you have **Rope** (you start with it)
4. Rope is used to create pulley system
5. Rubble cleared! Hear voices

#### Part C: Talk to Survivors
1. At Collapsed Tunnel (2,7), click **💬 TALK** again
2. Meet Foreman Garrett
3. 🧪 Receive: **Healing Potion** (automatically added to inventory)
4. ✅ Quest 3 completes

**Current Status:** ✅ WORKS (rope requirement, multi-step process)

---

### Quest 4: "Seal the shattered rune" ✅
**Location:** Deep Chamber → Rune Chamber
**Actions Required:**

#### Part A: Get the Sealing Stone
**Prerequisite:** Must complete Quest 3 first!
1. From Collapsed Tunnel (2,7), navigate to Deep Chamber (3,8):
   - **➡️ EAST** → Mining Camp (3,7)
   - **⬇️ SOUTH** → Deep Chamber (3,8)
2. Click **💬 TALK** button
3. 💠 Receive: **Sealing Stone** (automatically added to inventory)

#### Part B: Seal the Rune
1. From Deep Chamber (3,8), go **⬇️ SOUTH** → Rune Chamber (3,9)
2. Click **💬 TALK** button
3. Game checks if you have **Sealing Stone**
4. Dramatic sealing sequence plays
5. Sealing Stone consumed (removed from inventory)
6. ✅ Quest 4 completes
7. 🎉 ALL QUESTS COMPLETE!

**Current Status:** ✅ WORKS (requires stone, multi-step)

---

## Summary: Button Sequences

### Complete Game Playthrough
```
Start: Tavern (3,2)
│
├─ [💬 TALK] → Quest 1 ✅
│
├─ [⬇️ SOUTH] → City Gates
├─ [⬇️ SOUTH] → Forest Path
├─ [⬇️ SOUTH] → Mine Entrance → Quest 2 ✅
│
├─ [⬇️ SOUTH] → Shaft Junction
├─ [⬇️ SOUTH] → Mining Camp
├─ [💬 TALK] → Get Miner's Note
│
├─ [⬅️ WEST] → Collapsed Tunnel
├─ [💬 TALK] → Use Rope (clear rubble)
├─ [💬 TALK] → Talk to Garrett → Quest 3 ✅
│
├─ [➡️ EAST] → Mining Camp
├─ [⬇️ SOUTH] → Deep Chamber
├─ [💬 TALK] → Get Sealing Stone
│
├─ [⬇️ SOUTH] → Rune Chamber
└─ [💬 TALK] → Seal Rune → Quest 4 ✅

VICTORY! 🎉
```

---

## How Players Know What to Do

### Current Information Sources:
1. **Quest List (Right Panel):** Shows 4 objectives
2. **Adventure Log:** Shows text hints during gameplay
3. **TALK Button:** Main interaction mechanism
4. **Inventory:** Shows quest items with ⭐ marker

### Potential Issues:
❌ No explicit "Go here next" instructions
❌ Player might not know to click TALK at Mining Camp
❌ No indication that Rope is needed until you try
❌ Easy to miss the correct sequence

---

## Improvements Needed?

### Option 1: Quest Journal System
- Click quest in list to see details
- Shows current objective: "Search the Mining Camp"
- Updates as you progress

### Option 2: NPC Dialogue Hints
- Tavern NPCs mention "miners trapped in west tunnel"
- Surface NPCs say "bring rope if you go to mines"
- More contextual clues

### Option 3: Map Markers
- Quest locations marked with ⭐ on map
- Shows where to go next
- Updates dynamically

### Option 4: Tutorial Messages
- First time entering mines: "💡 TIP: Click TALK to search locations"
- At Mining Camp: "💡 This looks like a good place to investigate..."
- Context-sensitive hints

Would you like me to implement any of these improvements?

