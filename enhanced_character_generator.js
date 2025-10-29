/**
 * Enhanced D&D Character Generator - JavaScript Implementation
 * Integrates with MCP game interface for comprehensive character generation
 * Based on REF-103 through REF-108 specifications
 */

class CharacterType {
    static HERO = 'hero';
    static NPC = 'npc';
    static VILLAIN = 'villain';
    static MERCHANT = 'merchant';
    static GUARD = 'guard';
    static NOBLE = 'noble';
    static SCHOLAR = 'scholar';
}

class CharacterTone {
    static REALISTIC = 'realistic';
    static FANTASY = 'fantasy';
    static COMEDY = 'comedy';
    static DRAMATIC = 'dramatic';
}

class EnhancedCharacterGenerator {
    constructor() {
        // REF-103.1: Personality Trait Databases
        this.personalityData = {
            primaryTraits: ["Bold", "Cautious", "Intelligent", "Charismatic", "Mysterious",
                           "Loyal", "Independent", "Creative", "Practical", "Spiritual"],
            secondaryTraits: ["Humor", "Seriousness", "Optimism", "Pessimism", "Adventure",
                            "Comfort", "Knowledge", "Power", "Peace", "Justice"],
            motivations: ["Protect others", "Seek knowledge", "Gain power", "Find love",
                         "Avenge wrongs", "Explore the world", "Build something great",
                         "Help the needy", "Discover truth", "Achieve fame"],
            fears: ["Failure", "Loneliness", "Death", "Betrayal", "Poverty", "Insanity",
                   "Being forgotten", "Hurting others", "Losing control", "The unknown"],
            quirks: ["Always carries a lucky coin", "Speaks in rhymes", "Collects strange objects",
                    "Never lies", "Always punctual", "Hums while thinking", "Taps fingers when nervous",
                    "Quotes ancient texts", "Always has a plan", "Never gives up"]
        };

        // REF-103.2: Speech Pattern Classification
        this.speechPatterns = [
            "Formal", "Casual", "Scholarly", "Rough", "Poetic",
            "Direct", "Cryptic", "Humble", "Arrogant", "Wise"
        ];

        // REF-104.1: Background Data Structures
        this.backgroundData = {
            occupations: ["Warrior", "Scholar", "Merchant", "Artisan", "Noble",
                         "Commoner", "Criminal", "Priest", "Mage", "Explorer"],
            socialClasses: ["Noble", "Merchant", "Artisan", "Commoner", "Outcast",
                           "Slave", "Royal", "Guild Member", "Scholar", "Wanderer"],
            lifeEvents: ["Lost family", "Found treasure", "Saved someone", "Was betrayed",
                        "Learned magic", "Traveled far", "Fell in love", "Made enemy",
                        "Discovered secret", "Overcame fear"]
        };

        // REF-106.1: Base Equipment List
        this.baseEquipment = ["Clothes", "Backpack", "Rations", "Water skin"];

        // REF-106.2: Type-Specific Equipment Mapping
        this.equipmentByType = {
            [CharacterType.HERO]: ["Sword", "Shield", "Armor"],
            [CharacterType.MERCHANT]: ["Merchant's scale", "Trade goods", "Coin purse"],
            [CharacterType.GUARD]: ["Spear", "Chain mail", "Badge of office"],
            [CharacterType.SCHOLAR]: ["Books", "Writing materials", "Magnifying glass"],
            [CharacterType.NOBLE]: ["Fine clothes", "Signet ring", "Jewelry"]
        };

        // REF-107.1: Skills by Character Type
        this.skillData = {
            [CharacterType.HERO]: ["Combat", "Leadership", "Courage", "Strategy"],
            [CharacterType.NPC]: ["Local Knowledge", "Gossip", "Trade", "Survival"],
            [CharacterType.VILLAIN]: ["Deception", "Intimidation", "Strategy", "Power"],
            [CharacterType.MERCHANT]: ["Haggling", "Appraisal", "Networking", "Travel"],
            [CharacterType.GUARD]: ["Vigilance", "Combat", "Investigation", "Authority"],
            [CharacterType.NOBLE]: ["Etiquette", "Politics", "Wealth", "Influence"],
            [CharacterType.SCHOLAR]: ["Research", "Languages", "History", "Analysis"]
        };

        // REF-108.1: Spell Lists by Level
        this.spellLists = {
            basic: ["Detect Magic", "Light", "Mage Hand", "Prestidigitation"],
            combat: ["Magic Missile", "Fire Bolt", "Healing Word", "Cure Wounds"],
            utility: ["Identify", "Mage Armor", "Shield", "Feather Fall"]
        };

        // Basic character data
        this.races = [
            "Human", "Elf", "Dwarf", "Halfling", "Gnome", "Half-Orc",
            "Half-Elf", "Tiefling", "Dragonborn", "Aasimar"
        ];
        this.classes = [
            "Fighter", "Wizard", "Rogue", "Cleric", "Paladin", "Ranger",
            "Bard", "Barbarian", "Monk", "Warlock", "Sorcerer", "Druid"
        ];

        this.firstNames = ['Aria', 'Borin', 'Celia', 'Dain', 'Elena', 'Finn', 'Gwen', 'Haldor', 'Iris', 'Jax'];
        this.lastNames = ['Stormwind', 'Ironforge', 'Silverleaf', 'Goldheart', 'Shadowbane', 'Brightblade', 'Darkwood', 'Lightbringer'];
    }

