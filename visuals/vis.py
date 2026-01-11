from algorithms.generics import vector_length, DBZ, normalize_angles, normal_compare_angles, rotation_map, rotate_subarray, shift_array
from algorithms.indices import index_shape, get_start_pixels, get_pixel_indices
from visuals.textures.triangles_indices import angle_triangle_map
from visuals.textures.str_map import angle_triangle_mapp
from visuals.textures.textures import particle, ship, rotate, rotate2, rotate_texture
import numpy as np

import pygame
from pygame import Rect
# pygame.font.init()
    


def current_fill_map1(strength):
    # green to blue ratio: 1:1.71
    # darker green/blue bounds: 28, 48
    # ligher green/blue bounds: 149, 255
    # red spectrum: 105 lighter, 0 darker
    # spectrum from 105r, 255b to 0r, 48b 
    # (blue - red)*(1-.17) = green

    
    scaled = np.arctan(strength/4)
    percentile = scaled / (np.pi/2)
    
    r = 105 * (1 - percentile)
    b = 255 - ( (255 - 48) * percentile )
    g = (b - r) * (1 - .17)
    
    return int(r),int(g),int(b)

def current_fill_map2(strength):
    # green to blue ratio: 1:1.113537
    # darker green/blue bounds: 44, 48
    # ligher green/blue bounds: 229, 255
    # 0 red
    # (blue - red)*(1-.17) = green
    # str 0 RGB: 209, 187.69, 0
    
    scaled = np.arctan(strength/2)
    percentile = scaled / (np.pi/2)
    
    b = 209 - ( (209 - 48) * percentile )
    g = b / 1.113537
    r = 0
    
    return int(r),int(g),int(b)


    
    
    
    
def draw_world(win, world, cell_size = 0):    
    win.fill((0,0,0))
    
    for col in range(world.CURRENTS.shape[0]):
        for row in range(world.CURRENTS.shape[1]):
            x, y = world.CURRENTS[col, row, 0], world.CURRENTS[col, row, 1]
            s = vector_length(x, y)
            
            # Colored Square
            rect = Rect(col*cell_size, row*cell_size, cell_size, cell_size)
            
            wind_factor = world.WINDS[col, row] / 100
            grey_hue = 50 * wind_factor
            current_color = current_fill_map2(s)
            color = tuple(max(0, x - grey_hue) for x in current_color)
            
            pygame.draw.rect(win, color, rect)
            
            # Angle Line
            r = cell_size * (1/4) # radius of inner circle within rect
            m = ( col*cell_size + round(cell_size/2), row*cell_size + round(cell_size/2) ) # midpoint of circle on pygame surface
            norm_factor = DBZ(r, s, 0)
            front_x = round(x * norm_factor)
            front_y = - round(y * norm_factor)
            
            pygame.draw.line(win, (0,0,0), (m[0] + front_x, m[1] + front_y), (m[0] - front_x, m[1] - front_y), 1)

def draw_currents(win, currents, cell_size = 0):
    win.fill((0,0,0))
    
    for col in range(currents.shape[0]):
        for row in range(currents.shape[1]):
            x, y = currents[col, row, 0], currents[col, row, 1]
            s = vector_length(x, y)
            
            # Colored Square
            rect = Rect(col*cell_size, row*cell_size, cell_size, cell_size)
            color = current_fill_map2(s)
            pygame.draw.rect(win, color, rect)
            
def draw_winds(win, winds, cell_size = 0):
    win.fill((240,240,240))
    
    for col in range(winds.shape[0]):
        for row in range(winds.shape[1]):
            # Colored Square
            rect = Rect(col*cell_size, row*cell_size, cell_size, cell_size)
            
            strength = winds[col, row]
            color = (150 - strength, 150 - strength, 150 - strength)
            
            if strength > 0:
                pygame.draw.rect(win, color, rect)         
                


        
        
