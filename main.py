from world import World, Wind, WindGroup

from vis import *
from indices import get_pixel_indices
import numpy as np
import json

import pygame
import pygame.surfarray as sa
pygame.font.init()


np.set_printoptions(precision = 6, threshold = 1600, suppress = True)



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
        

def receive_escape_menu_inputs(mouse_movement = False):
    waiting = True
    while waiting:
        event = pygame.event.wait()
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN):
            return 'quit'
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            return True
            
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
        
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print(f'DOWN: {event}')
            return event.pos
        elif event.type == pygame.MOUSEMOTION and mouse_movement:
            print(f'MOVE: {event}')
            return event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            print(f'UP: {event}')
            return 0

def get_margin(outer_size, inner_size):
    '''
    INPUT: outer and inner container sizes; e.g. outer is screen size of 1221, inner is world-pixel size of 1200 (300*4)
    OUTPUT: excess units at start and end of outer container; e.g. 10 and 11 pixels in above example as the screen has 21 more pixels than the world requires to render
    '''
    margin = outer_size - inner_size
    start = margin // 2
    end = margin - start
    return start, end

def set_pixelarray(world, world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y):
    global pa
    print('set start: ', pa.__array_interface__)
    if WIDTH > world.SIZE[0] * CELL_SIZE:
        start, end = get_margin(WIDTH, world.SIZE[0] * CELL_SIZE)
        pa[:start] = (0,0,0)
        pa[-end:] = (0,0,0)
        pa = pa[start:-end]
        start_pixel_x = start
        world_slicer_x = slice(0, world.SIZE[0])
    elif WIDTH < world.SIZE[0] * CELL_SIZE:
        # get world slicer
        start, end = get_margin(world.SIZE[0], WIDTH // CELL_SIZE)
        world_slicer_x = slice(start, world.SIZE[0] - end)
        # get pixel slicer
        if WIDTH > CELL_SIZE * (world.SIZE[0] - start - end): # if screen WIDTH greater than sliced world size
            start, end = get_margin(WIDTH, CELL_SIZE * (world.SIZE[0] - start - end))
            pa[:start] = (0,0,0)
            pa[-end:] = (0,0,0)
            pa = pa[start:-end]
            start_pixel_x = start
    elif WIDTH == world.SIZE[0] * CELL_SIZE:
        start_pixel_x = 0
        world_slicer_x = slice(0, world.SIZE[0])
    
    if HEIGHT > world.SIZE[1] * CELL_SIZE:
        start, end = get_margin(HEIGHT, world.SIZE[1] * CELL_SIZE)
        pa[:, :start] = (0,0,0)
        pa[:, -end:] = (0,0,0)
        pa = pa[:, start:-end]
        start_pixel_y = start
        world_slicer_y = slice(0, world.SIZE[1])
    elif HEIGHT < world.SIZE[1] * CELL_SIZE:
        # get world slicer
        start, end = get_margin(world.SIZE[1], HEIGHT // CELL_SIZE)
        world_slicer_y = slice(start, world.SIZE[1] - end)
        # get pixel slicer
        if HEIGHT > CELL_SIZE * (world.SIZE[1] - start - end): # if screen WIDTH greater than sliced world size
            start, end = get_margin(HEIGHT, CELL_SIZE * (world.SIZE[1] - start - end))
            pa[:, :start] = (0,0,0)
            pa[:, -end:] = (0,0,0)
            pa = pa[:, start:-end]
            start_pixel_y = start
    elif HEIGHT == world.SIZE[1] * CELL_SIZE:
        start_pixel_y = 0
        world_slicer_y = slice(0, world.SIZE[1])
    
    print('set end: ', pa.__array_interface__)
    # return pa, world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y
    return world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y


def draw_menu(pa, scale = .9):
    left_marg = int(pa.shape[0] * (1 - scale))
    right_marg = int(pa.shape[0] * scale)
    top_marg = int(pa.shape[1] * (1 - scale))
    bot_marg = int(pa.shape[1] * scale)
    
    pa[left_marg:right_marg, top_marg:bot_marg,:] = 150
    
    f = pygame.font.SysFont('helvetica', size = 30, bold = True)
    r = f.render('test', 0, (0,0,0))
    pix = sa.pixels2d(r)
    ind = np.where(pix == 1)

    pa[(ind[0] + left_marg, ind[1] + top_marg)] = (0,0,0)



class InputHandler:
    def __init__(self, pa, width, height):
        self.pa = pa
        self.width = width
        self.height = height



class Menu:
    def __init__(self, pa):
        pass
class EscapeMenu(Menu):
    def __init__(self):
        pass
        # self.pa = pa
        # print('initmenu: ', hex(id(self.pa)), pa.shape)
        # self.left_marg = int(pa.shape[0] * (1 - scale))
        # self.right_marg = int(pa.shape[0] * scale)
        # self.top_marg = int(pa.shape[1] * (1 - scale))
        # self.bot_marg = int(pa.shape[1] * scale)    

    def resize(self, scale = .9):
        #self.pa = pa

        self.left_marg = int(pa.shape[0] * (1 - scale))
        self.right_marg = int(pa.shape[0] * scale)
        self.top_marg = int(pa.shape[1] * (1 - scale))
        self.bot_marg = int(pa.shape[1] * scale)   

    def display(self):
        print('disp: ', pa.__array_interface__)
        screen_blur(pa)
        pa[self.left_marg:self.right_marg, self.top_marg:self.bot_marg] = (166, 93, 7)
        pa[self.left_marg, self.top_marg:self.bot_marg] = (0,0,0)
        pa[self.right_marg, self.top_marg:self.bot_marg] = (0,0,0)
        pa[self.left_marg:self.right_marg, self.top_marg] = (0,0,0)
        pa[self.left_marg:self.right_marg, self.bot_marg] = (0,0,0)
        pygame.display.update()

    def wait_for_input(self):
        waiting = True
        while waiting:
            event = pygame.event.wait()
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN):
                return 'quit'
            
            elif event.type == [pygame.VIDEORESIZE, pygame.VIDEOEXPOSE]:
                global pa
                pa = sa.pixels3d(WINDOW)
                WIDTH, HEIGHT = pa.shape[0], pa.shape[1]
                world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y = set_pixelarray(world, world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y) 
                self.resize() 

            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False



            
WIDTH, HEIGHT = (1200,600)
CELL_SIZE = 3
pa = None

def run():
    pygame.init()
    
    global WIDTH, HEIGHT, CELL_SIZE, pa, WINDOW
    WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE) #(WIDTH, HEIGHT))
    pa = sa.pixels3d(WINDOW)

    world = World((500,300), 16) # 100,60
    
    count = 0
    sun_index_count = world.SOLAR_BAND[0].size
    sun_index = 0
    clock = pygame.time.Clock()
    times = {
        'Key': 0,
        'Prop Winds': 0,
        'Prop Currents': 0,
        'Apply Loss': 0,
        'Set Step': 0,
        'Draw': {'composite':0,
                 'currents':0,
                 'winds':0,
                 'np':0,
                 'sa':{'norm':0,
                       'rotate':0,
                       'blit':0}},
        'Render': 0
        }
    world_slicer_x = slice(0, world.SIZE[0])
    world_slicer_y = slice(0, world.SIZE[1])
    start_pixel_x = 0
    start_pixel_y = 0
    draw = 'fill'
    add_land = []
    mouse_movement = False
    ESC_MENU = EscapeMenu()
    run = True
    
    world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y = set_pixelarray(world, world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y)
    ESC_MENU.resize()

    with open('200x200_v1.json', 'r') as f:
        world.LAND = np.array(json.load(f), dtype = int)
    world.LAND = world.LAND[:, (world.LAND[0] < world.SIZE[0])&
                                  (world.LAND[0] >= 0)&
                                  (world.LAND[1] < world.SIZE[1])&
                                  (world.LAND[1] >= 0)]

    while run:
        #times['Key'] += clock.tick_busy_loop() / 1000
        
        ### SIMULATE WORLD ###
        world.apply_coriolis_force()
        # world.apply_centrifugal_force()
        
        if count % world.SUN_FRAMES == 0:
            sun_index += 1
            if sun_index == sun_index_count:
                sun_index = 0
            world.move_sun(sun_index)
            sun_dist = world.calc_solar_pressure_and_distance()
        
        ### Prop Winds and Set Current Thetas
        '''
        # OLD WINDS
        world.old_propogate_winds/pressure()
        world.set_current_thetas()
        '''
        world.apply_pressure_winds()
        
        ## Set Winds
        world.set_wind_thetas()
        world.propogate_array(array = 'winds')
        world.set_winds()
        world.apply_winds_to_currents()
        # #times['Prop Winds'] += clock.tick_busy_loop() / 1000

        ## Set Current Thetas
        world.impact_land()
        world.set_current_thetas()


        ### HANDLE INPUTS ###
        #inp = wait_for_input(mouse_movement)
        inp = receive_inputs(mouse_movement)
        
        if inp == 'quit':    
            run = False
            pygame.display.quit()
            break
        elif inp == 'escape menu':
            #print('premenu: ', id(pa), pa.shape)
            ESC_MENU.display()

            ESC_MENU.wait_for_input()
            #print('postmenu: ', id(pa), pa.shape)
        elif inp == 'resize':
            pa = sa.pixels3d(WINDOW)
            print('resize start: ', pa.__array_interface__)
            #print('nresize: ', id(pa), pa.shape)
            #print('pabase: ', pa.base, pa.shape)
            
            WIDTH, HEIGHT = pa.shape[0], pa.shape[1]
            world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y = set_pixelarray(world, world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y) 
            print('resize end: ', pa.__array_interface__)
            print('_______')
            ESC_MENU.resize() 
            #print('presize: ', id(pa), pa.shape)             
        elif isinstance(inp, tuple): # add land
            modified_pos = (inp[0] - start_pixel_x + world_slicer_x.start * CELL_SIZE,
                            inp[1] - start_pixel_y + world_slicer_y.start * CELL_SIZE)
            same_pos_size = world.LAND[:, (world.LAND[0] == modified_pos[0]//CELL_SIZE)& 
                                          (world.LAND[1] == modified_pos[1]//CELL_SIZE)].size
            if same_pos_size == 0 and modified_pos not in add_land:
                add_land.append(modified_pos)
            mouse_movement = True
        elif inp == 0: # end adding land
            add_land_array = np.array(add_land).T // CELL_SIZE
            world.LAND = np.concatenate([world.LAND, add_land_array], axis = 1) #, dtype = int)
            mouse_movement = False
        
        elif inp == 'text':
            draw = None
            draw_menu(pa)
        
        elif inp in ['fill','light','sun','sun2','ind','red','blue']:
            draw = inp

        
        ### RENDER ###
        if draw == 'fill':
            pa_fill_color(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], CELL_SIZE)
        elif draw == 'light':
            fill_color_light(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], sun_dist[world_slicer_x, world_slicer_y], CELL_SIZE)
        elif draw == 'sun':
            fill_color_sun(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], sun_dist[world_slicer_x, world_slicer_y], CELL_SIZE)
        elif draw == 'sun2':
            fill_color_sun2(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], sun_dist[world_slicer_x, world_slicer_y], CELL_SIZE, world.SIZE)
        elif draw == 'ind':
            fill_ind_colors(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], sun_dist[world_slicer_x, world_slicer_y], CELL_SIZE, world.SIZE)
        elif draw == 'red':
            fill_ind_red(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], sun_dist[world_slicer_x, world_slicer_y], CELL_SIZE, world.SIZE)
        elif draw == 'blue':
            fill_parabola(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], sun_dist[world_slicer_x, world_slicer_y], CELL_SIZE, world.SIZE)

        draw_land(pa, world.LAND, CELL_SIZE, (world_slicer_x, world_slicer_y))
        draw_sun(pa, world.SUN, CELL_SIZE, (world_slicer_x, world_slicer_y))

        # elif draw == 'sa':
        #     pa[...] = (64,204,190)
        #     draw_normal_current_triangles(pa, world.THETAS[world_slicer_x, world_slicer_y], CELL_SIZE)
        #     draw_str_modified_current_triangles(pa, world.THETAS[world_slicer_x, world_slicer_y], CELL_SIZE)
        #     rotate_current_triangles(pa, world.THETAS[world_slicer_x, world_slicer_y], CELL_SIZE)
            
        #draw_land(pa, world.POLAR_BAND[0], CELL_SIZE, (world_slicer_x, world_slicer_y), (244, 245, 226))
        #draw_land(pa, world.INNER_POLAR_BAND[0], CELL_SIZE, (world_slicer_x, world_slicer_y), (128,128,128))
        #draw_land(pa, world.INNER_EQ_BAND[0], CELL_SIZE, (world_slicer_x, world_slicer_y), (255,228,181))
        #draw_land(pa, world.SOLAR_BAND, CELL_SIZE, (world_slicer_x, world_slicer_y), (255,255,50))

        #times['Draw'] += clock.tick_busy_loop() / 1000
        
        pygame.display.update()
        #times['Render'] += clock.tick_busy_loop() / 1000
        
        
        ### SIMULATE WORLD ###
        world.propogate_array(array = 'currents')
        world.set_currents()

        world.apply_energy_loss()
        #times['Apply Loss'] += clock.tick_busy_loop() / 1000
        
        
        count += 1
        
        # if count == 200:
        #     draw = 'light'
        # if count == 400:
        #     draw = 'sun'
        # if count == 600:
        #     draw = 'sun2'
        # if count == 800:
        #     draw = 'ind'
        # if count == 1000:
        #     draw = 'red'
        # if count == 1200:
        #     draw = 'blue'
        # if count == 1400:
        #     run = False
        #     pygame.display.quit()
        #     break
    return count, world, times
            

        
if __name__ == '__main__':
    countc, worldc, timesc = run()


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


