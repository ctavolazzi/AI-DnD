/**
 * 🚀 Gemini API Cookbook Enhanced D&D Character Generator
 * JavaScript implementation for web interface integration
 */

class GeminiEnhancedCharacterGenerator {
    constructor(geminiClient = null) {
        this.geminiClient = geminiClient;
        this.enhancementCache = new Map();
        this.logger = {
            info: (msg, data) => console.log(`ℹ️ ${msg}`, data || ''),
            warning: (msg, data) => console.warn(`⚠️ ${msg}`, data || ''),
            error: (msg, data) => console.error(`❌ ${msg}`, data || '')
        };
    }

    /**
     * Generate AI-enhanced character using Gemini API
     * @param {Object} characterData - Base character data
     * @param {string} characterType - Type of character (hero, villain, etc.)
     * @param {string} tone - Character tone (serious, comedy, etc.)
     * @param {number} level - Character level
     * @returns {Promise<Object>} Enhanced character data
     */
    async generateAIEnhancedCharacter(characterData, characterType = 'hero', tone = 'serious', level = 1) {
        this.logger.info('🚀 Generating AI-enhanced character with Gemini');

        try {
            // Generate AI enhancement
            const aiEnhancement = await this.generateAIEnhancement(characterData, characterType, tone, level);

            // Merge with base character data
            const enhancedCharacter = {
                ...characterData,
                aiEnhanced: true,
                aiBackstory: aiEnhancement.aiBackstory,
                aiPersonalityInsights: aiEnhancement.aiPersonalityInsights,
                aiCharacterVoice: aiEnhancement.aiCharacterVoice,
                aiQuestHooks: aiEnhancement.aiQuestHooks,
                aiRelationshipDynamics: aiEnhancement.aiRelationshipDynamics,
                aiCharacterGoals: aiEnhancement.aiCharacterGoals,
                aiCharacterFlaws: aiEnhancement.aiCharacterFlaws,
                generatedAt: new Date().toISOString()
            };

            this.logger.info('✅ AI enhancement completed successfully');
            return enhancedCharacter;

        } catch (error) {
            this.logger.error('AI enhancement failed, using base character', error);
            return {
                ...characterData,
                aiEnhanced: false,
                error: error.message
            };
        }
    }

    /**
     * Generate AI enhancement using Gemini API
     * @param {Object} characterData - Base character data
     * @param {string} characterType - Type of character
     * @param {string} tone - Character tone
     * @param {number} level - Character level
     * @returns {Promise<Object>} AI enhancement data
     */
    async generateAIEnhancement(characterData, characterType, tone, level) {
        if (!this.geminiClient) {
            this.logger.warning('No Gemini client available, using fallback enhancement');
            return this.createFallbackEnhancement();
        }

        // Create cache key
        const cacheKey = `${characterData.name}_${characterData.charClass}_${characterData.race}`;

        if (this.enhancementCache.has(cacheKey)) {
            this.logger.info(`Using cached enhancement for ${characterData.name}`);
            return this.enhancementCache.get(cacheKey);
        }

        const prompt = `
Generate a comprehensive AI enhancement for this D&D character:

Character Details:
- Name: ${characterData.name || 'Unknown'}
- Class: ${characterData.charClass || 'Adventurer'}
- Race: ${characterData.race || 'Human'}
- Level: ${level}
- Background: ${characterData.background || 'Unknown'}
- Stats: ${JSON.stringify(characterData.abilityScores || {})}

Please provide a JSON response with the following structure:
{
    "aiBackstory": "A rich, detailed 3-4 paragraph backstory that explains how this character came to be, their motivations, and key life events that shaped them.",
    "aiPersonalityInsights": "Deep analysis of how their stats and class interact to create unique personality traits and behavioral patterns.",
    "aiCharacterVoice": "Specific examples of how this character speaks, including dialogue samples and speech patterns.",
    "aiQuestHooks": ["Quest hook 1", "Quest hook 2", "Quest hook 3"],
    "aiRelationshipDynamics": "How this character interacts with others, their social patterns, and relationship tendencies.",
    "aiCharacterGoals": ["Primary goal", "Secondary goal", "Personal goal"],
    "aiCharacterFlaws": ["Flaw 1", "Flaw 2", "Hidden weakness"]
}

Make the content rich, detailed, and suitable for D&D roleplay. Focus on creating depth and complexity that will make this character memorable and engaging.
        `;

        try {
            // Call Gemini API
            const response = await this.geminiClient.generateContent({
                model: 'gemini-2.5-flash',
                contents: [{ parts: [{ text: prompt }] }]
            });

            this.logger.info(`Gemini response received: ${response.text?.length || 0} characters`);

            // Extract JSON from response
            const responseText = response.text || '';
            const jsonStart = responseText.indexOf('{');
            const jsonEnd = responseText.lastIndexOf('}') + 1;

            if (jsonStart !== -1 && jsonEnd !== -1) {
                const jsonText = responseText.substring(jsonStart, jsonEnd);
                const enhancementData = JSON.parse(jsonText);

                const enhancement = {
                    aiBackstory: enhancementData.aiBackstory || '',
                    aiPersonalityInsights: enhancementData.aiPersonalityInsights || '',
                    aiCharacterVoice: enhancementData.aiCharacterVoice || '',
                    aiQuestHooks: enhancementData.aiQuestHooks || [],
                    aiRelationshipDynamics: enhancementData.aiRelationshipDynamics || '',
                    aiCharacterGoals: enhancementData.aiCharacterGoals || [],
                    aiCharacterFlaws: enhancementData.aiCharacterFlaws || []
                };

                // Cache the enhancement
                this.enhancementCache.set(cacheKey, enhancement);
                return enhancement;
            } else {
                this.logger.warning('Could not extract JSON from Gemini response');
                return this.createFallbackEnhancement();
            }

        } catch (error) {
            this.logger.error('Error calling Gemini API', error);
            return this.createFallbackEnhancement();
        }
    }

