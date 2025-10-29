from abc import ABC, abstractmethod

# On importe 'Player' de cette façon pour éviter les erreurs d'importation circulaire
# (quand deux fichiers essaient de s'importer l'un l'autre).
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from player import Player # La classe Player sera dans player.py qui sera defini par ismael


class Item(ABC):
    """
    Classe de base abstraite pour tous les objets (items) du jeu.
    (Corresponds à la classe 'Item' du diagramme UML )

    Attributs:
        name (str): Le nom de l'item (ex: "Clé", "Gemme").
        description (str): Une courte description de ce que fait l'item.
        vizuel (str): Le chemin vers le fichier image de l'item .
    """
    
    def __init__(self, name: str, description: str, vizuel: str):
        """
        Initialise un item.
        """
        self.name = name
        self.description = description
        self.vizuel = vizuel # Corresponds à 'vizuel: str' dans l'UML 

    @abstractmethod
    def use(self, player: 'Player'):
        """
        Méthode abstraite pour utiliser l'item.
        (Corresponds à la méthode 'use()' du diagramme )
        
        L'effet concret sera défini dans chaque classe enfant.
        
        :param player: Le joueur qui utilise l'item.
        """
        # 'pass' signifie qu'il n'y a rien à faire dans la classe de base,
        # mais les classes enfants DEVRONT implémenter cette méthode.
        pass

    def __str__(self) -> str:
        """Une représentation textuelle simple, utile pour le débogage."""
        return self.name