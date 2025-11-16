from typing import List, Optional
from renderer import Renderer
from renderable import Renderable
from map import Map
from player import Player, InventoryKey
from position import Position
from game_state import GameState
from room import Room
from logging import AppLogger
from game_renderer import GameRenderer
from input_handler import InputHandler
from room_interaction_handler import RoomInteractionHandler


class Game(Renderable):
    def __init__(self, display_helper=None):
        super().__init__(display_helper=display_helper)

        # Initialize map and player
        self.map = Map(width=5, height=9, display_helper=display_helper)
        self.map.generate_map_progressive()

        # Player starts at Entrance Hall position (2, 8)
        self.player = Player(position=Position(2, 8))

        # Mark starting room as visited
        entrance_room = self.map.get_room(self.player.position)
        if entrance_room:
            entrance_room.visited = True

        # Initialize door locks for all pre-placed rooms
        for y in range(self.map.height):
            for x in range(self.map.width):
                room = self.map.rooms[y][x]
                if room:
                    self._initialize_door_locks(room)

        # Game state
        self.game_state = GameState.ENTER_ROOM
        self.room_pool: List[Room] = []
        self.selected_room_index: int = 0
        self.selected_direction: Optional[str] = None  # "top", "bottom", "left", "right"
        self.pending_room_position: Optional[Position] = None
        self.status_message: Optional[str] = None  # Message to display in game area
        # Initialize handlers
        self.game_renderer = GameRenderer(self)
        self.input_handler = InputHandler(self)
        self.room_interaction_handler = RoomInteractionHandler(self)

    def get_current_room(self) -> Optional[Room]:
        """Get the room at the player's current position."""
        return self.map.get_room(self.player.position)

    def _restart_game(self):
        """Restart the game by resetting all game state."""
        # Reinitialize map and player
        self.map = Map(width=5, height=9, display_helper=self.display_helper)
        self.map.generate_map_progressive()

        # Reset player to starting position
        self.player = Player(position=Position(2, 8))

        # Mark starting room as visited
        entrance_room = self.map.get_room(self.player.position)
        if entrance_room:
            entrance_room.visited = True

        # Initialize door locks for all pre-placed rooms
        for y in range(self.map.height):
            for x in range(self.map.width):
                room = self.map.rooms[y][x]
                if room:
                    self._initialize_door_locks(room)

        # Reset game state
        self.game_state = GameState.ENTER_ROOM
        self.room_pool = []
        self.selected_room_index = 0
        self.selected_direction = None
        self.pending_room_position = None
        self.status_message = None
        # Initialize handlers
        self.game_renderer = GameRenderer(self)
        self.input_handler = InputHandler(self)
        self.room_interaction_handler = RoomInteractionHandler(self)

        AppLogger.i("Game restarted!")

    def check_win_condition(self) -> bool:
        """Check if the player has reached the Antechamber."""
        current_room = self.get_current_room()
        return current_room and current_room.is_target

    def check_lose_condition(self) -> bool:
        """Check if the player has lost (no more steps or no path to victory).

        According to the game rules, there are two ways to lose:
        1. The player has exhausted their step count (0 steps)
        2. The player cannot progress: no door can lead to the Antechamber,
           OR all doors require a key and the player has none.
        """
        # Check if already at target (not a lose condition)
        current_room = self.get_current_room()
        if current_room and current_room.is_target:
            return False

        # Condition 1: Out of steps (player loses immediately)
        if self.player.inventory[InventoryKey.STEP].count <= 0:
            return True

        # Condition 2: No possible path to Antechamber (player is stuck)
        if not self._has_path_to_victory():
            return True

        return False

    def _has_path_to_victory(self) -> bool:
        """Check if there's still a possible path to the Antechamber.

        According to the rules: player loses if no door can lead to arrival,
        OR all doors require a key and player has none.

        IMPORTANT: ALL movements cost 1 step (including returning to visited rooms).

        This checks if from current position, considering:
        - All movements cost 1 step
        - Keys needed to unlock doors
        - Gems available to place new rooms

        Returns:
            True if Antechamber is reachable, False otherwise
        """
        from collections import deque

        current_pos = self.player.position
        current_room = self.get_current_room()

        if not current_room:
            return False

        # If already at Antechamber
        if current_room.is_target:
            return True

        has_lockpick = self.player.has_item(InventoryKey.LOCK_PICK_KIT)

        # BFS to find path to Antechamber through existing rooms
        # State: (position, keys_left, steps_left)
        # ALL movements cost 1 step
        visited = set()
        queue = deque([(current_pos,
                       self.player.inventory[InventoryKey.KEY].count,
                       self.player.inventory[InventoryKey.STEP].count)])
        visited.add((current_pos.x, current_pos.y,
                    self.player.inventory[InventoryKey.KEY].count,
                    self.player.inventory[InventoryKey.STEP].count))

        # Track if we found any empty spaces where we could potentially place rooms
        found_placeable_space = False

        while queue:
            pos, keys_left, steps_left = queue.popleft()

            # Get room at this position
            room = self.map.get_room(pos)
            if not room:
                continue

            # Check all four directions
            directions = [
                ("top", -1, 0, room.has_top_door),
                ("bottom", 1, 0, room.has_bottom_door),
                ("left", 0, -1, room.has_left_door),
                ("right", 0, 1, room.has_right_door),
            ]

            for direction_name, dy, dx, has_door in directions:
                if not has_door:
                    continue

                new_x = pos.x + dx
                new_y = pos.y + dy

                # Check boundaries
                if not (0 <= new_x < self.map.width and 0 <= new_y < self.map.height):
                    continue

                # Check the next room to determine effective lock level
                next_room = self.map.get_room(Position(new_x, new_y))

                # Determine effective lock level (max of source and destination)
                source_lock_level = room.lock_level
                if next_room:
                    # Room exists - use max of both lock levels
                    effective_lock_level = max(source_lock_level, next_room.lock_level)
                else:
                    # Empty space - only source lock level applies
                    effective_lock_level = source_lock_level

                # Check if we can unlock this door
                keys_needed = 0
                can_pass = False

                if effective_lock_level == 0:
                    can_pass = True
                elif effective_lock_level == 1:
                    # Can use key or lockpick
                    if has_lockpick:
                        can_pass = True
                    elif keys_left > 0:
                        can_pass = True
                        keys_needed = 1
                elif effective_lock_level == 2:
                    # Can only use key
                    if keys_left > 0:
                        can_pass = True
                        keys_needed = 1

                if not can_pass:
                    continue

                new_keys = keys_left - keys_needed

                # ALL movements cost 1 step (rule from PDF)
                new_steps = steps_left - 1

                # Can't proceed if we don't have enough steps
                if new_steps < 0:
                    continue

                if next_room:
                    # Room exists - can we move there?
                    # Check if already visited this state
                    state = (new_x, new_y, new_keys, new_steps)
                    if state in visited:
                        continue

                    visited.add(state)

                    # Check if it's the target
                    if next_room.is_target:
                        return True  # Found path to Antechamber!

                    # Continue exploring from this room
                    queue.append((Position(new_x, new_y), new_keys, new_steps))
                else:
                    # Empty space - check if player can afford to place a room here
                    player_gems = self.player.inventory[InventoryKey.GEM].count

                    # Check if there are any available rooms to place
                    available_rooms = self.map.generate_room_pool(count=3)
                    affordable_rooms = [r for r in available_rooms if r.gem_cost <= player_gems]

                    if affordable_rooms:
                        # Player could potentially place a room here
                        found_placeable_space = True
                        # Don't return yet - continue exploring to find all possible paths

        # After exploring all paths through existing rooms:
        # If we found at least one empty space where we can afford to place a room,
        # then we're not stuck yet - the player could potentially find keys or resources
        if found_placeable_space:
            return True

        # If BFS found no direct path, but player still has resources,
        # they might find keys/items in future rooms
        # Only declare "no path" if player is truly stuck (no steps OR no placement options)
        player_steps = self.player.inventory[InventoryKey.STEP].count
        if player_steps > 0:
            # Player has steps - they might still find a way
            # Don't prematurely declare game over
            return True

        return False  # No path found and no steps to continue exploring

    def render(self, renderer: 'Renderer'):
        """Delegate rendering to GameRenderer."""
        self.game_renderer.render(renderer)









    def handle_keyboard_event(self, event):
        """Delegate keyboard input handling to InputHandler."""
        self.input_handler.handle_keyboard_event(event)



    def _attempt_move(self):
        """Attempt to move in the selected direction."""
        current_room = self.get_current_room()
        if not current_room or not self.selected_direction:
            return

        # Check if there's a door in the selected direction
        has_door = False
        new_position = None
        source_lock_level = 0

        if self.selected_direction == "top" and current_room.has_top_door:
            has_door = True
            source_lock_level = current_room.lock_level
            new_position = Position(self.player.position.x, self.player.position.y - 1)
        elif self.selected_direction == "bottom" and current_room.has_bottom_door:
            has_door = True
            source_lock_level = current_room.lock_level
            new_position = Position(self.player.position.x, self.player.position.y + 1)
        elif self.selected_direction == "left" and current_room.has_left_door:
            has_door = True
            source_lock_level = current_room.lock_level
            new_position = Position(self.player.position.x - 1, self.player.position.y)
        elif self.selected_direction == "right" and current_room.has_right_door:
            has_door = True
            source_lock_level = current_room.lock_level
            new_position = Position(self.player.position.x + 1, self.player.position.y)

        if not has_door:
            AppLogger.w("No door in that direction")
            self.status_message = "No door in that direction"
            self.selected_direction = None
            return

        # Check boundaries
        if not (0 <= new_position.x < self.map.width and 0 <= new_position.y < self.map.height):
            AppLogger.w("Can't go outside the manor!")
            self.selected_direction = None
            return

        # Check if room already exists at new position
        target_room = self.map.get_room(new_position)

        if target_room:
            # Room already exists - check if we've visited before
            # If the target room has been visited, we can move back without unlocking
            if target_room.visited:
                # Moving to previously visited room - still costs 1 step but no lock check
                if self.player.move_to(new_position):
                    AppLogger.i(f"Moved back to {target_room.name}")
                    self.selected_direction = None
                    # Don't re-trigger room interactions for visited rooms
                else:
                    # Failed to move (not enough steps)
                    AppLogger.w("Not enough steps to move!")
                    self.status_message = "Not enough steps to move!"
                    self.selected_direction = None
            else:
                # First time visiting this room - need to unlock the door
                # The effective lock level is the maximum of source and destination
                effective_lock_level = max(source_lock_level, target_room.lock_level)
                
                if self._can_unlock_door(effective_lock_level):
                    if self.player.move_to(new_position):  # Costs 1 step
                        target_room.visited = True
                        AppLogger.i(f"Moved to {target_room.name}")
                        self.selected_direction = None
                        # Trigger room interactions after first entry
                        self.room_interaction_handler.check_room_interactions()
                    else:
                        # Failed to move (not enough steps)
                        AppLogger.w("Not enough steps to move!")
                        self.status_message = "Not enough steps to move!"
                        self.selected_direction = None
                else:
                    message = f"Door is locked (level {effective_lock_level}). Need a key!"
                    AppLogger.w(message)
                    self.status_message = message
                    self.selected_direction = None
        else:
            # Need to choose a new room - only source lock level applies here
            if self._can_unlock_door(source_lock_level):
                self.pending_room_position = new_position
                self._start_room_selection(entry_direction=self.selected_direction)
                self.selected_direction = None
            else:
                message = f"Door is locked (level {source_lock_level}). Need a key!"
                AppLogger.w(message)
                self.status_message = message
                self.selected_direction = None

    def _can_unlock_door(self, lock_level: int) -> bool:
        """Check if player can unlock a door of given level."""
        if lock_level == 0:
            return True

        # Level 1: can use key or lockpick kit
        if lock_level == 1:
            if self.player.has_item(InventoryKey.KEY):
                self.player.inventory[InventoryKey.KEY].use()
                AppLogger.i("Used a key to unlock the door")
                return True
            elif self.player.has_item(InventoryKey.LOCK_PICK_KIT):
                AppLogger.i("Used lockpick kit to unlock the door")
                return True

        # Level 2: can only use key
        elif lock_level == 2:
            if self.player.has_item(InventoryKey.KEY):
                self.player.inventory[InventoryKey.KEY].use()
                AppLogger.i("Used a key to unlock the door")
                return True

        return False

    def _get_required_door_for_entry(self, entry_direction: str) -> str:
        """Get the door that the new room needs based on entry direction.

        Args:
            entry_direction: Direction player is entering from ("top", "bottom", "left", "right")

        Returns:
            The door position needed in the new room ("top", "bottom", "left", "right")
        """
        # If entering from top (going up), new room needs bottom door
        # If entering from bottom (going down), new room needs top door
        # etc.
        opposite_doors = {
            "top": "bottom",
            "bottom": "top",
            "left": "right",
            "right": "left"
        }
        return opposite_doors.get(entry_direction, "top")

    def _calculate_rotation_for_door(self, room, required_door: str) -> int:
        """Calculate rotation needed to align a room's door with the required position.

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

        # Map: (current_door, required_door) -> rotation
        # Rotation is counter-clockwise in pygame
        rotation_map = {
            ("top", "top"): 0,
            ("top", "right"): 270,  # -90 degrees
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

    def _start_room_selection(self, entry_direction: str = "bottom"):
        """Start the room selection process.

        Args:
            entry_direction: Direction player is entering from ("top", "bottom", "left", "right")
        """
        required_door = self._get_required_door_for_entry(entry_direction)
        self.room_pool = self.map.generate_room_pool(count=3, required_door=required_door)
        if self.room_pool:
            self.selected_room_index = 0
            self.game_state = GameState.CHOOSING_ROOM
            AppLogger.i("Choose a room from the available options")
        else:
            AppLogger.w("No more rooms available!")


    def _confirm_room_selection(self):
        """Confirmer et placer la pièce sélectionnée."""
        if not self.room_pool:
            AppLogger.w("Aucune pièce disponible dans le pool")
            return
        
        # Valider l'index sélectionné
        if self.selected_room_index < 0 or self.selected_room_index >= len(self.room_pool):
            AppLogger.w(f"Index de pièce invalide: {self.selected_room_index}")
            self.selected_room_index = 0
            return

        selected_room = self.room_pool[self.selected_room_index]

        # Check gem cost
        if selected_room.gem_cost > self.player.inventory[InventoryKey.GEM].count:
            AppLogger.w(f"Not enough gems! Need {selected_room.gem_cost}, have {self.player.inventory[InventoryKey.GEM].count}")
            return

        # Deduct gems
        for _ in range(selected_room.gem_cost):
            self.player.inventory[InventoryKey.GEM].use()

        # Place room at pending position
        if self.pending_room_position:
            selected_room.position = self.pending_room_position
            self.map.place_room(selected_room, self.pending_room_position)


            # Move player to new room
            self.player.move_to(self.pending_room_position)
            selected_room.visited = True

            AppLogger.i(f"Placed and entered {selected_room.name}")

            # Reset room selection state
            self.room_pool = []
            self.selected_room_index = 0
            self.pending_room_position = None
            self.game_state = GameState.ENTER_ROOM

            # Check for room interactions after placing
            self.room_interaction_handler.check_room_interactions()
            return

        # Reset state
        self.room_pool = []
        self.selected_room_index = 0
        self.pending_room_position = None
        self.game_state = GameState.ENTER_ROOM

    def _initialize_door_locks(self, room: Room):
        """Initialize random lock levels for room doors based on row position."""
        import random

        row = room.position.y

        # Calculate lock probability based on row
        # Row 0 (top): all unlocked (for Antechamber row)
        # Row 8 (bottom): all locked level 0 (starting row)
        # Rows in between: increasing lock levels

        if row == 8:  # Starting row
            lock_level = 0
        elif row == 0:  # Antechamber row
            lock_level = 2
        else:
            # Progressive difficulty: higher rows have higher lock levels
            progress = (8 - row) / 8.0  # 0.0 at bottom, 1.0 at top
            rand = random.random()

            if rand < (1.0 - progress):
                lock_level = 0
            elif rand < (1.0 - progress * 0.5):
                lock_level = 1
            else:
                lock_level = 2

        # Apply lock level to the room (all doors of a room share the same lock level)
        # Only apply lock level if the room has at least one door
        has_any_door = (room.has_top_door or room.has_bottom_door or
                       room.has_left_door or room.has_right_door)
        room.lock_level = lock_level if has_any_door else 0


# Example usage / test
if __name__ == '__main__':
    from logging import AppLogger
    from display_helper import DisplayHelper

    AppLogger.i("Testing Game class...")

    # Create display helper
    display_helper = DisplayHelper(1800, 900)

    # Create game
    game = Game(display_helper)
    AppLogger.i("Game initialized successfully!")

    # Check initial state
    AppLogger.i(f"Game state: {game.game_state}")
    AppLogger.i(f"Player position: {game.player.position}")

    # Check current room
    current_room = game.get_current_room()
    AppLogger.i(f"Current room: {current_room.name if current_room else 'None'}")
    assert current_room is not None
    assert current_room.visited

    # Check handlers
    AppLogger.i(f"Has GameRenderer: {game.game_renderer is not None}")
    AppLogger.i(f"Has InputHandler: {game.input_handler is not None}")
    AppLogger.i(f"Has RoomInteractionHandler: {game.room_interaction_handler is not None}")
    assert all([game.game_renderer, game.input_handler, game.room_interaction_handler])

    # Check win/lose conditions
    is_won = game.check_win_condition()
    is_lost = game.check_lose_condition()
    AppLogger.i(f"Won: {is_won}, Lost: {is_lost}")
    assert not is_won  # Shouldn't win at start
    assert not is_lost  # Shouldn't lose at start

    # Test restart
    game._restart_game()
    AppLogger.i("Game restarted successfully!")









