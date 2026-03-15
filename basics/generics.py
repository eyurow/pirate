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

def vector_length(x, y):
    if isinstance(x, tuple):
        return np.sqrt(x[0]**2 + x[1]**2)
    else:
        return np.sqrt(x**2 + y**2)

