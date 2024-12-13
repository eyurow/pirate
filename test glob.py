import numpy as np
from testclass import Test, test
import pygame
import pygame.surfarray as sa



def run():
    pygame.init()
    WIN = pygame.display.set_mode((500,500), pygame.RESIZABLE)
    PA = sa.pixels3d(WIN)
    pygame.event.set_allowed(pygame.QUIT)

    run = True
    while run:
        events = pygame.event.get()
        print(events)
        for event in events:
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
            
        
        test(PA)

def kwargs(**kwargs):
    global D, W
    D = 'sun'

global D, W
D = 'light'
W = 100

gl = {D:D,
      W:W}


if __name__ == '__main__':
    x = 3
    if x >= 5:
        print(5)
    elif x >= 4:
        print(4)
    elif x >= 3:
        print(3)   
    elif x >= 2:
        print(2)    
    elif x >= 1:
        print(1)