    generatePersonality() {
        return {
            primaryTrait: this.getRandomItem(this.personalityData.primaryTraits),
            secondaryTrait: this.getRandomItem(this.personalityData.secondaryTraits),
            motivation: this.getRandomItem(this.personalityData.motivations),
            fear: this.getRandomItem(this.personalityData.fears),
            quirk: this.getRandomItem(this.personalityData.quirks),
            speechPattern: this.getRandomItem(this.speechPatterns)
        };
    }

    generateBackground(characterType) {
        // REF-104.2: Character Type Background Mapping
        const typeMappings = {
            [CharacterType.NOBLE]: { occupation: "Noble", socialClass: "Noble" },
            [CharacterType.MERCHANT]: { occupation: "Merchant", socialClass: "Merchant" },
            [CharacterType.GUARD]: { occupation: "Guard", socialClass: "Commoner" },
            [CharacterType.SCHOLAR]: { occupation: "Scholar", socialClass: "Scholar" }
        };

        const mapping = typeMappings[characterType] || {};
        const occupation = mapping.occupation || this.getRandomItem(this.backgroundData.occupations);
        const socialClass = mapping.socialClass || this.getRandomItem(this.backgroundData.socialClasses);

        return {
            occupation: occupation,
            socialClass: socialClass,
            lifeEvents: this.getRandomItems(this.backgroundData.lifeEvents, 1, 3),
            hometown: `${this.getRandomItem(['North', 'South', 'East', 'West'])} ${this.getRandomItem(['Village', 'Town', 'City', 'Keep'])}`,
            familyStatus: this.getRandomItem(["Orphaned", "Large family", "Only child", "Adopted", "Royal blood"])
        };
    }

    generateStats(characterType, level = 1) {
        // REF-105.1: Base Stat Calculation
        let stats = {
            strength: 10, dexterity: 10, constitution: 10,
            intelligence: 10, wisdom: 10, charisma: 10
        };

        // REF-105.2: Character Type Stat Modifiers
        const modifiers = {
            [CharacterType.HERO]: { strength: +4, charisma: +3 },
            [CharacterType.SCHOLAR]: { intelligence: +5, wisdom: +3 },
            [CharacterType.MERCHANT]: { charisma: +4, intelligence: +3 },
            [CharacterType.GUARD]: { strength: +4, constitution: +3 }
        };

        const typeMods = modifiers[characterType] || {};
        for (const [stat, bonus] of Object.entries(typeMods)) {
            stats[stat] += bonus;
        }

        // REF-105.3: Random Stat Variation
        for (const stat of ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']) {
            const adjustment = Math.floor(Math.random() * 5) - 2; // -2 to +2
            stats[stat] = Math.max(3, Math.min(20, stats[stat] + adjustment));
        }

        return stats;
    }

    generateEquipment(characterType) {
        const typeEquipment = this.equipmentByType[characterType] || [];

        return {
            baseEquipment: [...this.baseEquipment],
            typeSpecificEquipment: [...typeEquipment],
            weapons: this.getRandomItems(["Sword", "Bow", "Staff", "Dagger", "Mace"], 1, 2),
            armor: this.getRandomItems(["Leather", "Chain mail", "Plate", "Robes"], 1, 1),
            tools: this.getRandomItems(["Lockpicks", "Healer's kit", "Thieves' tools", "Alchemist's supplies"], 0, 2)
        };
    }

