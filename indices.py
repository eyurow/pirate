import numpy as np


def get_start_pixels(world_indices, cell_size):
    # Convert world indices to PixelArray top-left corner indixes
    return (world_indices[0] * cell_size, world_indices[1] * cell_size)

def get_current_triangle_indices(thetas, left_bound, right_bound, strengths):
    # Used with normalized angles to get triangle shapes and regular thetas to flip triangles into place
    return np.where((thetas <= left_bound) & (thetas > right_bound) & (strengths > .5))

def index_range(index_array, size, pixel_indices = None):
    # Get full PixelArray index tuples for given shape (as size) or square axis ranges
    if pixel_indices: # set pixel indices to True and place current triangle indices in size for all indices correspoding to triangle
        return index_array[:, None] + size[None]
    else: # Get sqauare axis ranges from start indices
        # same as np.outer(ind_array, range(size))
        return index_array[:, None] + np.arange(stop = size)[None]
    
def index_shape(index_array, shape_array):
    # set pixel indices to True and place current triangle indices in size for all indices correspoding to triangle
    return index_array[:, None] + shape_array[None]
    
def index_block(index_array, block_size):
    # Get sqauare axis ranges from start indices
    # same as np.outer(ind_array, range(size))
    return index_array[:, None] + np.arange(stop = block_size)[None]

def get_pixel_indices(start_indices, cell_size):
    # Get full 10x10 pixels index for each start index
    x_range = index_block(start_indices[0], cell_size)
    y_range = index_block(start_indices[1], cell_size)
    
    x_rep = x_range.repeat(cell_size, axis = 0)
    y_rep = y_range.repeat(cell_size, axis = 1)
    
    return (x_rep.ravel(), y_rep.ravel())




## Rotations
# -45d  - np.rot90(np.flip(array, axis = 1), -1)
# -90d  - np.rot90(array, -1)
# -135d - np.flip(array, axis = 0)
# -180d - np.flip(array, axis = (0,1))
# -225d - array.T
# -270d - np.rot90(array, 1)
# -315d - np.flip(array, axis = 1)

