from generics import DBZ, rrange, get_ref_angle, shift_array, cartesian_to_theta, theta_to_cartesian, vector_length
import numpy as np


def generate_index(start, direction, length, width = 1):
    # TODO: force width to be added inside screen when on edge
    x_length = round(np.cos(direction) * length)
    y_length = - round(np.sin(direction) * length)
    slope = DBZ(y_length, x_length)
    
    if abs(x_length) >= abs(y_length):
        d_range = rrange(x_length)
        nd_dir = DBZ(abs(y_length), y_length, 1)
        def _nd(x):
            return round(slope * x)
    else:
        d_range = rrange(y_length)
        nd_dir = DBZ(abs(x_length), x_length, 1)
        def _nd(y):
            return round(DBZ(y, slope))
    
    x_ind = []
    y_ind = []
    for d in d_range:
        nd = _nd(d)
        if abs(x_length) >= abs(y_length):
            for w in range(width):
                x_ind.append(int( start[0] + d ))
                y_ind.append(int( start[1] + nd + (w * nd_dir) ))
        else:
            for w in range(width):
                x_ind.append(int( start[0] + nd + (w * nd_dir) ))
                y_ind.append(int( start[1] + d ))
    
    return np.array([np.array(x_ind), np.array(y_ind)], dtype = int)


class Wind:
    def __init__(self, location, strength, direction = None, xy = None, x = None, y = None): # add size and strength per size unit?
        self.location = location
        if direction:
            self.direction = direction
            self.x = np.cos(direction)
            self.y = np.sin(direction)
        elif xy or (x and y):
            if xy:
                x = xy[0]
                y = xy[1]
            length = vector_length(x, y)
            self.direction = np.arctan2(y, x)
            self.x = x / length
            self.y = y / length
        self.strength = strength
        
    def array(self):
        return np.array([self.direction[0],self.direction[1],self.strength])
    
    def world_points(self):
        # return array of points on world array where this object exists
        pass
 


            
                
def calc_bresenham_params(x, y):
    if abs(x) >= abs(y):
        return abs(x), abs(y), DBZ(abs(x), x, 0), DBZ(abs(y), y, 0), 'x' # dom size, non dom size, dom step, non-dom step, orientation
    else:
        return abs(y), abs(x), DBZ(abs(y), y, 0), DBZ(abs(x), x, 0), 'y'
           
            
class WindGroup:
    def __init__(self, start, dimensions, strength, direction = None, xy = None, x = None, y = None, duration = -1, movement = 0, decay = False):
        self.start = start # tuple e.g. 0,10
        
        if direction != None:
            self.direction = direction
            self.x = np.cos(direction) * strength
            self.y = np.sin(direction) * strength
        elif xy or (x and y):
            if xy:
                x = xy[0]
                y = xy[1]
            length = vector_length(x, y)
            self.direction = np.arctan2(y, x)
            self.x = x / length
            self.y = y / length
            
        self.length = dimensions[0]
        self.width = dimensions[1]
        self.strength = strength
        
        self.duration = duration
        self.decay = decay
        if movement > 0:
            self.d_size, self.nd_size, self.d_step, self.nd_step, self.orientation = calc_bresenham_params(self.x, self.y)
            self.error = self.d_size / 2
        self.movement = movement
        self.index = generate_index(self.start, self.direction, self.length, self.width)
        
    def __repr__(self):
        return f'Start: {self.start}, Angle: {self.direction}, Size: {self.length},{self.width}, Strength: {self.strength}'
    
    def propogate_wind(self):
        if self.duration == 0:
            # TODO - delete self?
            pass
        
        if self.decay:
            self.strength = self.strength * (1 - self.decay)
        
        if self.duration > 0:
            self.duration -= 1
            
        if self.movement > 0:
            if self.orientation == 'x':
                self.index[0] = self.index[0] + (self.d_step * self.movement)
            elif self.orientation == 'y':
                self.index[1] = self.index[1] - (self.d_step * self.movement)
                
            if self.error < 0:
                self.error += self.d_size
                if self.orientation == 'x':
                    self.index[1] = self.index[1] - self.nd_step
                elif self.orientation == 'y':
                    self.index[0] = self.index[0] + self.nd_step
            
            self.error -= self.nd_size * self.movement
                
                
            
        

        
        


    

