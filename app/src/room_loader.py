import os
import json
from logging import AppLogger

class RoomLoader:
    """Loads and manages room data from the assets/rooms_catalogue.json file"""

    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.join(current_dir, "..", "assets", "rooms")
        self.json_path = os.path.join(current_dir, "..", "assets", "rooms_catalogue.json")

        self.room_data: dict = {}
        self._load_room_data()


    def _load_room_data(self):
        """Load room data from JSON file and populate room_data dictionary.

        The room_data dictionary is indexed by room name for easy lookup.
        Each entry contains the full room configuration dictionary.
        """
        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    rooms_list = json.load(f)

                    # Index rooms by name for quick lookup
                    for room_dict in rooms_list:
                        room_name = room_dict.get("name")
                        if room_name:
                            self.room_data[room_name] = room_dict

                    AppLogger.i(f"Loaded {len(self.room_data)} room definitions from JSON")
            else:
                AppLogger.w(f"Room catalogue not found at {self.json_path}")
        except Exception as e:
            AppLogger.w(f"Could not load room data JSON: {e}")

    def get_room_info(self, room_name: str) -> dict:
        """Get room information from JSON based on room name.

        Args:
            room_name: The name of the room to retrieve

        Returns:
            dict: Room configuration dictionary, or empty dict if not found
        """
        return self.room_data.get(room_name, {})

    def get_all_rooms(self) -> dict:
        """Get all loaded room data.

        Returns:
            dict: Dictionary of all room configurations indexed by room name
        """
        return self.room_data.copy()

    def get_rooms_by_color(self, color: str) -> list:
        """Get all rooms of a specific color.

        Args:
            color: The color to filter by (e.g., "blue", "purple", "orange")

        Returns:
            list: List of room dictionaries matching the color
        """
        return [room for room in self.room_data.values() if room.get("color") == color]

    def get_rooms_by_rarity(self, rarity: int) -> list:
        """Get all rooms of a specific rarity level.

        Args:
            rarity: The rarity level to filter by (0, 1, or 2)

        Returns:
            list: List of room dictionaries matching the rarity
        """
        return [room for room in self.room_data.values() if room.get("rarity") == rarity]

    def get_rooms_by_placement(self, placement_condition: str) -> list:
        """Get all rooms with a specific placement condition.

        Args:
            placement_condition: The placement condition (e.g., "any", "start_only", "end_only")

        Returns:
            list: List of room dictionaries matching the placement condition
        """
        return [room for room in self.room_data.values() if room.get("placement_condition") == placement_condition]

    def get_available_room_names(self, exclude_names: list = None) -> list:
        """Get list of all available room names, optionally excluding specific names.

        Args:
            exclude_names: List of room names to exclude (e.g., already used rooms)

        Returns:
            list: List of available room names
        """
        exclude_names = exclude_names or []
        return [name for name in self.room_data.keys() if name not in exclude_names]
