def run():
    import pygame
    import os
    background_colour = (255,255,255)

    pygame.init() 
    desktop_size = pygame.display.get_desktop_sizes()[0]  # Returns a list of tuples 
    
    room_size = min(90,(desktop_size[1]- 200)/9)


    (width, height) = (min(1800, desktop_size[0]- 50), room_size * 9 + 5)
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Blue Prince by KALIPE | DIALLO | MOUSTADRANE')
    screen.fill(background_colour)
    left_side_color = (0, 0, 0) # La couleur gauche (noir)
    right_side_color = (255, 255, 255) # La couleur droite (blanc)
    
    
    pygame.draw.rect(screen, left_side_color, pygame.Rect(0, 0, room_size * 5 + 5, height))
    pygame.draw.rect(screen, right_side_color, pygame.Rect(room_size * 5 + 5, 0, width - (room_size * 5 + 5), height))
    
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(app_dir, 'assets')
    print(dir)
    examples = [os.path.join(assets_dir, "rooms/001-012/Attic_Icon.webp") for i in range (9)]
    for i in range(5):
        loaded_image = pygame.transform.scale(pygame.image.load(examples[i]).convert(), (room_size, room_size))
        
        screen.blit(loaded_image, (i * room_size + 2, height - room_size - 2))
        
    for i in range(9):
        loaded_image = pygame.transform.scale(pygame.image.load(examples[i]).convert(), (room_size, room_size))
        
        screen.blit(loaded_image, (0, room_size * i +2,))
    
    
    pygame.display.flip()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

if __name__ == "__main__":
    run()
    
