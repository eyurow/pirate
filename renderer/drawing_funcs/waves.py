import numpy as np

from renderer.textures.waves import angle_triangle_map, angle_triangle_mapp
from basics.indices import get_pixel_indices, get_start_pixels, index_shape

'''
Use textures for six degrees of angle variation within a pi/2-pi/4 arc 
NOTE - Cell size must match texture size

Normalize Angles: normalizes all world thetas to the pi/2-pi/4 arc

Triangle rotation: rotate groups of pixels 

Drawing Process:
    1. normalize world thetas
    2. loop 6 degrees of variance and draw appropriate wave texture
    3. rotate pixel blocks back to real position

    -->
            draw_str_modified_current_triangles / draw_normal_current_triangles (pa, world.THETAS[world_slicer_x, world_slicer_y], cell_size)
            rotate_current_triangles (pa, world.THETAS[world_slicer_x, world_slicer_y], cell_size)
'''


## Rotate world thetas to normalized arc segment
def normalize_angles(array):
    # array: array of thetas (from WORLD)
    # returns thetas normalized to a pi/2-pi/4 arc section
    normal = np.zeros(array.shape)
    
    normal[ (array <= np.pi/2)&(array >= np.pi/4) ] = array[ (array <= np.pi/2)&(array >= np.pi/4) ] 
    
    normal[ (array < np.pi/4)&(array >= 0) ] = np.absolute( array[ (array < np.pi/4)&(array >= 0) ] - np.pi/2 ) # -45d reflect
    normal[ (array < 0)&(array >= -np.pi/4) ] = array[ (array < 0)&(array >= -np.pi/4) ] + np.pi/2 # -90d rotate
    
    normal[ (array < -np.pi/4)&(array >= -np.pi/2) ] = np.absolute( array[ (array < -np.pi/4)&(array >= -np.pi/2) ] )
    normal[ (array < -np.pi/2)&(array >= -3*np.pi/4) ] = array[ (array < -np.pi/2)&(array >= -3*np.pi/4) ] + np.pi
    
    normal[ (array < -3*np.pi/4)&(array >= -np.pi) ] = np.absolute( array[ (array < -3*np.pi/4)&(array >= -np.pi) ] ) - (np.pi/2)
    normal[ (array <= np.pi)&(array >= 3*np.pi/4) ] = array[ (array <= np.pi)&(array >= 3*np.pi/4)] - (np.pi/2)
    
    normal[ (array < 3*np.pi/4)&(array > np.pi/2) ] = np.absolute( array[ (array < 3*np.pi/4)&(array > np.pi/2) ] - np.pi )
    
    return normal

normal_compare_angles = np.linspace((np.pi/4) + (np.pi/4 / 10), (np.pi/2) - (np.pi/4 / 10), 5)   



## Rotate normalized textures back to actual orientation
rotation_map = {# TODO: shift by 1/
                45: (np.pi/4, 0),
                90: (0, -np.pi/4),
                135: (-np.pi/4, -np.pi/2),
                180: (-np.pi/2, -3*np.pi/4),
                225: (-3*np.pi/4, -np.pi),
                270: (np.pi, 3*np.pi/4),
                315: (3*np.pi/4, np.pi/2)
                }

def rotate_subarray(array, rotation):
    if rotation == 45:
        return np.rot90(np.flip(array, axis = 2), -1, axes = (1,2))
    elif rotation == 90:
        return np.rot90(array, -1, axes = (1,2))
    elif rotation == 135:
        return np.flip(array, axis = 1)
    elif rotation == 180:
        return np.flip(array, axis = (1,2))
    elif rotation == 225:
        return np.transpose(array, axes = (0,2,1,3))
    elif rotation == 270:
        return np.rot90(array, 1, axes = (1,2))
    elif rotation == 315:
        return np.flip(array, axis = 2)

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
    


## Basic wave triangles 
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



## Shading given by current strength
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

