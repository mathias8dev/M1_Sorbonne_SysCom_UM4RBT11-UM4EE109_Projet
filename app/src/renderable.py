from abc import ABC, abstractmethod
from typing import Optional
from renderer import Renderer



class Renderable(ABC):
    """ Classe de base abstraite pour tout objet qui peut se rendre sur l'ecran. """
    def __init__(self, display_helper=None):
        self.display_helper = display_helper

    @abstractmethod
    def render(self, renderer: Renderer):
        pass



