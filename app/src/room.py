from ast import List
from enum import Enum
from chest import Chest
from items import Item, Key
from renderable import Renderable
from position import Position
from typing import Optional
from renderer import Renderer
from app.src.display_helper import Constants

class RoomColor(Enum):
    BLUE = "blue"

class Room(Renderable):
    def __init__(
        self,
        name: str,
        position: Position,
        asset_path: str,
        rarity_degree: int = 1,
    ):
        super().__init__(asset_path)
        self.name: str = name
        self.position = position
        self.rarity_degree: int = rarity_degree
        self.has_top_door: bool = False
        self.has_bottom_door: bool = False
        self.has_left_door: bool = False
        self.has_right_door: bool = False
        self.visited: bool = False
        self.is_locked: bool = False
        self.color: RoomColor = RoomColor.BLUE
        self.dug = False
        self.chest: Optional[Chest] = None
        self.has_treasure: bool = False


    def take_items(self) -> List[Item]:
        items = self.items.copy()
        self.items.clear()
        return items
    
    def unlock(self, key: Key) -> bool:
        if not self.is_locked and key.use():
            self.is_locked = False
            return True
        return False
    
    def render(self, renderer: Renderer):
        pass
    