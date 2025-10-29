"""Gemini API client with comprehensive error handling"""
from google import genai
from google.genai import types
import time
from typing import Tuple


class GeminiError(Exception):
    """Base exception for Gemini API errors"""
    pass


class QuotaExceededError(GeminiError):
    """Raised when API quota is exhausted"""
    pass


class GenerationTimeoutError(GeminiError):
    """Raised when generation takes too long"""
    pass


class GeminiClient:
    """Wrapper for Gemini API with error handling and timeout management"""

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize Gemini client

        Args:
            api_key: Gemini API key
            timeout: Maximum generation time in seconds
        """
        self.client = genai.Client(api_key=api_key)
        self.timeout = timeout

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9"
    ) -> Tuple[bytes, int]:
        """
        Generate image from prompt

        Args:
            prompt: Text description of image to generate
            aspect_ratio: Image aspect ratio (1:1, 16:9, 4:3, 9:16)
                         Note: aspect_ratio is accepted but not currently functional
                         with google-genai 0.2.2

        Returns:
            Tuple of (image_bytes, generation_time_ms)

        Raises:
            QuotaExceededError: API quota exhausted
            GenerationTimeoutError: Generation took too long
            GeminiError: Other generation failures
        """
        start = time.time()

        try:
            # Note: Simplified API call without config
            # google-genai 0.2.2 doesn't support aspect_ratio via config
            response = self.client.models.generate_content(
                model='gemini-2.5-flash-image',
                contents=[prompt]
            )

            # Extract image
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    elapsed_ms = int((time.time() - start) * 1000)
                    return part.inline_data.data, elapsed_ms

            raise GeminiError("No image in response")

        except Exception as e:
            error_msg = str(e).lower()

            # Check for quota errors
            if "429" in error_msg or "quota" in error_msg or "resource exhausted" in error_msg:
                raise QuotaExceededError("API quota exceeded") from e

            # Check for timeout
            if time.time() - start > self.timeout:
                raise GenerationTimeoutError(f"Generation timeout after {self.timeout}s") from e

            # Generic error
            raise GeminiError(f"Generation failed: {e}") from e

    def generate_text(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash"
    ) -> Tuple[str, int]:
        """
        Generate text from prompt using Gemini

        Args:
            prompt: Text prompt for generation
            model: Gemini model to use (default: gemini-2.5-flash)

        Returns:
            Tuple of (generated_text, generation_time_ms)

        Raises:
            QuotaExceededError: API quota exhausted
            GenerationTimeoutError: Generation took too long
            GeminiError: Other generation failures
        """
        start = time.time()

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=[prompt]
            )

            # Extract text from response
            text_parts = []
            for part in response.candidates[0].content.parts:
                if part.text:
                    text_parts.append(part.text)

            if not text_parts:
                raise GeminiError("No text in response")

            elapsed_ms = int((time.time() - start) * 1000)
            return "\n".join(text_parts), elapsed_ms

        except Exception as e:
            error_msg = str(e).lower()

            # Check for quota errors
            if "429" in error_msg or "quota" in error_msg or "resource exhausted" in error_msg:
                raise QuotaExceededError("API quota exceeded") from e

            # Check for timeout
            if time.time() - start > self.timeout:
                raise GenerationTimeoutError(f"Generation timeout after {self.timeout}s") from e

            # Generic error
            raise GeminiError(f"Text generation failed: {e}") from e

    def generate_character_enhancement(
        self,
        character_data: dict,
        enhancement_type: str = "full"
    ) -> Tuple[dict, int]:
        """
        Generate character enhancement using specialized prompts

        Args:
            character_data: Character data dictionary
            enhancement_type: Type of enhancement ("backstory", "personality", "quests", "full")

        Returns:
            Tuple of (enhancement_data, generation_time_ms)

        Raises:
            QuotaExceededError: API quota exhausted
            GenerationTimeoutError: Generation took too long
            GeminiError: Other generation failures
        """
        start = time.time()

        try:
            # Build specialized prompt based on enhancement type
            if enhancement_type == "backstory":
                prompt = self._build_backstory_prompt(character_data)
            elif enhancement_type == "personality":
                prompt = self._build_personality_prompt(character_data)
            elif enhancement_type == "quests":
                prompt = self._build_quest_prompt(character_data)
            else:  # full
                prompt = self._build_full_enhancement_prompt(character_data)

            # Generate text
            text_response, text_time = self.generate_text(prompt)

            # Parse response into structured data
            enhancement_data = self._parse_enhancement_response(text_response, enhancement_type)

            elapsed_ms = int((time.time() - start) * 1000)
            return enhancement_data, elapsed_ms

        except Exception as e:
            error_msg = str(e).lower()

            # Check for quota errors
            if "429" in error_msg or "quota" in error_msg or "resource exhausted" in error_msg:
                raise QuotaExceededError("API quota exceeded") from e

            # Check for timeout
            if time.time() - start > self.timeout:
                raise GenerationTimeoutError(f"Enhancement timeout after {self.timeout}s") from e

            # Generic error
            raise GeminiError(f"Character enhancement failed: {e}") from e

    def _build_backstory_prompt(self, character_data: dict) -> str:
        """Build backstory generation prompt"""
        return f"""
