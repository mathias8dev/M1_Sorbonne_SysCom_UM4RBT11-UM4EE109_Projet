from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player # Gestion de la dépendance circulaire pour eviter les conflits entre les fichiers

#-------------------------------------------Les classes abstraites-----------------------------------------------

class Item(ABC):
    """ Classe de base abstraite pour tous les items. """
    def __init__(self, count : int):
        self.count = count
    def use(self):
        pass 

class Food(Item) :
    def __init__(self, count : int = 1, add_step : int = 0) :
        super().__init__(count)
        self.add_step = add_step
    def use(self):
        if self.count > 1 :
            self.count = self.count - 1

class PermanentItem(Item):
    pass

#---------------------------------------------SECTION : Consommation rapide ------------------------------------
class Meal(Food):
    pass

class Banana(Food):
    pass

class Sandwich(Food):
    pass

class Apple(Food):
    pass

class Cake(Food):
    pass


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

