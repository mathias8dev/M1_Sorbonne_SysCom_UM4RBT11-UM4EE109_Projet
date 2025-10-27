import pygame
import os

class Game:
    def __init__(self):
        # Initialisation de Pygame
        pygame.init()
        
        # Configuration des couleurs
        self.background_colour = (255, 255, 255)
        self.white_color = (255, 255, 255)  # blanc pour la partie droite
        self.black_color = (0, 0, 0)
        
        # Configuration de la police
        self.game_font = pygame.font.SysFont('Arial', 30, True, False)
        
        # Calcul de la taille de la fenêtre
        self._calculate_window_size()
        
        # Création de la fenêtre
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Blue Prince by KALIPE | DIALLO | MOUSTADRANE')
        
        # Configuration des chemins
        self._setup_assets_path()
        
        # État du jeu
        self.running = True
        
        # Initialisation de l'affichage
        self._setup_initial_display()
    
    def _calculate_window_size(self):
        """Calcule la taille optimale de la fenêtre"""
        # Récupère la taille du bureau/écran principal
        desktop_size = pygame.display.get_desktop_sizes()[0]
        
        # Calcul d'une taille de « case » (room_size) pour afficher les icônes
        self.room_size = int(min(90, (desktop_size[1] - 200) / 9))
        
        # Calcul de la largeur et hauteur de la fenêtre
        self.width = int(min(1800, desktop_size[0] - 50))
        self.height = int(self.room_size * 9 + 5)
        
        # Position de la partie droite
        self.right_side_x = int(self.room_size * 5 + 5)
    
    def _setup_assets_path(self):
        """Configure le chemin vers les assets"""
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(app_dir, 'assets')
        
        # DEBUG : affiche la référence à la fonction/objet dir
        print(dir)
        
        # Prépare une liste d'exemples d'images
        self.examples = [os.path.join(self.assets_dir, "rooms/001-012/Attic_Icon.webp") for i in range(9)]
    
    def _setup_initial_display(self):
        """Configure l'affichage initial du jeu"""
        # Remplissage initial de la fenêtre
        self.screen.fill(self.background_colour)
        
        # Dessine deux rectangles pour créer un split gauche/droite
        pygame.draw.rect(self.screen, self.black_color, 
                        pygame.Rect(0, 0, self.right_side_x, self.height))
        pygame.draw.rect(self.screen, self.white_color, 
                        pygame.Rect(self.right_side_x, 0, self.width - self.right_side_x, self.height))
        
        # Charge et affiche les images
        self._load_and_display_images()
        
        # Affiche l'interface utilisateur
        self._display_ui_text()
        
        # Met à jour l'affichage
        pygame.display.flip()
    
    def _load_and_display_images(self):
        """Charge et affiche les images sur l'interface"""
        # Affiche les 5 premières images en bas (partie gauche)
        for i in range(5):
            loaded_image = pygame.transform.scale(
                pygame.image.load(self.examples[i]).convert(), 
                (self.room_size, self.room_size)
            )
            self.screen.blit(loaded_image, (int(i * self.room_size + 2), int(self.height - self.room_size - 2)))
        
        # Affiche 9 images en colonne sur la gauche
        for i in range(9):
            loaded_image = pygame.transform.scale(
                pygame.image.load(self.examples[i]).convert(), 
                (self.room_size, self.room_size)
            )
            self.screen.blit(loaded_image, (0, int(self.room_size * i + 2)))
    
    def _display_ui_text(self):
        """Affiche les textes de l'interface utilisateur"""
        # Création des surfaces de texte
        inventory_text = self.game_font.render("Inventory:", 1, self.black_color)
        shovel_text = self.game_font.render("Shovel", 1, self.black_color)
        metal_detector_text = self.game_font.render("Metal Detector", 1, self.black_color)
        
        # Transfert des surfaces dans la fenêtre principale
        self.screen.blit(inventory_text, (self.right_side_x + 60, 70))
        self.screen.blit(shovel_text, (self.right_side_x + 60, 120))
        self.screen.blit(metal_detector_text, (self.right_side_x + 60, 170))
    
    def run(self):
        """Boucle principale du jeu"""
        while self.running:
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

if __name__ == "__main__":
    game = Game()
    game.run()