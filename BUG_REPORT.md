# Bug Report & Fix Plan

## 🐛 Critical Bugs Identified

### BUG #1: Encounters Don't Clear Properly ⚠️⚠️⚠️
**Issue:**
- Combat choices get removed but encounter text stays in log
- New encounters stack on top of old ones
- Multiple choice buttons can appear simultaneously
- No "in combat" state tracking

**Root Cause:**
```javascript
choicesDiv.remove(); // Removes buttons
// But encounter text stays in log forever
// No flag to prevent new encounters during combat
```

**Fix:**
- Add `gameState.inCombat` flag
- Prevent movement during combat
- Clear combat state when resolved
- Add visual separator after encounter ends

---

### BUG #2: Encounter Rate Too High 🎲
**Issue:** 30% chance on EVERY move = too frequent

**Current Code:**
```javascript
if (Math.random() < 0.3) {  // 30% = way too much
    triggerEncounter();
}
```

**Fix:** Lower to 10-15%, add cooldown system

---

### BUG #3: No Encounter Cooldown ⏱️
**Issue:** Can trigger encounter immediately after finishing previous one

**Fix:**
```javascript
gameState.lastEncounterLocation = null;
// Don't trigger at same location twice in a row
```

---

### BUG #4: Multiple Choice Buttons 🔘
**Issue:** If you spam movement, multiple `.choices` divs can exist

**Fix:** Remove ALL existing choice divs before creating new ones

---

### BUG #5: No Quest System 📋
**Issue:** Objectives are static HTML, never complete

**Fix:** Build dynamic quest system with completion tracking

---

## 🔧 Fix Implementation Order

### Phase 1: Critical Combat Bugs (15 min)
- [ ] Add `inCombat` flag
- [ ] Prevent actions during combat
- [ ] Clear combat state properly
- [ ] Remove duplicate choices

### Phase 2: Encounter System (20 min)
- [ ] Lower encounter rate to 15%
- [ ] Add location-based cooldown
- [ ] Add encounter variety per location
- [ ] Fix encounter stacking

### Phase 3: Quest System (30 min)
- [ ] Dynamic quest rendering
- [ ] Quest completion triggers
- [ ] Quest rewards
- [ ] Quest progression tracking

### Phase 4: Dialogue System (20 min)
- [ ] Location-based NPCs
- [ ] Context-aware dialogue
- [ ] Dialogue choices
- [ ] Quest dialogue integration

---

## 🚀 Ready to implement?

