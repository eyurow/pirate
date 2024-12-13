from world import World, Wind, WindGroup

from vis import *
from ui import EscapeMenu, Context
from indices import get_pixel_indices
from generics import get_margin
import numpy as np
import json

import pygame
import pygame.surfarray as sa
pygame.font.init()


np.set_printoptions(precision = 2, threshold = 1600, suppress = True)



def wait_for_input(mouse_movement = False):
    waiting = True
    while waiting:
        event = pygame.event.wait()
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN):
            return 'quit'
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            return True
        
        elif event.type in [pygame.VIDEORESIZE, pygame.VIDEOEXPOSE]:
            return 'resize'
        # elif event.type == pygame.VIDEOEXPOSE:
        #     return 'resize'
            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            return 'text'
            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            return 'fill'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            return 'light'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            return 'sun'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
            return 'sun2'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            return 'ind'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            return 'red'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            return 'blue'
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print(f'DOWN: {event}')
            return event.pos
        elif event.type == pygame.MOUSEMOTION and mouse_movement:
            print(f'MOVE: {event}')
            return event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            print(f'UP: {event}')
            return 0


def receive_inputs(mouse_movement = False):
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN):
            return 'quit'
        
        elif event.type == pygame.VIDEORESIZE:
            return 'resize'
        elif event.type == pygame.VIDEOEXPOSE:
            return 'resize'
        
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'escape menu'
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            return 'text'
            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            return 'fill'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            return 'light'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            return 'sun'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
            return 'sun2'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            return 'ind'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            return 'red'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            return 'blue'
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print(f'DOWN: {event}')
            return event.pos
        elif event.type == pygame.MOUSEMOTION and mouse_movement:
            print(f'MOVE: {event}')
            return event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            print(f'UP: {event}')
            return 0
        