def pa_random_color(pa, strengths, distance, cell_size, ref_size = (400,200)):
    shape = pa.shape[:2]
    
    #str_big = np.repeat(np.repeat(strengths, cell_size, axis = 1), cell_size, axis = 0)
    str_big = strengths.repeat(cell_size, axis = 1).repeat(cell_size, axis = 0)
    pa[:,:,2] = 190 - ( 100 * np.minimum(1, np.sqrt(str_big)/10) ) # make 10 a parameter
    #pa[:,:,1] = pa[:,:,2]
    #pa[:,:,1] = pa[:,:,2] * np.random.uniform(.57,1.2,shape)
    pa[:,:,1] = pa[:,:,2] * np.random.normal(.9, .1, shape)
    pa[:,:,0] = np.random.uniform(20,30,shape)
    

def pa_fill_color(pa, strengths, distance, cell_size, ref_size = (400,200)):
    scaled = np.arctan(strengths/2)
    percentile = scaled / (np.pi/2)
    
    blue = 209 - ( (209 - 48) * percentile )
    green = blue / 1.113537
    
    blue_big = np.repeat(np.repeat(blue, cell_size, axis = 1), cell_size, axis = 0)
    green_big = np.repeat(np.repeat(green, cell_size, axis = 1), cell_size, axis = 0)
    
    pa[:,:,2] = blue_big
    pa[:,:,1] = green_big #pa[:,:,2] / 1.113537
    pa[:,:,0] = 0
    

def funky1(pa, strengths, distance, cell_size, ref_size = (400,200)):
    scaled = np.arctan(strengths/2)
    percentile = scaled / (np.pi/2)
    
    blue = 209 - ( (209 - 48) * percentile * distance )
    green = blue / 1.113537
    
    blue_big = np.repeat(np.repeat(blue, cell_size, axis = 1), cell_size, axis = 0)
    green_big = np.repeat(np.repeat(green, cell_size, axis = 1), cell_size, axis = 0)
    
    pa[:,:,2] = blue_big
    pa[:,:,1] = pa[:,:,2] / 1.113537
    pa[:,:,0] = 0
    

    
def funky2(pa, strengths, distance, cell_size, ref_size = (400,200)):
    dist_big = np.repeat(np.repeat(distance, cell_size, axis = 1), cell_size, axis = 0)
    
    pa[:,:,2] = 209 - ( (209 - 48) * dist_big )     #(1 - dist_big / distance.max()) 
    pa[:,:,1] = pa[:,:,2] / 1.113537
    pa[:,:,0] = 0
    
    
    
def fill_color_light(pa, strengths, distance, cell_size, ref_size = (400,200)):
    #adjusted_strength = np.maximum(( 70 * (strengths**(1/3)) ), 200)
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = np.minimum(distance / 282, 1) #np.sqrt(300**2 + 300**2)
    
    blue = (240 - (240) * adjusted_strength) * (1 - adjusted_distance)**2
    green = blue / 1.113537
    red = blue * .6315789 * (1 - adjusted_distance)**2 # np.zeros(blue.shape) #
    
    blue_big = np.repeat(np.repeat(blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big
    
    
def fill_color_sun(pa, strengths, distance, cell_size, ref_dist = 200):
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = np.minimum(distance / 200, 1) #np.sqrt(300**2 + 300**2)
    
    base_blue = (240 - (240) * adjusted_strength) * (1 - adjusted_distance)**2
    base_green = base_blue * .898039 # blue / 1.113 as base; increased when near sun
    base_red = np.zeros(base_blue.shape)
    
    # Under sun slightly yellow
    base_green[adjusted_distance <= .3] = base_blue[adjusted_distance <= .3] * \
                                            ( .898039 + (.992157 - .898039) * (1 - \
                                                        ( adjusted_distance[adjusted_distance <= .3]/.3) ) )
    
    base_red[adjusted_distance <= .3] = base_blue[adjusted_distance <= .3] * .866071 * \
                                                        ( 1 - (adjusted_distance[adjusted_distance <= .3]/.3) )
                                                        
    blue_big = np.repeat(np.repeat(base_blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(base_green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(base_red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big
                                                        
                                                        

def fill_color_sun2(pa, strengths, distance, cell_size, ref_size = (400,200)):
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = distance / np.sqrt(ref_size[0]**2 + ref_size[1]**2) #np.sqrt(300**2 + 300**2)
    
    base_blue = 240 - ( (240) * adjusted_strength * (1 - adjusted_distance)**2 )
    base_green = base_blue * .992157 * (1 - np.maximum(0, adjusted_distance - .28))**2 # blue / 1.113 as base; increased when near sun
    
    #base_red = np.zeros(base_blue.shape)
    #base_red[adjusted_distance > .5] = 40
    base_red = base_blue * (1 - np.absolute(adjusted_distance - .4))**3
    #base_red = base_blue * 2 * (np.maximum((adjusted_distance - .45), 0))
    # base_red[adjusted_distance <= .3] = base_blue[adjusted_distance <= .3] * .866071 * \
    #                                                     ( 1 - (adjusted_distance[adjusted_distance <= .3]/.3) )

    blue_big = np.repeat(np.repeat(base_blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(base_green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(base_red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big
    
    
def fill_ind_colors(pa, strengths, distance, cell_size, ref_size = (400,200)):
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = distance / np.sqrt(ref_size[0]**2 + ref_size[1]**2) #np.sqrt(300**2 + 300**2)
    
    #base_blue = 30 + ( 210 * (1 - adjusted_strength) * (1 - adjusted_distance)**2 )
    base_blue = 30 + ( 210 * (1 - adjusted_strength) * (1 - adjusted_distance)**2 * (np.absolute(.5 - adjusted_distance) / .5)**2 )
    
    base_green = 245 * (1 - adjusted_strength) * (1 - adjusted_distance)**2 * (np.absolute(.5 - adjusted_distance) / .5)**2
    base_red = 50 * (1 - adjusted_strength) * (1 - np.absolute(.55 - adjusted_distance))**7
    
    blue_big = np.repeat(np.repeat(base_blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(base_green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(base_red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big    
    
def fill_ind_red(pa, strengths, distance, cell_size, ref_size = (400,200)):
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = distance / np.sqrt(ref_size[0]**2 + ref_size[1]**2) #np.sqrt(300**2 + 300**2)

    base_blue = 230 * (1 - adjusted_strength) * (1 - adjusted_distance)**2 * ( np.minimum(.07,np.absolute(.52 - adjusted_distance)) / .07)
    
    base_green = 300 * (1 - adjusted_strength) * (.9 - adjusted_distance)**2 * ( np.minimum(.07,np.absolute(.58 - adjusted_distance)) / .07)
    # base_red = 60 * (1 - adjusted_strength) * (1 - np.absolute(.55 - adjusted_distance))**7
    base_red = 50 * (1 - adjusted_strength) * (1 - np.absolute(.55 - adjusted_distance))**7
    
    blue_big = np.repeat(np.repeat(base_blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(base_green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(base_red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big       
    
    
def fill_fluc_blue(pa, strengths, distance, cell_size, ref_size = (400,200)):
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = distance / np.sqrt(ref_size[0]**2 + ref_size[1]**2) #np.sqrt(300**2 + 300**2)
    
    base_blue = ( 60 * adjusted_distance**3 ) + 240 * (1 - adjusted_strength) * \
                (1 - adjusted_distance)**2 * ( np.minimum(.2, np.absolute(adjusted_distance - .6)) / .2 )
    
    base_green = 250 * (1 - adjusted_strength) * (1 - adjusted_distance)**2
    # base_red = np.maximum(0, 120 * np.sin(10 * adjusted_distance - 3.4) * (1 - adjusted_strength))
    base_red = 120 * ( 1 - np.minimum(.1, np.absolute(.55-adjusted_distance)) / .1 )
    
    blue_big = np.repeat(np.repeat(base_blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(base_green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(base_red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big      
    
    
def fill_parabola(pa, strengths, distance, cell_size, ref_size = (400,200)):
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = distance / np.sqrt(ref_size[0]**2 + ref_size[1]**2) #np.sqrt(300**2 + 300**2)
    
    base_blue = 60 * (1 - adjusted_strength) * (2 - adjusted_distance)**2 * ( np.minimum(.07, np.absolute(adjusted_distance - .52)) / .07 )
    
    base_green = 77 * (1 - adjusted_strength) * (1.8 - adjusted_distance)**2 * ( np.minimum(.07, np.absolute(adjusted_distance - .58)) / .07 )
    base_red = np.maximum(0,140 + -7000 * (.55-adjusted_distance)**2) * (1 - adjusted_strength)
    
    blue_big = np.repeat(np.repeat(base_blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(base_green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(base_red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big      
        
    
    
def draw_str_modified_current_triangles(pa, thetas, cell_size = 10): #world_indices, world_strengths, angle = 1.1, cell_size = 10):
    pa[:,:,0] = 0
    
    normalized = normalize_angles(thetas[:,:,0])
    for i in range(6):
        if i == 0:
            world_indices = np.where((normalized <= normal_compare_angles[i]) & (normalized >= np.pi/4))
        elif i <= 4:
            world_indices = np.where((normalized <= normal_compare_angles[i]) & (normalized > normal_compare_angles[i-1]))
        elif i == 5:
            world_indices = np.where((normalized <= np.pi/2) & (normalized > normal_compare_angles[i-1]))
            
        world_strengths = thetas[(world_indices[0], world_indices[1], 1)]
        start_indices = get_start_pixels(world_indices, cell_size)
        textures = np.tile(angle_triangle_mapp.get(i+1, angle_triangle_mapp[6]), world_strengths.size)
        pixel_blocks = get_pixel_indices(start_indices, cell_size)
        pixel_strengths = world_strengths.repeat(cell_size*cell_size)
        mod_pixel_strengths = pixel_strengths * textures
        
        scaled = np.arctan(mod_pixel_strengths/2)
        percentile = scaled / (np.pi/2)
        
        pa[(pixel_blocks[0],pixel_blocks[1],2)] = 209 - ( (209 - 48) * percentile )
        pa[(pixel_blocks[0],pixel_blocks[1],1)] = pa[(pixel_blocks[0],pixel_blocks[1],2)] / 1.113537
    
    
def draw_normal_current_triangles(pa, thetas, cell_size):
    ## Paint triangle indices on normalized angles
    normalized = normalize_angles(thetas[:,:,0])
    for i in range(6):
        if i == 0:
            world_indices = np.where((normalized <= normal_compare_angles[i]) & (normalized >= np.pi/4) & (thetas[:,:,1]> .5) )
        elif i <= 4:
            world_indices = np.where((normalized <= normal_compare_angles[i]) & (normalized > normal_compare_angles[i-1]) & (thetas[:,:,1] > .5) )
        elif i == 5:
            world_indices = np.where((normalized <= np.pi/2) & (normalized > normal_compare_angles[i-1]) & (thetas[:,:,1] > .5) )
            
        start_pixels = get_start_pixels(world_indices, cell_size)
        triangles = angle_triangle_map.get(i+1, angle_triangle_map[6])[0]
        pixels = ( index_shape(start_pixels[0], triangles[0]).ravel(), 
                   index_shape(start_pixels[1], triangles[1]).ravel() )
        
        pa[pixels] = (0,0,0)
    

def rotate_current_triangles(pa, thetas, cell_size):
    for rotation, angles in rotation_map.items():
        if rotation == 45:
            world_indices = np.where((thetas[:,:,0] < angles[0])&
                                     (thetas[:,:,0] > angles[1]))
        elif rotation == 225: 
            world_indices = np.where((thetas[:,:,0] <= angles[0])&
                                     (thetas[:,:,0] >= angles[1]))            
        else:
            world_indices = np.where((thetas[:,:,0] <= angles[0])&
                                     (thetas[:,:,0] > angles[1]))
        start_pixels = get_start_pixels(world_indices, cell_size)
        
        ranges = get_pixel_indices(start_pixels, cell_size)
        arrays = pa[ranges].reshape(world_indices[0].size, cell_size, cell_size, 3) # first axis in list of pixel squares, 2 and 3 X/Y, 4 RGB
        rotated = rotate_subarray(arrays, rotation)
        
        pa[ranges] = rotated.reshape(int(rotated.size/3),3)
    
    
def screen_blur(pa):
    # shift pa array to calculate average 3x3 colors
    summ = pa[...].astype(float)
    y = True
    for pair in [(-1, 1),(1, 1),(1, -1),(-1, -1)]:  
        if y:
            cell = [(0, pair[0]), (pair[1], pair[0])]
        else:
            cell = [(pair[0], 0), (pair[0], pair[1])]
            
        ## Shift 1
        shift = shift_array(pa, pair[0], y = y, fill = 0)
        summ += shift

        ## Shift 2
        shift = shift_array(shift, pair[1], y = not y, fill = 0)
        summ += shift
    
        y = not y
    
    pa[...] = (summ / 9).astype(int)
    
    




def current_fill_np(angle, strength, cell_size):
    scaled = np.arctan(strength/4)
    percentile = scaled / (np.pi/2)
    pass


def draw_land(pa, land, cell_size, world_slicers, color = (255,0,0)):
    visible_land = land[:,  (land[0] >= world_slicers[0].start)&
                            (land[0] < world_slicers[0].stop)&
                            (land[1] >= world_slicers[1].start)&
                            (land[1] < world_slicers[1].stop)]
    visible_land[0] -= world_slicers[0].start
    visible_land[1] -= world_slicers[1].start
        
    start_pixels = get_start_pixels(visible_land, cell_size)
    pixels = get_pixel_indices(start_pixels, cell_size)
    
    pa[pixels] = color

def draw_sun(pa, sun, cell_size, world_slicers, color = (200,100,100)):
    if sun[0] >= world_slicers[0].start and sun[1] < world_slicers[0].stop \
        and sun[1] >= world_slicers[1].start and sun[1] < world_slicers[1].stop:
            
        drawn_sun = (sun[0] - world_slicers[0].start, sun[1] - world_slicers[1].start)
            
        start_pixels = get_start_pixels(drawn_sun, cell_size)
        pixels = np.mgrid[start_pixels[0]:start_pixels[0] + cell_size,
                          start_pixels[1]:start_pixels[1] + cell_size]
        
        pa[(pixels[0], pixels[1])] = color

def draw_particles(pa, particles, pa_size, cell_size, world_slicers, start_pixels, color = (0,0,0)):
    world_idx = particles[:2,   (particles[0] >= world_slicers[0].start)&
                                (particles[0] < world_slicers[0].stop)&
                                (particles[1] >= world_slicers[1].start)&
                                (particles[1] < world_slicers[1].stop)]
    # print('WORLD_IDX 1: ', world_idx.T)
    world_idx[0] -= world_slicers[0].start # Get world index zerod on displayed world
    world_idx[1] -= world_slicers[1].start
    # print('WORLD_IDX 2: ', world_idx.T)
    
    draw_idx = world_idx * cell_size # convert to pixel index
    # print('DRAW_IDX 1: ', draw_idx.T)

    draw_idx[0] -= start_pixels[0]
    draw_idx[1] -= start_pixels[1]
    # print('DRAW_IDX 2: ', draw_idx.T)

    texture = particle()
    pixels = (  index_shape(draw_idx[0], texture[0]).ravel(), 
                index_shape(draw_idx[1], texture[1]).ravel() )
    on_screen = (pixels[0] >= 0)&(pixels[0] < pa_size[0])&(pixels[1] >= 0)&(pixels[1] < pa_size[1])

    
    asint = (pixels[0][on_screen].astype(int), pixels[1][on_screen].astype(int))
    # print('DRAW_IDX 3: ', draw_idx.astype(int).T)
    # print('_____________________________')
    pa[asint] = (0,0,0)


def draw_ship(pa, _ship, pa_size, cell_size, world_slicers, start_pixels, color = (0,0,0)):
    x = (_ship.position[0] - world_slicers[0].start) * cell_size - start_pixels[0]
    y = (_ship.position[1] - world_slicers[1].start) * cell_size - start_pixels[1]

    texture = rotate2(ship, _ship.heading)
    #texture = rotate_texture(ship, _ship.heading)
    # TODO: rotate texture

    pixels = (  index_shape(np.array([x], dtype = int), texture[0]).ravel(), 
                index_shape(np.array([y], dtype = int), texture[1]).ravel() )

    in_bounds = ((pixels[0] >= 0)&
                       (pixels[0] < pa_size[0])&
                       (pixels[1] >= 0)&
                       (pixels[1] < pa_size[1]))
    pa[(pixels[0][in_bounds], pixels[1][in_bounds])] = color






    
    
    
    
    
    




   