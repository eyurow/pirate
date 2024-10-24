from generics import vector_length, DBZ, normalize_angles, normal_compare_angles, rotation_map, rotate_subarray, shift_array
from indices import index_shape, get_start_pixels, get_pixel_indices
from textures.triangles_indices import angle_triangle_map
from textures.str_map import angle_triangle_mapp
import numpy as np

import pygame
from pygame import Rect
pygame.font.init()
    


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
            
            # # Angle Line
            # r = cell_size * (1/4) # radius of inner circle within rect
            # m = ( col*cell_size + round(cell_size/2), row*cell_size + round(cell_size/2) ) # midpoint of circle on pygame surface
            # norm_factor = DBZ(r, s, 0)
            # front_x = round(x * norm_factor)
            # front_y = - round(y * norm_factor)
            
            # pygame.draw.line(win, (0,0,0), (m[0] + front_x, m[1] + front_y), (m[0] - front_x, m[1] - front_y), 1)
            
            
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
        
        
def pa_random_color(pa, strengths, cell_size):
    shape = pa.shape[:2]
    
    #str_big = np.repeat(np.repeat(strengths, cell_size, axis = 1), cell_size, axis = 0)
    str_big = strengths.repeat(cell_size, axis = 1).repeat(cell_size, axis = 0)
    pa[:,:,2] = 190 - ( 100 * np.minimum(1, np.sqrt(str_big)/10) ) # make 10 a parameter
    #pa[:,:,1] = pa[:,:,2]
    #pa[:,:,1] = pa[:,:,2] * np.random.uniform(.57,1.2,shape)
    pa[:,:,1] = pa[:,:,2] * np.random.normal(.9, .1, shape)
    pa[:,:,0] = np.random.uniform(20,30,shape)
    

def pa_fill_color(pa, strengths, cell_size):
    str_big = np.repeat(np.repeat(strengths, cell_size, axis = 1), cell_size, axis = 0)
    
    scaled = np.arctan(str_big/2)
    percentile = scaled / (np.pi/2)
    
    pa[:,:,2] = 209 - ( (209 - 48) * percentile )
    pa[:,:,1] = pa[:,:,2] / 1.113537
    pa[:,:,0] = 0
    
    
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
    
    

def draw_current_triangles(pa, thetas, cell_size):
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
        


def current_fill_np(angle, strength, cell_size):
    scaled = np.arctan(strength/4)
    percentile = scaled / (np.pi/2)
    pass


def draw_land(pa, land, cell_size, world_slicers, world):
    visible_land = land[:,  (land[0] >= world_slicers[0].start)&
                            (land[0] < world_slicers[0].stop)&
                            (land[1] >= world_slicers[1].start)&
                            (land[1] < world_slicers[1].stop)]
    visible_land[0] -= world_slicers[0].start
    visible_land[1] -= world_slicers[1].start
    
    print(np.may_share_memory(visible_land, world.LAND))
    #print(world.LAND.base)
    print(visible_land.base)
    #print(land.base)
        
    start_pixels = get_start_pixels(visible_land, cell_size)
    pixels = get_pixel_indices(start_pixels, cell_size)
    
    pa[pixels] = (255,0,0)
    
    
    
    
    
    




   