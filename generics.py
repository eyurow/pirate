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
    
def DBZArray(n, d, handle = 0):
    if isinstance(d, np.ndarray):
        mask = d == 0
        d[mask] = 1 # allow division on zero elements
        ret = n / d
        ret[mask] = handle # set zero elements back to handle
        return ret
    elif isinstance(n, np.ndarray): # and implicitly d is int or float
        if d == 0:
            return np.full(n.shape, handle, dtype = n.dtype)
        else:
            return n / d
        
def get_margin(outer_size, inner_size):
    '''
    INPUT: outer and inner container sizes; e.g. outer is screen size of 1221, inner is WORLD-pixel size of 1200 (300*4)
    OUTPUT: excess units at start and end of outer container; e.g. 10 and 11 pixels in above example as the screen has 21 more pixels than the WORLD requires to render
    '''
    margin = outer_size - inner_size
    start = margin // 2
    end = margin - start
    return start, end

    
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
    
def compare_angles(a1, a2):
    # clockwise, a1 > a2
    if a1 < 0 and a2 > 0:
        diff = a1 - (a2 - 2*np.pi)
    else:
        diff = a1 - a2
    
    # if diff < 0:
    #     diff += 2*np.pi
    
    return diff

def normalize_angle(angle):
    # if angle > np.pi or angle <= -np.pi:
    _abs = abs(angle)
    sign = int(_abs / angle)
    revolutions = _abs//np.pi
    remaining = _abs%np.pi
    norm = (-sign * np.pi * (revolutions%2)) + sign * remaining
    return norm
    # else:
    #     return angle

def clockwise_distance(a1, a2):
    if a1 > np.pi or a1 <= -np.pi:
        a1 = normalize_angle(a1)
    if a2 > a1:
        return a1 - (a2 - np.pi*2)
    else:
        return a1 - a2


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




## Wind/Current Sim Loop Flow
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
    

    
    