Create a detailed D&D character backstory for:
- Name: {character_data.get('name', 'Unknown')}
- Type: {character_data.get('character_type', 'Hero')}
- Age: {character_data.get('age', 'Unknown')}, Gender: {character_data.get('gender', 'Unknown')}
- Occupation: {character_data.get('occupation', 'Adventurer')}
- Personality: {character_data.get('primary_trait', 'Brave')}, motivated by {character_data.get('motivation', 'adventure')}
- Secret: {character_data.get('secret', 'has a mysterious past')}

Generate 3-4 rich paragraphs covering:
1. Early life and formative experiences
2. Key events that shaped their personality
3. Current situation and immediate challenges
4. Future aspirations and fears

Style: Engaging fantasy writing, character-driven narrative.
"""

    def _build_personality_prompt(self, character_data: dict) -> str:
        """Build personality analysis prompt"""
        return f"""
Analyze the personality of this D&D character:
- Name: {character_data.get('name', 'Unknown')}
- Primary Trait: {character_data.get('primary_trait', 'Brave')}
- Secondary Trait: {character_data.get('secondary_trait', 'Loyal')}
- Motivation: {character_data.get('motivation', 'adventure')}
- Fear: {character_data.get('fear', 'failure')}
- Quirk: {character_data.get('quirk', 'always punctual')}

Provide:
1. Deep personality analysis (2-3 sentences)
2. How traits interact and create conflicts
3. Character voice examples (2-3 dialogue samples)
4. Mannerisms and speech patterns
5. How they react under stress

Format as structured analysis.
"""

    def _build_quest_prompt(self, character_data: dict) -> str:
        """Build quest generation prompt"""
        return f"""
Generate personalized quest hooks for this D&D character:
- Name: {character_data.get('name', 'Unknown')}
- Motivation: {character_data.get('motivation', 'adventure')}
- Fear: {character_data.get('fear', 'failure')}
- Goals: {character_data.get('goals', 'become famous')}
- Secret: {character_data.get('secret', 'has a mysterious past')}

Create 3 quest opportunities that:
1. Connect to their personal motivations
2. Challenge their fears
3. Utilize their unique abilities
4. Create meaningful character development

Format each quest as: Title, Brief Description, Personal Connection, Potential Rewards.
"""

    def _build_full_enhancement_prompt(self, character_data: dict) -> str:
        """Build comprehensive enhancement prompt"""
        return f"""
Enhance this D&D character with rich details:

CHARACTER DATA:
- Name: {character_data.get('name', 'Unknown')}
- Type: {character_data.get('character_type', 'Hero')}
- Age: {character_data.get('age', 'Unknown')}, Gender: {character_data.get('gender', 'Unknown')}
- Occupation: {character_data.get('occupation', 'Adventurer')}
- Personality: {character_data.get('primary_trait', 'Brave')} / {character_data.get('secondary_trait', 'Loyal')}
- Motivation: {character_data.get('motivation', 'adventure')}
- Fear: {character_data.get('fear', 'failure')}
- Secret: {character_data.get('secret', 'has a mysterious past')}
- Goals: {character_data.get('goals', 'become famous')}

ENHANCEMENT REQUEST:
Provide comprehensive character enhancement including:

1. BACKSTORY (3-4 paragraphs):
   - Early life and formative experiences
   - Key events that shaped their personality
   - Current situation and immediate challenges
   - Future aspirations and fears

2. PERSONALITY INSIGHTS (2-3 sentences):
   - Deep analysis of trait interactions
   - Character development potential
   - Internal conflicts and motivations

3. CHARACTER VOICE (2-3 examples):
   - Sample dialogue showing speech patterns
   - How they express different emotions
   - Unique phrases or mannerisms

4. QUEST HOOKS (3 opportunities):
   - Personal quests connected to motivations
   - Challenges that test their fears
   - Opportunities for character growth

Format as structured sections with clear headers.
"""

    def _parse_enhancement_response(self, response_text: str, enhancement_type: str) -> dict:
        """Parse Gemini response into structured enhancement data"""
        try:
            # Simple parsing - in production, you might want more sophisticated parsing
            sections = response_text.split('\n\n')

            enhancement_data = {
                "raw_response": response_text,
                "enhancement_type": enhancement_type,
                "sections": sections
            }

            # Try to extract specific sections based on enhancement type
            if enhancement_type == "backstory":
                enhancement_data["backstory"] = response_text
            elif enhancement_type == "personality":
                enhancement_data["personality_analysis"] = response_text
            elif enhancement_type == "quests":
                enhancement_data["quest_hooks"] = response_text
            else:  # full
                # Try to parse structured sections
                enhancement_data.update(self._parse_full_enhancement(response_text))

            return enhancement_data

        except Exception as e:
            # Fallback to raw response
            return {
                "raw_response": response_text,
                "enhancement_type": enhancement_type,
                "parse_error": str(e)
            }

    def _parse_full_enhancement(self, response_text: str) -> dict:
        """Parse full enhancement response into structured sections"""
        sections = {}

        # Look for section headers
        lines = response_text.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for section headers
            if any(header in line.upper() for header in ['BACKSTORY', 'PERSONALITY', 'VOICE', 'QUEST']):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.lower().replace(':', '').replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)

        # Add final section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections
