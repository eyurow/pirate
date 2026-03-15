import numpy as np

from parameters import DEFAULT_ARRAY_ROUNDING, DEFAULT_SINGLE_ROUNDING
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
    def __init__(self, array, dtype = int, rounding = DEFAULT_ARRAY_ROUNDING): # rounding: can be ufunc or array method
        self.array = array.astype(dtype)
        self.rounding = rounding
        # self.get_stats()

    @classmethod
    def empty(cls):
        tmp = super().__new__(cls)
        tmp.array = np.zeros((2,0), dtype = int)
        tmp.rounding = DEFAULT_ARRAY_ROUNDING

    @classmethod
    def from_tuple(cls, tuple, dtype = int, rounding = DEFAULT_ARRAY_ROUNDING):
        tmp = super().__new__(cls)
        tmp.array = np.array([tuple[0], tuple[1]], dtype = dtype)
        tmp.rounding = rounding
        tmp.get_stats()
        return tmp
    @classmethod
    def from_texture_array(cls, texture_array, dtype = int, rounding = DEFAULT_ARRAY_ROUNDING):
        tmp = super().__new__(cls)
        tmp.from_tuple(np.where(texture_array), dtype)
        tmp.rounding = rounding
        return tmp
    @classmethod
    def from_texture(cls, texture, dtype = int, rounding = DEFAULT_ARRAY_ROUNDING):
        tmp = super().__new__(cls)
        tmp.from_tuple(np.where(texture == 0), dtype)
        tmp.rounding = rounding
        return tmp
    
    def to_texture_array(self):
        tmp = TextureArray(size = (self.xrng, self.yrng))
        tmp.array[self[0] - self.xmin, self[1] - self.ymin] = 1
        return tmp
    def to_tuple(self):
        return (self[0], self[1])#, self.color
    
    def to_start_pixels(self, cell_size):
        # Convert world indices to PixelArray top-left corner indixes
        self[0] *= cell_size; self[1] *= cell_size

    def to_index_block(self, cell_size):
        # Get full cell_size X xell_size pixels index for each start index
        return IndexArray.from_tuple(get_start_pixels(self, cell_size))


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
        x_min = self[0].min(); x_max = self[0].max(); y_min = self[1].min(); y_max = self[1].max()
        x_rng = x_max - x_min; y_rng = y_max - y_min
        mid_x = x_min + (x_rng / 2); mid_y = y_min + (y_rng / 2)

        if force_int:   mid_x = DEFAULT_SINGLE_ROUNDING(mid_x); mid_y = DEFAULT_SINGLE_ROUNDING(mid_y)
        
        # self.xmin = x_min; self.xmax = x_max; self.ymin = y_min; self.ymax = y_max
        # self.midx = mid_x; self.midy = mid_y; self.xrng = x_rng; self.yrng = y_rng
        return x_min, x_max, y_min, y_max, mid_x, mid_y, x_rng, y_rng
    
    def center(self, on = (0,0)):
        self[0] -= on[0]; self[1] -= on[1]

    def true_center(self):
        self[0] -= self.midx; self[1] -= self.midy

    def offset(self, by = (0,0)):
        self[0] += by[0]; self[1] += by[1]

    def rotate(self, rotation):
        # For pre-centered index arrays
        thetas = np.arctan2(self[1], self[0]) # Note: this means that 'up' on the texture array is 0rads in world/pixel array, e.g. 'right'
        str = np.sqrt(self[0] ** 2 + self[1] ** 2)

        new_thetas = thetas + rotation
        new_x = np.cos(new_thetas) * str
        new_y = np.sin(new_thetas) * str

        self[...] = (self.rounding(new_x), self.rounding(new_y)) #TODO: compare doing self.rounding(new_x, out = self[0]); self.rounding(new_y, out = self[1])

    def rotate_around(self, rotation = 0, around = (0,0)):
        thetas = np.arctan2(self[1] - around[1], self[0] - around[0]) # Note: this means that 'up' on the texture array is 0rads in world/pixel array, e.g. 'right'
        str = np.sqrt((self[0] - around[0]) ** 2 + (self[1] - around[1]) ** 2)

        new_thetas = thetas + rotation
        new_x = (np.cos(new_thetas) * str) #+ around[0]
        new_y = (np.sin(new_thetas) * str) #+ around[1]

        self[...] = (self.rounding(new_x), self.rounding(new_y)) #TODO: compare doing self.rounding(new_x, out = self[0]); self.rounding(new_y, out = self[1])

    def trim(self, xmin = 0, xmax = 0, ymin = 0, ymax = 0):
        self.array = self.array[:, (self.array[0] >= xmin) &
                                    (self.array[0] <= xmax) &
                                    (self.array[1] >= ymin) &
                                    (self.array[1] <= ymax)]

    def null_round(self, array):
        return array



