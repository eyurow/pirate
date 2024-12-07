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
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            return 'composite'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            return 'currents'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
            return 'np'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            return 'sa'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            return 'mod'
        
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
        

class Menu:
    def __init__(self, pa):
        pass




def get_margin(outer_size, inner_size):
    '''
    INPUT: outer and inner container sizes; e.g. outer is screen size of 1221, inner is world-pixel size of 1200 (300*4)
    OUTPUT: excess units at start and end of outer container; e.g. 10 and 11 pixels in above example as the screen has 21 more pixels than the world requires to render
    '''
    margin = outer_size - inner_size
    start = margin // 2
    end = margin - start
    return start, end

def set_pixelarray(pa, world, width, height, cell_size, world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y):
    if width > world.SIZE[0] * cell_size:
        start, end = get_margin(width, world.SIZE[0] * cell_size)
        pa[:start] = (0,0,0)
        pa[-end:] = (0,0,0)
        pa = pa[start:-end]
        start_pixel_x = start
        world_slicer_x = slice(0, world.SIZE[0])
    elif width < world.SIZE[0] * cell_size:
        # get world slicer
        start, end = get_margin(world.SIZE[0], width // cell_size)
        world_slicer_x = slice(start, world.SIZE[0] - end)
        # get pixel slicer
        if width > cell_size * (world.SIZE[0] - start - end): # if screen width greater than sliced world size
            start, end = get_margin(width, cell_size * (world.SIZE[0] - start - end))
            pa[:start] = (0,0,0)
            pa[-end:] = (0,0,0)
            pa = pa[start:-end]
            start_pixel_x = start
    elif width == world.SIZE[0] * cell_size:
        start_pixel_x = 0
        world_slicer_x = slice(0, world.SIZE[0])
        
    
    if height > world.SIZE[1] * cell_size:
        start, end = get_margin(height, world.SIZE[1] * cell_size)
        pa[:, :start] = (0,0,0)
        pa[:, -end:] = (0,0,0)
        pa = pa[:, start:-end]
        start_pixel_y = start
        world_slicer_y = slice(0, world.SIZE[1])
    elif height < world.SIZE[1] * cell_size:
        # get world slicer
        start, end = get_margin(world.SIZE[1], height // cell_size)
        world_slicer_y = slice(start, world.SIZE[1] - end)
        # get pixel slicer
        if height > cell_size * (world.SIZE[1] - start - end): # if screen width greater than sliced world size
            start, end = get_margin(height, cell_size * (world.SIZE[1] - start - end))
            pa[:, :start] = (0,0,0)
            pa[:, -end:] = (0,0,0)
            pa = pa[:, start:-end]
            start_pixel_y = start
    elif height == world.SIZE[1] * cell_size:
        start_pixel_y = 0
        world_slicer_y = slice(0, world.SIZE[1])
    
    return pa, world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y



            
WIDTH, HEIGHT = (1200,600)
CELL_SIZE = 4

def run():
    pygame.init()
    
    global WIDTH, HEIGHT, CELL_SIZE
    WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE) #(WIDTH, HEIGHT))
    pa = sa.pixels3d(WINDOW)
    world = World((200,200), 16) # 100,60
    
    cell_size = CELL_SIZE #WIDTH // world.SIZE[0]
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
    esc_menu_open = False
    run = True
    
    pa, world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y = set_pixelarray(pa, world, WIDTH, HEIGHT, cell_size, 
                                                                                      world_slicer_x, world_slicer_y, 
                                                                                      start_pixel_x, start_pixel_y)


    with open('200x200_v1.json', 'r') as f:
        world.LAND = np.array(json.load(f), dtype = int)
    
    world.LAND = world.LAND[:, (world.LAND[0] < world.SIZE[0])&
                                  (world.LAND[0] >= 0)&
                                  (world.LAND[1] < world.SIZE[1])&
                                  (world.LAND[1] >= 0)]
    # world.LAND[1] += 40
        
    # world.WIND_SEEDS.append(WindGroup((10,10), (7, 18), 30, direction = -.2, movement = 0))
    # world.WIND_SEEDS.append(WindGroup((110,10), (30,4), 20, direction = -np.pi/2))
    # world.WIND_SEEDS.append(WindGroup((160,30), (8,15), 40, direction = -3*np.pi/4 - .143))
    
    # world.WIND_SEEDS.append(WindGroup((115,115), (10, 5), 40, direction = np.pi/2 + .156))
    # world.WIND_SEEDS.append(WindGroup((175,60), (10, 10), 50, -np.pi + .198765))
    # world.WIND_SEEDS.append(WindGroup((55,110), (3,50), 30, direction = np.pi/2-.24))
    # world.WIND_SEEDS.append(WindGroup((20,75), (5, 20), 30, .254))
    
    # world.WIND_SEEDS.append(WindGroup((90,55), (20, 20), 5, 0))

    while run:
        # if world.CURRENTS.sum() < 1:
                
        #     world.WINDS[70,160,0] = 0
        #     world.WINDS[70,160,1] = 200

        # world.WIND_SEEDS[-1].direction += np.pi/30
        # world.WIND_SEEDS[-1].x = np.cos(world.WIND_SEEDS[-1].direction) * 5
        # world.WIND_SEEDS[-1].y = np.sin(world.WIND_SEEDS[-1].direction) * 5
        #times['Key'] += clock.tick_busy_loop() / 1000

        #world.WINDS[80,100,0] = 100
        #world.WINDS[80,100,1] = 0
        
        
        ### SIMULATE WORLD ###
        world.apply_coriolis_force()
        # world.apply_centrifugal_force()
        
        if count % world.SUN_FRAMES == 0:
            sun_index += 1
            if sun_index == sun_index_count:
                sun_index = 0
            world.move_sun(sun_index)
            #world.calc_solar_pressure()
            sun_dist = world.calc_solar_pressure_and_distance()
            
        
        ### Prop Winds and Set Current Thetas
        '''
        # OLD WINDS
        world.old_propogate_winds()
        world.set_current_thetas()
        '''
        # #world.apply_wind_generators()
        world.apply_pressure_winds()
        
        ## Set 
        world.set_wind_thetas()
        world.propogate_array(array = 'winds')
        world.set_winds()
        world.apply_winds_to_currents()
        # #times['Prop Winds'] += clock.tick_busy_loop() / 1000

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
            pa[...] = pa.mean()
        elif inp == 'resize':
            pa = sa.pixels3d(WINDOW)
            WIDTH, HEIGHT = pa.shape[0], pa.shape[1]
            pa, world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y = set_pixelarray(pa, world, WIDTH, HEIGHT, cell_size, 
                                                                                              world_slicer_x, world_slicer_y, 
                                                                                              start_pixel_x, start_pixel_y)                
        elif isinstance(inp, tuple): # add land
            modified_pos = (inp[0] - start_pixel_x + world_slicer_x.start * cell_size,
                            inp[1] - start_pixel_y + world_slicer_y.start * cell_size)
            same_pos_size = world.LAND[:, (world.LAND[0] == modified_pos[0]//cell_size)& 
                                          (world.LAND[1] == modified_pos[1]//cell_size)].size
            if same_pos_size == 0 and modified_pos not in add_land:
                add_land.append(modified_pos)
            mouse_movement = True
        elif inp == 0: # end adding land
            add_land_array = np.array(add_land).T // cell_size
            world.LAND = np.concatenate([world.LAND, add_land_array], axis = 1) #, dtype = int)
            mouse_movement = False
        
        elif inp == 'text':
            draw = None
            draw_menu(pa)
        
        elif inp in ['fill','light','sun','sun2','ind','red','blue']:
            draw = inp

        
        ### RENDER ###
        if draw == 'fill':
            pa_fill_color(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], cell_size)
        elif draw == 'light':
            fill_color_light(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], sun_dist[world_slicer_x, world_slicer_y], cell_size)
        elif draw == 'sun':
            fill_color_sun(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], sun_dist[world_slicer_x, world_slicer_y], cell_size)
        elif draw == 'sun2':
            fill_color_sun2(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], sun_dist[world_slicer_x, world_slicer_y], cell_size, world.SIZE)
        elif draw == 'ind':
            fill_ind_colors(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], sun_dist[world_slicer_x, world_slicer_y], cell_size, world.SIZE)
        elif draw == 'red':
            fill_ind_red(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], sun_dist[world_slicer_x, world_slicer_y], cell_size, world.SIZE)
        elif draw == 'blue':
            fill_parabola(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], sun_dist[world_slicer_x, world_slicer_y], cell_size, world.SIZE)


            
        # elif draw == 'sa':
        #     pa[...] = (64,204,190)
        #     draw_normal_current_triangles(pa, world.THETAS[world_slicer_x, world_slicer_y], cell_size)
        #     rotate_current_triangles(pa, world.THETAS[world_slicer_x, world_slicer_y], cell_size)
        # elif draw == 'mod':
        #     draw_str_modified_current_triangles(pa, world.THETAS[world_slicer_x, world_slicer_y], cell_size)
        #     rotate_current_triangles(pa, world.THETAS[world_slicer_x, world_slicer_y], cell_size)
            
        draw_land(pa, world.LAND, cell_size, (world_slicer_x, world_slicer_y))
        
        #draw_land(pa, world.POLAR_BAND[0], cell_size, (world_slicer_x, world_slicer_y), (244, 245, 226))
        #draw_land(pa, world.INNER_POLAR_BAND[0], cell_size, (world_slicer_x, world_slicer_y), (128,128,128))
        #draw_land(pa, world.INNER_EQ_BAND[0], cell_size, (world_slicer_x, world_slicer_y), (255,228,181))
        
        #draw_land(pa, world.SOLAR_BAND, cell_size, (world_slicer_x, world_slicer_y), (255,255,50))
        draw_sun(pa, world.SUN, cell_size, (world_slicer_x, world_slicer_y))
            
        #times['Draw'] += clock.tick_busy_loop() / 1000
        
        pygame.display.update()
        #times['Render'] += clock.tick_busy_loop() / 1000
        
        
        ### Simulate World
        world.propogate_array(array = 'currents')
        world.set_currents()

        world.apply_energy_loss()
        #times['Apply Loss'] += clock.tick_busy_loop() / 1000
        
        
        count += 1
        
        if count == 200:
            draw = 'light'
        if count == 400:
            draw = 'sun'
        if count == 600:
            draw = 'sun2'
        if count == 800:
            draw = 'ind'
        if count == 1000:
            draw = 'red'
        if count == 1200:
            draw = 'blue'
        if count == 1400:
            run = False
            pygame.display.quit()
            break
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


