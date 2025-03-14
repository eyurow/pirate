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



