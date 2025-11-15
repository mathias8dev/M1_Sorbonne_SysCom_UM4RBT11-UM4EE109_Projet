from typing import TYPE_CHECKING
from player import InventoryKey
from game_state import GameState
from logging import AppLogger

if TYPE_CHECKING:
    from game import Game


class InputHandler:
    """Handles all keyboard input for the game."""

    def __init__(self, game: 'Game'):
        """Initialize the input handler.

        Args:
            game: The Game instance to handle input for
        """
        self.game = game

    def handle_keyboard_event(self, event):
        """Handle keyboard input based on current game state."""
        import pygame

        # Handle game over/victory popup input
        if self.game.game_state == GameState.GAME_OVER or self.game.game_state == GameState.VICTORY:
            if event.key == pygame.K_r:  # R for restart
                self.game._restart_game()
                return
            elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:  # Q or ESC for quit
                pygame.quit()
                import sys
                sys.exit()
            return

        # Check win/lose conditions
        if self.game.check_win_condition():
            self.game.game_state = GameState.VICTORY
            AppLogger.i("Victory! You reached the Antechamber!")
            return

        if self.game.check_lose_condition():
            self.game.game_state = GameState.GAME_OVER
            # Determine why player lost
            if self.game.player.inventory[InventoryKey.STEP].count <= 0:
                AppLogger.i("Game Over! You ran out of steps.")
            else:
                AppLogger.i("Game Over! No path to victory - you're stuck!")
            return

        if self.game.game_state == GameState.ENTER_ROOM:
            self._handle_movement_input(event)

        elif self.game.game_state == GameState.CHOOSING_ROOM:
            self._handle_room_selection_input(event)

        elif self.game.game_state == GameState.ROOM_INTERACTION:
            self._handle_room_interaction_input(event)

    def _handle_movement_input(self, event):
        """Handle ZQSD movement in the manor."""
        import pygame

        current_room = self.game.get_current_room()
        if not current_room:
            return

        # Direction selection with ZQSD
        if event.key == pygame.K_z:  # Up
            self.game.selected_direction = "top"
            self.game.status_message = None  # Clear previous messages
        elif event.key == pygame.K_s:  # Down
            self.game.selected_direction = "bottom"
            self.game.status_message = None  # Clear previous messages
        elif event.key == pygame.K_q:  # Left
            self.game.selected_direction = "left"
            self.game.status_message = None  # Clear previous messages
        elif event.key == pygame.K_d:  # Right
            self.game.selected_direction = "right"
            self.game.status_message = None  # Clear previous messages
        elif event.key == pygame.K_SPACE and self.game.selected_direction:
            # Validate movement
            self.game._attempt_move()

    def _handle_room_selection_input(self, event):
        """Handle room selection input (horizontal navigation with arrow keys)."""
        import pygame

        # Horizontal navigation with arrow keys (Left/Right)
        if event.key == pygame.K_LEFT:  # Left arrow
            self.game.selected_room_index = (self.game.selected_room_index - 1) % len(self.game.room_pool)
        elif event.key == pygame.K_RIGHT:  # Right arrow
            self.game.selected_room_index = (self.game.selected_room_index + 1) % len(self.game.room_pool)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self.game._confirm_room_selection()
        elif event.key == pygame.K_r:
            # Reroll with dice (R key)
            if self.game.player.has_item(InventoryKey.DICE):
                self.game.player.inventory[InventoryKey.DICE].use()
                # Get required door for current entry direction
                if self.game.selected_direction:
                    required_door = self.game._get_required_door_for_entry(self.game.selected_direction)
                    self.game.room_pool = self.game.map.generate_room_pool(count=3, required_door=required_door)
                else:
                    self.game.room_pool = self.game.map.generate_room_pool(count=3)
                self.game.selected_room_index = 0
                AppLogger.i("Rerolled room selection!")
            else:
                AppLogger.w("No dice available to reroll")

    def _handle_room_interaction_input(self, event):
        """Handle room interaction input (chest, digging, etc.)."""
        import pygame

        if not hasattr(self.game, '_pending_interaction'):
            self.game.game_state = GameState.ENTER_ROOM
            return

        if self.game._pending_interaction == "chest":
            if event.key == pygame.K_k:
                # Open chest with key
                self.game._open_chest_with_key()
            elif event.key == pygame.K_h:
                # Open chest with hammer
                self.game._open_chest_with_hammer()
            elif event.key == pygame.K_ESCAPE:
                # Skip chest interaction
                AppLogger.i("Skipped chest interaction")
                self.game._pending_interaction = None
                self.game.game_state = GameState.ENTER_ROOM

        elif self.game._pending_interaction == "dig":
            if event.key == pygame.K_d:
                # Dig with shovel
                self.game._dig_with_shovel()
            elif event.key == pygame.K_ESCAPE:
                # Skip digging
                AppLogger.i("Skipped digging")
                self.game._pending_interaction = None
                self.game.game_state = GameState.ENTER_ROOM


# Example usage / test
if __name__ == '__main__':
    from game import Game
    from display_helper import DisplayHelper
    import pygame

    AppLogger.i("Testing InputHandler...")

    # Create display helper and game
    display_helper = DisplayHelper(1800, 900)
    game = Game(display_helper)

    AppLogger.i("InputHandler initialized successfully!")
    AppLogger.i(f"Handler attached to game: {game.input_handler is not None}")
    AppLogger.i(f"Initial game state: {game.game_state}")

    # Test movement input simulation
    class MockEvent:
        def __init__(self, key):
            self.key = key

    # Simulate pressing 'Z' (up)
    game.input_handler._handle_movement_input(MockEvent(pygame.K_z))
    AppLogger.i(f"After pressing Z: selected_direction = {game.selected_direction}")

    # Simulate pressing 'D' (right)
    game.input_handler._handle_movement_input(MockEvent(pygame.K_d))
    AppLogger.i(f"After pressing D: selected_direction = {game.selected_direction}")