    /**
     * Create fallback enhancement when AI is unavailable
     * @returns {Object} Fallback enhancement data
     */
    createFallbackEnhancement() {
        return {
            aiBackstory: "A mysterious character with a hidden past that drives their current motivations. Their journey has been marked by both triumph and tragedy, shaping them into the person they are today.",
            aiPersonalityInsights: "Their stats suggest a balanced approach to challenges, adapting their strategy based on the situation. They show wisdom in their decisions and courage in their actions.",
            aiCharacterVoice: "Speaks with measured words, choosing their phrases carefully. When passionate about a topic, their speech becomes more animated and expressive.",
            aiQuestHooks: ["Seeking answers about their past", "Protecting those they care about", "Mastering their abilities"],
            aiRelationshipDynamics: "Forms deep bonds with those who earn their trust, but remains guarded with strangers. Values loyalty above all else.",
            aiCharacterGoals: ["Uncover their true purpose", "Become stronger", "Find their place in the world"],
            aiCharacterFlaws: ["Trusts too easily", "Fear of failure", "Stubbornness"]
        };
    }

    /**
     * Generate character portrait using Gemini Image generation
     * @param {Object} characterData - Character data
     * @returns {Promise<string|null>} Portrait URL or null
     */
    async generateCharacterPortrait(characterData) {
        if (!this.geminiClient) {
            this.logger.warning('No Gemini client available for image generation');
            return null;
        }

        try {
            const portraitPrompt = `
Create a detailed fantasy character portrait for:
- Name: ${characterData.name || 'Unknown'}
- Class: ${characterData.charClass || 'Adventurer'}
- Race: ${characterData.race || 'Human'}
- Level: ${characterData.level || 1}

Style: D&D fantasy art, detailed, professional, high quality
Include: Character equipment, appropriate fantasy setting, detailed facial features
            `;

            // Note: This would use Gemini Image generation when available
            // For now, return a placeholder
            this.logger.info('Character portrait generation requested');
            return 'placeholder_portrait_url';

        } catch (error) {
            this.logger.error('Error generating character portrait', error);
            return null;
        }
    }

