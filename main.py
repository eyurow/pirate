from world import World, Wind, WindGroup

from vis import pa_fill_color, draw_normal_current_triangles, draw_str_modified_current_triangles, rotate_current_triangles, draw_currents, draw_winds, draw_world, draw_land
import numpy as np
import json

import pygame
import pygame.surfarray as sa
# pygame.font.init()

np.set_printoptions(precision = 3, threshold = 1600, suppress = True)



def wait_for_input(mouse_movement = False):
    waiting = True
    while waiting:
        event = pygame.event.wait()
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN):
            return 'quit'
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            return True
            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            return 'winds'
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
            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            return 'winds'
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
        

def receive_escape_menu_inputs(mouse_movement = False):
    waiting = True
    while waiting:
        event = pygame.event.wait()
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN):
            return 'quit'
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            return True
            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            return 'winds'
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
    
    print(pa.shape)
    print(world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y)
    
    return world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y
    

class Menu:
    def __init__(self):
        pass



            
WIDTH, HEIGHT = (1200,600)
CELL_SIZE = 10

def run():
    pygame.init()
    
    global WIDTH, HEIGHT, CELL_SIZE
    WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE) #(WIDTH, HEIGHT))
    world = World((79,79), 16) # 100,60
    
    cell_size = CELL_SIZE #WIDTH // world.SIZE[0]
    
    #with open('sun_boundary_v1.json', 'r') as f:
    #    world.LAND = np.array(json.load(f), dtype = int)
        
    # world.WIND_SEEDS.append(WindGroup((10,10), (7, 18), 30, direction = -.2, movement = 0))
    # world.WIND_SEEDS.append(WindGroup((110,10), (30,4), 20, direction = -np.pi/2))
    # world.WIND_SEEDS.append(WindGroup((160,30), (8,15), 40, direction = -3*np.pi/4 - .143))
    
    # world.WIND_SEEDS.append(WindGroup((115,115), (10, 5), 40, direction = np.pi/2 + .156))
    # world.WIND_SEEDS.append(WindGroup((175,60), (10, 10), 50, -np.pi + .198765))
    # world.WIND_SEEDS.append(WindGroup((55,110), (3,50), 30, direction = np.pi/2-.24))
    # world.WIND_SEEDS.append(WindGroup((20,75), (5, 20), 30, .254))
    
    # world.WIND_SEEDS.append(WindGroup((90,55), (20, 20), 5, 0))

    count = 1
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
    draw = 'np'
    pa = sa.pixels3d(WINDOW)
    add_land = []
    mouse_movement = False
    esc_menu_open = False
    run = True
    
    
    if WIDTH > world.SIZE[0] * cell_size:
        start, end = get_margin(WIDTH, world.SIZE[0] * cell_size)
        pa[:start] = (0,0,0)
        pa[-end:] = (0,0,0)
        pa = pa[start:-end]
        start_pixel_x = start
        world_slicer_x = slice(0, world.SIZE[0])
    if HEIGHT > world.SIZE[1] * cell_size:
        start, end = get_margin(HEIGHT, world.SIZE[1] * cell_size)
        pa[:, :start] = (0,0,0)
        pa[:, -end:] = (0,0,0)
        pa = pa[:, start:-end]
        start_pixel_y = start
        world_slicer_y = slice(0, world.SIZE[1])
        
    if WIDTH < world.SIZE[0] * cell_size:
        # get world slicer
        start, end = get_margin(world.SIZE[0], WIDTH // cell_size)
        world_slicer_x = slice(start, world.SIZE[0] - end)
        # get pixel slicer
        if WIDTH > cell_size * (world.SIZE[0] - start - end): # if screen width greater than sliced world size
            start, end = get_margin(WIDTH, cell_size * (world.SIZE[0] - start - end))
            pa[:start] = (0,0,0)
            pa[-end:] = (0,0,0)
            pa = pa[start:-end]
            start_pixel_x = start
    if HEIGHT < world.SIZE[1] * cell_size:
        # get world slicer
        start, end = get_margin(world.SIZE[1], HEIGHT // cell_size)
        world_slicer_y = slice(start, world.SIZE[1] - end)
        # get pixel slicer
        if HEIGHT > cell_size * (world.SIZE[1] - start - end): # if screen width greater than sliced world size
            start, end = get_margin(HEIGHT, cell_size * (world.SIZE[1] - start - end))
            pa[:, :start] = (0,0,0)
            pa[:, -end:] = (0,0,0)
            pa = pa[:, start:-end]
            start_pixel_y = start
    
    
    
    while run:
        # world.WIND_SEEDS[-1].direction += np.pi/30
        # world.WIND_SEEDS[-1].x = np.cos(world.WIND_SEEDS[-1].direction) * 5
        # world.WIND_SEEDS[-1].y = np.sin(world.WIND_SEEDS[-1].direction) * 5
        #times['Key'] += clock.tick_busy_loop() / 1000



        ### Prop Winds and Set Current Thetas
        '''
        # OLD WINDS
        world.old_propogate_winds()
        world.set_current_thetas()
        '''
        
        world.apply_wind_generators()
        
        world.set_wind_thetas()
        world.propogate_array(array = 'winds')
        world.set_winds()
        #times['Prop Winds'] += clock.tick_busy_loop() / 1000
        
        world.apply_winds_to_currents()
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
            print(WIDTH, HEIGHT)

            ### NEW 
            # world_slicer_x, world_slicer_y, start_pixel_x, start_pixel_y = set_pixelarray(pa, world, WIDTH, HEIGHT, cell_size, 
            #                                                                               world_slicer_x, world_slicer_y, 
            #                                                                               start_pixel_x, start_pixel_y)

            
            if WIDTH > world.SIZE[0] * cell_size:
                start, end = get_margin(WIDTH, world.SIZE[0] * cell_size)
                pa[:start] = (0,0,0)
                pa[-end:] = (0,0,0)
                pa = pa[start:-end]
                start_pixel_x = start
                world_slicer_x = slice(0, world.SIZE[0])
            if HEIGHT > world.SIZE[1] * cell_size:
                start, end = get_margin(HEIGHT, world.SIZE[1] * cell_size)
                pa[:, :start] = (0,0,0)
                pa[:, -end:] = (0,0,0)
                pa = pa[:, start:-end]
                start_pixel_y = start
                world_slicer_y = slice(0, world.SIZE[1])
                
            if WIDTH < world.SIZE[0] * cell_size:
                # get world slicer
                start, end = get_margin(world.SIZE[0], WIDTH // cell_size)
                world_slicer_x = slice(start, world.SIZE[0] - end)
                # get pixel slicer
                if WIDTH > cell_size * (world.SIZE[0] - start - end): # if screen width greater than sliced world size
                    start, end = get_margin(WIDTH, cell_size * (world.SIZE[0] - start - end))
                    pa[:start] = (0,0,0)
                    pa[-end:] = (0,0,0)
                    pa = pa[start:-end]
                    start_pixel_x = start
            if HEIGHT < world.SIZE[1] * cell_size:
                # get world slicer
                start, end = get_margin(world.SIZE[1], HEIGHT // cell_size)
                world_slicer_y = slice(start, world.SIZE[1] - end)
                # get pixel slicer
                if HEIGHT > cell_size * (world.SIZE[1] - start - end): # if screen width greater than sliced world size
                    start, end = get_margin(HEIGHT, cell_size * (world.SIZE[1] - start - end))
                    pa[:, :start] = (0,0,0)
                    pa[:, -end:] = (0,0,0)
                    pa = pa[:, start:-end]
                    start_pixel_y = start
                
                
        elif inp in ['currents','composite','winds','np','sa','mod']:
            draw = inp
        elif isinstance(inp, tuple):
            modified_pos = (inp[0] - start_pixel_x + world_slicer_x.start * cell_size,
                            inp[1] - start_pixel_y + world_slicer_y.start * cell_size)
            same_pos_size = world.LAND[:, (world.LAND[0] == modified_pos[0]//cell_size)& 
                                          (world.LAND[1] == modified_pos[1]//cell_size)].size
            if same_pos_size == 0 and modified_pos not in add_land:
                add_land.append(modified_pos)
            mouse_movement = True
        elif inp == 0:
            add_land_array = np.array(add_land).T // cell_size
            world.LAND = np.concatenate([world.LAND, add_land_array], axis = 1) #, dtype = int)
            mouse_movement = False

        
        ### RENDER ###
        theta_slice = world.THETAS[world_slicer_x, world_slicer_y]
        
        if draw == 'composite':
            draw_world(WINDOW, world, cell_size)
            #times['Draw']['composite'] = (times['Draw']['composite']  + clock.tick_busy_loop() / 1000) / 2 
        elif draw == 'currents': 
            draw_currents(WINDOW, world.CURRENTS, cell_size)
            #times['Draw']['currents'] = (times['Draw']['currents']  + clock.tick_busy_loop() / 1000) / 2 
        elif draw == 'winds':
            draw_winds(WINDOW, world.WINDS, cell_size)
            #times['Draw']['winds'] = (times['Draw']['winds']  + clock.tick_busy_loop() / 1000) / 2 
        elif draw == 'np':
            #sa.pixels3d(WINDOW)
            pa_fill_color(pa, world.THETAS[world_slicer_x, world_slicer_y, 1], cell_size)
            #pa_random_color(pa, world.THETAS[:,:,1], cell_size)
            #screen_blur(pa)
            #times['Draw']['np'] = (times['Draw']['np']  + clock.tick_busy_loop() / 1000) / 2 
        elif draw == 'sa':
            pa[...] = (64,204,190)
            draw_normal_current_triangles(pa, world.THETAS[world_slicer_x, world_slicer_y], cell_size)
            #times['Draw']['sa']['norm'] = (times['Draw']['sa']['norm'] + clock.tick_busy_loop() / 1000) / 2
            rotate_current_triangles(pa, world.THETAS[world_slicer_x, world_slicer_y], cell_size)
            #times['Draw']['sa']['rotate'] = (times['Draw']['sa']['rotate'] + clock.tick_busy_loop() / 1000) / 2
        elif draw == 'mod':
            draw_str_modified_current_triangles(pa, world.THETAS[world_slicer_x, world_slicer_y], cell_size)
            rotate_current_triangles(pa, world.THETAS[world_slicer_x, world_slicer_y], cell_size)
            
        draw_land(pa, world.LAND, cell_size, (world_slicer_x, world_slicer_y), world)
            
        # # TO BLIT to Window Without Using Pixels3D Object
        # if count == 5:
        #     del pa
        #     #WINDOW.unlock()
        #     print(WINDOW.mustlock())
        #     surf = pygame.Surface((30,40))
        #     print(type(surf))
        #     WINDOW.blit(surf, (500,300))
        #     pa = sa.pixels3d(WINDOW)
            
        #times['Draw'] += clock.tick_busy_loop() / 1000
        
        pygame.display.update()
        #times['Render'] += clock.tick_busy_loop() / 1000
        
        ### SIMULATE WORLD ###
        world.propogate_array(array = 'currents')
        world.set_currents()
        #times['Prop Currents'] += clock.tick_busy_loop() / 1000
        # world.impact_land()
        world.apply_energy_loss()
        #times['Apply Loss'] += clock.tick_busy_loop() / 1000
        
        count += 1
        
        # if count == 200:
        #     draw = 'mod'
        # if count == 400:
        #     draw = 'np'
        # if count == 600:
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
    t[:] = [(tup[0][x], tup[1][x]) for x in range(1948)]
    
    unq = np.unique(t)
    new_land = np.empty((2,unq.size), dtype = int)
    new_land[0] = [x[0] for x in unq]
    new_land[1] = [x[1] for x in unq]
    
    with open(f'{name}.json', 'w') as f:
        json.dump(new_land.tolist(), f)


