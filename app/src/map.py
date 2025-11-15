import random
from typing import Optional, List
from items import *
from room import Room
from position import Position
from chest import Chest
import os

from room_loader import RoomLoader
from display_helper import DisplayHelper
from logging import AppLogger

class Map:
    def __init__(
        self, width: int = 5, height: int = 9, room_loader: Optional[RoomLoader] = None,
        display_helper=None
    ):
        self.width = width
        self.height = height
        self.rooms: List[List[Optional[Room]]] = []
        self.room_pool: List[Room] = []
        self.used_room_names: set = set()  # Track used room names to prevent duplicates
        self.room_loader = room_loader if room_loader else RoomLoader()
        self.display_helper = display_helper

    

    def generate_room_pool(self, count: int = 3, required_door: str = None) -> List[Room]:
        """Generate a pool of random rooms with weighted selection by rarity.

        Rarity distribution:
        - Rarity 0: 50% probability
        - Rarity 1: 35% probability
        - Rarity 2: 15% probability

        Args:
            count: Number of rooms to generate in the pool
            required_door: The door position needed for entry ("top", "bottom", "left", "right")

        Returns:
            List of Room instances with weighted random selection and appropriate rotation
        """
        pool_rooms = []

        # Get room names already in the pool
        pool_room_names = {room.name for room in self.room_pool}

        # Separate available rooms by rarity
        rarity_0_rooms = []
        rarity_1_rooms = []
        rarity_2_rooms = []

        for room_name, room_dict in self.room_loader.get_all_rooms().items():
            if (room_name not in self.used_room_names and
                room_name not in pool_room_names and
                room_dict.get("placement_condition") in ["any", None]):

                rarity = room_dict.get("rarity", 0)
                if rarity == 0:
                    rarity_0_rooms.append(room_dict)
                elif rarity == 1:
                    rarity_1_rooms.append(room_dict)
                elif rarity == 2:
                    rarity_2_rooms.append(room_dict)

        # Generate rooms with weighted selection
        for _ in range(count):
            rand_value = random.random()
            selected_room_dict = None

            if rand_value < 0.50 and rarity_0_rooms:  # 50% for rarity 0
                selected_room_dict = random.choice(rarity_0_rooms)
            elif rand_value < 0.85 and rarity_1_rooms:  # 35% for rarity 1
                selected_room_dict = random.choice(rarity_1_rooms)
            elif rarity_2_rooms:  # 15% for rarity 2
                selected_room_dict = random.choice(rarity_2_rooms)
            else:
                # Fallback: pick from any available
                all_available = rarity_0_rooms + rarity_1_rooms + rarity_2_rooms
                if all_available:
                    selected_room_dict = random.choice(all_available)

            if selected_room_dict:
                room = Room.from_dict(selected_room_dict, position=None, display_helper=self.display_helper)

                # Apply rotation if required_door is specified
                if required_door:
                    rotation = self._calculate_room_rotation(room, required_door)
                    room.rotation = rotation
                    # Apply rotation to door positions
                    self._apply_rotation_to_doors(room, rotation)

                pool_rooms.append(room)
                pool_room_names.add(room.name)

                # Remove from available lists to prevent duplicates
                if selected_room_dict in rarity_0_rooms:
                    rarity_0_rooms.remove(selected_room_dict)
                elif selected_room_dict in rarity_1_rooms:
                    rarity_1_rooms.remove(selected_room_dict)
                elif selected_room_dict in rarity_2_rooms:
                    rarity_2_rooms.remove(selected_room_dict)

        # Ensure at least one room with gem_cost = 0
        has_free_room = any(room.gem_cost == 0 for room in pool_rooms)
        if not has_free_room and pool_rooms:
            # Replace last room with a free one if possible
            free_rooms = [r for r in rarity_0_rooms + rarity_1_rooms + rarity_2_rooms
                         if r.get("gem_cost", 0) == 0]
            if free_rooms:
                last_room = Room.from_dict(random.choice(free_rooms), position=None, display_helper=self.display_helper)
                if required_door:
                    rotation = self._calculate_room_rotation(last_room, required_door)
                    last_room.rotation = rotation
                    self._apply_rotation_to_doors(last_room, rotation)
                pool_rooms[-1] = last_room

        return pool_rooms

    def _calculate_room_rotation(self, room: Room, required_door: str) -> int:
        """Calculate rotation needed to align a room's door with required position.

        Args:
            room: The Room instance
            required_door: The door position needed ("top", "bottom", "left", "right")

        Returns:
            Rotation angle in degrees (0, 90, 180, 270)
        """
        # First check: does the room already have the required door? If yes, no rotation needed!
        if required_door == "top" and room.has_top_door:
            return 0
        elif required_door == "bottom" and room.has_bottom_door:
            return 0
        elif required_door == "left" and room.has_left_door:
            return 0
        elif required_door == "right" and room.has_right_door:
            return 0

        # Room doesn't have the required door, find which door it has
        room_door = None
        if room.has_top_door:
            room_door = "top"
        elif room.has_bottom_door:
            room_door = "bottom"
        elif room.has_left_door:
            room_door = "left"
        elif room.has_right_door:
            room_door = "right"

        if not room_door:
            return 0  # No doors to rotate

        # Map: (current_door, required_door) -> rotation (counter-clockwise)
        rotation_map = {
            ("top", "top"): 0,
            ("top", "right"): 270,
            ("top", "bottom"): 180,
            ("top", "left"): 90,
            ("bottom", "top"): 180,
            ("bottom", "right"): 90,
            ("bottom", "bottom"): 0,
            ("bottom", "left"): 270,
            ("left", "top"): 270,
            ("left", "right"): 180,
            ("left", "bottom"): 90,
            ("left", "left"): 0,
            ("right", "top"): 90,
            ("right", "right"): 0,
            ("right", "bottom"): 270,
            ("right", "left"): 180,
        }

        return rotation_map.get((room_door, required_door), 0)

    def _apply_rotation_to_doors(self, room: Room, rotation: int):
        """Transform door positions based on rotation angle.

        Args:
            room: The Room instance to modify
            rotation: Rotation angle in degrees (0, 90, 180, 270)
        """
        if rotation == 0:
            return  # No rotation needed

        # Store original door states
        orig_top = room.has_top_door
        orig_bottom = room.has_bottom_door
        orig_left = room.has_left_door
        orig_right = room.has_right_door

        # Apply rotation transformation
        if rotation == 90:  # Counter-clockwise
            # top -> left, left -> bottom, bottom -> right, right -> top
            room.has_top_door = orig_right
            room.has_left_door = orig_top
            room.has_bottom_door = orig_left
            room.has_right_door = orig_bottom
        elif rotation == 180:
            # top -> bottom, bottom -> top, left -> right, right -> left
            room.has_top_door = orig_bottom
            room.has_bottom_door = orig_top
            room.has_left_door = orig_right
            room.has_right_door = orig_left
        elif rotation == 270:  # Counter-clockwise (or 90 clockwise)
            # top -> right, right -> bottom, bottom -> left, left -> top
            room.has_top_door = orig_left
            room.has_right_door = orig_top
            room.has_bottom_door = orig_right
            room.has_left_door = orig_bottom

    

    def place_room(self, room: Room, position: Position) -> bool:
        """Place a room on the map at the specified position.

        Args:
            room: The Room instance to place
            position: The position where to place the room

        Returns:
            bool: True if room was placed successfully, False otherwise
        """
        if not (0 <= position.x < self.width and 0 <= position.y < self.height):
            return False

        if self.rooms[position.y][position.x] is not None:
            return False

        # Update room position
        room.position = position

        # Place room on map
        self.rooms[position.y][position.x] = room

        # Mark room as used
        self.used_room_names.add(room.name)

        return True



    def generate_map_progressive(self):
        """Generate map progressively - grid with starting room (Entrance Hall) and ending room (Antechamber).
        Entrance Hall at bottom center, Antechamber at top."""
        # Initialize grid with None values
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(None)
            self.rooms.append(row)

        # Starting position: ENTRANCE HALL at bottom center
        entrance_x = 2
        entrance_y = 8  

        # Get Entrance Hall room from catalogue
        entrance_dict = self.room_loader.get_room_info("Entrance Hall")

        if not entrance_dict:
            AppLogger.w("Entrance Hall not found in catalogue")
            return

        # Create starting room using from_dict
        entrance_hall = Room.from_dict(
            entrance_dict,
            position=Position(entrance_x, entrance_y),
            display_helper=self.display_helper
        )
        entrance_hall.visited = True
        

       
        # Place the starting room
        self.rooms[entrance_y][entrance_x] = entrance_hall
        self.used_room_names.add(entrance_hall.name)

        # Ending position: ANTECHAMBER near top center
        antechamber_x = 2
        antechamber_y = 0 

        # Get Antechamber room from catalogue using room_loader
        antechamber_dict = self.room_loader.get_room_info("Antechamber")

        if not antechamber_dict:
            AppLogger.w("Antechamber not found in catalogue")
            return

        # Create ending room using from_dict
        antechamber = Room.from_dict(
            antechamber_dict,
            position=Position(antechamber_x, antechamber_y),
            display_helper=self.display_helper
        )

        # The Antechamber's door locks will be initialized by Game._initialize_door_locks
        # Since it's at row 0, its doors will have lock_level = 2 (highest difficulty)

        self.rooms[antechamber_y][antechamber_x] = antechamber
        self.used_room_names.add(antechamber.name)

        AppLogger.i(f"Map initialized:")
        AppLogger.i(f"  - {entrance_hall.name} at position ({entrance_x}, {entrance_y})")
        AppLogger.i(f"  - {antechamber.name} at position ({antechamber_x}, {antechamber_y})")



    def get_room(self, position: Position) -> Optional[Room]:
        if 0 <= position.y < self.height and 0 <= position.x < self.width:
            return self.rooms[position.y][position.x]
        return None