class World:
    def __init__(self, size, land_size):
        self.SIZE = size
        self.LAND = np.zeros((2,land_size), dtype = int) # x, y indices
        self.SEA = []
        
        self.WIND_SEEDS = []
        self.WINDS = np.zeros((self.SIZE[0], self.SIZE[1], 2))
        self.CURRENTS = np.zeros((self.SIZE[0], self.SIZE[1], 2))
        self.THETAS = np.zeros((self.SIZE[0], self.SIZE[1], 2))
        self.PROP_ARRAY = np.zeros((self.SIZE[0], self.SIZE[1], 2))
        # self.PROP_CURRENTS = np.zeros((self.SIZE[0], self.SIZE[1], 2))
        # self.THETA_MASK = np.zeros((self.SIZE[0], self.SIZE[1], 2))
        
        self.WIND_STRESS_FACTOR = .03
        self.CURRENT_LOSS_FACTOR = .1
        self.WIND_LOSS_FACTOR = .1
        self.INNER_BOUND_THETA = np.pi/6 # angle from vector angle whicn forms bound of its impact arc
        self.CORNER_BOUND_THETA = np.pi/8 # angle from which bounds of impact to corners are calculated
        
        self.count = 1
        
    
    def get_ref_angle_bounds(self, ref_angle):
        if ref_angle in [np.pi/2, 0, -np.pi/2, np.pi]:
            rbound = ref_angle - (np.pi/4 - self.CORNER_BOUND_THETA)
            lbound = ref_angle + (np.pi/4 - self.CORNER_BOUND_THETA)
        else:
            rbound = ref_angle - self.CORNER_BOUND_THETA
            lbound = ref_angle + self.CORNER_BOUND_THETA
        return rbound, lbound
    
    def get_prop_index_steps(self, ref_angle):
        if ref_angle == np.pi/2:
            return (0,-1)
        elif ref_angle == np.pi/4:
            return (1,-1)
        elif ref_angle == 0:
            return (1,0)
        elif ref_angle == -np.pi/4:
            return (1,1)
        elif ref_angle == -np.pi/2:
            return (0,1)
        elif ref_angle == 5*np.pi/4:
            return (-1,1)
        elif ref_angle == np.pi:
            return (-1,0)
        elif ref_angle == 3*np.pi/4:
            return (-1,-1)
    
    def get_prop_indices(self, ref_angle, indices):
        index_steps = self.get_prop_index_steps(ref_angle)
        keep = np.where((indices[0] + index_steps[0] < self.SIZE[0])&  # indices in world bounds
                        (indices[0] + index_steps[0] >= 0)&
                        (indices[1] + index_steps[1] < self.SIZE[1])&
                        (indices[1] + index_steps[1] >= 0))
        prop_indices = (indices[0][keep] + index_steps[0], indices[1][keep] + index_steps[1]) # indices to propogate to within array
        
        return prop_indices, keep

    def calc_impact_ind_arrays(self, angles, ref_angle, lbound, rbound):
        ### ONE CALC
        impact = ( (2*self.INNER_BOUND_THETA) - 
                      np.maximum(0, rbound - (angles - self.INNER_BOUND_THETA) ) - 
                      np.maximum(0, (angles + self.INNER_BOUND_THETA) - lbound ) )  \
                    / (2*self.INNER_BOUND_THETA)
        
        return impact
    

    def old_propogate_winds(self):
        for wind in self.WIND_SEEDS:
            strength = wind.strength * self.WIND_STRESS_FACTOR # get strength of wind on sea
            x = wind.x * strength
            y = wind.y * strength
                            
            if isinstance(wind, WindGroup):
                wind.propogate_wind()

                #self.WINDS[tuple(wind.index.astype(int))] = wind.strength
                
                self.CURRENTS[:,:,0][tuple(wind.index.astype(int))] += x
                self.CURRENTS[:,:,1][tuple(wind.index.astype(int))] += y
            
            elif isinstance(wind, Wind):
                self.CURRENTS[wind.location][0] += x
                self.CURRENTS[wind.location][1] += y
        
    def apply_wind_generators(self):
        # Apply Wind Generators to WINDS
        for wind in self.WIND_SEEDS:
            self.WINDS[(wind.index[0], wind.index[1], 0)] += wind.x
            self.WINDS[(wind.index[0], wind.index[1], 1)] += wind.y

    def set_wind_thetas(self):
        self.THETAS[:,:,0] = np.arctan2(self.WINDS[:,:,1], self.WINDS[:,:,0]) # calc thetas from x, y coords
        self.THETAS[:,:,1] = np.sqrt(self.WINDS[:,:,1]**2 + self.WINDS[:,:,0]**2) # calc strength using pythag

    def set_winds(self):
        self.WINDS[...] = self.PROP_ARRAY[...]
        self.PROP_ARRAY[...] = 0
            
    
    def apply_winds_to_currents(self):
        self.CURRENTS += self.WINDS * self.WIND_STRESS_FACTOR
    
     
    def set_current_thetas(self):
        self.THETAS[:,:,0] = np.arctan2(self.CURRENTS[:,:,1], self.CURRENTS[:,:,0]) # calc thetas from x, y coords
        self.THETAS[:,:,1] = np.sqrt(self.CURRENTS[:,:,1]**2 + self.CURRENTS[:,:,0]**2) # calc strength using pythag
        
    def set_currents(self):
        self.CURRENTS[...] = self.PROP_ARRAY[...]
        self.PROP_ARRAY[...] = 0    
        
    
    def propogate_array(self, array):
        for ref_angle in [np.pi/2, np.pi/4, 0, -np.pi/4, -np.pi/2, -3*np.pi/4, np.pi, 3*np.pi/4]: # Flip positive thetas at -3*np.pi/4, Flip negative thetas at np.pi and 3*np.pi/4
            if ref_angle == -3*np.pi/4:
                self.THETAS[self.THETAS[:,:,0] < 0, 0] += 2*np.pi
                ref_angle = 5*np.pi/4
                
            rbound, lbound = self.get_ref_angle_bounds(ref_angle)

            indices = np.where((self.THETAS[:,:,0] >= rbound - self.INNER_BOUND_THETA)&
                               (self.THETAS[:,:,0] <= lbound + self.INNER_BOUND_THETA))
            prop_indices, keep = self.get_prop_indices(ref_angle, indices)
            
            impact = self.calc_impact_ind_arrays(self.THETAS[(indices[0][keep], indices[1][keep], 0)], ref_angle, lbound, rbound)
            if array == 'winds':
                self.PROP_ARRAY[(prop_indices[0],prop_indices[1],0)] += self.WINDS[(indices[0][keep],indices[1][keep],0)] * impact
                self.PROP_ARRAY[(prop_indices[0],prop_indices[1],1)] += self.WINDS[(indices[0][keep],indices[1][keep],1)] * impact
            elif array == 'currents':
                self.PROP_ARRAY[(prop_indices[0],prop_indices[1],0)] += self.CURRENTS[(indices[0][keep],indices[1][keep],0)] * impact
                self.PROP_ARRAY[(prop_indices[0],prop_indices[1],1)] += self.CURRENTS[(indices[0][keep],indices[1][keep],1)] * impact                

        
    def apply_energy_loss(self):
        # for wind in self.WIND_SEEDS:
        #     if wind.duration > 0:
        #         wind.strength = wind.strength * (1 - self.WIND_LOSS_FACTOR)
        self.CURRENTS = self.CURRENTS * (1 - self.CURRENT_LOSS_FACTOR)
        self.WINDS = self.WINDS * (1 - self.WIND_LOSS_FACTOR)
        
    def impact_land(self):
        #self.PROP_CURRENTS[self.LAND[0],self.LAND[1]] = 0 
        self.CURRENTS[self.LAND[0],self.LAND[1]] = 0     
    
    




    
    

    
