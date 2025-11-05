from typing import List
from items import Item, Key, Hammer

class Chest:
    def __init__(self, ):
        self.is_opened : bool = False
        self.contents : list[Item] = []
        
    def add_item(self, item : Item):
        self.contents.append(item)
        
    def open_with_key(self, key: Key) -> bool:
        if not self.is_opened and key.use():
            self.is_opened = True
            return True
        return False
    
    def open_with_hammer(self, hammer: Hammer) -> bool:
        if not self.is_opened and hammer.use():
            self.is_opened = True
            return True
        return False
    
    def get_contents(self) -> List[Item]:
        if self.is_opened:
            return self.contents
        return []
    
    