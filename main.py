import numpy as np
import json
import psutil
import os

import pygame
import pygame.surfarray as sa
pygame.font.init()

from main_modules import renderer, input_handler
from world import World, Particles
from ships import Ship

np.set_printoptions(precision = 1, threshold = 1600, suppress = True)



class Screen:
    def __init__(self, width, height):
        self.WIN = None
        self.WIDTH = width
        self.HEIGHT = height
        # self.world = world
        self.init_window(width, height)

    def init_window(self, width, height):
        self.WIN = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    def update_display(self):
        pygame.display.update()

    def close(self):
        pygame.display.quit()



def live_world():
    world = World((500,300), 16) # 100,60
    with open('200x200_v1.json', 'r') as f:
        world.LAND = np.array(json.load(f), dtype = int)
    world.LAND = world.LAND[:, (world.LAND[0] < world.SIZE[0])&
                                    (world.LAND[0] >= 0)&
                                    (world.LAND[1] < world.SIZE[1])&
                                    (world.LAND[1] >= 0)]
    world.INIT_PHYSICAL_WORLD()
    return world


def report_memory():
    total = psutil.virtual_memory().total
    process = psutil.Process(os.getpid())
    ram = process.memory_info().rss
    return ram, ram/total



WIDTH, HEIGHT = (1200,600)
CELL_SIZE = 3
PA = None

diagnostics = [] # ship diagnostics
m_diagn = {} # memory diagnostics

def run():
    # global WORLD, RUN, ESC_MENU, RENDERER

    pygame.init()
    # WORLD = World((500,300), 16) # 100,60
    # WORLD.INIT_PHYSICAL_WORLD()
    # with open('200x200_v1.json', 'r') as f:
    #     WORLD.LAND = np.array(json.load(f), dtype = int)
    # WORLD.LAND = WORLD.LAND[:, (WORLD.LAND[0] < WORLD.SIZE[0])&
    #                               (WORLD.LAND[0] >= 0)&
    #                               (WORLD.LAND[1] < WORLD.SIZE[1])&
    #                               (WORLD.LAND[1] >= 0)]


    ## TEST WORLD    
    WORLD = World((500,300), 0)
    # WORLD.INIT_EMPTY_WORLD()
    WORLD.DISTANCE_FROM_SUN = np.zeros(WORLD.SIZE)
    WORLD.SUN = (0,0)
    

    ship = Ship(world = WORLD, position = (100,150), heading = -np.pi/2)
    # ship.main_sail.area = 0
    ship.main_sail.set = -np.pi/2
    ship.main_sail.give = -np.pi/6
    particles = Particles(12, WORLD, type = 'grid')

    SCREEN = Screen(WIDTH, HEIGHT)
    RENDERER = renderer.Renderer(SCREEN, WORLD, CELL_SIZE)
    INP_HANDLER = input_handler.InputHandler(SCREEN, RENDERER, WORLD)
    # ESC_MENU = EscapeMenu(owner = RENDERER, pos = ((RENDERER.PA_SIZE[0] - 1000)//2, (RENDERER.PA_SIZE[1] - 550)//2))
    RUN = True

    count = 0
    
    sun_index = 0
    clock = pygame.time.Clock()
    times = {
        'Sim':0,
        'Handle':0,
        'Render':0
        }
    # WORLD.CURRENTS[0,150,0] = 0
    # WORLD.CURRENTS[0,150,1] = 50
    # print(WORLD.STANDARD_CURRENT_STRENGTH_LEVEL)
    while RUN:
        print('______________________________________________')
        # WORLD.sim()
        WORLD.test_sim()
        particles.sim_particles()
        ship.sim(diagnostics)
        times['Sim'] += clock.tick_busy_loop() / 1000

        WORLD.WINDS[30:90,100:200,0] = 3
        WORLD.WINDS[30:90,100:200,1] = 0

        # diagnostics.append({'WINDS': WORLD.WINDS[int(ship.position[0]), int(ship.position[1])],
        #                     'CURRENTS': WORLD.CURRENTS[int(ship.position[0]), int(ship.position[1])],
        #                     'SHIP P': (ship.position),
        #                     'SHIP V': (ship.x, ship.y)})

        direction = INP_HANDLER.handle()
        if direction == 'quit':
            SCREEN.close()
            break
        times['Handle'] += clock.tick_busy_loop() / 1000

        RENDERER.draw_world()
        RENDERER.draw_particles(particles)
        RENDERER.draw_ship(ship)
        RENDERER.draw_ship_xy_diagram(ship)
        RENDERER.draw_ship_zx_diagram(ship)

        RENDERER.draw_post()
        SCREEN.update_display()
        RENDERER.clear_post()
        times['Render'] += clock.tick_busy_loop() / 1000


        
        count += 1

        # if count == 1000:
        #     RENDERER.DRAW = fill_color_sun
        # if count == 2000:
        #     RUN = False
        #     pygame.display.quit()
        # if count in [10,100,500,1000,2000,5000]:
        #     m_diagn[count] = report_memory()
        #     if count == 5000:
        #         return count, WORLD, times
            

        
if __name__ == '__main__':
    try:
        countc, worldc, timesc = run()
        avg = {k: v/countc for k, v in timesc.items()}
    
    finally:
        import pandas as pd
        # df = pd.DataFrame(diagnostics)
        # dictt = diagnostics[1]
        # cols = df.columns
        # for col in cols:
        #     if col != 'SHIP P':
        #         try:
        #             len(dictt[col])
        #             df[f'{col} SPEED'] = np.nan
        #             df[f'{col} DIR'] = np.nan
        #             for row in range(len(df)):
        #                 print(col, row)
        #                 df.loc[row, f'{col} SPEED'] = np.sqrt(df.loc[row, col][0]**2 + df.loc[row, col][1]**2)
        #                 df.loc[row, f'{col} DIR'] = np.arctan2(df.loc[row, col][1], df.loc[row, col][0])
        #         except TypeError:
        #             pass

        mdf = pd.DataFrame(m_diagn)






def save_land(world, name):
    land = world.LAND
    
    tup = tuple(land)
    t = np.empty(land.shape[1], dtype = 'object')
    t[:] = [(tup[0][x], tup[1][x]) for x in range(land.shape[1])]
    
    unq = np.unique(t)
    new_land = np.empty((2,unq.size), dtype = int)
    new_land[0] = [x[0] for x in unq]
    new_land[1] = [x[1] for x in unq]
    
    with open(f'{name}.json', 'w') as f:
        json.dump(new_land.tolist(), f)


