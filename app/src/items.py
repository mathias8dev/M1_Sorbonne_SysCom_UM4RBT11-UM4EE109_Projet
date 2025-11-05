from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player # Gestion de la dépendance circulaire pour eviter les conflits entre les fichiers

#-------------------------------------------Les classes abstraites-----------------------------------------------

class Item(ABC):
    """ Classe de base abstraite pour tous les items. """
    def __init__(self, count : int):
        self.count = count
    def use(self) -> bool:
        pass 
    
    def add(self, count : int):
        self.count += count
        
    
class Food(Item) :
    def __init__(self, count : int = 1, add_step : int = 0) :
        super().__init__(count)
        self.add_step = add_step
    def use(self) -> bool:
        if self.count > 1 :
            self.count = self.count - 1
            return True
        return False
    
            
class PermanentItem(Item):
    
    def use(self) -> bool:
        return True


class Collectable(Item) :
    def __init__(self, count : int = 1) :
        super().__init__(count)
    def use(self) -> bool:
        if self.count > 0 :
            self.count = self.count - 1
            return True
        return False

#---------------------------------------------SECTION : Consommation rapide ------------------------------------
class Meal(Food):
    def __init__(self, count : int = 1, add_step : int = 25) :
        super().__init__(count, add_step)

class Banana(Food):
    def __init__(self, count : int = 1, add_step : int = 3) :
        super().__init__(count, add_step)

class Sandwich(Food):
    def __init__(self, count : int = 1, add_step : int = 15) :
        super().__init__(count, add_step)

class Apple(Food):
    def __init__(self, count : int = 1, add_step : int = 2) :
        super().__init__(count, add_step)

class Cake(Food):
    def __init__(self, count : int = 1, add_step : int = 10) :
        super().__init__(count, add_step)


#------------------------------- SECTION :Permananent  Items--------------------------------------


class MetalDetector(PermanentItem):
    pass

class Shovel(PermanentItem):
    pass

class Hammer(PermanentItem):
    pass

class LockPickKit(PermanentItem):
    pass

class RabbitFoot(PermanentItem):
    pass

#------------------------------- SECTION :Collectable--------------------------------------


class Step(Collectable):
    pass

class Coin(Collectable):
    pass

class Gem(Collectable):
    pass

class Key(Collectable):
    pass

class Dice(Collectable):
    pass



