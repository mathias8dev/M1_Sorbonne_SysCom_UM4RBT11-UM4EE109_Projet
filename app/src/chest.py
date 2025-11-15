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


# Example usage / test
if __name__ == '__main__':
    from logging import AppLogger
    from items import Coin, Gem, Key, Hammer

    AppLogger.i("Testing Chest class...")

    # Create chest
    chest = Chest()
    AppLogger.i(f"Created chest, is_opened: {chest.is_opened}")

    # Add items
    chest.add_item(Coin(count=10))
    chest.add_item(Gem(count=5))
    AppLogger.i(f"Added items to chest, count: {len(chest.contents)}")

    # Try to get contents before opening
    contents_before = chest.get_contents()
    AppLogger.i(f"Contents before opening: {len(contents_before)} items")
    assert len(contents_before) == 0, "Shouldn't get contents before opening"

    # Open with key
    key = Key()
    success = chest.open_with_key(key)
    AppLogger.i(f"Opened with key: {success}")
    assert chest.is_opened

    # Get contents after opening
    contents_after = chest.get_contents()
    AppLogger.i(f"Contents after opening: {len(contents_after)} items")
    assert len(contents_after) == 2

    # Test opening with hammer
    chest2 = Chest()
    chest2.add_item(Coin(count=20))
    hammer = Hammer(count=1)
    success2 = chest2.open_with_hammer(hammer)
    AppLogger.i(f"Opened chest 2 with hammer: {success2}")
