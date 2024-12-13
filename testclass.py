import numpy as np
import pygame

def test(PA):
    PA[:,:] = (150,150,150)
    pygame.display.update()

class Test:
    def __init__(self, intt, ar):
        self.intt = intt
        self.ar = ar

    def mi(self):
        self.intt += 1
    
    def ma(self):
        self.ar[1,1] = 10

    def mr(self):
        global globi
        globi += 5
        globa[:2] = (3,3,3)

def run():
    global globi, globa
    globi = 10
    globa = np.zeros((3,3,3))
    c = Test(10, np.zeros((5,5)))
    c.mr()
    print(globi, globa)

if __name__ == '__main__':

    run()