

import numpy as np
from algorithms.indices import get_pixel_indices, get_start_pixels
from algorithms.generics import normalize_angles, normal_compare_angles

# 30, 120, 110 good sea blue/green
# cloudy dark blue: 25, 109, 158
# tuquoise: 64, 204, 190

# blue slider: 190 for light, 90 for dark
# b:g ratio (min/max): .752, 1.29; g:b - 1.33, .776
# red slider: min of 20 for clear, up to 90 for near grey



## WIND/Current assumptions
# winds between 0-120, every ten represnets one step on Beaufort Scale
# currents assumed 3% of wind speed - 0 - 


# world = np.array([[.1,.3,.5,.7],
#                 [.3,.4,.6,.9],
#                 [1.1,1.5,.6,.7],
#                 [.8,.3,.1,1.2]])


# world_indices = (np.array([1,2]),np.array([2,1]))
# start_indices = (world_indices[0] * 10, world_indices[1] * 10)
# pixel_blocks = get_pixel_indices(start_indices, 10)


# world_strengths = world[world_indices]

# pixel_strengths = world_strengths.repeat(10*10)

one = np.array([   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 4, 4, 3, 2, 1, 0, 0, 0],
                   [0, 0, 0, 4, 3, 2, 1, 1, 0, 0],
                   [0, 0, 0, 0, 3, 3, 2, 2, 0, 0],
                   [0, 0, 0, 0, 0, 3, 3, 3, 0, 0],
                   [0, 0, 0, 0, 0, 0, 4, 4, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 4, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]).ravel()

two = np.array([   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
                   [0, 4, 4, 2, 2, 2, 1, 1, 0, 0],
                   [0, 0, 4, 3, 3, 2, 2, 1, 0, 0],
                   [0, 0, 0, 0, 3, 3, 2, 2, 0, 0],
                   [0, 0, 0, 0, 0, 3, 4, 4, 0, 0],
                   [0, 0, 0, 0, 0, 0, 3, 4, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]).ravel()

thre = np.array([  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                   [0, 0, 0, 4, 2, 1, 1, 1, 0, 0],
                   [0, 4, 4, 3, 3, 2, 1, 1, 0, 0],
                   [0, 0, 0, 3, 3, 3, 2, 2, 0, 0],
                   [0, 0, 0, 0, 0, 3, 3, 4, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 4, 4, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]).ravel()

three = np.array([ [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                   [0, 0, 0, 4, 2, 2, 1, 1, 0, 0],
                   [0, 4, 4, 3, 3, 3, 2, 2, 0, 0],
                   [0, 0, 0, 3, 3, 3, 3, 2, 0, 0],
                   [0, 0, 0, 0, 0, 3, 3, 4, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 4, 4, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]).ravel()

four = np.array([   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                    [0, 0, 3, 2, 2, 1, 1, 0, 0, 0],
                    [0, 4, 4, 3, 3, 2, 2, 1, 0, 0],
                    [0, 0, 4, 3, 3, 3, 3, 2, 0, 0],
                    [0, 0, 0, 0, 0, 3, 3, 4, 4, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 4, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]).ravel()

five = np.array([  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                   [0, 0, 0, 0, 1, 1, 2, 0, 0, 0],
                   [0, 0, 0, 4, 3, 2, 2, 0, 0, 0],
                   [0, 4, 4, 4, 3, 3, 3, 4, 0, 0],
                   [0, 0, 0, 0, 0, 3, 3, 4, 4, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]).ravel()


six = np.array([   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                   [0, 0, 0, 2, 1, 1, 2, 0, 0, 0],
                   [0, 0, 4, 3, 2, 2, 2, 4, 0, 0],
                   [0, 4, 4, 3, 3, 3, 3, 4, 4, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]).ravel()




# textures = np.tile(three.ravel(), int(pixel_strengths.size/(10*10)))


# mod_pixel_strengths = pixel_strengths * textures

# scaled = np.arctan(mod_pixel_strengths/2)
# percentile = scaled / (np.pi/2)

# blue = 209 - ( (209 - 48) * percentile )
# green = blue / 1.113537
# red = 0

angle_triangle_mapp = {6: six,
                      5: five,
                      4: four,
                      3: thre,
                      2: two,
                      1: one
                     }
    




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
        
