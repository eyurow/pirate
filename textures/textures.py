# import sys
# sys.path.append("..")
# print('path: ', sys.path)

import numpy as np


particle = np.array( [[130,  0,130],
                      [  0,  0,  0],
                      [130,  0,130]])
def particle(): # 6/6
    one = np.array([np.array([1]), np.array([2])])
    two = np.array([np.array([0,1,2]), np.array([1,1,1])])
    three = np.array([np.array([1]), np.array([0])])
    return np.concatenate([one,two,three], axis = 1)


smallship = np.flip( np.array( [ [130,130,  0,130,130],
                                 [130,130,  0,130,130],
                                 [130,  0,  0,  0,130],
                                 [130,  0,  0,  0,130],
                                 [  0,  0,  0,  0,  0],
                                 [130,  0,  0,  0,130],
                                 [130,  0,  0,  0,130],
                                 [130,130,  0,130,130]]), 0)

ship = np.flip( np.array( [[130,130,  0,130,130],
                           [130,130,  0,130,130],
                           [130,130,  0,130,130],
                           [130,  0,  0,  0,130],
                           [130,  0,  0,  0,130],
                           [130,  0,  0,  0,130],
                           [  0,  0,  0,  0,  0],
                           [130,  0,  0,  0,130],
                           [130,  0,  0,  0,130],
                           [130,  0,  0,  0,130],
                           [130,130,  0,130,130],
                           [130,130,  0,130,130]]), 0)
# def ship():
#     outline = np.array( [[130,130,  0,130,130],
#                         [130,130,  0,130,130],
#                         [130,130,  0,130,130],
#                         [130,  0,  0,  0,130],
#                         [130,  0,  0,  0,130],
#                         [130,  0,  0,  0,130],
#                         [  0,  0,  0,  0,  0],
#                         [130,  0,  0,  0,130],
#                         [130,  0,  0,  0,130],
#                         [130,  0,  0,  0,130],
#                         [130,130,  0,130,130],
#                         [130,130,  0,130,130]])
#     return np.nonzero(outline == 0)#.nonzero()#np.where(outline == 0)


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
