from size import Size
from color import Color
from rectangle import Rectangle
from typing import List
from renderer import Renderer
from renderable import Renderable

white_color = Color(255, 255, 255)
black_color = Color(0, 0, 0)


# TODO utiliser DisplayHelper
class Game(Renderable):
    def __init__(self, desktop_size: List[float]):
        super().__init__()
        self.room_size = min(90, (desktop_size[1] - 200) / 9)
        (self.width, self.height) = (min(1800, desktop_size[0] - 50), self.room_size * 9 + 5)
        self.mansion_width = self.room_size * 5 + 5
        
    
        
    def render(self, renderer: 'Renderer'):
        # Dessiner le manoir
        self._draw_mansion(renderer)
        # Dessiner l'espace de jeu
        self._draw_game_area(renderer)
        
    def _draw_mansion(self, renderer: 'Renderer'):
        renderer.draw_rectangle(Rectangle(x = 0, y = 0, width = self.mansion_width, height = self.height), fill_color=black_color)
    
    def _draw_game_area(self, renderer: 'Renderer'):
        renderer.draw_rectangle(Rectangle(x = self.mansion_width, y = 0, width = self.width - self.mansion_width, height = self.height), fill_color=white_color)

    
