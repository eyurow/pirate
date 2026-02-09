import numpy as np

from basics.indices import *
# from basics.TextureArray import TextureArray

class TextureArray:
    def __init__(self, size = 0):
        self.array = np.zeros(shape = size, dtype = bool)

    @classmethod    
    def from_texture(cls, texture):
        tmp = super().__new__(cls)
        tmp.array = np.zeros(shape = texture.shape, dtype = bool)
        tmp.array[texture == 0] = 1
        return tmp
    @classmethod    
    def from_index_array(cls, array):
        tmp = super().__new__(cls)
        tmp.array = np.zeros(shape = (array[0].max() - array[0].min(), 
                                       array[1].max() - array[1].min()), 
                                       dtype = bool)
        tmp.array[array[0] - array[0].min(), array[1] - array[1].min()] = 1
        return tmp

    def to_index_tuple(self):
        return np.where(self)

    def __getitem__(self, index):
        return self.array[index]
    def __setitem__(self, index, value):
        self.array[index] = value
    def __getattr__(self, property):
        return self.array.__getattribute__(property)
    def __repr__(self):
        return self.array.__repr__()
    def __str__(self):
        return self.array.__str__()


class IndexArray:
    def __init__(self, array):
        self.array = array
        self.color = np.ones((4, array.shape[1]), dtype = int)
        self.get_stats()

    @classmethod    
    def from_array(cls, array):
        tmp = cls(array.shape[1])
        tmp.array[...] = array[...]
        tmp.color = np.ones((4, array.shape[1]), dtype = int)
        tmp.get_stats()
        return tmp
    @classmethod
    def from_tuple(cls, tuple):
        tmp = super().__new__(cls)
        tmp.array = np.array([tuple[0], tuple[1]], dtype = int)
        tmp.color = np.ones((4, array.shape[1]), dtype = int)
        tmp.get_stats()
        return tmp
    @classmethod
    def from_texture_array(cls, texture_array):
        tmp = super().__new__(cls)
        tmp.from_tuple(np.where(texture_array))
        tmp.color = np.ones((4, tmp.shape[1]), dtype = int)
        return tmp
    @classmethod
    def from_texture(cls, texture):
        tmp = super().__new__(cls)
        tmp.from_tuple(np.where(texture == 0))
        tmp.color = np.ones((4, tmp.shape[1]), dtype = int)
        return tmp
    
    def to_texture_array(self):
        tmp = TextureArray(size = (self.xrng, self.yrng))
        tmp.array[self[0] - self.xmin, self[1] - self.ymin] = 1
        return tmp
    def to_tuple(self):
        return (self[0], self[1])#, self.color

    def __getitem__(self, index):
        return self.array[index]
    def __setitem__(self, index, value):
        self.array[index] = value
    def __getattr__(self, property):
        return self.array.__getattribute__(property)
    def __repr__(self):
        return self.array.__repr__()
    def __str__(self):
        return self.array.__str__()
    
    def get_stats(self, force_int = True):
        x_min = self[0].min()
        x_max = self[0].max()
        y_min = self[1].min()
        y_max = self[1].max()

        x_rng = x_max - x_min
        y_rng = y_max - y_min

        mid_x = x_min + (x_rng / 2)
        mid_y = y_min + (y_rng / 2)

        if force_int:
            mid_x = round(mid_x)
            mid_y = round(mid_y)
        
        self.xmin = x_min;self.xmax = x_max;self.ymin = y_min;self.ymax = y_max
        self.midx = mid_x;self.midy = mid_y;self.xrng = x_rng;self.y_rng = y_rng
        # return (x_min, x_max, y_min, y_max, mid_x, mid_y, x_rng,)
    
    def center(self, on = (0,0)):
        self[0] -= on[0]
        self[1] -= on[1]

    def true_center(self):
        self[0] -= self.midx
        self[1] -= self.midy

    def rotate(self, rotation):
        # For pre-centered index arrays
        thetas = np.arctan2(self[1], self[0]) # Note: this means that 'up' on the texture array is 0rads in world/pixel array, e.g. 'right'
        str = np.sqrt(self[0] ** 2 + self[1] ** 2)

        new_thetas = thetas + rotation
        new_x = np.cos(new_thetas) * str
        new_y = np.sin(new_thetas) * str

        self[...] = (new_x, new_y)

        # new_indices = np.array((new_x.round(), new_y.round()), dtype = int)
        # return new_indices
    
    def offset(self, by = (0,0)):
        self[0] += by[0]
        self[1] += by[1]

    def rotate_around(self, rotation = 0, around = (0,0)):
        thetas = np.arctan2(self[1] - around[1], self[0] - around[0]) # Note: this means that 'up' on the texture array is 0rads in world/pixel array, e.g. 'right'
        str = np.sqrt((self[0] - around[0]) ** 2 + (self[1] - around[1]) ** 2)

        new_thetas = thetas + rotation
        new_x = (np.cos(new_thetas) * str) + around[0]
        new_y = (np.sin(new_thetas) * str) + around[1]

        self[...] = (new_x.round(), new_y.round())


