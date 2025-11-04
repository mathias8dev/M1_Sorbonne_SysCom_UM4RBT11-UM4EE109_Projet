from abc import ABC, abstractmethod
from typing import Optional
from renderer import Renderer



class Renderable(ABC):
    """ Classe de base abstraite pour tout objet qui peut se rendre sur l'ecran. """
    def __init__(self, asset_path : Optional[str] = None):
        self.asset_path = asset_path

    @abstractmethod
    def render(self, renderer : Renderer) : 
        pass 



