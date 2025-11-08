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

    

    def generate_room_pool(self, count: int = 3) -> List[Room]:
        """Generate a pool of random rooms with weighted selection by rarity.

        Rarity distribution:
        - Rarity 0: 50% probability
        - Rarity 1: 35% probability
        - Rarity 2: 15% probability

        Args:
            count: Number of rooms to generate in the pool

        Returns:
            List of Room instances with weighted random selection
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
                pool_rooms[-1] = Room.from_dict(random.choice(free_rooms), position=None, display_helper=self.display_helper)

        return pool_rooms

    

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

        
        self.rooms[antechamber_y][antechamber_x] = antechamber
        self.used_room_names.add(antechamber.name)

        AppLogger.i(f"Map initialized:")
        AppLogger.i(f"  - {entrance_hall.name} at position ({entrance_x}, {entrance_y})")
        AppLogger.i(f"  - {antechamber.name} at position ({antechamber_x}, {antechamber_y})")



    def get_room(self, position: Position) -> Optional[Room]:
        if 0 <= position.y < self.height and 0 <= position.x < self.width:
            return self.rooms[position.y][position.x]
        return None
