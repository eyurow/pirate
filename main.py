from world import World, Wind, WindGroup, Particles

from vis import *
from ui import EscapeMenu, Context, Rectangle, InfoBox
from indices import get_pixel_indices
from generics import get_margin
from shapes import generate_line, generate_patterned_line, generate_perpendicular_line
from ships import Ship
from textures.ship_diagram import zx_diagram, xy_diagram
import numpy as np
import json
import psutil
import os

import pygame
import pygame.surfarray as sa
pygame.font.init()


np.set_printoptions(precision = 1, threshold = 1600, suppress = True)



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
        self.lmb_mode = False
        self.rmb_mode = False
        self.add_land = []
        self.pa_pos = (0,0)
        self.info_box = InfoBox(owner = self)

    def generate_info_box(self, pos):
        world_pos = ( (pos[0] - self.renderer.START_PIXEL_X) // self.renderer.CELL_SIZE + self.renderer.WORLD_SLICER_X.start, 
                          (pos[1] - self.renderer.START_PIXEL_X) // self.renderer.CELL_SIZE + self.renderer.WORLD_SLICER_Y.start )
            
        current_x = WORLD.CURRENTS[world_pos[0], world_pos[1], 0]
        current_y = WORLD.CURRENTS[world_pos[0], world_pos[1], 1]
        winds_x = WORLD.WINDS[world_pos[0], world_pos[1], 0]
        winds_y = WORLD.WINDS[world_pos[0], world_pos[1], 1]
        r = self.renderer.PA[pos[0] - self.renderer.START_PIXEL_X, pos[1] - self.renderer.START_PIXEL_Y, 0]
        g = self.renderer.PA[pos[0] - self.renderer.START_PIXEL_X, pos[1] - self.renderer.START_PIXEL_Y, 1]
        b = self.renderer.PA[pos[0] - self.renderer.START_PIXEL_X, pos[1] - self.renderer.START_PIXEL_Y, 2]

        posx, posy = pos[0] + 4 - self.renderer.START_PIXEL_X, pos[1] - self.renderer.START_PIXEL_Y
        if posx + self.info_box.size[0] >= self.renderer.PA_SIZE[0]:
            posx = posx - self.info_box.size[0]
        if posy + self.info_box.size[1] >= self.renderer.PA_SIZE[1]:
            posy = posy - self.info_box.size[1]
    
        self.info_box.generate((posx, posy))
        self.info_box.generate_info(current_x, current_y, winds_x, winds_y, r, g, b) # TODO: call generate info from generate??
        
        self.renderer.add_post(self.renderer.draw_info_box, self.info_box)

    def default_handle(self, event, mouse_press = None):
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

        elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3): # or mouse_press[2] == 1:
            self.generate_info_box(event.pos)
        
        elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
            modified_pos = (event.pos[0] - self.renderer.START_PIXEL_X + self.renderer.WORLD_SLICER_X.start * self.renderer.CELL_SIZE,
                            event.pos[1] - self.renderer.START_PIXEL_Y + self.renderer.WORLD_SLICER_Y.start * self.renderer.CELL_SIZE)
            same_pos_size = WORLD.LAND[:, (WORLD.LAND[0] == modified_pos[0]//self.renderer.CELL_SIZE)& 
                                          (WORLD.LAND[1] == modified_pos[1]//self.renderer.CELL_SIZE)].size
            if same_pos_size == 0 and modified_pos not in self.add_land:
                self.add_land.append(modified_pos)
            self.lmb_mode = 'add land'
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            add_land_array = np.array(self.add_land).T // self.renderer.CELL_SIZE
            WORLD.LAND = np.concatenate([WORLD.LAND, add_land_array], axis = 1) #, dtype = int)
            self.lmb_mode = False

    def end_handle(self, mouse_press):
        if mouse_press[2] == 1: # and self.rmb_mode == 'info':
            self.generate_info_box(pygame.mouse.get_pos())
        
        if mouse_press[0] == 1 and self.lmb_mode == 'add land':
            pos = pygame.mouse.get_pos()
            modified_pos = (pos[0] - self.renderer.START_PIXEL_X + self.renderer.WORLD_SLICER_X.start * self.renderer.CELL_SIZE,
                            pos[1] - self.renderer.START_PIXEL_Y + self.renderer.WORLD_SLICER_Y.start * self.renderer.CELL_SIZE)
            
            same_pos_size = WORLD.LAND[:, (WORLD.LAND[0] == modified_pos[0]//self.renderer.CELL_SIZE)& 
                                          (WORLD.LAND[1] == modified_pos[1]//self.renderer.CELL_SIZE)].size
            if same_pos_size == 0 and modified_pos not in self.add_land:
                self.add_land.append(modified_pos)

    
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
                    mouse_press = pygame.mouse.get_pressed()
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
                            self.default_handle(event, mouse_press)
                    self.end_handle(mouse_press)
                            
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
                            self.default_handle(event, mouse_press = [])

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
                        
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
        ESC_MENU.generate(pos = ((self.renderer.PA_SIZE[0] - 1000)//2, (self.renderer.PA_SIZE[1] - 550)//2))        




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

class Renderer:
    def __init__(self, screen, cell_size):
        self.screen = screen
        self.PA = None
        self.PA_SIZE = (0,0)
        self.CELL_SIZE = cell_size
        # self.world = world  --  if moved out of main will need to tie to world here
        self.WORLD_SLICER_X = slice(0, WORLD.SIZE[0])
        self.WORLD_SLICER_Y = slice(0, WORLD.SIZE[0])
        self.START_PIXEL_X = 0
        self.START_PIXEL_Y = 0
        self.pa_pos = (0,0)
        self.DRAW = pa_fill_color
        self.post = []

        self.refresh_PA()
        self.set_pixelarray()

    def refresh_PA(self):
        self.PA = sa.pixels3d(self.screen.WIN)
        self.screen.WIDTH, self.screen.HEIGHT = self.PA.shape[:2]
    
    def set_draw(self, func):
        self.DRAW = func
    
    def draw_world(self):
        self.DRAW(self.PA, WORLD.THETAS[self.WORLD_SLICER_X, self.WORLD_SLICER_Y, 1], WORLD.DISTANCE_FROM_SUN[self.WORLD_SLICER_X, self.WORLD_SLICER_Y], self.CELL_SIZE, WORLD.SIZE)
        draw_land(self.PA, WORLD.LAND, self.CELL_SIZE, (self.WORLD_SLICER_X, self.WORLD_SLICER_Y))
        draw_sun(self.PA, WORLD.SUN, self.CELL_SIZE, (self.WORLD_SLICER_X, self.WORLD_SLICER_Y))
        # self.update_display()

    def draw_post(self):
        for item in self.post:
            func = item[0]
            func(*item[1:])


    def draw_menu(self, menu):
        # screen_blur(PA)
        self.PA[menu.left_marg:menu.right_marg, menu.top_marg:menu.bot_marg] = (166, 93, 7)
        self.PA[menu.left_marg, menu.top_marg:menu.bot_marg] = (0,0,0)
        self.PA[menu.right_marg, menu.top_marg:menu.bot_marg] = (0,0,0)
        self.PA[menu.left_marg:menu.right_marg, menu.top_marg] = (0,0,0)
        self.PA[menu.left_marg:menu.right_marg, menu.bot_marg] = (0,0,0)

    def draw_button(self, button, menu_pos = (0,0)):
        self.draw_rectangle(button)
        if button.text:
            self.PA[(button.pa_pos[0] + button.text_ind[0], button.pa_pos[1] + button.text_ind[1])] = button.text_color

    def draw_particles(self, particles):
        draw_particles(self.PA, particles, self.PA_SIZE, self.CELL_SIZE, (self.WORLD_SLICER_X, self.WORLD_SLICER_Y), (self.START_PIXEL_X, self.START_PIXEL_Y))

    def draw_ship(self, ship):
        draw_ship(self.PA, ship, self.PA_SIZE, self.CELL_SIZE, (self.WORLD_SLICER_X, self.WORLD_SLICER_Y), (self.START_PIXEL_X, self.START_PIXEL_Y))


    def draw_rectangle(self, rect):
        if rect.color:
            self.PA[rect.pa_pos[0]:rect.pa_pos[0] + rect.size[0], rect.pa_pos[1]:rect.pa_pos[1] + rect.size[1]] = rect.color
        if rect.border_color:
            self.PA[rect.pa_pos[0], rect.pa_pos[1]:rect.pa_pos[1] + rect.size[1]] = rect.border_color
            self.PA[rect.pa_pos[0] + rect.size[0], rect.pa_pos[1]:rect.pa_pos[1] + rect.size[1]] = rect.border_color
            self.PA[rect.pa_pos[0]:rect.pa_pos[0] + rect.size[0], rect.pa_pos[1]] = rect.border_color
            self.PA[rect.pa_pos[0]:rect.pa_pos[0] + rect.size[0], rect.pa_pos[1] + rect.size[1]] = rect.border_color

    def draw_info_box(self, info_box):
        self.draw_rectangle(info_box)

        row = 4
        for info in [info_box.xcurrents_text, info_box.ycurrents_text, info_box.xwinds_text, info_box.ywinds_text]:
            idx = np.where(info == 1)
            adjusted = (idx[0] + info_box.pa_pos[0] + 5, idx[1] + info_box.pa_pos[1] + row)
            self.PA[adjusted] = info_box.text_color
            row += 15

        row = 10
        for info in [info_box.r_text, info_box.g_text, info_box.b_text]:
            idx = np.where(info == 1)
            adjusted = (idx[0] + info_box.pa_pos[0] + 95, idx[1] + info_box.pa_pos[1] + row)
            self.PA[adjusted] = info_box.text_color
            row += 15

        idx = info_box.currents_compass
        adjusted = (idx[0] + info_box.pa_pos[0], idx[1] + info_box.pa_pos[1])
        self.PA[adjusted] = (0,0,0)

        idx = info_box.current_line
        adjusted = (idx[0] + info_box.pa_pos[0], idx[1] + info_box.pa_pos[1])
        self.PA[adjusted] = (50,150,175)

    def draw_ship_zx_diagram(self, ship):
        x_range, y_range, zx_diag = zx_diagram(ship, 'small')
        start_x = x_range[0] + self.PA_SIZE[0] - (x_range[1] * 2) - (10 * 2) # two diagrams from bottom right corner, 10 pix buffer
        start_y = y_range[0] + self.PA_SIZE[1] - y_range[1] - 10
       
        print(self.PA_SIZE)        
        print(x_range, y_range)
        print(zx_diag[0].min(), zx_diag[0].max())
        print(zx_diag[1].min(), zx_diag[1].max())

        self.PA[start_x:start_x + x_range[1],start_y:start_y + y_range[1]] = (0,0,0)
        self.PA[(zx_diag[0] + start_x, zx_diag[1] + start_y)] = (255,255,255)

    def draw_ship_xy_diagram(self, ship):
        x_range, y_range, xy_diag = xy_diagram(ship, 'small')
        start_x = x_range[0] + self.PA_SIZE[0] - x_range[1] - 10 # one diagram from bottom right corner, 10 pix buffer
        start_y = y_range[0] + self.PA_SIZE[1] - y_range[1] - 10

        self.PA[start_x:start_x + x_range[1],start_y:start_y + y_range[1]] = (0,0,0)
        self.PA[(xy_diag[0] + start_x, xy_diag[1] + start_y)] = (255,255,255)


    def draw_line(self, p1, p2, thick, thick_quotient = .5, thick_offset = -1, num_lines = 1, even_offset = 0, color = (0,0,0)):
        line = generate_line(p1, p2, thick, thick_quotient, thick_offset, num_lines, even_offset)
        self.PA[tuple(line)] = color
    def draw_perp_line(self, p1, p2, thick, color = (0,0,0)):
        line = generate_perpendicular_line(p1, p2, thick)
        self.PA[tuple(line)] = color
    def draw_patterned_line(self, p1, p2, thick, color = (0,0,0)):
        line = generate_patterned_line(p1, p2, thick)
        self.PA[tuple(line)] = color
    
    def add_post(self, func, *args):
        self.post.append((func, *args))

    def clear_post(self):
        self.post = []

    
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

        self.PA_SIZE = self.PA.shape[:2]

    def update_display(self):
        self.screen.update_display()


def live_world():
    world = World((500,300), 16) # 100,60
    with open('200x200_v1.json', 'r') as f:
        world.LAND = np.array(json.load(f), dtype = int)
    world.LAND = WORLD.LAND[:, (world.LAND[0] < world.SIZE[0])&
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
    global WORLD, RUN, ESC_MENU, RENDERER

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
    

    ship = Ship(world = WORLD, position = (100,150), heading = -np.pi/8)
    # ship.main_sail.area = 0
    ship.main_sail.set = -np.pi/6
    ship.main_sail.give = -np.pi/6
    particles = Particles(12, WORLD, type = 'grid')

    SCREEN = Screen(WIDTH, HEIGHT)
    RENDERER = Renderer(SCREEN, CELL_SIZE)
    INP_HANDLER = InputHandler(SCREEN, RENDERER)
    ESC_MENU = EscapeMenu(owner = RENDERER, pos = ((RENDERER.PA_SIZE[0] - 1000)//2, (RENDERER.PA_SIZE[1] - 550)//2))
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
        # WORLD.sim()
        WORLD.test_sim()

        WORLD.WINDS[30:90,100:200,0] = 1
        WORLD.WINDS[30:90,100:200,1] = 0

        # diagnostics.append({'WINDS': WORLD.WINDS[int(ship.position[0]), int(ship.position[1])],
        #                     'CURRENTS': WORLD.CURRENTS[int(ship.position[0]), int(ship.position[1])],
        #                     'SHIP P': (ship.position),
        #                     'SHIP V': (ship.x, ship.y)})

        particles.sim_particles()
        ship.sim(diagnostics)
        times['Sim'] += clock.tick_busy_loop() / 1000

        direction = INP_HANDLER.handle()
        if direction == 'quit':
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


