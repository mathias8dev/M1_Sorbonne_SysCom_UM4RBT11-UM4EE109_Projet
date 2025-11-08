from renderer import Renderer
from game import Game
from display_helper import DisplayHelper
from logging import AppLogger
import os

def run():
    import pygame
    pygame.init()

    # Configure logging to file by default
    # Create logs directory in the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(current_dir, "..", "..", "logs")
    log_file = os.path.join(log_dir, "app.log")
    AppLogger.set_log_file(log_file)

    AppLogger.i("Application started")

    display_info = pygame.display.Info()
    desktop_width = display_info.current_w
    desktop_height = display_info.current_h

    display_helper = DisplayHelper(desktop_width, desktop_height)
    game = Game(display_helper=display_helper)

    (min_width, min_height) = display_helper.compute_min_size()

    # Initialize dimensions
    display_helper.update_dimensions(min_width, min_height)
    screen = pygame.display.set_mode((display_helper.SCREEN_WIDTH, display_helper.SCREEN_HEIGHT), pygame.RESIZABLE)

    pygame.display.set_caption('Blue Prince by KALIPE | DIALLO | MOUSTADRANE')
    clock = pygame.time.Clock()
    renderer = Renderer(screen)

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # User requested size
                requested_width = event.w
                requested_height = event.h

                # Update dimensions based on requested size
                display_helper.update_dimensions(requested_width, requested_height)


                AppLogger.i(f"Resize requested: {requested_width}x{requested_height}")
                AppLogger.i(f"Screen set to: {display_helper.SCREEN_WIDTH}x{display_helper.SCREEN_HEIGHT}")
                AppLogger.i(f"Room size: {display_helper.ROOM_SIZE}px")

            elif event.type == pygame.KEYDOWN:
                # Pass keyboard events to game
                game.handle_keyboard_event(event)

        game.render(renderer)
        renderer.flip()
        clock.tick(DisplayHelper.FPS)

if __name__ == "__main__":
    run()
    