if __name__ == '__main__':
    '''
    import json
    import pygame
    world = World((200,125), 2)
    
    with open('land1.json', 'r') as f:
        world.LAND = np.array(json.load(f), dtype = int)
    
    world.WIND_SEEDS.append(WindGroup((10,10), (7, 18), 50, direction = -.2, movement = 0))
    world.WIND_SEEDS.append(WindGroup((110,10), (30,4), 30, direction = -np.pi/2))
    world.WIND_SEEDS.append(WindGroup((160,30), (8,15), 50, direction = -3*np.pi/4 - .143))
    
    world.WIND_SEEDS.append(WindGroup((115,115), (10, 5), 40, direction = np.pi/2 + .156))
    world.WIND_SEEDS.append(WindGroup((175,60), (10, 10), 70, -np.pi + .198765))
    world.WIND_SEEDS.append(WindGroup((55,110), (3,50), 20, direction = np.pi/2-.24))
    world.WIND_SEEDS.append(WindGroup((20,75), (5, 20), 30, .254))
    
    world.WIND_SEEDS.append(WindGroup((75,45), (50, 30), 7, 0))
    
    
    times = {
        'Prop Winds': 0,
        'Prop Currents': 0,
        'Apply Loss': 0, #AND Land
        }
    clock = pygame.time.Clock()
    
    count = 0
    while count <= 2000:
        world.WIND_SEEDS[-1].direction += np.pi/30
        world.WIND_SEEDS[-1].x = np.cos(world.WIND_SEEDS[-1].direction)
        world.WIND_SEEDS[-1].y = np.sin(world.WIND_SEEDS[-1].direction)
        
        world.apply_wind_generators()
        world.set_wind_thetas()
        world.propogate_array(array = 'winds')
        world.set_winds()
        times['Prop Winds'] += clock.tick_busy_loop() / 1000
        
        world.apply_winds_to_currents()
        world.set_current_thetas()
        
        # Draw Here
        
        world.propogate_array(array = 'currents')
        world.set_currents()
        times['Prop Currents'] += clock.tick_busy_loop() / 1000
        world.impact_land()
        world.apply_energy_loss()
        times['Apply Loss'] += clock.tick_busy_loop() / 1000
        
        count += 1
    '''
        
    '''
        # OLD WINDS
        world.old_propogate_winds()
        times['Prop Winds'] += clock.tick_busy_loop() / 1000
        world.set_current_thetas()
        
        # Draw Here
        
        world.propogate_array(array = 'currents')
        world.set_currents()
        times['Prop Currents'] += clock.tick_busy_loop() / 1000
        world.impact_land()
        world.apply_energy_loss()
        times['Apply Loss'] += clock.tick_busy_loop() / 1000
        
        count += 1
    '''
        
    
    
    
    
    world = World((8,8), 2)
    world.LAND[...] = [[4],[6]]
    world.WINDS[4,7,1] = 10
    
    world.set_wind_thetas()
    print(world.THETAS[:,:,1].T)
    world.propogate_array(array = 'winds')
    world.set_winds()
    print(world.WINDS[:,:,1].T)
    
    
            
    world.apply_winds_to_currents()
    world.impact_land()
    print(world.CURRENTS[:,:,1].T)
    world.set_current_thetas()
    print(world.THETAS[:,:,1].T)
    
    
    world.propogate_array(array = 'currents')
    world.set_currents()

    print(world.CURRENTS[:,:,1].T)
    world.apply_energy_loss()
    


