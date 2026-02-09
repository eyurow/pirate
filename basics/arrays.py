import numpy as np


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
    # y-axis flipped
    distance = np.sqrt((position[0] - index[0])**2 + (index[1] - position[1])**2)
    distance[distance == 0] = handle
    x = (position[0] - index[0]) / distance
    y = (index[1] - position[1]) / distance
    if return_distance:
        return x, y, distance
    else:
        return x, y