import numpy as np



class TextureArray:
    def __init__(self, size = (0,0)):
        self.array = np.zeros(shape = size, dtype = bool)
        self.color = np.zeros(shape = (size[0], size[1], 4), dtype  = int)
        #TODO: color array

    @classmethod    
    def from_texture(cls, texture):
        tmp = super().__new__(cls)
        shape = texture.shape
        tmp.array = np.zeros(shape = shape, dtype = bool)
        tmp.array[texture == 0] = 1
        tmp.color = np.zeros(shape = (shape[0], shape[1], 4), dtype  = int)
        tmp.color[tmp.array, 3] = 1
        #TODO: add custom colors
        return tmp
    @classmethod    
    def from_index_array(cls, array):
        tmp = super().__new__(cls)
        shape = (array[0].max() - array[0].min(), 
                 array[1].max() - array[1].min())
        tmp.array = np.zeros(shape = shape, dtype = bool)
        tmp.array[shape[0], shape[1]] = 1

        tmp.color = np.zeros(shape = (shape[0], shape[1], 4), dtype  = int)
        tmp.color[tmp.array, 3] = 1
        #TODO: add custom colors
        return tmp

    def to_index_tuple(self):
        return np.where(self)#, self.color[self])

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