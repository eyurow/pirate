import numpy as np
import pygame

def test(PA):
    PA[:,:] = (150,150,150)
    pygame.display.update()

class Test:
    v = 1
    def __init__(self):
        self.ar = np.arange(9).reshape((3,3))

    @classmethod
    def p(cls):
        cls.v += 1

    def __getitem__(self, key):
        return self.ar[key]

    def __setitem__(self, key, val):
        self.ar[key] = val

def run():
    global globi, globa
    globi = 10
    globa = np.zeros((3,3,3))
    c = Test(10, np.zeros((5,5)))
    c.mr()
    print(globi, globa)

if __name__ == '__main__':
    t = Test()
    t.p()
    t.v += 1
    print(t.v)
    Test.v = 10
    b = Test()
    print(b.v)