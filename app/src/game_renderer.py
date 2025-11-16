from typing import TYPE_CHECKING
from rectangle import Rectangle
from position import Position
from color import Color
from app_color import white_color, black_color, door_color, trophy_color
from drawables import Drawables
from player import InventoryKey
from game_state import GameState
from display_helper import DisplayHelper
from logging import AppLogger

if TYPE_CHECKING:
    from renderer import Renderer
    from game import Game
    from room import Room


class GameRenderer:
    """Handles all rendering for the game."""

    def __init__(self, game: 'Game'):
        """Initialize the renderer with a reference to the game.

        Args:
            game: The Game instance to render
        """
        self.game = game
        

    def render(self, renderer: 'Renderer'):
        """Main render method that draws the entire game state.

        Args:
            renderer: The Renderer to use for drawing
        """
        if not self.game.display_helper:
            return

        # Draw the manor background
        self._draw_mansion(renderer)

        # Draw all rooms on the map
        self._draw_rooms(renderer)


        # Draw the action area
        self._draw_game_area(renderer)

        # Draw inventory in action area
        inventory_end_y = self._draw_inventory(renderer)

        # Draw room pool if in room selection mode
        if self.game.game_state == GameState.CHOOSING_ROOM and self.game.room_pool:
            self._draw_room_selection(renderer, inventory_end_y)

        # Draw game status messages
        self._draw_game_status(renderer)

        # Draw selected direction indicator
        if self.game.selected_direction and self.game.game_state == GameState.ENTER_ROOM:
            self._draw_direction_indicator(renderer)

    def _draw_mansion(self, renderer: 'Renderer'):
        """Draw the manor background."""
        if not self.game.display_helper:
            return
        renderer.draw_rectangle(
            Rectangle(
                x=self.game.display_helper.MANOR_X,
                y=0,
                width=self.game.display_helper.MANOR_WIDTH,
                height=self.game.display_helper.SCREEN_HEIGHT
            ),
            fill_color=black_color
        )

    def _draw_game_area(self, renderer: 'Renderer'):
        """Draw the action/UI area background."""
        if not self.game.display_helper:
            return
        renderer.draw_rectangle(
            Rectangle(
                x=self.game.display_helper.ACTION_X,
                y=0,
                width=self.game.display_helper.ACTION_WIDTH,
                height=self.game.display_helper.SCREEN_HEIGHT
            ),
            fill_color=white_color
        )

    def _draw_rooms(self, renderer: 'Renderer'):
        """Draw all rooms in the map grid."""
        for y in range(self.game.map.height):
            for x in range(self.game.map.width):
                room = self.game.map.rooms[y][x]
                if room:
                    # Highlight if this is the player's current position
                    highlight = (x == self.game.player.position.x and y == self.game.player.position.y)
                    room.render(renderer, highlight=highlight)


    def _draw_inventory(self, renderer: 'Renderer') -> int:
        """Draw the player's inventory in the action area with two columns.

        Returns:
            The final y_offset after drawing all inventory items.
        """
        if not self.game.display_helper:
            return 20

        # Starting position for inventory display
        start_x = self.game.display_helper.ACTION_X + 20
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
        col1_x = start_x
        action_right_edge = self.game.display_helper.ACTION_X + self.game.display_helper.ACTION_WIDTH
        col2_x = action_right_edge - right_margin - 80

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
            has_item = self.game.player.inventory[item_key].count > 0
            if has_item:
                icon_rect = Rectangle(col1_x, perm_y_offset, icon_size, icon_size)
                renderer.draw_image(icon_path, icon_rect)
                renderer.display_text(
                    label,
                    black_color,
                    18,
                    Position(col1_x + icon_size + 10, perm_y_offset + 5)
                )
                perm_y_offset += line_height

        # RIGHT COLUMN: Display consumable items
        cons_y_offset = items_start_y
        inventory_items = [
            (InventoryKey.STEP, "Steps", Drawables.STEPS),
            (InventoryKey.COIN, "Coins", Drawables.COIN),
            (InventoryKey.GEM, "Gems", Drawables.GEM),
            (InventoryKey.KEY, "Keys", Drawables.KEY),
            (InventoryKey.DICE, "Dice", Drawables.DICE),
        ]

        for item_key, label, icon_path in inventory_items:
            count = self.game.player.inventory[item_key].count
            count_text = f"{count:>2}"
            renderer.display_text(
                count_text,
                black_color,
                24,
                Position(col2_x, cons_y_offset + 3)
            )
            icon_x = col2_x + 30 + 10
            icon_rect = Rectangle(icon_x, cons_y_offset, icon_size, icon_size)
            renderer.draw_image(icon_path, icon_rect)
            cons_y_offset += line_height

        # Calculate final y position
        final_y = max(perm_y_offset, cons_y_offset) + 20

        # Display current room name
        current_room = self.game.get_current_room()
        if current_room:
            renderer.display_text(
                f"Current Room: {current_room.name}",
                black_color,
                22,
                Position(start_x, final_y)
            )
            final_y += 35

        return final_y

    def _draw_room_selection(self, renderer: 'Renderer', inventory_end_y: int):
        """Draw the room selection UI showing 3 room choices."""
        if not self.game.display_helper or not self.game.room_pool:
            return

        panel_x = self.game.display_helper.ACTION_X + 20
        panel_y = inventory_end_y + 140

        # Draw title
        renderer.display_text(
            "Choose a room to draft",
            black_color,
            28,
            Position(panel_x + 200, panel_y - 60)
        )

        renderer.display_text(
            "Redraw",
            black_color,
            24,
            Position(panel_x + 650, panel_y - 60)
        )

        # Draw each room option
        room_width = 220
        spacing = 30
        preview_size = 180

        for i, room in enumerate(self.game.room_pool):
            room_x = panel_x + i * (room_width + spacing)
            room_y = panel_y

            # Highlight selected room
            if i == self.game.selected_room_index:
                renderer.draw_rectangle(
                    Rectangle(room_x - 5, room_y - 5, room_width + 10, preview_size + 120),
                    Color(200, 230, 255),
                    trophy_color,
                    4
                )
            else:
                renderer.draw_rectangle(
                    Rectangle(room_x - 5, room_y - 5, room_width + 10, preview_size + 120),
                    Color(250, 250, 250),
                    black_color,
                    2
                )

            # Render room preview
            self._draw_room_preview(renderer, room,
                                   Rectangle(room_x + 10, room_y + 5, preview_size, preview_size),
                                   i == self.game.selected_room_index)

            # Draw room info
            info_y = room_y + preview_size + 20
            renderer.display_text(
                room.name,
                black_color,
                20 if i == self.game.selected_room_index else 18,
                Position(room_x + 20, info_y)
            )

            # Display gem cost
            if room.gem_cost > 0:
                gem_icon_size = 20
                gem_icon_rect = Rectangle(room_x + 20, info_y + 30, gem_icon_size, gem_icon_size)
                renderer.draw_image(Drawables.GEM, gem_icon_rect)
                renderer.display_text(
                    f"{room.gem_cost} gems",
                    black_color,
                    16,
                    Position(room_x + 20 + gem_icon_size + 5, info_y + 32)
                )

        # Draw instructions
        instruction_y = panel_y + preview_size + 150
        renderer.display_text(
            "You use a key to open the door.",
            black_color,
            16,
            Position(panel_x + 50, instruction_y)
        )

        renderer.display_text(
            "with dice",
            black_color,
            14,
            Position(panel_x + 650, panel_y - 30)
        )

    def _draw_room_preview(self, renderer: 'Renderer', room: 'Room', rect: Rectangle, is_selected: bool):
        """Draw a preview of a room."""
        # Draw room image with rotation
        renderer.draw_image(room.asset_path, rect, rotation=room.rotation)

        # Draw border
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

    def _draw_popup(self, renderer: 'Renderer', title: str, message: str):
        """Draw a popup dialog with title, message, and restart/quit options."""
        if not self.game.display_helper:
            return

        # Draw semi-transparent overlay
        overlay_color = Color(0, 0, 0, 180)
        renderer.draw_overlay(overlay_color)

        # Popup dimensions
        popup_width = 600
        popup_height = 300
        popup_x = (self.game.display_helper.SCREEN_WIDTH - popup_width) // 2
        popup_y = (self.game.display_helper.SCREEN_HEIGHT - popup_height) // 2

        # Draw shadow with rounded corners
        popup_rect = Rectangle(popup_x, popup_y, popup_width, popup_height)
        corner_radius = 15
        shadow_color = Color(0, 0, 0, 20)
        renderer.draw_shadow(
            popup_rect,
            blur_radius=10,
            shadow_color=shadow_color,
            border_radius=corner_radius,
            offset_x=0,
            offset_y=0
        )

        # Draw popup background
        popup_bg_color = Color(245, 245, 245)
        popup_border_color = Color(60, 60, 60)
        renderer.draw_rectangle(popup_rect, popup_bg_color, popup_border_color, 3, border_radius=corner_radius)

        # Draw title
        title_color = Color(200, 50, 50) if "GAME OVER" in title else Color(50, 150, 50)
        title_x = popup_x + (popup_width // 2) - (len(title) * 10)
        title_y = popup_y + 40
        renderer.display_text(title, title_color, 48, Position(title_x, title_y))

        # Draw message
        message_x = popup_x + (popup_width // 2) - (len(message) * 6)
        message_y = popup_y + 120
        renderer.display_text(message, black_color, 24, Position(message_x, message_y))

        # Draw instructions
        instruction1 = "Press R to Restart"
        instruction2 = "Press Q or ESC to Quit"

        inst1_x = popup_x + (popup_width // 2) - (len(instruction1) * 6)
        inst1_y = popup_y + 190
        renderer.display_text(instruction1, black_color, 22, Position(inst1_x, inst1_y))

        inst2_x = popup_x + (popup_width // 2) - (len(instruction2) * 6)
        inst2_y = popup_y + 230
        renderer.display_text(instruction2, black_color, 22, Position(inst2_x, inst2_y))

    def _draw_game_status(self, renderer: 'Renderer'):
        """Draw game status messages at the bottom of the action area."""
        if not self.game.display_helper:
            return

        status_x = self.game.display_helper.ACTION_X + 20
        status_y = self.game.display_helper.SCREEN_HEIGHT - 100

        if self.game.game_state == GameState.VICTORY:
            self._draw_popup(renderer, "VICTORY!", "You reached the Antechamber!")
        elif self.game.game_state == GameState.GAME_OVER:
            reason = "You ran out of steps." if self.game.player.inventory[InventoryKey.STEP].count <= 0 else "No path to victory!"
            self._draw_popup(renderer, "GAME OVER", reason)
        elif self.game.game_state == GameState.ENTER_ROOM:
            if self.game.status_message:
                renderer.display_text(
                    self.game.status_message,
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
        elif self.game.game_state == GameState.ROOM_INTERACTION:
            if hasattr(self.game, '_pending_interaction'):
                if self.game._pending_interaction == "chest":
                    renderer.display_text(
                        "Chest: Press K (key) or H (hammer) to open, ESC to skip",
                        black_color,
                        18,
                        Position(status_x, status_y)
                    )
                elif self.game._pending_interaction == "dig":
                    renderer.display_text(
                        "Digging Spot: Press D to dig with shovel, ESC to skip",
                        black_color,
                        18,
                        Position(status_x, status_y)
                    )

    def _draw_direction_indicator(self, renderer: 'Renderer'):
        """Draw an arrow indicating selected direction on the current room."""
        if not self.game.display_helper:
            return

        current_room = self.game.get_current_room()
        if not current_room or not current_room.position:
            return

        # Calculate room center position
        room_x = self.game.display_helper.MANOR_X + DisplayHelper.GRID_MARGIN + \
                 current_room.position.x * (self.game.display_helper.ROOM_SIZE + DisplayHelper.ROOM_GAP)
        room_y = DisplayHelper.GRID_MARGIN_TOP + \
                 current_room.position.y * (self.game.display_helper.ROOM_SIZE + DisplayHelper.ROOM_GAP)

        room_center_x = room_x + self.game.display_helper.ROOM_SIZE // 2
        room_center_y = room_y + self.game.display_helper.ROOM_SIZE // 2

        # Draw arrow
        arrow_size = 30

        if self.game.selected_direction == "top":
            renderer.display_text("↑", trophy_color, arrow_size, Position(room_center_x - 10, room_y - 40))
        elif self.game.selected_direction == "bottom":
            renderer.display_text("↓", trophy_color, arrow_size, Position(room_center_x - 10, room_y + self.game.display_helper.ROOM_SIZE + 10))
        elif self.game.selected_direction == "left":
            renderer.display_text("←", trophy_color, arrow_size, Position(room_x - 40, room_center_y - 15))
        elif self.game.selected_direction == "right":
            renderer.display_text("→", trophy_color, arrow_size, Position(room_x + self.game.display_helper.ROOM_SIZE + 10, room_center_y - 15))


# Example usage / test
if __name__ == '__main__':
    from game import Game
    from display_helper import DisplayHelper
    import pygame

    AppLogger.i("Testing GameRenderer...")

    # Initialize pygame
    pygame.init()

    # Create display helper and game
    display_helper = DisplayHelper(1800, 900)
    game = Game(display_helper)

    # Create screen and renderer
    screen = pygame.display.set_mode((display_helper.SCREEN_WIDTH, display_helper.SCREEN_HEIGHT))
    from renderer import Renderer
    renderer = Renderer(screen)

    # Test rendering
    game.game_renderer.render(renderer)
    pygame.display.flip()

    AppLogger.i("GameRenderer initialized successfully!")
    AppLogger.i(f"Game state: {game.game_state}")
    AppLogger.i(f"Player position: {game.player.position}")
    AppLogger.i(f"Current room: {game.get_current_room().name if game.get_current_room() else 'None'}")

    pygame.quit()
