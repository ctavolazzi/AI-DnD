"""
Pixel Art Dialogue Box

Inspired by Nano Banana Games dungeon mockup.
Features:
- NPC portrait with frame
- Typewriter text effect
- Decorative vine/leaf border
- Name label
"""

import pygame
from typing import Optional, Callable, List
from dataclasses import dataclass

try:
    from pygame_mvp.config import SCREEN_WIDTH, SCREEN_HEIGHT
    from pygame_mvp.ui.pixel_theme import (
        get_pixel_theme, PARCHMENT_LIGHT, VINE_GREEN, VINE_GREEN_DARK,
        TEXT_DARK, BANANA_YELLOW
    )
except ImportError:
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    from ui.pixel_theme import (
        get_pixel_theme, PARCHMENT_LIGHT, VINE_GREEN, VINE_GREEN_DARK,
        TEXT_DARK, BANANA_YELLOW
    )


@dataclass
class DialogueLine:
    """A single line of dialogue."""
    speaker: str
    text: str
    portrait_color: tuple = (100, 100, 180)  # Default blue for wizard


class PixelDialogueBox:
    """
    Dialogue box with NPC portrait and typewriter effect.
    
    Usage:
        dialogue = PixelDialogueBox(screen)
        dialogue.show("WIZARD", '"Watch out! This dungeon floor is slippery with... peels?"')
        
        # In game loop:
        dialogue.update()
        dialogue.render()
    """
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.theme = get_pixel_theme()
        self.visible = False
        
        # Fonts
        pygame.font.init()
        self.name_font = pygame.font.Font(None, 26)
        self.text_font = pygame.font.Font(None, 24)
        
        # Layout
        self.box_height = 140
        self.box_margin = 50
        self.box_y = SCREEN_HEIGHT - self.box_height - self.box_margin
        self.box_x = self.box_margin
        self.box_width = SCREEN_WIDTH - self.box_margin * 2
        
        self.portrait_size = 80
        self.portrait_x = self.box_x + 20
        self.portrait_y = self.box_y + 20
        
        self.text_x = self.portrait_x + self.portrait_size + 30
        self.text_y = self.box_y + 35
        self.text_width = self.box_width - self.portrait_size - 80
        
        # State
        self.speaker_name = ""
        self.full_text = ""
        self.displayed_text = ""
        self.text_index = 0
        self.typewriter_speed = 2  # characters per frame
        self.portrait_color = (100, 100, 180)
        
        # Animation
        self.frame_count = 0
        
        # Callbacks
        self.on_complete: Optional[Callable] = None
        self.on_advance: Optional[Callable] = None
    
    def show(self, speaker: str, text: str, portrait_color: tuple = None) -> None:
        """Show dialogue with typewriter effect."""
        self.visible = True
        self.speaker_name = speaker
        self.full_text = text
        self.displayed_text = ""
        self.text_index = 0
        
        if portrait_color:
            self.portrait_color = portrait_color
    
    def show_line(self, line: DialogueLine) -> None:
        """Show a DialogueLine."""
        self.show(line.speaker, line.text, line.portrait_color)
    
    def hide(self) -> None:
        """Hide the dialogue box."""
        self.visible = False
    
    def is_complete(self) -> bool:
        """Check if all text has been displayed."""
        return self.text_index >= len(self.full_text)
    
    def skip_to_end(self) -> None:
        """Skip typewriter effect and show full text."""
        self.displayed_text = self.full_text
        self.text_index = len(self.full_text)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z):
                if self.is_complete():
                    # Advance to next dialogue or close
                    if self.on_advance:
                        self.on_advance()
                    else:
                        self.hide()
                else:
                    # Skip to end
                    self.skip_to_end()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check if click is in dialogue box
                box_rect = pygame.Rect(self.box_x, self.box_y, self.box_width, self.box_height)
                if box_rect.collidepoint(event.pos):
                    if self.is_complete():
                        if self.on_advance:
                            self.on_advance()
                        else:
                            self.hide()
                    else:
                        self.skip_to_end()
                    return True
        
        return False
    
    def update(self) -> None:
        """Update typewriter effect."""
        if not self.visible:
            return
        
        self.frame_count += 1
        
        if self.text_index < len(self.full_text):
            # Add characters
            self.text_index = min(self.text_index + self.typewriter_speed, len(self.full_text))
            self.displayed_text = self.full_text[:self.text_index]
            
            # Call completion callback when done
            if self.is_complete() and self.on_complete:
                self.on_complete()
    
    def render(self) -> None:
        """Render the dialogue box."""
        if not self.visible:
            return
        
        # Draw dialogue box background
        box_rect = pygame.Rect(self.box_x, self.box_y, self.box_width, self.box_height)
        
        # Parchment background
        pygame.draw.rect(self.screen, PARCHMENT_LIGHT, box_rect, border_radius=12)
        
        # Vine border
        self._draw_vine_border(box_rect)
        
        # Portrait frame
        portrait_rect = pygame.Rect(self.portrait_x, self.portrait_y, 
                                   self.portrait_size, self.portrait_size)
        pygame.draw.rect(self.screen, (60, 40, 20), portrait_rect, border_radius=4)
        
        # Portrait inner
        inner_rect = pygame.Rect(self.portrait_x + 3, self.portrait_y + 3,
                                self.portrait_size - 6, self.portrait_size - 6)
        pygame.draw.rect(self.screen, (200, 180, 150), inner_rect, border_radius=2)
        
        # Draw simple character portrait
        self._draw_portrait(inner_rect)
        
        # Speaker name
        name_text = self.name_font.render(f"{self.speaker_name}:", True, TEXT_DARK)
        self.screen.blit(name_text, (self.text_x, self.text_y - 20))
        
        # Dialogue text (wrapped)
        self._render_text()
        
        # Continue indicator (blinking triangle)
        if self.is_complete():
            if (self.frame_count // 20) % 2 == 0:
                indicator_x = self.box_x + self.box_width - 35
                indicator_y = self.box_y + self.box_height - 25
                points = [
                    (indicator_x, indicator_y),
                    (indicator_x + 12, indicator_y + 6),
                    (indicator_x, indicator_y + 12),
                ]
                pygame.draw.polygon(self.screen, TEXT_DARK, points)
    
    def _draw_vine_border(self, rect: pygame.Rect) -> None:
        """Draw decorative vine border."""
        # Main border
        pygame.draw.rect(self.screen, VINE_GREEN, rect, 6, border_radius=12)
        pygame.draw.rect(self.screen, VINE_GREEN_DARK, rect, 3, border_radius=12)
        
        # Leaf decorations
        leaf_positions = [
            (rect.left + 30, rect.top - 5),
            (rect.right - 50, rect.top - 5),
            (rect.left + 60, rect.bottom - 15),
            (rect.right - 80, rect.bottom - 15),
        ]
        
        for lx, ly in leaf_positions:
            # Draw simple leaf
            points = [(lx, ly + 8), (lx + 10, ly), (lx + 20, ly + 8), (lx + 10, ly + 16)]
            pygame.draw.polygon(self.screen, VINE_GREEN, points)
        
        # Banana decorations
        self._draw_banana(rect.left + 120, rect.top - 8, 24)
        self._draw_banana(rect.right - 140, rect.bottom - 18, 22)
    
    def _draw_banana(self, x: int, y: int, size: int) -> None:
        """Draw a simple banana icon."""
        points = [
            (x, y + size // 3),
            (x + size // 4, y),
            (x + size * 3 // 4, y),
            (x + size, y + size // 3),
            (x + size * 3 // 4, y + size * 2 // 3),
            (x + size // 4, y + size * 2 // 3),
        ]
        pygame.draw.polygon(self.screen, BANANA_YELLOW, points)
        pygame.draw.rect(self.screen, (100, 80, 40), (x + size // 2 - 2, y - 3, 5, 6))
    
    def _draw_portrait(self, rect: pygame.Rect) -> None:
        """Draw a simple character portrait."""
        cx = rect.centerx
        cy = rect.centery
        
        # Determine portrait type by color (simple heuristic)
        r, g, b = self.portrait_color
        
        if b > r and b > g:
            # Wizard (blue)
            # Hat
            hat_points = [
                (cx - 20, cy + 10),
                (cx, cy - 30),
                (cx + 20, cy + 10),
            ]
            pygame.draw.polygon(self.screen, (60, 60, 140), hat_points)
            
            # Face
            pygame.draw.ellipse(self.screen, (200, 170, 140), 
                              (cx - 18, cy, 36, 40))
            
            # Beard
            pygame.draw.ellipse(self.screen, (200, 200, 200),
                              (cx - 15, cy + 20, 30, 30))
            
            # Eyes
            pygame.draw.circle(self.screen, (40, 40, 60), (cx - 7, cy + 10), 3)
            pygame.draw.circle(self.screen, (40, 40, 60), (cx + 7, cy + 10), 3)
            
        elif g > r and g > b:
            # Ranger/Elf (green)
            # Hair
            pygame.draw.ellipse(self.screen, (80, 60, 30),
                              (cx - 18, cy - 20, 36, 30))
            
            # Pointed ears
            pygame.draw.polygon(self.screen, (230, 190, 150),
                              [(cx - 22, cy), (cx - 30, cy - 15), (cx - 18, cy - 10)])
            pygame.draw.polygon(self.screen, (230, 190, 150),
                              [(cx + 22, cy), (cx + 30, cy - 15), (cx + 18, cy - 10)])
            
            # Face
            pygame.draw.ellipse(self.screen, (230, 190, 150),
                              (cx - 18, cy - 10, 36, 45))
            
            # Eyes
            pygame.draw.circle(self.screen, (40, 100, 40), (cx - 7, cy + 5), 3)
            pygame.draw.circle(self.screen, (40, 100, 40), (cx + 7, cy + 5), 3)
            
        else:
            # Generic NPC (default)
            # Hair
            pygame.draw.ellipse(self.screen, (100, 70, 40),
                              (cx - 20, cy - 18, 40, 30))
            
            # Face
            pygame.draw.ellipse(self.screen, (230, 190, 150),
                              (cx - 18, cy - 5, 36, 45))
            
            # Eyes
            pygame.draw.circle(self.screen, (60, 40, 30), (cx - 7, cy + 10), 3)
            pygame.draw.circle(self.screen, (60, 40, 30), (cx + 7, cy + 10), 3)
            
            # Simple smile
            pygame.draw.arc(self.screen, (60, 40, 30),
                          (cx - 8, cy + 18, 16, 10), 3.14, 0, 2)
    
    def _render_text(self) -> None:
        """Render wrapped dialogue text."""
        lines = self._wrap_text(self.displayed_text)
        
        y = self.text_y
        for line in lines[:4]:  # Max 4 lines
            text_surface = self.text_font.render(line, True, TEXT_DARK)
            self.screen.blit(text_surface, (self.text_x, y))
            y += 26
    
    def _wrap_text(self, text: str) -> List[str]:
        """Wrap text to fit width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.text_font.render(test_line, True, TEXT_DARK)
            
            if test_surface.get_width() <= self.text_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines


class DialogueSequence:
    """
    Manages a sequence of dialogue lines.
    
    Usage:
        sequence = DialogueSequence(dialogue_box)
        sequence.add_line("WIZARD", "Hello, adventurer!")
        sequence.add_line("WIZARD", "The dungeon awaits...")
        sequence.start()
    """
    
    def __init__(self, dialogue_box: PixelDialogueBox):
        self.dialogue_box = dialogue_box
        self.lines: List[DialogueLine] = []
        self.current_index = 0
        self.on_complete: Optional[Callable] = None
        
        # Hook into dialogue box
        self.dialogue_box.on_advance = self._advance
    
    def add_line(self, speaker: str, text: str, portrait_color: tuple = None) -> None:
        """Add a line to the sequence."""
        color = portrait_color or (100, 100, 180)
        self.lines.append(DialogueLine(speaker, text, color))
    
    def start(self) -> None:
        """Start the dialogue sequence."""
        self.current_index = 0
        if self.lines:
            self.dialogue_box.show_line(self.lines[0])
    
    def _advance(self) -> None:
        """Advance to the next line."""
        self.current_index += 1
        
        if self.current_index < len(self.lines):
            self.dialogue_box.show_line(self.lines[self.current_index])
        else:
            # Sequence complete
            self.dialogue_box.hide()
            if self.on_complete:
                self.on_complete()
    
    def is_active(self) -> bool:
        """Check if sequence is currently playing."""
        return self.dialogue_box.visible and self.current_index < len(self.lines)

