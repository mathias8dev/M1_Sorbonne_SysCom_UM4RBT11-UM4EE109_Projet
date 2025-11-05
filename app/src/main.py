from renderer import Renderer
from game import Game
from display_helper import DisplayHelper

def run():
    import pygame
    pygame.init()
    desktop_size = pygame.display.get_desktop_sizes()[0]

    # Création de la fenêtre et configuration du titre
    game = Game(desktop_size=desktop_size)
    display_helper = DisplayHelper()
    (min_width, min_height) = display_helper.compute_min_size()
    screen = pygame.display.set_mode((min_width, min_height), pygame.RESIZABLE)
    
    pygame.display.set_caption('Blue Prince by KALIPE | DIALLO | MOUSTADRANE')
    clock = pygame.time.Clock()
    renderer = Renderer(screen)

    # Boucle d'événements principale minimaliste (ferme la fenêtre room_size = min(90, (desktop_size[1] - 200) / 9)quand on clique sur la croix)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                new_width = max(event.w, min_width)
                new_height = max(event.h, min_height)
                display_helper.update_dimensions(new_width, new_height)
                screen = pygame.dpslay.set_mode((DisplayHelper.SCREEN_WIDTH, DisplayHelper.SCREEN_HEIGHT), pygame.RESIZABLE)
                renderer.screen = screen

                print(f"Window resized to {new_width}x{new_height}, Room size: {DisplayHelper.ROOM_SIZE}px")
        
        game.render(renderer)
        renderer.flip()
        clock.tick(DisplayHelper.FPS)

if __name__ == "__main__":
    run()
    
