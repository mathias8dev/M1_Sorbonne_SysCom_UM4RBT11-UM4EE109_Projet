def run():
    import pygame
    import os
    from renderer import Renderer
    from color import Color
    from position import Position

    # Couleur de fond de la fenêtre
    background_colour = (255, 255, 255)
    

    # Initialisation de pygame (doit être appelée avant d'utiliser les API pygame)
    pygame.init()
    
    game_font = pygame.font.SysFont('Arial', 30, True, False)

    # Récupère la taille du bureau/écran principal. pygame.display.get_desktop_sizes()
    # renvoie une liste de résolutions; on prend le premier élément.
    desktop_size = pygame.display.get_desktop_sizes()[0]

    # Calcul d'une taille de « case » (room_size) pour afficher les icônes.
    # On limite la taille à 90px max et on prend en compte la hauteur de l'écran
    # pour tenir 9 cases avec une marge.
    room_size = min(90, (desktop_size[1] - 200) / 9)

    # Calcul de la largeur et hauteur de la fenêtre. La largeur est limitée
    # à 1800px et laisse une petite marge par rapport à la largeur du bureau.
    (width, height) = (min(1800, desktop_size[0] - 50), room_size * 9 + 5)

    # Création de la fenêtre et configuration du titre
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Blue Prince by KALIPE | DIALLO | MOUSTADRANE')

    # Remplissage initiale de la fenêtre
    screen.fill(background_colour)

    # Définitions des couleurs pour la mise en page (gauche / droite)
    white_color = (255, 255, 255)  # blanc pour la partie droite
    black_color = (0, 0, 0)
    
    right_side_x = room_size * 5 + 5

    # Dessine deux rectangles couvrant l'écran pour créer un split gauche/droite
    pygame.draw.rect(screen, black_color, pygame.Rect(0, 0, right_side_x, height))
    pygame.draw.rect(screen, white_color, pygame.Rect(right_side_x, 0, width - right_side_x, height))

    # Construction du chemin vers le dossier assets à partir du fichier courant
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(app_dir, 'assets')

    # DEBUG : affiche la référence à la fonction/objet dir (probablement non voulu)
    # Remarque: ceci affichera le built-in 'dir' et non le contenu du dossier.
    print(dir)

    # Prépare une liste d'exemples d'images (ici on réutilise la même image 9 fois)
    examples = [os.path.join(assets_dir, "rooms/001-012/Attic_Icon.webp") for i in range(9)]

    # Affiche les 5 premières images en bas (une rangée sur la partie gauche)
    for i in range(5):
        loaded_image = pygame.transform.scale(pygame.image.load(examples[i]).convert(), (room_size, room_size))
        # Position horizontale dépendante de l'indice, verticale en bas avec marge de 2px
        screen.blit(loaded_image, (i * room_size + 2, height - room_size - 2))

    # Affiche 9 images en colonne sur la gauche (une par case)
    for i in range(9):
        loaded_image = pygame.transform.scale(pygame.image.load(examples[i]).convert(), (room_size, room_size))
        # Position horizontale à 0 (gauche), verticale calculée par l'indice
        screen.blit(loaded_image, (0, room_size * i + 2))
        
    
    # Création des surfaces
    inventory_text = game_font.render("Inventory:", 1, black_color)
    shovel_text = game_font.render("Shovel", 1, black_color)
    metal_detector_text = game_font.render("Metal Detector", 1, black_color)
    #  Transfert des surfaces dans la fenêtre principale
    screen.blit(inventory_text, (right_side_x + 60, 70))
    screen.blit(shovel_text, (right_side_x + 60, 120))
    screen.blit(metal_detector_text, (right_side_x + 60, 170))

    renderer = Renderer(screen)
    renderer.display_text("MATHIAS LE GITHUB MAN", Color(200,255,100), "Arial", 64 ,Position(right_side_x,0))

    # Met à jour l'affichage pour rendre visibles les dessins
    pygame.display.flip()

    # Boucle d'événements principale minimaliste (ferme la fenêtre quand on clique sur la croix)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


if __name__ == "__main__":
    run()
    
