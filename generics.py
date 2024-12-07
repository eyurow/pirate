import numpy as np


## Generic
def rrange(stop, start = 0):
    num = start
    if stop > 0:
        while num < stop:
            yield num
            num += 1
    elif stop < 0:
        while num > stop:
            yield num
            num += -1
    else:
        return []

def DBZ(n, d, handle = 0):
    if d == 0:
        return handle
    else:
        return n / d
        
    
## Trig
def vector_length(x, y):
    if isinstance(x, tuple):
        return np.sqrt(x[0]**2 + x[1]**2)
    else:
        return np.sqrt(x**2 + y**2)

def cartesian_to_theta(cartesian, fill = None):
    thetas = np.zeros(cartesian.shape)
    thetas[:,:,0] = np.arctan2(cartesian[:,:,1], cartesian[:,:,0]) # calc thetas from x, y coords
    thetas[:,:,1] = np.sqrt(cartesian[:,:,1]**2 + cartesian[:,:,0]**2) # calc strength using pythag
    if fill:
        thetas[thetas[:,:,1] == 0] = fill # fill zero strength cells with nan
    return thetas

def theta_to_cartesian(thetas, fill = None):
    cartesians = np.zeros(thetas.shape)
    cartesians[:,:,0] = np.cos(thetas[:,:,0]) * thetas[:,:,1]
    cartesians[:,:,1] = np.sin(thetas[:,:,0]) * thetas[:,:,1]
    if fill:
        pass
    return cartesians

def calc_normal_carts_to_position(index, position, handle = 1, return_distance = False):
    distance = np.sqrt((position[0] - index[0])**2 + (index[1] - position[1])**2)
    distance[distance == 0] = handle
    x = (position[0] - index[0]) / distance
    y = (index[1] - position[1]) / distance
    if return_distance:
        return x, y, distance
    else:
        return x, y

def generate_circle(radius = 5, offset = (0,0)):
    x = radius 
    y = 0
    
    xs = []
    ys = []
    while y <= x:
        if (x**2) + (y**2) <= radius**2:
            xs.append(x)
            ys.append(y)
            y += 1
        else:
            x -= 1
            xs.append(x)
            ys.append(y)
            y += 1
    
    oct_len = len(xs)
    arr = np.empty((2, oct_len * 8), dtype = int)
    arr[0, :oct_len] = xs
    arr[1, :oct_len] = ys
    
    arr[0, oct_len:2*oct_len] = ys[::-1] #arr[1, :oct_len] # second octant
    arr[1, oct_len:2*oct_len] = xs[::-1] #arr[0, :oct_len]
    
    arr[0, 2*oct_len:4*oct_len] = np.flip(-arr[0, :2*oct_len]) # second quadrant
    arr[1, 2*oct_len:4*oct_len] = np.flip(arr[1, :2*oct_len])
    
    arr[0, 4*oct_len:8*oct_len] = np.flip(arr[0, :4*oct_len]) # second half
    arr[1, 4*oct_len:8*oct_len] = np.flip(-arr[1, :4*oct_len])
    
    arr[0] += int(offset[0])
    arr[1] += int(offset[1])
    
    return arr

def generate_thick_circle(radius = 5, thick = 2, offset = (0,0)):
    outer = generate_circle(radius = radius, offset = offset)
    for x in range(1, thick):
        append = generate_circle(radius = radius - x, offset = offset)
        outer = np.concatenate([outer, append], axis = 1, dtype = int)
    outer = np.unique(outer, axis = 1)
        
    return outer



## Array Transforms
def shift_array(arr, num, y = False, fill = 0):
    result = np.zeros(arr.shape) #np.empty_like(arr)
    
    if not y:
        if num > 0:
            result[:num, :] = fill
            result[num:, :] = arr[:-num, :]
        elif num < 0:
            result[num:, :] = fill
            result[:num, :] = arr[-num:, :]
        else:
            result[:] = arr
    
    else:
        if num > 0:
            result[:, :num] = fill
            result[:, num:] = arr[:, :-num]
        elif num < 0:
            result[:, num:] = fill
            result[:, :num] = arr[:, -num:]
        else:
            result[:] = arr
            
    return result


def normalize_angles(array):
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




## Main Loop Flow
def get_ref_angle(shift_index):
    if shift_index == (0,-1):
        return np.pi/2
    elif shift_index == (1,-1):
        return np.pi/4
    elif shift_index == (1,0):
        return 0
    elif shift_index == (1,1):
        return -np.pi/4
    elif shift_index == (0,1):
        return -np.pi/2
    elif shift_index == (-1,1):
        return -3*np.pi/4
    elif shift_index == (-1,0):
        return np.pi
    elif shift_index == (-1,-1):
        return 3*np.pi/4
    
normal_compare_angles = np.linspace((np.pi/4) + (np.pi/4 / 10), (np.pi/2) - (np.pi/4 / 10), 5)     
    
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
    

    
    