class InputHandler:
    def __init__(self, screen, renderer):
        self.screen = screen
        self.renderer = renderer

        self.context = 'run'
        self.queue = []
        self.mouse_movement = False
        self.add_land = []

    def default_handle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            self.renderer.set_draw(pa_fill_color)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            self.renderer.set_draw(fill_color_light)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            self.renderer.set_draw(fill_color_sun)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
            self.renderer.set_draw(fill_color_sun2)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            self.renderer.set_draw(fill_ind_colors)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.renderer.set_draw(fill_ind_red)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            self.renderer.set_draw(fill_fluc_blue)
        
        elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or (event.type == pygame.MOUSEMOTION and self.mouse_movement):
            modified_pos = (event.pos[0] - self.renderer.START_PIXEL_X + self.renderer.WORLD_SLICER_X.start * self.renderer.CELL_SIZE,
                            event.pos[1] - self.renderer.START_PIXEL_Y + self.renderer.WORLD_SLICER_Y.start * self.renderer.CELL_SIZE)
            same_pos_size = WORLD.LAND[:, (WORLD.LAND[0] == modified_pos[0]//self.renderer.CELL_SIZE)& 
                                        (WORLD.LAND[1] == modified_pos[1]//self.renderer.CELL_SIZE)].size
            if same_pos_size == 0 and modified_pos not in self.add_land:
                self.add_land.append(modified_pos)
            self.mouse_movement = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            add_land_array = np.array(self.add_land).T // self.renderer.CELL_SIZE
            WORLD.LAND = np.concatenate([WORLD.LAND, add_land_array], axis = 1) #, dtype = int)
            self.mouse_movement = False

    
    def handle(self):
        global WORLD

        handling = True
        events = []
        # events = pygame.event.get()
        if pygame.event.peek(pygame.QUIT):
            return self.quit()
        if pygame.event.peek([pygame.VIDEORESIZE, pygame.VIDEOEXPOSE]):
            self.resize()

        while handling:
            match self.context:
                case 'run':
                    handling = False # set to False, will be intercepted below if need be (quit, EscapeMenu, pause)
                    events = pygame.event.get()
                    # for event in events:
                    for _ in range(len(events)):
                        event = events.pop(0)

                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            ESC_MENU.display()
                            self.context = 'escape menu'
                            handling = True
                            break
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                            self.context = 'pause'
                            handling = True

                        else:
                            self.default_handle(event)
                            
                case 'pause':
                    waiting = True
                    while waiting:
                        if events:
                            event = events.pop(0)
                        else:
                            event = pygame.event.wait()

                        if event.type == pygame.QUIT:
                            return self.quit()
                        elif event.type in [pygame.VIDEORESIZE, pygame.VIDEOEXPOSE]:
                            self.resize()
                        
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            ESC_MENU.display()
                            self.context = 'escape menu'
                            waiting = False
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                            self.context = 'run'
                            waiting = False
                            handling = False
                        
                        else:
                            self.default_handle(event)


                case 'escape menu':
                    waiting = True
                    while waiting:
                        event = pygame.event.wait()
                        if event.type == pygame.QUIT:
                            return self.quit()
                        elif event.type in [pygame.VIDEORESIZE, pygame.VIDEOEXPOSE]:
                            self.resize()
                            ESC_MENU.display()
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: # reset context, close menu and continue frame
                            ESC_MENU.bcontext.restore_base()
                            self.context = 'run'
                            waiting = False
                            handling = False
                        
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            pos = (event.pos[0] - self.renderer.START_PIXEL_X, event.pos[1] - self.renderer.START_PIXEL_Y)
                            ctx = ESC_MENU.context.button_context
                            check = ctx.map[4, (ctx.map[0] <= pos[0])&(ctx.map[1] <= pos[1])&(ctx.map[2] >= pos[0])&(ctx.map[3] >= pos[1])] # return any buttons on context map where click was within button borders
                            if check.size > 0:
                                button = ctx.key[check[0]]
                                button.press(self)
                            else:
                                if ESC_MENU.bcontext.active:
                                    ESC_MENU.refresh_base()
                


    def quit(self):
        global RUN
        RUN = False
        pygame.display.quit()
        return 'quit'
    
    def resize(self):
        self.renderer.refresh_PA()
        self.renderer.set_pixelarray()
        ESC_MENU.resize()        




class Screen:
    def __init__(self, width, height):
        self.WIN = None
        self.WIDTH = width
        self.HEIGHT = height
        self.init_window(width, height)

    def init_window(self, width, height):
        self.WIN = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    def update_display(self):
        pygame.display.update()

    



class Renderer:
    def __init__(self, screen, cell_size):
        self.screen = screen
        self.PA = None
        # self.WIDTH = None
        # self.HEIGHT = None
        self.CELL_SIZE = cell_size
        self.DRAW = fill_ind_colors
        # self.world = world  --  if moved out of main will need to tie to world here
        self.WORLD_SLICER_X = slice(0, WORLD.SIZE[0])
        self.WORLD_SLICER_Y = slice(0, WORLD.SIZE[0])
        self.START_PIXEL_X = 0
        self.START_PIXEL_Y = 0

    def refresh_PA(self):
        self.PA = sa.pixels3d(self.screen.WIN)
        self.screen.WIDTH, self.screen.HEIGHT = self.PA.shape[:2]
    
    def set_draw(self, func):
        self.DRAW = func
    
    def draw_world(self, sun_dist):
        self.DRAW(self.PA, WORLD.THETAS[self.WORLD_SLICER_X, self.WORLD_SLICER_Y, 1], sun_dist[self.WORLD_SLICER_X, self.WORLD_SLICER_Y], self.CELL_SIZE, WORLD.SIZE)
        draw_land(self.PA, WORLD.LAND, self.CELL_SIZE, (self.WORLD_SLICER_X, self.WORLD_SLICER_Y))
        draw_sun(self.PA, WORLD.SUN, self.CELL_SIZE, (self.WORLD_SLICER_X, self.WORLD_SLICER_Y))
        self.update_display()

    def draw_menu(self, menu):
        # screen_blur(PA)
        self.PA[menu.left_marg:menu.right_marg, menu.top_marg:menu.bot_marg] = (166, 93, 7)
        self.PA[menu.left_marg, menu.top_marg:menu.bot_marg] = (0,0,0)
        self.PA[menu.right_marg, menu.top_marg:menu.bot_marg] = (0,0,0)
        self.PA[menu.left_marg:menu.right_marg, menu.top_marg] = (0,0,0)
        self.PA[menu.left_marg:menu.right_marg, menu.bot_marg] = (0,0,0)

    def draw_button(self, button, menu_pos = (0,0)):
        if button.type == 'array':
            self.PA[menu_pos[0] + button.pos[0]:menu_pos[0] + button.pos[0] + button.size[0], 
                    menu_pos[1] + button.pos[1]:menu_pos[1] + button.pos[1] + button.size[1]] = button.array
            
        elif button.type == 'index':
            self.PA[(menu_pos[0] + button.pos[0] + button.text_ind[0], menu_pos[1] + button.pos[0] + button.text_ind[1])] = button.text_color
            self.PA[(menu_pos[0] + button.border_ind[0], menu_pos[1] + button.border_ind[1])] = button.border_color

        elif button.type == 'text':
            self.PA[(menu_pos[0] + button.pos[0] + button.text_ind[0], menu_pos[1] + button.pos[0] + button.text_ind[1])] = button.text_color


    
    def set_pixelarray(self):
        if self.screen.WIDTH > WORLD.SIZE[0] * self.CELL_SIZE:
            start, end = get_margin(self.screen.WIDTH, WORLD.SIZE[0] * self.CELL_SIZE)
            self.PA[:start] = (0,0,0)
            self.PA[-end:] = (0,0,0)
            self.PA = self.PA[start:-end]
            self.START_PIXEL_X = start
            self.WORLD_SLICER_X = slice(0, WORLD.SIZE[0])
        elif self.screen.WIDTH < WORLD.SIZE[0] * self.CELL_SIZE:
            # get WORLD slicer
            start, end = get_margin(WORLD.SIZE[0], self.screen.WIDTH // self.CELL_SIZE)
            self.WORLD_SLICER_X = slice(start, WORLD.SIZE[0] - end)
            # get pixel slicer
            if self.screen.WIDTH > self.CELL_SIZE * (WORLD.SIZE[0] - start - end): # if screen WIDTH greater than sliced WORLD size
                start, end = get_margin(self.screen.WIDTH, self.CELL_SIZE * (WORLD.SIZE[0] - start - end))
                self.PA[:start] = (0,0,0)
                self.PA[-end:] = (0,0,0)
                self.PA = self.PA[start:-end]
                self.START_PIXEL_X = start
        elif self.screen.WIDTH == WORLD.SIZE[0] * self.CELL_SIZE:
            self.START_PIXEL_X = 0
            self.WORLD_SLICER_X = slice(0, WORLD.SIZE[0])
        
        if self.screen.HEIGHT > WORLD.SIZE[1] * self.CELL_SIZE:
            start, end = get_margin(self.screen.HEIGHT, WORLD.SIZE[1] * CELL_SIZE)
            self.PA[:, :start] = (0,0,0)
            self.PA[:, -end:] = (0,0,0)
            self.PA = self.PA[:, start:-end]
            self.START_PIXEL_Y = start
            self.WORLD_SLICER_Y = slice(0, WORLD.SIZE[1])
        elif self.screen.HEIGHT < WORLD.SIZE[1] * self.CELL_SIZE:
            # get WORLD slicer
            start, end = get_margin(WORLD.SIZE[1], self.screen.HEIGHT // self.CELL_SIZE)
            self.WORLD_SLICER_Y = slice(start, WORLD.SIZE[1] - end)
            # get pixel slicer
            if self.screen.HEIGHT > self.CELL_SIZE * (WORLD.SIZE[1] - start - end): # if screen WIDTH greater than sliced WORLD size
                start, end = get_margin(self.screen.HEIGHT, self.CELL_SIZE * (WORLD.SIZE[1] - start - end))
                self.PA[:, :start] = (0,0,0)
                self.PA[:, -end:] = (0,0,0)
                self.PA = self.PA[:, start:-end]
                self.START_PIXEL_Y = start
        elif self.screen.HEIGHT == WORLD.SIZE[1] * self.CELL_SIZE:
            self.START_PIXEL_Y = 0
            self.WORLD_SLICER_Y = slice(0, WORLD.SIZE[1])

    def update_display(self):
        self.screen.update_display()
    


            
WIDTH, HEIGHT = (1200,600)
CELL_SIZE = 3
PA = None

def run():
    global WORLD, RUN, ESC_MENU

    pygame.init()
    WORLD = World((500,300), 16) # 100,60
    with open('200x200_v1.json', 'r') as f:
        WORLD.LAND = np.array(json.load(f), dtype = int)
    WORLD.LAND = WORLD.LAND[:, (WORLD.LAND[0] < WORLD.SIZE[0])&
                                  (WORLD.LAND[0] >= 0)&
                                  (WORLD.LAND[1] < WORLD.SIZE[1])&
                                  (WORLD.LAND[1] >= 0)]

    SCREEN = Screen(WIDTH, HEIGHT)
    RENDERER = Renderer(SCREEN, CELL_SIZE)
    INP_HANDLER = InputHandler(SCREEN, RENDERER)
    ESC_MENU = EscapeMenu(RENDERER)
    RUN = True

    RENDERER.refresh_PA()
    RENDERER.set_pixelarray()
    ESC_MENU.resize()

    count = 0
    sun_index_count = WORLD.SOLAR_BAND[0].size
    sun_index = 0
    clock = pygame.time.Clock()
    times = {
        'Sim':0,
        'Handle':0,
        'Render':0
        }

    while RUN:
        #times['Key'] += clock.tick_busy_loop() / 1000
        
        ########################
        ### SIMULATE WORLD ###
        WORLD.apply_coriolis_force()
        # WORLD.apply_centrifugal_force()
        
        if count % WORLD.SUN_FRAMES == 0:
            sun_index += 1
            if sun_index == sun_index_count:
                sun_index = 0
            WORLD.move_sun(sun_index)
            sun_dist = WORLD.calc_solar_pressure_and_distance()
        
        ### Prop Winds and Set Current Thetas
        '''
        # OLD WINDS
        WORLD.old_propogate_winds/pressure()
        WORLD.set_current_thetas()
        '''
        WORLD.apply_pressure_winds()
        
        ## Set Winds
        WORLD.set_wind_thetas()
        WORLD.propogate_array(array = 'winds')
        WORLD.set_winds()
        WORLD.apply_winds_to_currents()
        # #times['Prop Winds'] += clock.tick_busy_loop() / 1000

        ## Set Current Thetas
        WORLD.impact_land()
        WORLD.set_current_thetas()
        times['Sim'] += clock.tick_busy_loop() / 1000

        ####################
        ### HANDLE INPUTS ###
        direction = INP_HANDLER.handle()
        if direction == 'quit':
            break
        times['Handle'] += clock.tick_busy_loop() / 1000

        #####################
        ### RENDER ###
        RENDERER.draw_world(sun_dist)
        times['Render'] += clock.tick_busy_loop() / 1000
        
        
        ######################
        ### SIMULATE WORLD ###
        WORLD.propogate_array(array = 'currents')
        WORLD.set_currents()

        WORLD.apply_energy_loss()
        # times['Sim2'] += clock.tick_busy_loop() / 1000
        
        count += 1
        
        if count == 1000:
            RENDERER.DRAW = fill_color_sun
        if count == 2000:
            draw = 'sun'
        if count == 3000:
            draw = 'sun2'
        if count == 4000:
            draw = 'ind'
        if count == 5000:
            draw = 'red'
        if count == 6000:
            draw = 'blue'
        if count == 7000:
            run = False
            pygame.display.quit()
    return count, WORLD, times
            

        
if __name__ == '__main__':
    countc, worldc, timesc = run()
    avg = {k: v/countc for k, v in times.items()}


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


