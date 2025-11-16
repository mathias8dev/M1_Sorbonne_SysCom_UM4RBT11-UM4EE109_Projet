from typing import Optional
from color import Color
from position import Position
import pygame
from rectangle import Rectangle
from logging import AppLogger


class Renderer:
    def __init__(self, screen: pygame.surface.Surface):
        self.screen = screen
        self._image_cache = {}  # Cache pour éviter de recharger les images à chaque frame

    def display_text(
        self, text: str, color: Color, font_size: float, position: Position, police: str = "Arial",
    ):
        font = pygame.font.SysFont(police, font_size)
        surface = font.render(text, True, color.to_rgb_tuple())
        self.screen.blit(surface, position.to_tuple())

    def draw_image(self, asset_path: str, rect: Rectangle, rotation: int = 0):
        """Draw an image with optional rotation.

        Args:
            asset_path: Path to the image file
            rect: Rectangle defining position and size
            rotation: Rotation angle in degrees (0, 90, 180, 270). Positive values rotate counter-clockwise.
        """
        # Clé de cache incluant le chemin, taille et rotation
        cache_key = (asset_path, rect.width, rect.height, rotation)
        
        if cache_key not in self._image_cache:
            # Charger et transformer l'image seulement si pas en cache
            surface = pygame.image.load(asset_path).convert_alpha()
            surface = pygame.transform.smoothscale(surface, (rect.width, rect.height))

            # Appliquer la rotation si spécifiée
            if rotation != 0:
                surface = pygame.transform.rotate(surface, rotation)
            
            # Mettre en cache
            self._image_cache[cache_key] = surface
        else:
            surface = self._image_cache[cache_key]

        self.screen.blit(surface, (rect.x, rect.y))

    def draw_rectangle(
        self, rect: Rectangle, fill_color: Optional[Color] = None, stroke_color: Optional[Color] = None,
        stroke_width: float = 0, border_radius: int = 0
    ):
        """Draw a rectangle with optional rounded corners and alpha transparency support.

        Args:
            rect: Rectangle to draw
            fill_color: Fill color with optional alpha channel
            stroke_color: Border/stroke color with optional alpha channel
            stroke_width: Border width in pixels (default: 0)
            border_radius: Corner radius in pixels (default: 0 for sharp corners)
        """
        pygame_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height)

        # Draw fill with alpha support
        if fill_color:
            if fill_color.alpha < 255:
                # Use alpha-enabled surface for transparency
                shape_surf = pygame.Surface(pygame_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(shape_surf, fill_color.to_tuple(), shape_surf.get_rect(), border_radius=border_radius)
                self.screen.blit(shape_surf, (rect.x, rect.y))
            else:
                # Direct draw for opaque colors (faster)
                pygame.draw.rect(
                    self.screen,
                    fill_color.to_rgb_tuple(),
                    pygame_rect,
                    border_radius=border_radius
                )

        # Draw stroke with alpha support
        if stroke_color and stroke_width > 0:
            if stroke_color.alpha < 255:
                # Use alpha-enabled surface for transparency
                shape_surf = pygame.Surface(pygame_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    shape_surf,
                    stroke_color.to_tuple(),
                    shape_surf.get_rect(),
                    int(stroke_width),
                    border_radius=border_radius
                )
                self.screen.blit(shape_surf, (rect.x, rect.y))
            else:
                # Direct draw for opaque colors (faster)
                pygame.draw.rect(
                    self.screen,
                    stroke_color.to_rgb_tuple(),
                    pygame_rect,
                    int(stroke_width),
                    border_radius=border_radius
                )

    def draw_overlay(self, color: Color):
        """Draw a semi-transparent overlay over the entire screen.

        Args:
            color: Color with alpha channel for transparency
        """
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(color.alpha)
        overlay.fill(color.to_rgb_tuple())
        self.screen.blit(overlay, (0, 0))

    def draw_shadow(self, rect: Rectangle, blur_radius: int = 10, shadow_color: Color = None,
                    border_radius: int = 0, offset_x: int = 0, offset_y: int = 4):
        """Draw a realistic blurred shadow effect like mobile apps (Material Design style).

        Args:
            rect: Rectangle to draw shadow for
            blur_radius: Blur radius in pixels (default: 10)
            shadow_color: Base color of the shadow (default: semi-transparent black)
            border_radius: Corner radius for rounded shadows (default: 0)
            offset_x: Horizontal shadow offset in pixels (default: 0)
            offset_y: Vertical shadow offset in pixels (default: 4, downward)
        """
        if shadow_color is None:
            shadow_color = Color(0, 0, 0, 80)

        # Réduire le nombre de couches pour améliorer les performances
        layers = min(4, max(2, blur_radius // 4))  # Moins de couches = plus rapide

        for i in range(layers, 0, -1):
            # Gaussian-like falloff: stronger near center, weaker at edges
            distance_ratio = i / layers
            spread = int(blur_radius * distance_ratio)

            # Alpha falloff: darker near the object, lighter far away
            # Using exponential falloff for more realistic shadow
            alpha_ratio = 1.0 - (distance_ratio ** 1.5)  # Exponential falloff
            layer_alpha = int(shadow_color.alpha * alpha_ratio)

            if layer_alpha < 5:  # Skip nearly invisible layers
                continue

            # Calculate layer dimensions (spreading outward)
            shadow_width = rect.width + spread * 2
            shadow_height = rect.height + spread * 2

            # Create surface for this shadow layer
            shadow_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)

            # Draw rounded rectangle on the shadow surface
            shadow_rect = pygame.Rect(0, 0, shadow_width, shadow_height)
            shadow_layer_color = (*shadow_color.to_rgb_tuple(), layer_alpha)
            pygame.draw.rect(shadow_surface, shadow_layer_color, shadow_rect, border_radius=border_radius)

            # Blit the shadow layer with offset (light source from top)
            shadow_x = rect.x - spread + offset_x
            shadow_y = rect.y - spread + offset_y
            self.screen.blit(shadow_surface, (shadow_x, shadow_y))

    def flip(self):
        pygame.display.flip()
