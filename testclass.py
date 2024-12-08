import numpy as np
import pygame
import pygame.surfarray as sa


def set_pixelarray(): #(pa, world, WIDTH, HEIGHT, CELL_SIZE, world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y):
    print(globals())
    pa[:20] = (0,0,0)
           



def test():
    print(globals())

    glob[2,2] = 10
    print(locals())

class Test:
    def __init__(self):
        pass

    def t(self):
        glob[:, 5:] = 10

# glob = None
# glob = np.zeros((10,10))

WIDTH, HEIGHT = (1200,600)
pa = None

def run():
    pygame.init()
    
    global WIDTH, HEIGHT, pa
    WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE) #(WIDTH, HEIGHT))
    pa = sa.pixels3d(WINDOW)

    col = 50
    
    set_pixelarray()

    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type in [pygame.VIDEORESIZE, pygame.VIDEOEXPOSE]:
                pa = sa.pixels3d(WINDOW)
                pa[...] = col
                set_pixelarray()
                col += 10
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                break
        pygame.display.update()


if __name__ == '__main__':
    run()