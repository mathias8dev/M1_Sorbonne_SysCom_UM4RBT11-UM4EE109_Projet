from position import Position
from typing import Dict, Optional
from items import *
from enum import Enum

class InventoryKey(Enum) :
    COIN = 0
    DICE = 1
    KEY = 2
    GEM = 3
    STEP = 4
    SHOVEL = 5
    METAL_DETECTOR = 6
    HAMMER = 7
    LOCK_PICK_KIT = 8
    RABBIT_FOOT = 9


class Player:
    def __init__(self, position : Position):
        self.inventory : Dict[InventoryKey, Item] = {
            InventoryKey.COIN : Coin(count = 0),
            InventoryKey.DICE : Dice(count = 10),
            InventoryKey.KEY : Key(count = 0),
            InventoryKey.GEM : Gem(count = 8),
            InventoryKey.STEP : Step(count = 70),
            InventoryKey.SHOVEL : Shovel(count = 0),
            InventoryKey.METAL_DETECTOR: MetalDetector(count = 0),
            InventoryKey.HAMMER : Hammer(count = 0),
            InventoryKey.LOCK_PICK_KIT : LockPickKit(count = 2),
            InventoryKey.RABBIT_FOOT : RabbitFoot(count = 9)
        }
        self.position = position
        self.current_selected_item : Optional[Item] = None

    def move_to(self, position : Position) :
        if self.inventory[InventoryKey.STEP].use() :
            self.position = position 
    
    def take_item(self, item : Item):
        """Add an item to the player's inventory."""
        if isinstance(item, Coin) :
            self.inventory[InventoryKey.COIN].add(item.count)
        elif isinstance(item, Gem) :
            self.inventory[InventoryKey.GEM].add(item.count)
        elif isinstance(item, Dice) :
            self.inventory[InventoryKey.DICE].add(item.count)
        elif isinstance(item, Key) :
            self.inventory[InventoryKey.KEY].add(item.count)
        elif isinstance(item, Step) :
            self.inventory[InventoryKey.STEP].add(item.count)
        elif isinstance(item, Shovel) :
            self.inventory[InventoryKey.SHOVEL].add(item.count)
        elif isinstance(item, MetalDetector) :
            self.inventory[InventoryKey.METAL_DETECTOR].add(item.count)
        elif isinstance(item, Hammer) :
            self.inventory[InventoryKey.HAMMER].add(item.count)
        elif isinstance(item, LockPickKit) :
            self.inventory[InventoryKey.LOCK_PICK_KIT].add(item.count)
        elif isinstance(item, RabbitFoot) :
            self.inventory[InventoryKey.RABBIT_FOOT].add(item.count)
        elif isinstance(item, Food) :
            # Food items restore steps when consumed
            self.inventory[InventoryKey.STEP].add(item.add_step)

    def has_item(self, item_key: InventoryKey) -> bool:
        """Check if player has at least one of the specified item."""
        return self.inventory.get(item_key, None) and self.inventory[item_key].count > 0

    def use_item(self) -> bool:
        """Use the currently selected item, if any."""
        if self.current_selected_item:
            return self.current_selected_item.use()
        return False

    def select_item(self, item_key: InventoryKey):
        """Select an item from the inventory."""
        self.current_selected_item = self.inventory.get(item_key, None)
    def get_stats(self) -> Dict[InventoryKey, Item]:
        """Return a dictionary of the player's stats."""
        return self.inventory