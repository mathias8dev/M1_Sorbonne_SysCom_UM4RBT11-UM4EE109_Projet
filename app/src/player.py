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


class player:
    def __init__(self, position : Position):
        self.inventory : Dict[int, Item] = {InventoryKey.COIN : Coin(count = 0),
                              InventoryKey.DICE : Dice(count = 0),
                              InventoryKey.KEY : Key(count = 0),
                              InventoryKey.GEM : Gem(count = 2),
                              InventoryKey.STEP : Step(count = 70),
                              InventoryKey.SHOVEL : Shovel(count = 0),
                              InventoryKey.HAMMER : Hammer(count = 0),
                              InventoryKey.LOCK_PICK_KIT : LockPickKit(count = 0),
                              InventoryKey.RABBIT_FOOT : RabbitFoot(count = 0)}
        self.position = position
        self.current_selected_item : Optional[Item] = None

    def move_to(self, position : Position) :
        if self.inventory[InventoryKey.STEP].use() :
            self.position = position 
    
    def take_item(self, item : Item):
        
        if isinstance(item, Gem) : 
            self.inventory.update({InventoryKey.GEM : self.inventory[InventoryKey.GEM].add(item.count)})
        if isinstance(item, Dice) : 
            self.inventory.update({InventoryKey.DICE: self.inventory[InventoryKey.DICE].add(item.count)})       
        if isinstance(item, Key) : 
            self.inventory.update({InventoryKey.KEY : self.inventory[InventoryKey.KEY].add(item.count)})
        if isinstance(item, Step) : 
            self.inventory.update({InventoryKey.STEP : self.inventory[InventoryKey.STEP].add(item.count)})           
        if isinstance(item, Shovel) : 
            self.inventory.update({InventoryKey.SHOVEL : self.inventory[InventoryKey.SHOVEL].add(item.count)})
        if isinstance(item, Hammer) : 
            self.inventory.update({InventoryKey.HAMMER : self.inventory[InventoryKey.HAMMER].add(item.count)})
        if isinstance(item, LockPickKit) : 
            self.inventory.update({InventoryKey.LOCK_PICK_KIT : self.inventory[InventoryKey.LOCK_PICK_KIT].add(item.count)})
        if isinstance(item, RabbitFoot) : 
            self.inventory.update({InventoryKey.RABBIT_FOOT : self.inventory[InventoryKey.RABBIT_FOOT].add(item.count)})
            
        if isinstance(item, Food) : 
            self.inventory.update({InventoryKey.STEP : self.inventory[InventoryKey.STEP].add(item.add_step)})