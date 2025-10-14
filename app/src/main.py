def run():
    import pygame
    background_colour = (255,255,255)
    (width, height) = (1800, 820)
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Blue Prince by KALIPE | DIALLO | MOUSTADRANE')
    screen.fill(background_colour)
    left_side_color = (0, 0, 0) # La couleur gauche (noir)
    right_side_color = (255, 255, 255) # La couleur droite (blanc)
    
    room_size = 140
    
    pygame.draw.rect(screen, left_side_color, pygame.Rect(0, 0, room_size * 5, height))
    pygame.draw.rect(screen, right_side_color, pygame.Rect(room_size * 5, 0, width - room_size * 5, height))
    pygame.display.flip()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

if __name__ == "__main__":
    run()
    