    /**
     * Generate personalized quests based on character backstory and goals
     * @param {Object} characterData - Character data
     * @returns {Promise<Array>} Array of quest objects
     */
    async generateCharacterQuests(characterData) {
        if (!this.geminiClient) {
            this.logger.warning('No Gemini client available for quest generation');
            return [];
        }

        try {
            const questPrompt = `
Based on this D&D character's details, generate 3 unique quests:

Character: ${characterData.name || 'Unknown'}
Class: ${characterData.charClass || 'Adventurer'}
Race: ${characterData.race || 'Human'}
Level: ${characterData.level || 1}
Goals: ${JSON.stringify(characterData.aiCharacterGoals || [])}
Flaws: ${JSON.stringify(characterData.aiCharacterFlaws || [])}

Generate quests that:
1. Connect to their personal goals
2. Challenge their fears and flaws
3. Utilize their class abilities
4. Create meaningful character development

Return as JSON array with quest objects containing:
- title: Quest name
- description: Quest details
- objectives: List of objectives
- rewards: Potential rewards
- difficulty: Easy/Medium/Hard
- questHook: How it connects to character
            `;

            const response = await this.geminiClient.generateContent({
                model: 'gemini-2.5-flash',
                contents: [{ parts: [{ text: questPrompt }] }]
            });

            // Parse quest response
            const responseText = response.text || '';
            const jsonStart = responseText.indexOf('[');
            const jsonEnd = responseText.lastIndexOf(']') + 1;

            if (jsonStart !== -1 && jsonEnd !== -1) {
                const jsonText = responseText.substring(jsonStart, jsonEnd);
                return JSON.parse(jsonText);
            } else {
                this.logger.warning('Could not parse quest response from Gemini');
                return [];
            }

        } catch (error) {
            this.logger.error('Error generating character quests', error);
            return [];
        }
    }

    /**
     * Generate character story using Gemini's storytelling capabilities
     * @param {Object} characterData - Character data
     * @param {string} storyType - Type of story (origin, adventure, etc.)
     * @returns {Promise<string>} Generated story
     */
    async generateCharacterStory(characterData, storyType = 'origin') {
        if (!this.geminiClient) {
            this.logger.warning('No Gemini client available for story generation');
            return 'Story generation requires Gemini API access.';
        }

        try {
            const storyPrompt = `
Write a compelling ${storyType} story for this D&D character:

Character: ${characterData.name || 'Unknown'}
Class: ${characterData.charClass || 'Adventurer'}
Race: ${characterData.race || 'Human'}
Background: ${characterData.background || 'Unknown'}
Backstory: ${characterData.aiBackstory || 'Unknown'}

Create a narrative that:
1. Captures the character's personality and motivations
2. Includes vivid descriptions and dialogue
3. Shows character growth and development
4. Fits the D&D fantasy setting
5. Is engaging and memorable

Write in third person narrative style, 2-3 paragraphs long.
            `;

            const response = await this.geminiClient.generateContent({
                model: 'gemini-2.5-flash',
                contents: [{ parts: [{ text: storyPrompt }] }]
            });

            return response.text || 'Story generation failed.';

        } catch (error) {
            this.logger.error('Error generating character story', error);
            return 'Story generation encountered an error.';
        }
    }

    /**
     * Clear enhancement cache
     */
    clearCache() {
        this.enhancementCache.clear();
        this.logger.info('Enhancement cache cleared');
    }

    /**
     * Get cache statistics
     * @returns {Object} Cache statistics
     */
    getCacheStats() {
        return {
            size: this.enhancementCache.size,
            keys: Array.from(this.enhancementCache.keys())
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GeminiEnhancedCharacterGenerator;
}

// Example usage
async function testGeminiEnhancedGenerator() {
    console.log('🚀 Testing Gemini Enhanced Character Generator');

    // Initialize generator (without Gemini client for testing)
    const generator = new GeminiEnhancedCharacterGenerator();

    // Test character data
    const testCharacter = {
        name: 'Aria Shadowbane',
        charClass: 'Rogue',
        race: 'Elf',
        level: 5,
        background: 'Criminal',
        abilityScores: {
            strength: 12,
            dexterity: 18,
            constitution: 14,
            intelligence: 16,
            wisdom: 15,
            charisma: 13
        }
    };

    // Generate enhanced character
    const enhancedCharacter = await generator.generateAIEnhancedCharacter(testCharacter);
    console.log('Generated character:', enhancedCharacter.name);
    console.log('AI Enhanced:', enhancedCharacter.aiEnhanced);

    // Test quest generation
    const quests = await generator.generateCharacterQuests(enhancedCharacter);
    console.log(`Generated ${quests.length} quests for character`);

    // Test story generation
    const story = await generator.generateCharacterStory(enhancedCharacter, 'origin');
    console.log('Generated story length:', story.length);
}

// Run test if this file is executed directly
if (typeof window === 'undefined') {
    testGeminiEnhancedGenerator().catch(console.error);
}