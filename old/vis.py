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
                




   