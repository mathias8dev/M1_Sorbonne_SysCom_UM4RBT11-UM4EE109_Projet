from size import Size
from rectangle import Rectangle
from typing import List, Optional
from renderer import Renderer
from renderable import Renderable
from app_color import white_color, black_color
from color import Color
from map import Map
from player import Player, InventoryKey
from position import Position
from game_state import GameState
from room import Room
from drawables import Drawables
from logging import AppLogger


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

    def get_current_room(self) -> Optional[Room]:
        """Get the room at the player's current position."""
        return self.map.get_room(self.player.position)

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
        if not self.display_helper:
            return

        # Draw the manor background
        self._draw_mansion(renderer)

        # Draw all rooms on the map
        self._draw_rooms(renderer)

        # Draw player highlight
        self._draw_player_cursor(renderer)

        # Draw the action area
        self._draw_game_area(renderer)

        # Draw inventory in action area
        inventory_end_y = self._draw_inventory(renderer)

        # Draw room pool if in room selection mode
        if self.game_state == GameState.CHOOSING_ROOM and self.room_pool:
            self._draw_room_selection(renderer, inventory_end_y)

        # Draw game status messages
        self._draw_game_status(renderer)

        # Draw selected direction indicator
        if self.selected_direction and self.game_state == GameState.ENTER_ROOM:
            self._draw_direction_indicator(renderer)

    def _draw_mansion(self, renderer: 'Renderer'):
        if not self.display_helper:
            return
        renderer.draw_rectangle(
            Rectangle(
                x=self.display_helper.MANOR_X,
                y=0,
                width=self.display_helper.MANOR_WIDTH,
                height=self.display_helper.SCREEN_HEIGHT
            ),
            fill_color=black_color
        )

    def _draw_game_area(self, renderer: 'Renderer'):
        if not self.display_helper:
            return
        renderer.draw_rectangle(
            Rectangle(
                x=self.display_helper.ACTION_X,
                y=0,
                width=self.display_helper.ACTION_WIDTH,
                height=self.display_helper.SCREEN_HEIGHT
            ),
            fill_color=white_color
        )

    def _draw_rooms(self, renderer: 'Renderer'):
        """Draw all rooms in the map grid."""
        for y in range(self.map.height):
            for x in range(self.map.width):
                room = self.map.rooms[y][x]
                if room:
                    # Highlight if this is the player's current position
                    highlight = (x == self.player.position.x and y == self.player.position.y)
                    AppLogger.d(f"Rendering room at {room.position} with highlight {highlight}")
                    room.render(renderer, highlight=highlight)

    def _draw_player_cursor(self, renderer: 'Renderer'):
        """Draw a cursor or highlight around the player's current room."""
        # This is handled by the highlight parameter in _draw_rooms
        pass

    def _draw_inventory(self, renderer: 'Renderer') -> int:
        """Draw the player's inventory in the action area with two columns.

        Returns:
            The final y_offset after drawing all inventory items.
        """
        if not self.display_helper:
            return 20

        # Starting position for inventory display
        start_x = self.display_helper.ACTION_X + 20
        start_y = 20
        line_height = 35
        icon_size = 25
        right_margin = 20  # Margin from the right edge

        # Display title
        renderer.display_text(
            "Inventory:",
            black_color,
            24,
            Position(start_x, start_y)
        )

        # Calculate column positions
        # Left column: permanent items (starts at start_x)
        col1_x = start_x

        # Right column: consumable items (aligned to the right edge of action area)
        # ACTION_X + ACTION_WIDTH gives us the right edge
        # We subtract right_margin and space for icon + text (approximately 80px)
        action_right_edge = self.display_helper.ACTION_X + self.display_helper.ACTION_WIDTH
        col2_x = action_right_edge - right_margin - 80  # 80px for icon + number display

        # Start drawing items below title
        items_start_y = start_y + 40

        # LEFT COLUMN: Display permanent items
        perm_y_offset = items_start_y
        permanent_items = [
            (InventoryKey.SHOVEL, "Shovel", Drawables.SHOVEL),
            (InventoryKey.HAMMER, "Hammer", Drawables.HAMMER),
            (InventoryKey.LOCK_PICK_KIT, "Lockpick Kit", Drawables.LOCK_PICK_KIT),
            (InventoryKey.METAL_DETECTOR, "Metal Detector", Drawables.METAL_DETECTOR),
            (InventoryKey.RABBIT_FOOT, "Rabbit's Foot", Drawables.RABBIT_FOOT),
        ]

        for item_key, label, icon_path in permanent_items:
            has_item = self.player.inventory[item_key].count > 0
            if has_item:
                # Draw icon
                icon_rect = Rectangle(col1_x, perm_y_offset, icon_size, icon_size)
                renderer.draw_image(icon_path, icon_rect)

                # Draw text next to icon
                renderer.display_text(
                    label,
                    black_color,
                    18,
                    Position(col1_x + icon_size + 10, perm_y_offset + 5)
                )
                perm_y_offset += line_height

        # RIGHT COLUMN: Display consumable items (aligned to the right)
        cons_y_offset = items_start_y
        inventory_items = [
            (InventoryKey.STEP, "Steps", Drawables.STEPS),
            (InventoryKey.COIN, "Coins", Drawables.COIN),
            (InventoryKey.GEM, "Gems", Drawables.GEM),
            (InventoryKey.KEY, "Keys", Drawables.KEY),
            (InventoryKey.DICE, "Dice", Drawables.DICE),
        ]

        for item_key, label, icon_path in inventory_items:
            count = self.player.inventory[item_key].count

            # Draw count first (before icon) - pad with spaces for alignment (2 digits width)
            count_text = f"{count:>2}"  # Right-align to 2 characters width
            renderer.display_text(
                count_text,
                black_color,
                24,  # Increased font size from 20 to 24
                Position(col2_x, cons_y_offset + 3)
            )

            # Draw icon after the count (fixed position since all counts are same width)
            # 2 digits * ~15px per digit for font size 24 = ~30px
            icon_x = col2_x + 30 + 10
            icon_rect = Rectangle(icon_x, cons_y_offset, icon_size, icon_size)
            renderer.draw_image(icon_path, icon_rect)

            cons_y_offset += line_height

        # Calculate final y position (max of both columns)
        final_y = max(perm_y_offset, cons_y_offset)

        # Display current room name below both columns
        final_y += 20
        current_room = self.get_current_room()
        if current_room:
            renderer.display_text(
                f"Current Room: {current_room.name}",
                black_color,
                22,
                Position(start_x, final_y)
            )
            final_y += 35  # Account for current room text height

        # Return final y position (end of inventory area)
        return final_y

    def _draw_room_selection(self, renderer: 'Renderer', inventory_end_y: int):
        """Draw the room selection UI showing 3 room choices with visual previews (horizontal layout).

        Args:
            renderer: The renderer to draw with.
            inventory_end_y: The y-coordinate where the inventory display ends.
        """
        if not self.display_helper or not self.room_pool:
            return

        # Draw selection panel in action area
        panel_x = self.display_helper.ACTION_X + 20
        # Position panel below inventory with proper top margin for visual separation
        panel_y = inventory_end_y + 140

        # Draw title
        renderer.display_text(
            "Choose a room to draft",
            black_color,
            28,
            Position(panel_x + 200, panel_y - 60)
        )

        # Draw "Redraw" button text on the right
        renderer.display_text(
            "Redraw",
            black_color,
            24,
            Position(panel_x + 650, panel_y - 60)
        )

        # Draw each room option with preview (horizontal layout)
        room_width = 220  # Width of each room card
        spacing = 30
        preview_size = 180  # Size of room preview

        for i, room in enumerate(self.room_pool):
            room_x = panel_x + i * (room_width + spacing)
            room_y = panel_y

            # Highlight selected room with background and border
            if i == self.selected_room_index:
                from app_color import trophy_color
                # Draw highlighted background
                renderer.draw_rectangle(
                    Rectangle(room_x - 5, room_y - 5, room_width + 10, preview_size + 120),
                    Color(200, 230, 255),  # Light blue background
                    trophy_color,
                    4
                )
            else:
                # Draw normal border
                renderer.draw_rectangle(
                    Rectangle(room_x - 5, room_y - 5, room_width + 10, preview_size + 120),
                    Color(250, 250, 250),  # Very light gray background
                    black_color,
                    2
                )

            # Render the room preview on top
            self._draw_room_preview(renderer, room,
                                   Rectangle(room_x + 10, room_y + 5,
                                           preview_size, preview_size),
                                   i == self.selected_room_index)

            # Draw room info below preview
            info_y = room_y + preview_size + 20
            text_color = black_color

            # Room name centered
            renderer.display_text(
                room.name,
                text_color,
                20 if i == self.selected_room_index else 18,
                Position(room_x + 20, info_y)
            )

            # Display gem cost with icon (only if cost > 0)
            if room.gem_cost > 0:
                gem_icon_size = 20
                gem_icon_rect = Rectangle(room_x + 20, info_y + 30, gem_icon_size, gem_icon_size)
                renderer.draw_image(Drawables.GEM, gem_icon_rect)

                cost_text = f"{room.gem_cost} gems"
                renderer.display_text(
                    cost_text,
                    black_color,
                    16,
                    Position(room_x + 20 + gem_icon_size + 5, info_y + 32)
                )

        # Draw instructions at bottom
        instruction_y = panel_y + preview_size + 150
        renderer.display_text(
            "You use a key to open the door.",
            black_color,
            16,
            Position(panel_x + 50, instruction_y)
        )

        # Draw "with dice" note next to Redraw
        renderer.display_text(
            "with dice",
            black_color,
            14,
            Position(panel_x + 650, panel_y - 30)
        )

    def _draw_room_preview(self, renderer: 'Renderer', room: Room, rect: Rectangle, is_selected: bool):
        """Draw a preview of a room at the specified rectangle."""
        from app_color import room_stroke_visited_color, room_stroke_default_color, door_color

        # Draw room image with rotation
        renderer.draw_image(room.asset_path, rect, rotation=room.rotation)

        # Draw border (thicker if selected)
        stroke_color = Color(0, 150, 0) if is_selected else black_color
        stroke_width = 3 if is_selected else 2
        renderer.draw_rectangle(rect, None, stroke_color, stroke_width)

        # Draw doors as small indicators
        door_size_ratio = 0.2
        door_offset_ratio = 0.05

        if room.has_top_door:
            door_rect = Rectangle(
                rect.x + int(rect.width * 0.4),
                rect.y - int(rect.height * door_offset_ratio),
                int(rect.width * door_size_ratio),
                int(rect.height * 0.1),
            )
            renderer.draw_rectangle(door_rect, door_color, stroke_color, 1)

        if room.has_bottom_door:
            door_rect = Rectangle(
                rect.x + int(rect.width * 0.4),
                rect.y + int(rect.height * (1 - door_offset_ratio)),
                int(rect.width * door_size_ratio),
                int(rect.height * 0.1),
            )
            renderer.draw_rectangle(door_rect, door_color, stroke_color, 1)

        if room.has_left_door:
            door_rect = Rectangle(
                rect.x - int(rect.width * door_offset_ratio),
                rect.y + int(rect.height * 0.4),
                int(rect.width * 0.1),
                int(rect.height * door_size_ratio),
            )
            renderer.draw_rectangle(door_rect, door_color, stroke_color, 1)

        if room.has_right_door:
            door_rect = Rectangle(
                rect.x + int(rect.width * (1 - door_offset_ratio)),
                rect.y + int(rect.height * 0.4),
                int(rect.width * 0.1),
                int(rect.height * door_size_ratio),
            )
            renderer.draw_rectangle(door_rect, door_color, stroke_color, 1)

    def handle_keyboard_event(self, event):
        """Handle keyboard input based on current game state."""

        if self.game_state == GameState.GAME_OVER or self.game_state == GameState.VICTORY:
            return

        # Check win/lose conditions
        if self.check_win_condition():
            self.game_state = GameState.VICTORY
            AppLogger.i("Victory! You reached the Antechamber!")
            return

        if self.check_lose_condition():
            self.game_state = GameState.GAME_OVER
            # Determine why player lost
            if self.player.inventory[InventoryKey.STEP].count <= 0:
                AppLogger.i("Game Over! You ran out of steps.")
            else:
                AppLogger.i("Game Over! No path to victory - you're stuck!")
            return

        if self.game_state == GameState.ENTER_ROOM:
            self._handle_movement_input(event)

        elif self.game_state == GameState.CHOOSING_ROOM:
            self._handle_room_selection_input(event)

        elif self.game_state == GameState.ROOM_INTERACTION:
            self._handle_room_interaction_input(event)

    def _handle_movement_input(self, event):
        """Handle ZQSD movement in the manor."""
        import pygame

        current_room = self.get_current_room()
        if not current_room:
            return

        # Direction selection with ZQSD
        if event.key == pygame.K_z:  # Up
            self.selected_direction = "top"
            self.status_message = None  # Clear previous messages
        elif event.key == pygame.K_s:  # Down
            self.selected_direction = "bottom"
            self.status_message = None  # Clear previous messages
        elif event.key == pygame.K_q:  # Left
            self.selected_direction = "left"
            self.status_message = None  # Clear previous messages
        elif event.key == pygame.K_d:  # Right
            self.selected_direction = "right"
            self.status_message = None  # Clear previous messages
        elif event.key == pygame.K_SPACE and self.selected_direction:
            # Validate movement
            self._attempt_move()

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
            # Room already exists - check lock level from BOTH sides
            # The effective lock level is the maximum of source and destination
            effective_lock_level = max(source_lock_level, target_room.lock_level)

            # If the target room has been visited, we can move back without unlocking
            if target_room.visited:
                self.player.move_to(new_position)  # Still costs 1 step
                AppLogger.i(f"Moved back to {target_room.name}")
                self.selected_direction = None
                # Don't re-trigger room interactions for visited rooms
            else:
                # First time visiting this room - need to unlock the door
                if self._can_unlock_door(effective_lock_level):
                    self.player.move_to(new_position)  # Costs 1 step
                    target_room.visited = True
                    AppLogger.i(f"Moved to {target_room.name}")
                    self.selected_direction = None
                    # Trigger room interactions after first entry
                    self._check_room_interactions()
                else:
                    message = f"Door is locked (level {effective_lock_level}). Need a key!"
                    AppLogger.w(message)
                    self.status_message = message
        else:
            # Need to choose a new room - only source lock level applies here
            if self._can_unlock_door(source_lock_level):
                self.pending_room_position = new_position
                self._start_room_selection(entry_direction=self.selected_direction)
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

    def _handle_room_selection_input(self, event):
        """Handle room selection input (horizontal navigation with arrow keys)."""
        import pygame

        # Horizontal navigation with arrow keys (Left/Right)
        if event.key == pygame.K_LEFT:  # Left arrow
            self.selected_room_index = (self.selected_room_index - 1) % len(self.room_pool)
        elif event.key == pygame.K_RIGHT:  # Right arrow
            self.selected_room_index = (self.selected_room_index + 1) % len(self.room_pool)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self._confirm_room_selection()
        elif event.key == pygame.K_r:
            # Reroll with dice (R key)
            if self.player.has_item(InventoryKey.DICE):
                self.player.inventory[InventoryKey.DICE].use()
                self.room_pool = self.map.generate_room_pool(count=3)
                self.selected_room_index = 0
                AppLogger.i("Rerolled room selection!")
            else:
                AppLogger.w("No dice available to reroll")

    def _confirm_room_selection(self):
        """Confirm and place the selected room."""
        if not self.room_pool or self.selected_room_index >= len(self.room_pool):
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
            self._check_room_interactions()
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

    def _check_room_interactions(self):
        """Check and handle room interactions (items, chest, digging spot)."""
        current_room = self.get_current_room()
        if not current_room:
            return

        # Automatically collect items from the room
        if current_room.items:
            items_collected = current_room.take_items()
            for item in items_collected:
                self.player.take_item(item)
                AppLogger.i(f"Collected {item.__class__.__name__}!")

        # Check for chest
        if current_room.chest and not current_room.chest.is_opened:
            self.game_state = GameState.ROOM_INTERACTION
            self._pending_interaction = "chest"
            AppLogger.i("There's a chest here! Press 'K' to open with key, 'H' to smash with hammer, or 'ESC' to skip")
            return

        # Check for digging spot (has_treasure flag)
        if current_room.has_treasure and not current_room.dug:
            if self.player.has_item(InventoryKey.SHOVEL):
                self.game_state = GameState.ROOM_INTERACTION
                self._pending_interaction = "dig"
                AppLogger.i("There's a digging spot here! Press 'D' to dig with shovel or 'ESC' to skip")
                return

    def _handle_room_interaction_input(self, event):
        """Handle room interaction input (chest, digging, etc.)."""
        import pygame

        if not hasattr(self, '_pending_interaction'):
            self.game_state = GameState.ENTER_ROOM
            return

        if self._pending_interaction == "chest":
            if event.key == pygame.K_k:
                # Open chest with key
                self._open_chest_with_key()
            elif event.key == pygame.K_h:
                # Open chest with hammer
                self._open_chest_with_hammer()
            elif event.key == pygame.K_ESCAPE:
                # Skip chest interaction
                AppLogger.i("Skipped chest interaction")
                self._pending_interaction = None
                self.game_state = GameState.ENTER_ROOM

        elif self._pending_interaction == "dig":
            if event.key == pygame.K_d:
                # Dig with shovel
                self._dig_with_shovel()
            elif event.key == pygame.K_ESCAPE:
                # Skip digging
                AppLogger.i("Skipped digging")
                self._pending_interaction = None
                self.game_state = GameState.ENTER_ROOM

    def _open_chest_with_key(self):
        """Open chest using a key."""
        current_room = self.get_current_room()
        if not current_room or not current_room.chest:
            return

        if self.player.has_item(InventoryKey.KEY):
            key = self.player.inventory[InventoryKey.KEY]
            if current_room.chest.open_with_key(key):
                AppLogger.i("Opened chest with key!")
                self._collect_chest_contents(current_room.chest)
                self._pending_interaction = None
                self.game_state = GameState.ENTER_ROOM
            else:
                AppLogger.w("Failed to open chest")
        else:
            AppLogger.w("You don't have a key!")

    def _open_chest_with_hammer(self):
        """Open chest by smashing it with a hammer."""
        current_room = self.get_current_room()
        if not current_room or not current_room.chest:
            return

        if self.player.has_item(InventoryKey.HAMMER):
            hammer = self.player.inventory[InventoryKey.HAMMER]
            if current_room.chest.open_with_hammer(hammer):
                AppLogger.i("Smashed chest open with hammer!")
                self._collect_chest_contents(current_room.chest)
                self._pending_interaction = None
                self.game_state = GameState.ENTER_ROOM
            else:
                AppLogger.w("Failed to open chest")
        else:
            AppLogger.w("You don't have a hammer!")

    def _collect_chest_contents(self, chest):
        """Collect all items from an opened chest."""
        contents = chest.get_contents()
        for item in contents:
            self.player.take_item(item)
            AppLogger.i(f"Found {item.__class__.__name__} in chest!")

    def _dig_with_shovel(self):
        """Dig at a digging spot using shovel."""
        current_room = self.get_current_room()
        if not current_room or current_room.dug:
            return

        if self.player.has_item(InventoryKey.SHOVEL):
            # Mark room as dug
            current_room.dug = True
            AppLogger.i("Dug with shovel!")

            # TODO: Add treasure items based on room configuration
            # For now, add some random items
            import random
            if random.random() < 0.7:  # 70% chance to find something
                from items import Coin, Gem
                found_item = Coin(count=random.randint(5, 15)) if random.random() < 0.6 else Gem(count=random.randint(1, 3))
                self.player.take_item(found_item)
                AppLogger.i(f"Found {found_item.__class__.__name__} buried here!")
            else:
                AppLogger.i("Nothing found...")

            self._pending_interaction = None
            self.game_state = GameState.ENTER_ROOM
        else:
            AppLogger.w("You don't have a shovel!")

    def _draw_game_status(self, renderer: 'Renderer'):
        """Draw game status messages at the bottom of the action area."""
        if not self.display_helper:
            return

        status_x = self.display_helper.ACTION_X + 20
        status_y = self.display_helper.SCREEN_HEIGHT - 100

        if self.game_state == GameState.VICTORY:
            renderer.display_text(
                "VICTORY! You reached the Antechamber!",
                black_color,
                28,
                Position(status_x, status_y)
            )
        elif self.game_state == GameState.GAME_OVER:
            renderer.display_text(
                "GAME OVER! You ran out of steps.",
                black_color,
                28,
                Position(status_x, status_y)
            )
        elif self.game_state == GameState.ENTER_ROOM:
            # Display status message if available, otherwise show default instructions
            if self.status_message:
                renderer.display_text(
                    self.status_message,
                    black_color,
                    20,
                    Position(status_x, status_y)
                )
            else:
                renderer.display_text(
                    "Use ZQSD to select direction, SPACE to move",
                    black_color,
                    18,
                    Position(status_x, status_y)
                )
        elif self.game_state == GameState.ROOM_INTERACTION:
            if hasattr(self, '_pending_interaction'):
                if self._pending_interaction == "chest":
                    renderer.display_text(
                        "Chest: Press K (key) or H (hammer) to open, ESC to skip",
                        black_color,
                        18,
                        Position(status_x, status_y)
                    )
                elif self._pending_interaction == "dig":
                    renderer.display_text(
                        "Digging Spot: Press D to dig with shovel, ESC to skip",
                        black_color,
                        18,
                        Position(status_x, status_y)
                    )

    def _draw_direction_indicator(self, renderer: 'Renderer'):
        """Draw an arrow indicating selected direction on the current room."""
        if not self.display_helper:
            return

        current_room = self.get_current_room()
        if not current_room or not current_room.position:
            return

        from display_helper import DisplayHelper

        # Calculate room center position
        room_x = self.display_helper.MANOR_X + DisplayHelper.GRID_MARGIN + \
                 current_room.position.x * (self.display_helper.ROOM_SIZE + DisplayHelper.ROOM_GAP)
        room_y = DisplayHelper.GRID_MARGIN_TOP + \
                 current_room.position.y * (self.display_helper.ROOM_SIZE + DisplayHelper.ROOM_GAP)

        room_center_x = room_x + self.display_helper.ROOM_SIZE // 2
        room_center_y = room_y + self.display_helper.ROOM_SIZE // 2

        # Draw arrow based on selected direction
        arrow_size = 30
        from app_color import trophy_color

        if self.selected_direction == "top":
            renderer.display_text("↑", trophy_color, arrow_size, Position(room_center_x - 10, room_y - 40))
        elif self.selected_direction == "bottom":
            renderer.display_text("↓", trophy_color, arrow_size, Position(room_center_x - 10, room_y + self.display_helper.ROOM_SIZE + 10))
        elif self.selected_direction == "left":
            renderer.display_text("←", trophy_color, arrow_size, Position(room_x - 40, room_center_y - 15))
        elif self.selected_direction == "right":
            renderer.display_text("→", trophy_color, arrow_size, Position(room_x + self.display_helper.ROOM_SIZE + 10, room_center_y - 15))
