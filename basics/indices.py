import numpy as np

DEFAULT_ARRAY_ROUNDING = np.round
DEFAULT_SINGLE_ROUNDING = round


def get_start_pixels(world_indices, cell_size):
    # Convert world indices to PixelArray top-left corner indixes
    return (world_indices[0] * cell_size, world_indices[1] * cell_size)

def get_current_triangle_indices(thetas, left_bound, right_bound, strengths):
    # Used with normalized angles to get triangle shapes and regular thetas to flip triangles into place
    return np.where((thetas <= left_bound) & (thetas > right_bound) & (strengths > .5))

def index_range(index_array, size, pixel_indices = None):
    # Get full PixelArray index tuples for given shape (as size) or square axis ranges
    if pixel_indices: # equivalent to index_shape
        return index_array[:, None] + size[None]
    else: # equivalent to index_block
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

def get_indices_within_bounds(indices, x_max, y_max, x_min = 0, y_min = 0):
    # trim in IndexArray class
    return indices[:, (indices[0] < x_max)&
                      (indices[0] >= x_min)&
                      (indices[1] < y_max)&
                      (indices[1] >= y_min)]








def rotate(texture, rotation):
    indices = np.asarray(texture == 0).nonzero()

    if texture.shape[0] % 2 == 0:
        mid_y = texture.shape[0] / 2 - .5
    else:
        mid_y = texture.shape[0] // 2

    if texture.shape[1] % 2 == 0:
        mid_x = texture.shape[1] / 2 - .5
    else:
        mid_x = texture.shape[1] // 2

    centered = np.array((indices[0] - mid_y, indices[1] - mid_x))
    thetas = np.arctan2(centered[1], centered[0]) # Note: this means that 'up' on the texture array is 0rads in world/pixel array, e.g. 'right'
    str = np.sqrt(centered[0] ** 2 + centered[1] ** 2)

    new_thetas = thetas + rotation
    new_indices =  np.array(((np.cos(new_thetas) * str).round(), (np.sin(new_thetas) * str).round()), dtype = int)

    new_indices[0] -= new_indices[0].min()
    new_indices[1] -= new_indices[1].min()

    x_size = new_indices[1].max() - new_indices[1].min() + 1
    y_size = new_indices[0].max() - new_indices[0].min() + 1

    new_array = np.ones((y_size, x_size), dtype = int)
    new_array[:,:] = 130
    new_array[(new_indices[0], new_indices[1])] = 0

    return new_array

def rotate2(texture, rotation):
    indices = np.asarray(texture == 0).nonzero()

    if texture.shape[0] % 2 == 0:
        mid_y = texture.shape[0] / 2 - .5
    else:
        mid_y = texture.shape[0] // 2

    if texture.shape[1] % 2 == 0:
        mid_x = texture.shape[1] / 2 - .5
    else:
        mid_x = texture.shape[1] // 2

    centered = np.array((indices[0] - mid_y, indices[1] - mid_x))
    thetas = np.arctan2(centered[1], centered[0]) # Note: this means that 'up' on the texture array is 0rads in world/pixel array, e.g. 'right'
    str = np.sqrt(centered[0] ** 2 + centered[1] ** 2)

    new_thetas = thetas - rotation
    new_x = np.cos(new_thetas) * str
    new_y = np.sin(new_thetas) * str

    new_x -= new_x.min()
    new_y -= new_y.min()

    new_indices = np.array((new_x.round(), new_y.round()), dtype = int)

    x_size = new_indices[0].max() - new_indices[0].min() + 1
    y_size = new_indices[1].max() - new_indices[1].min() + 1

    new_array = np.ones((x_size, y_size), dtype = int)
    new_array[:,:] = 13
    new_array[(new_indices[0], new_indices[1])] = 0

    return new_indices




def get_centered_texture(texture):
    '''
    Docstring for get_centered_texture
    
    :param texture: rectangular array where selected indices are set to 0 (default is any nonzero)
    '''
    indices = np.asarray(texture == 0).nonzero()

    if texture.shape[0] % 2 == 0:
        mid_y = texture.shape[0] / 2 - .5
    else:
        mid_y = texture.shape[0] // 2

    if texture.shape[1] % 2 == 0:
        mid_x = texture.shape[1] / 2 - .5
    else:
        mid_x = texture.shape[1] // 2

    centered = np.array((indices[0] - mid_y, indices[1] - mid_x))
    return centered

def get_centered_index_array(index_array):
    x_min = index_array[0].min()
    x_max = index_array[0].max()
    y_min = index_array[1].min()
    y_max = index_array[1].max()
    x_rng = x_max - x_min
    y_rng = y_max - y_min

    if y_rng % 2 == 0:
        mid_y = y_rng / 2 - .5
    else:
        mid_y = y_rng // 2

    if x_rng % 2 == 0:
        mid_x = x_rng / 2 - .5
    else:
        mid_x = x_rng // 2

    centered = np.array([index_array[0] - mid_x, index_array[1] - mid_y])
    return centered

def center_index_array(index_array):
    x_min = index_array[0].min()
    x_max = index_array[0].max()
    y_min = index_array[1].min()
    y_max = index_array[1].max()
    x_rng = x_max - x_min
    y_rng = y_max - y_min

    if y_rng % 2 == 0:
        mid_y = y_rng / 2 - .5
    else:
        mid_y = y_rng // 2

    if x_rng % 2 == 0:
        mid_x = x_rng / 2 - .5
    else:
        mid_x = x_rng // 2

    index_array[0] -= mid_x
    index_array[1] -= mid_y

def rotate_index_array(index_array, rotation = 0):
    thetas = np.arctan2(index_array[1], index_array[0]) # Note: this means that 'up' on the texture array is 0rads in world/pixel array, e.g. 'right'
    str = np.sqrt(index_array[0] ** 2 + index_array[1] ** 2)

    new_thetas = thetas + rotation
    new_x = np.cos(new_thetas) * str
    new_y = np.sin(new_thetas) * str

    new_indices = np.array((new_x.round(), new_y.round()), dtype = int)
    return new_indices

def rotate_texture(texture, rotation):
    centered = get_centered_texture(texture)
    rotated_index = rotate_index_array(centered, rotation)

    rotated_index[0] -= rotated_index[0].min()
    rotated_index[1] -= rotated_index[1].min()

    x_size = rotated_index[0].max() - rotated_index[0].min() + 1
    y_size = rotated_index[1].max() - rotated_index[1].min() + 1

    new_array = np.ones((x_size, y_size), dtype = int)
    new_array[:,:] = 13
    new_array[(rotated_index[0], rotated_index[1])] = 0

    return new_array




## Rotations
# -45d  - np.rot90(np.flip(array, axis = 1), -1)
# -90d  - np.rot90(array, -1)
# -135d - np.flip(array, axis = 0)
# -180d - np.flip(array, axis = (0,1))
# -225d - array.T
# -270d - np.rot90(array, 1)
# -315d - np.flip(array, axis = 1)

