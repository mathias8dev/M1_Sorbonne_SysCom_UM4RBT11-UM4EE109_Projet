from typing import TYPE_CHECKING
from player import InventoryKey
from game_state import GameState
from logging import AppLogger

if TYPE_CHECKING:
    from game import Game
    from chest import Chest


class RoomInteractionHandler:
    """Handles room interactions like chests and digging."""

    def __init__(self, game: 'Game'):
        """Initialize the room interaction handler.

        Args:
            game: The Game instance to handle interactions for
        """
        self.game = game

    def check_room_interactions(self):
        """Check and handle room interactions (items, chest, digging spot)."""
        current_room = self.game.get_current_room()
        if not current_room:
            return

        # Automatically collect items from the room
        if current_room.items:
            items_collected = current_room.take_items()
            for item in items_collected:
                self.game.player.take_item(item)
                AppLogger.i(f"Collected {item.__class__.__name__}!")

        # Check for chest
        if current_room.chest and not current_room.chest.is_opened:
            self.game.game_state = GameState.ROOM_INTERACTION
            self.game._pending_interaction = "chest"
            AppLogger.i("There's a chest here! Press 'K' to open with key, 'H' to smash with hammer, or 'ESC' to skip")
            return

        # Check for digging spot (has_treasure flag)
        if current_room.has_treasure and not current_room.dug:
            if self.game.player.has_item(InventoryKey.SHOVEL):
                self.game.game_state = GameState.ROOM_INTERACTION
                self.game._pending_interaction = "dig"
                AppLogger.i("There's a digging spot here! Press 'D' to dig with shovel or 'ESC' to skip")
                return

    def open_chest_with_key(self):
        """Open chest using a key."""
        current_room = self.game.get_current_room()
        if not current_room or not current_room.chest:
            return

        if self.game.player.has_item(InventoryKey.KEY):
            key = self.game.player.inventory[InventoryKey.KEY]
            if current_room.chest.open_with_key(key):
                AppLogger.i("Opened chest with key!")
                self._collect_chest_contents(current_room.chest)
                self.game._pending_interaction = None
                self.game.game_state = GameState.ENTER_ROOM
            else:
                AppLogger.w("Failed to open chest")
        else:
            AppLogger.w("You don't have a key!")

    def open_chest_with_hammer(self):
        """Open chest by smashing it with a hammer."""
        current_room = self.game.get_current_room()
        if not current_room or not current_room.chest:
            return

        if self.game.player.has_item(InventoryKey.HAMMER):
            hammer = self.game.player.inventory[InventoryKey.HAMMER]
            if current_room.chest.open_with_hammer(hammer):
                AppLogger.i("Smashed chest open with hammer!")
                self._collect_chest_contents(current_room.chest)
                self.game._pending_interaction = None
                self.game.game_state = GameState.ENTER_ROOM
            else:
                AppLogger.w("Failed to open chest")
        else:
            AppLogger.w("You don't have a hammer!")

    def _collect_chest_contents(self, chest: 'Chest'):
        """Collect all items from an opened chest."""
        contents = chest.get_contents()
        for item in contents:
            self.game.player.take_item(item)
            AppLogger.i(f"Found {item.__class__.__name__} in chest!")

    def dig_with_shovel(self):
        """Dig at a digging spot using shovel."""
        current_room = self.game.get_current_room()
        if not current_room or current_room.dug:
            return

        if self.game.player.has_item(InventoryKey.SHOVEL):
            # Mark room as dug
            current_room.dug = True
            AppLogger.i("Dug with shovel!")

            # TODO: Add treasure items based on room configuration
            # For now, add some random items
            import random
            if random.random() < 0.7:  # 70% chance to find something
                from items import Coin, Gem
                found_item = Coin(count=random.randint(5, 15)) if random.random() < 0.6 else Gem(count=random.randint(1, 3))
                self.game.player.take_item(found_item)
                AppLogger.i(f"Found {found_item.__class__.__name__} buried here!")
            else:
                AppLogger.i("Nothing found...")

            self.game._pending_interaction = None
            self.game.game_state = GameState.ENTER_ROOM
        else:
            AppLogger.w("You don't have a shovel!")


# Example usage / test
if __name__ == '__main__':
    from game import Game
    from display_helper import DisplayHelper
    from chest import Chest
    from items import Coin, Gem, Key

    AppLogger.i("Testing RoomInteractionHandler...")

    # Create display helper and game
    display_helper = DisplayHelper(1800, 900)
    game = Game(display_helper)

    AppLogger.i("✓ RoomInteractionHandler initialized successfully!")
    AppLogger.i(f"Handler attached to game: {game.room_interaction_handler is not None}")

    # Test chest interaction
    current_room = game.get_current_room()
    if current_room:
        # Add a chest to the current room
        chest = Chest()
        chest.add_item(Coin(count=10))
        chest.add_item(Gem(count=2))
        current_room.chest = chest

        AppLogger.i(f"Added chest to {current_room.name}")
        AppLogger.i(f"Chest contents: {len(chest.contents)} items")

        # Give player a key
        game.player.take_item(Key())
        AppLogger.i(f"Player has key: {game.player.has_item(InventoryKey.KEY)}")

        # Test opening chest
        initial_coins = game.player.inventory[InventoryKey.COIN].count
        game.room_interaction_handler.open_chest_with_key()

        if chest.is_opened:
            AppLogger.i("Chest opened successfully!")
            AppLogger.i(f"Player coins: {initial_coins} → {game.player.inventory[InventoryKey.COIN].count}")
        else:
            AppLogger.w("Failed to open chest")

    # Test room interaction check
    game.room_interaction_handler.check_room_interactions()
    AppLogger.i("Room interaction check completed")
