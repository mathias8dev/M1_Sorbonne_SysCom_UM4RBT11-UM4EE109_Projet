from color import Color
from position import Position
import pygame

class Renderer :
    def __init__ (self, screen) :
        self.screen = screen
    
    def display_text(self, text : str, color : Color, police : str, font_size : float, position : Position) :
        font = pygame.font.SysFont(police,font_size)
        surface = font.render(text, True, color.to_tuple())
        self.screen.blit(surface, position.to_tuple())