    generateSkills(characterType) {
        const typeSkills = this.skillData[characterType] || ["General Knowledge", "Survival"];

        return {
            combatSkills: this.getRandomItems(["Swordsmanship", "Archery", "Unarmed Combat", "Tactics"], 1, 2),
            socialSkills: this.getRandomItems(["Persuasion", "Intimidation", "Deception", "Insight"], 1, 2),
            knowledgeSkills: [...typeSkills],
            utilitySkills: this.getRandomItems(["Stealth", "Perception", "Investigation", "Athletics"], 1, 2)
        };
    }

    generateSpells(characterType, level = 1) {
        if (![CharacterType.SCHOLAR, CharacterType.HERO].includes(characterType)) {
            return { basicSpells: [], combatSpells: [], utilitySpells: [], spellLevel: 0 };
        }

        // REF-108.2: Spell Selection Algorithm
        const basicSpells = this.getRandomItems(this.spellLists.basic, 1, 2);
        let combatSpells = [];
        let utilitySpells = [];

        if (level > 1) {
            combatSpells = this.getRandomItems(this.spellLists.combat, 1, level - 1);
            utilitySpells = this.getRandomItems(this.spellLists.utility, 1, level - 1);
        }

        return {
            basicSpells: basicSpells,
            combatSpells: combatSpells,
            utilitySpells: utilitySpells,
            spellLevel: level
        };
    }

    generateCharacter(characterType = null, tone = null, level = 1) {
        if (!characterType) {
            characterType = this.getRandomItem(Object.values(CharacterType));
        }
        if (!tone) {
            tone = this.getRandomItem(Object.values(CharacterTone));
        }

        const name = `${this.getRandomItem(this.firstNames)} ${this.getRandomItem(this.lastNames)}`;

        return {
            name: name,
            characterType: characterType,
            tone: tone,
            level: level,
            race: this.getRandomItem(this.races),
            charClass: this.getRandomItem(this.classes),
            personality: this.generatePersonality(),
            background: this.generateBackground(characterType),
            stats: this.generateStats(characterType, level),
            equipment: this.generateEquipment(characterType),
            skills: this.generateSkills(characterType),
            spells: this.generateSpells(characterType, level),
            appearance: {
                age: Math.floor(Math.random() * 62) + 18, // 18-80
                height: `${Math.floor(Math.random() * 4) + 4}'${Math.floor(Math.random() * 12)}"`,
                weight: `${Math.floor(Math.random() * 200) + 100} lbs`,
                hairColor: this.getRandomItem(["Black", "Brown", "Blonde", "Red", "Gray", "White"]),
                eyeColor: this.getRandomItem(["Brown", "Blue", "Green", "Hazel", "Gray", "Amber"]),
                distinguishingFeatures: this.getRandomItem(["Scar", "Tattoo", "Piercing", "Birthmark", "Missing finger", "Limp"])
            },
            bio: `A ${characterType} ${tone} character with a ${this.generatePersonality().primaryTrait.toLowerCase()} personality.`
        };
    }

    generateMultipleCharacters(count, characterType = null) {
        const characters = [];
        for (let i = 0; i < count; i++) {
            characters.push(this.generateCharacter(characterType));
        }
        return characters;
    }

    // Utility methods
    getRandomItem(array) {
        return array[Math.floor(Math.random() * array.length)];
    }

    getRandomItems(array, min = 1, max = null) {
        if (max === null) max = min;
        const count = Math.floor(Math.random() * (max - min + 1)) + min;
        const shuffled = [...array].sort(() => 0.5 - Math.random());
        return shuffled.slice(0, Math.min(count, array.length));
    }

    // Convenience methods for MCP integration
    generateHero(level = 1) {
        return this.generateCharacter(CharacterType.HERO, CharacterTone.FANTASY, level);
    }

    generateNPC(characterType = null) {
        if (!characterType) {
            characterType = this.getRandomItem([CharacterType.MERCHANT, CharacterType.GUARD, CharacterType.SCHOLAR]);
        }
        return this.generateCharacter(characterType, CharacterTone.REALISTIC);
    }

    generateParty(size = 4) {
        return this.generateMultipleCharacters(size, CharacterType.HERO);
    }

    // Format character for display
    formatCharacterForDisplay(character) {
        return {
            name: character.name,
            race: character.race,
            class: character.charClass,
            level: character.level,
            stats: character.stats,
            personality: character.personality,
            background: character.background,
            equipment: character.equipment,
            skills: character.skills,
            spells: character.spells,
            appearance: character.appearance,
            bio: character.bio
        };
    }
}

// Export for use in HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EnhancedCharacterGenerator, CharacterType, CharacterTone };
}
