from renderer import Renderer
from game import Game

def run():
    import pygame
    pygame.init()
    desktop_size = pygame.display.get_desktop_sizes()[0]

    # Création de la fenêtre et configuration du titre
    game = Game(desktop_size=desktop_size)
    screen_size = game.get_screen_size()
    screen = pygame.display.set_mode(screen_size.to_tuple())
    pygame.display.set_caption('Blue Prince by KALIPE | DIALLO | MOUSTADRANE')
    renderer = Renderer(screen)
    game.render(renderer)
    pygame.display.flip()

    # Boucle d'événements principale minimaliste (ferme la fenêtre room_size = min(90, (desktop_size[1] - 200) / 9)quand on clique sur la croix)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


if __name__ == "__main__":
    run()
    
