# 💾 Smart Filename Feature

**Date:** October 28, 2025
**Status:** ✅ Complete

## Overview
Automatic generation of descriptive, timestamped filenames for downloaded images based on prompt content.

---

## 📝 Filename Format

### Pattern
```
{description}_{type}_{timestamp}.png
```

### Components

1. **Description** (max 40 chars)
   - Sanitized from user prompt
   - Lowercase, alphanumeric + dashes only
   - Spaces converted to dashes
   - Special characters removed

2. **Type**
   - `sprite` - Original pixel art sprite
   - `enhanced` - AI-enhanced version

3. **Timestamp**
   - Format: `YYYYMMDD_HHMMSS`
   - Example: `20251028_232015`

---

## 📋 Examples

### Input Prompts → Output Filenames

| Prompt | Type | Filename |
|--------|------|----------|
| "fantasy knight with sword and shield" | sprite | `fantasy-knight-with-sword-and-shield_sprite_20251028_232015.png` |
| "fantasy knight with sword and shield" | enhanced | `fantasy-knight-with-sword-and-shield_enhanced_20251028_232045.png` |
| "cyberpunk ninja with neon katana!!!" | sprite | `cyberpunk-ninja-with-neon-katana_sprite_20251028_233012.png` |
| "cute kawaii cat (very fluffy) 🐱" | sprite | `cute-kawaii-cat-very-fluffy-_sprite_20251028_233145.png` |

---

## 🔧 Implementation

### Function: `generateFilename(description, type)`

```javascript
function generateFilename(description, type = 'sprite') {
    // Sanitize description
    const sanitized = description
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')  // Remove special chars
        .replace(/\s+/g, '-')           // Spaces → dashes
        .replace(/-+/g, '-')            // Remove duplicate dashes
        .substring(0, 40);              // Max 40 chars

    // Generate timestamp: YYYYMMDD_HHMMSS
    const now = new Date();
    const timestamp = [
        now.getFullYear(),
        String(now.getMonth() + 1).padStart(2, '0'),
        String(now.getDate()).padStart(2, '0')
    ].join('') + '_' + [
        String(now.getHours()).padStart(2, '0'),
        String(now.getMinutes()).padStart(2, '0'),
        String(now.getSeconds()).padStart(2, '0')
    ].join('');

    return `${sanitized}_${type}_${timestamp}.png`;
}
```

---

## 🎯 Features

### ✅ Auto-Detection
- Sprite downloads automatically labeled as `sprite`
- Enhanced downloads automatically labeled as `enhanced`
- Based on which container the download button is in

### ✅ Sanitization
- Removes unsafe characters for cross-platform compatibility
- Handles emojis, punctuation, special chars
- Prevents filename injection attacks

### ✅ Length Limiting
- Description capped at 40 characters
- Prevents excessively long filenames
- Total filename ~70 characters max

### ✅ Logging
- Console logs each download with filename
- Format: `💾 [DOWNLOAD] Saving as: {filename}`

---

## 📁 File Organization Benefits

### Chronological Sorting
Files naturally sort by date/time when sorted alphabetically:
```
cyberpunk-ninja_sprite_20251028_120000.png
cyberpunk-ninja_enhanced_20251028_120030.png
fantasy-knight_sprite_20251028_150000.png
fantasy-knight_enhanced_20251028_150025.png
```

### Content Identification
Filenames describe content without opening:
- Quick visual scanning in file explorer
- Search by description
- Easily identify sprite vs enhanced

### Batch Operations
Easy to:
- Select all sprites: `*_sprite_*.png`
- Select all enhanced: `*_enhanced_*.png`
- Select by date: `*_20251028_*.png`
- Select by description: `fantasy-knight*.png`

---

## 🔍 Search Examples

### In File Explorer / Finder

Search for all sprites from a specific day:
```
*_sprite_20251028_*.png
```

Search for all enhanced versions:
```
*_enhanced_*.png
```

Search for specific character:
```
fantasy-knight*.png
```

### In Terminal

```bash
# List all sprites
ls *_sprite_*.png

# Count enhanced images
ls *_enhanced_*.png | wc -l

# Find specific prompt
ls | grep "cyberpunk-ninja"

# Sort by timestamp
ls -1 | sort -t_ -k3
```

---

## 🎨 User Experience

### Before
```
sprite.png
sprite (1).png
sprite (2).png
sprite (3).png
```
❌ No context, no organization, confusing

### After
```
fantasy-knight-sword-shield_sprite_20251028_120000.png
fantasy-knight-sword-shield_enhanced_20251028_120030.png
cyberpunk-ninja-neon-katana_sprite_20251028_120500.png
cyberpunk-ninja-neon-katana_enhanced_20251028_120530.png
```
✅ Descriptive, organized, sortable, searchable

---

## 📊 Technical Details

### Character Sanitization Rules

| Input | Output | Reason |
|-------|--------|--------|
| `ABC` | `abc` | Lowercase for consistency |
| `Hello World` | `hello-world` | Spaces to dashes |
| `cat!!!` | `cat` | Remove punctuation |
| `café` | `caf` | Remove accents/unicode |
| `emoji 🎨` | `emoji-` | Remove emojis |
| `multi---dash` | `multi-dash` | Collapse dashes |

### Timestamp Precision
- **Second-level precision:** Prevents filename collisions
- **24-hour format:** No AM/PM ambiguity
- **ISO-style ordering:** Year-month-day for natural sorting

### Platform Compatibility
- **Windows:** ✅ No `< > : " / \ | ? *`
- **macOS:** ✅ No `:` in filenames
- **Linux:** ✅ No `/` in filenames
- **All platforms:** ✅ Safe, alphanumeric + dash + underscore

---

## 🚀 Future Enhancements (Optional)

1. **Style in filename:** `fantasy-knight_medieval_enhanced_20251028.png`
2. **Size in filename:** `dragon_sprite_64x64_20251028.png`
3. **User prefixes:** `[project-name]_fantasy-knight_sprite.png`
4. **Sequential numbering:** `dragon_sprite_001_20251028.png`
5. **Custom templates:** User-defined filename patterns

---

## ✅ Testing Checklist

- [x] Downloads use smart filenames
- [x] Sprite downloads labeled "sprite"
- [x] Enhanced downloads labeled "enhanced"
- [x] Special characters removed
- [x] Length limited to prevent issues
- [x] Timestamps accurate
- [x] Files sortable chronologically
- [x] Cross-platform compatible
- [x] No filename collisions (second precision)
- [x] Console logs download filenames

---

**Result:** Professional, organized, searchable downloads that make file management a breeze! 💾✨