class FloatIndArray(IndexArray):
    def __init__(self, array):
        super().__init__(array, dtype = float, rounding = DEFAULT_ARRAY_ROUNDING)

    @classmethod
    def from_tuple(cls, tuple, dtype = float, rounding = DEFAULT_ARRAY_ROUNDING):
        tmp = super().__new__(cls)
        tmp.array = np.array([tuple[0], tuple[1]], dtype = dtype)
        tmp.color = np.ones((4, tmp.array.shape[1]), dtype = int)
        tmp.rounding = rounding
        tmp.get_stats()
        return tmp
    
    def to_int(self):
        return IndexArray(self.rounding(self).astype(int))
    
    def get_stats(self):
        x_min = self[0].min(); x_max = self[0].max(); y_min = self[1].min(); y_max = self[1].max()
        x_rng = x_max - x_min; y_rng = y_max - y_min
        mid_x = x_min + (x_rng / 2); mid_y = y_min + (y_rng / 2)

        # self.xmin = x_min; self.xmax = x_max; self.ymin = y_min; self.ymax = y_max
        # self.midx = mid_x; self.midy = mid_y; self.xrng = x_rng; self.yrng = y_rng
        return x_min, x_max, y_min, y_max, mid_x, mid_y, x_rng, y_rng

    def rotate(self, rotation):
        # For pre-centered index arrays
        thetas = np.arctan2(self[1], self[0]) # Note: this means that 'up' on the texture array is 0rads in world/pixel array, e.g. 'right'
        str = np.sqrt(self[0] ** 2 + self[1] ** 2)

        new_thetas = thetas + rotation
        self[0] = np.cos(new_thetas) * str
        self[1] = np.sin(new_thetas) * str

    def rotate_around(self, rotation = 0, around = (0,0)):
        # inherently zeros array to 'around' point
        thetas = np.arctan2(self[1] - around[1], self[0] - around[0]) # Note: this means that 'up' on the texture array is 0rads in world/pixel array, e.g. 'right'
        str = np.sqrt((self[0] - around[0]) ** 2 + (self[1] - around[1]) ** 2)

        new_thetas = thetas + rotation
        self[0] = (np.cos(new_thetas) * str) #+ around[0]
        self[1] = (np.sin(new_thetas) * str) #+ around[1]



class PixelIndex(IndexArray):
    def __init__(self, array, color = (0,0,0), opacity = 1):
        super().__init__(array)
        self.color = color
        self.opacity = opacity # between 0-1
        # TODO: remove color from basic IndexArray, move all to here
        # TODO: allow color/opacity to be tuple/float or array

    def to_index_block(self, cell_size):
        # Get full cell_size X xell_size pixels index for each start index
        # TODO: include repeated color/opacity arrays
        return PixelIndex.from_tuple(get_start_pixels(self, cell_size))


class ColorArray:
    def __init__(self, color = (0,0,0)):
        self.color_array = np.zeros()
