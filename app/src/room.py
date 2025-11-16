
from enum import Enum
from display_helper import DisplayHelper
from rectangle import Rectangle
from chest import Chest
from items import (
    Item, Key, Coin, Gem, Dice, Step,
    Shovel, Hammer, MetalDetector, LockPickKit, RabbitFoot,
    Apple, Banana, Cake, Sandwich, Meal
)
from renderable import Renderable
from position import Position
from typing import Optional, List
from renderer import Renderer
from app_color import (
    room_stroke_visited_color,
    room_stroke_default_color,
    door_color,
)
import random
from logging import AppLogger




class Room(Renderable):
    def __init__(
        self,
        name: str = None,
        position: Position = None,
        asset_path: str = None,
        rarity_degree: int = 1,
        display_helper=None,
    ):
        super().__init__(display_helper)
        self.name: str = name
        self.position = position
        self.asset_path = asset_path
        self.rarity_degree: int = rarity_degree
        self.has_top_door: bool = False
        self.has_bottom_door: bool = False
        self.has_left_door: bool = False
        self.has_right_door: bool = False
        self.lock_level: int = 0
        self.visited: bool = False
        self.is_locked: bool = False
        self.gem_cost: int = 0
        self.color: str = ""
        self.dug = False
        self.chest: Optional[Chest] = None
        self.has_treasure: bool = False
        self.is_target: bool = False
        self.shop: bool = False
        self.items: list = []
        self.rotation: int = 0  # Rotation angle in degrees (0, 90, 180, 270)

    @classmethod
    def from_dict(cls, room_dict: dict, position: Position = None, display_helper=None):
        """Create a Room instance from a dictionary object.

        Args:
            room_dict: Dictionary containing room data from rooms_catalogue.json
            position: Optional Position object. If None, a default position will be used.
            display_helper: DisplayHelper instance for rendering

        Returns:
            Room: A new Room instance populated with data from the dictionary
        """
        if position is None:
            position = Position(0, 0)

        room = cls(
            name=room_dict.get("name", "Unknown Room"),
            position=position,
            asset_path=room_dict.get("image", ""),
            rarity_degree=room_dict.get("rarity", 0),
            display_helper=display_helper
        )

        doors = room_dict.get("doors", {})
        room.has_top_door = doors.get("top", False)
        room.has_bottom_door = doors.get("bottom", False)
        room.has_left_door = doors.get("left", False)
        room.has_right_door = doors.get("right", False)

        room.is_locked = room_dict.get("doors_lock", False)
        room.lock_level = room_dict.get("lock_level", 0)

        room.color = room_dict.get("color", "")
        room.gem_cost = room_dict.get("gem_cost", 0)

        # Instantiate items from configuration
        items_config = room_dict.get("items", [])
        item_class_map = {
            "Coin": Coin,
            "Gem": Gem,
            "Dice": Dice,
            "Step": Step,
            "Key": Key,
            "Shovel": Shovel,
            "Hammer": Hammer,
            "MetalDetector": MetalDetector,
            "LockPickKit": LockPickKit,
            "RabbitFoot": RabbitFoot,
            "Apple": Apple,
            "Banana": Banana,
            "Cake": Cake,
            "Sandwich": Sandwich,
            "Meal": Meal,
        }

        for item_config in items_config:
            probability = item_config.get("probability", 1.0)
            if random.random() < probability:
                item_key = item_config.get("item_key")
                quantity = item_config.get("quantity", 1)

                # Get the corresponding item class
                item_class = item_class_map.get(item_key)
                if item_class:
                    room.items.append(item_class(count=quantity))

        room.special_effect = room_dict.get("special_effect", {})
        room.placement_condition = room_dict.get("placement_condition", "any")
        room.shop = room_dict.get("color", "") == "yellow"
        room.is_target = room_dict.get("name", "") == "Antechamber"

        return room


    def take_items(self) -> List[Item]:
        items = self.items.copy()
        self.items.clear()
        return items
    
    def unlock(self, key: Key) -> bool:
        if not self.is_locked and key.use():
            self.is_locked = False
            return True
        return False
    
    def render(
        self, renderer: Renderer, highlight: bool = False
    ):
        """Render the room - if rect is None, render at grid position"""
        
            
        rect = Rectangle(
            self.display_helper.MANOR_X + DisplayHelper.GRID_MARGIN + self.position.x * (self.display_helper.ROOM_SIZE + DisplayHelper.ROOM_GAP),
            DisplayHelper.GRID_MARGIN_TOP + self.position.y * (self.display_helper.ROOM_SIZE + DisplayHelper.ROOM_GAP),
            self.display_helper.ROOM_SIZE,
            self.display_helper.ROOM_SIZE,
        )

        stroke_color = room_stroke_visited_color if self.visited else room_stroke_default_color
        stroke_width = 4 if highlight else 2

        # Draw room image with rotation
        renderer.draw_image(self.asset_path, rect, rotation=self.rotation)
        renderer.draw_rectangle(rect, None, stroke_color, stroke_width)

       
        # Draw doors
        if self.has_top_door:
            door_rect = Rectangle(
                rect.x + int(rect.width * 0.375),
                rect.y - int(rect.height * 0.05),
                int(rect.width * 0.25),
                int(rect.height * 0.1),
            )
            renderer.draw_rectangle(door_rect, door_color, stroke_color, 2)

        if self.has_bottom_door:
            door_rect = Rectangle(
                rect.x + int(rect.width * 0.375),
                rect.y + int(rect.height * 0.95),
                int(rect.width * 0.25),
                int(rect.height * 0.1),
            )
            renderer.draw_rectangle(door_rect, door_color, stroke_color, 2)

        if self.has_left_door:
            door_rect = Rectangle(
                rect.x - int(rect.width * 0.05),
                rect.y + int(rect.height * 0.375),
                int(rect.width * 0.1),
                int(rect.height * 0.25),
            )
            renderer.draw_rectangle(door_rect, door_color, stroke_color, 2)

        if self.has_right_door:
            door_rect = Rectangle(
                rect.x + int(rect.width * 0.95),
                rect.y + int(rect.height * 0.375),
                int(rect.width * 0.1),
                int(rect.height * 0.25),
            )
            renderer.draw_rectangle(door_rect, door_color, stroke_color, 2)
    

    def __repr__(self):
        return f"Room(name={self.name}, position={self.position}, asset_path={self.asset_path}, rarity_degree={self.rarity_degree}, visited={self.visited}, is_locked={self.is_locked})"

    def __str__(self):
        return self.__repr__()