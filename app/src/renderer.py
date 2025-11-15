from typing import Optional
from color import Color
from position import Position
import pygame
from rectangle import Rectangle
from logging import AppLogger


class Renderer:
    def __init__(self, screen: pygame.surface.Surface):
        self.screen = screen

    def display_text(
        self, text: str, color: Color, font_size: float, position: Position, police: str = "Arial", 
    ):
        font = pygame.font.SysFont(police, font_size)
        surface = font.render(text, True, color.to_tuple())
        self.screen.blit(surface, position.to_tuple())

    def draw_image(self, asset_path: str, rect: Rectangle, rotation: int = 0):
        """Draw an image with optional rotation.

        Args:
            asset_path: Path to the image file
            rect: Rectangle defining position and size
            rotation: Rotation angle in degrees (0, 90, 180, 270). Positive values rotate counter-clockwise.
        """
        surface = pygame.image.load(asset_path).convert_alpha()
        surface = pygame.transform.smoothscale(surface, (rect.width, rect.height))

        # Apply rotation if specified
        if rotation != 0:
            surface = pygame.transform.rotate(surface, rotation)

        self.screen.blit(surface, (rect.x, rect.y))

    def draw_rectangle(
        self, rect: Rectangle, fill_color: Optional[Color] = None, stroke_color: Optional[Color]=None, stroke_width: float = 0
    ):
        AppLogger.d(f"Drawing rectangle at {rect} with fill color {fill_color} and stroke color {stroke_color} and stroke width {stroke_width}")
        pygame_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height)
        if fill_color:
            AppLogger.d(f"Filling rectangle with color {fill_color}")
            pygame.draw.rect(
                self.screen,
                fill_color.to_tuple(),
                pygame_rect,
            )
        if stroke_color and stroke_width > 0:
            AppLogger.d(f"Drawing rectangle stroke with color {stroke_color} and width {stroke_width}")
            pygame.draw.rect(
                self.screen,
                stroke_color.to_tuple(),
                pygame_rect,
                int(stroke_width),
            )
        
    def flip(self):
        pygame.display.flip()
