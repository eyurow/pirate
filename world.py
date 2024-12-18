from generics import DBZ, rrange, get_ref_angle, shift_array, cartesian_to_theta, theta_to_cartesian, calc_normal_carts_to_position, vector_length, generate_circle, generate_thick_circle
from indices import get_indices_within_bounds
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
                
                
class WindIndex:
    def __init__(self):
        pass


class Particles:
    def __init__(self, size, world, type = 'random'):
        if type == 'random':
            self.array = np.zeros((4,size), dtype = float)
            self.array[0] = np.random.randint(0, world.SIZE[0], size)
            self.array[1] = np.random.randint(0, world.SIZE[1], size)
        elif type == 'grid':
            # self.array = np.zeros((4,size), dtype = float)
            grid = np.mgrid[20:world.SIZE[0] - 20:15, 20:world.SIZE[1]:20]
            xs = grid[0].ravel()
            ys = grid[1].ravel()
            self.array = np.array([xs, ys, xs, ys], dtype = float)
        self.type = type
        self.world = world

    def __getitem__(self, key):
        return self.array[key]
    def __setitem__(self, key, val):
        self.array[key] = val

    def particles_in_world(self):
        return (self[0] >= 0)&(self[0] < self.world.SIZE[0])&(self[1] >= 0)&(self[1] < self.world.SIZE[1])

    def sim_particles(self):
        in_world = self.particles_in_world()
        self.recycle(in_world)

        asint = tuple(self[:2, in_world].astype(int))

        self[0, in_world] += self.world.CURRENTS[(asint[0], asint[1], 0)] / 4 # propogate particle
        self[1, in_world] += -self.world.CURRENTS[(asint[0], asint[1], 1)] / 4

    def sim_particles_accelerating(self): # not workable now, index 2 and 3 repurposed for initial position
        in_world = self.particles_in_world()
        self.recycle(in_world)

        asint = tuple(self[:2, in_world].astype(int))

        self[2, in_world] += self.world.CURRENTS[(asint[0], asint[1], 0)] # add current to particle's vector
        self[3, in_world] -= self.world.CURRENTS[(asint[0], asint[1], 1)]

        self[2, (self[0] < 0)|(self[0] >= self.world.SIZE[0])] = -self[2, (self[0] < 0)|(self[0] >= self.world.SIZE[0])] # if particle is outside world, add partial vector to push back in
        self[3, (self[1] < 0)|(self[1] >= self.world.SIZE[1])] = -self[3, (self[1] < 0)|(self[1] >= self.world.SIZE[1])]

        self[0] += self[2] # propogate particle
        self[1] += self[3]

        self[2] -= self[2] * self.world.WIND_LOSS_FACTOR**2 # energy loss
        self[3] -= self[3] * self.world.WIND_LOSS_FACTOR**2

    def recycle(self, in_world):
        # sun = self.world.SUN
        # dist = np.sqrt((self[0]-sun[0])**2 + (self[1]-sun[1])**2)
        # near_sun = dist < 15
        # cut = ~in_world|near_sun
        # self[0, cut] = np.random.randint(0, self.world.SIZE[0], cut.sum())
        # self[1, cut] = np.random.randint(0, self.world.SIZE[1], cut.sum())
        # self[2:, cut] = 0


        clumped = self.detect_clumps_tuple()
        cut = clumped[0][:clumped[0].size//2]

        if self.type == 'random':
            self[0, cut] = np.random.randint(0, self.world.SIZE[0], cut.size)
            self[1, cut] = np.random.randint(0, self.world.SIZE[1], cut.size)
            self[2:, cut] = 0
        elif self.type == 'grid':
            self[0, cut] = self[2, cut]
            self[1, cut] = self[3, cut]

    def detect_clumps_narrowdown(self, precision = 20, threshold = 15):
        # grid = np.mgrid[:self.world.SIZE[0]:20, :self.world.SIZE[1]:20]
        xs = self[0]//precision*precision
        ys = self[1]//precision*precision

        xu, xc = np.unique(xs, return_counts = True) # count of all binned x values
        maxx = np.isin(xs, xu[xc >= threshold]) # indices where x's equal max count
        maxxys = ys[maxx] # filter ys for max x
        yu, yc = np.unique(maxxys, return_counts = True) # count of filtered ys
        maxy = np.isin(ys, yu[yc >= threshold])

        return np.where(maxx & maxy)
    
    def detect_clumps_tuple(self, precision = 20, threshold = 15):
        xs = self[0]//precision*precision
        ys = self[1]//precision*precision

        # tuple arrays
        # ar = np.empty((self[0].size), dtype = object)
        ar = np.zeros((self[0].size), dtype = [('x', 'i'), ('y', 'i')])

        ar['x'] = xs
        ar['y'] = ys

        np.unique(ar, return_counts = True)
        u, c = np.unique(ar, return_counts = True)
        return np.where(np.isin(ar,u[c >= threshold]))
    

class World:
    def __init__(self, size, land_size):
        self.SIZE = size
        self.CENTER = (self.SIZE[0]/2, self.SIZE[1]/2)
        self.LAND = np.zeros((2,land_size), dtype = int) # x, y indices
        self.SEA = []
        #self.SUN_INDEX = generate_circle(round(self.SIZE[1]/2 * .7), (self.SIZE[0]/2, self.SIZE[1]/2))[:, 1:]
        
        #self.SUN = (self.SUN_INDEX[0][0],self.SUN_INDEX[1][0]) # 80,80 world
        
        self.WIND_SEEDS = []
        self.WINDS = np.zeros((self.SIZE[0], self.SIZE[1], 2))
        self.CURRENTS = np.zeros((self.SIZE[0], self.SIZE[1], 2))
        self.THETAS = np.zeros((self.SIZE[0], self.SIZE[1], 2))
        self.PROP_ARRAY = np.zeros((self.SIZE[0], self.SIZE[1], 2))
        # self.PROP_CURRENTS = np.zeros((self.SIZE[0], self.SIZE[1], 2))
        # self.THETA_MASK = np.zeros((self.SIZE[0], self.SIZE[1], 2))
        self.MGRID = np.mgrid[:self.SIZE[0], :self.SIZE[1]]
        
        self.GENERATE_PRESSURE_BANDS()
        self.SUN = (self.SOLAR_BAND[0][0],self.SOLAR_BAND[1][0])
        self.SUN_FRAMES = 20
        self.SUN_INDEX_COUNT = self.SOLAR_BAND[0].size
        self.SUN_INDEX = 0
        self.ANGULAR_VELOCITY = (np.pi * 2) / (self.SOLAR_BAND.shape[1] * self.SUN_FRAMES/2)
        self.CALC_ROTATIONAL_FORCES()
        
        self.WIND_STRESS_FACTOR = .03
        self.CURRENT_LOSS_FACTOR = .07
        self.WIND_LOSS_FACTOR = .2
        self.INNER_BOUND_THETA = np.pi/16 # angle from vector angle whicn forms bound of its impact arc
        self.CORNER_BOUND_THETA = np.pi/8 # angle from which bounds of impact to corners are calculated
        
        self.CALC_STANDARD_STRENGTH_UNIT()
        
        self.count = 1
        
    
    def CALC_STANDARD_STRENGTH_UNIT(self):
        # Current strength magnitude needed to cross 1/10th the vertical diameter with strength of 1 remaining
        self.STANDARD_CURRENT_STRENGTH_LEVEL = 1 / (1 - self.WIND_LOSS_FACTOR)**(self.SIZE[1])
        

    def CALC_ROTATIONAL_FORCES(self):
        radius_vector = np.array( [self.MGRID[0] - self.CENTER[0], self.CENTER[1] - self.MGRID[1]] ) # vector away from center
        self.CENT_FORCE = radius_vector * self.ANGULAR_VELOCITY**2
        radius = np.sqrt( radius_vector[0]**2 + radius_vector[1]**2 )
        self.CORIOLIS_PARAM = 2 * self.ANGULAR_VELOCITY * (1 - radius / radius.max())
        
    def apply_coriolis_force(self):
        self.WINDS[:,:,0] += self.WINDS[:,:,1] * self.CORIOLIS_PARAM
        self.WINDS[:,:,1] += -self.WINDS[:,:,0] * self.CORIOLIS_PARAM
        
        self.CURRENTS[:,:,0] += self.CURRENTS[:,:,1] * self.CORIOLIS_PARAM
        self.CURRENTS[:,:,1] += -self.CURRENTS[:,:,0] * self.CORIOLIS_PARAM
        
    def apply_centrifugal_force(self):
        self.WINDS[:,:,0] += self.CENT_FORCE[0]
        self.WINDS[:,:,1] += self.CENT_FORCE[1]
        
        self.CURRENTS[:,:,0] += self.CENT_FORCE[0]
        self.CURRENTS[:,:,1] += self.CENT_FORCE[1]

    def GENERATE_PRESSURE_BANDS(self):
        POLAR_BAND = generate_thick_circle(max(round(self.SIZE[1]/2 * .03), 2), 2, (self.CENTER[0], self.CENTER[1]))
        x_carts, y_carts = calc_normal_carts_to_position(POLAR_BAND, ( self.CENTER[0], self.CENTER[1] ))
        x_carts = -x_carts * 20
        y_carts = -y_carts * 20
        self.POLAR_BAND = (POLAR_BAND, np.array([x_carts, y_carts]))
        
        INNER_POLAR_BAND = generate_thick_circle(round(self.SIZE[1]/2 * .53), 2, (self.CENTER[0], self.CENTER[1]))
        x_carts, y_carts = calc_normal_carts_to_position(INNER_POLAR_BAND, ( self.CENTER[0], self.CENTER[1] ))
        x_carts = x_carts * 3
        y_carts = y_carts * 3
        self.INNER_POLAR_BAND = (INNER_POLAR_BAND, np.array([x_carts, y_carts]))
        
        INNER_EQ_BAND = generate_thick_circle(round(self.SIZE[1]/2 * .53) + 2, 2, (self.CENTER[0], self.CENTER[1]))
        x_carts, y_carts = calc_normal_carts_to_position(INNER_EQ_BAND, ( self.CENTER[0], self.CENTER[1] ))
        x_carts = -x_carts * 5
        y_carts = -y_carts * 5
        self.INNER_EQ_BAND = (INNER_EQ_BAND, np.array([x_carts, y_carts]))
        
        #OUTER_HI_PRS_BAND = generate_thick_circle(round(self.SIZE[0]/2 * .8), 2, (self.SIZE[0]/2, self.SIZE[1]/2))
    
        solar_indices = generate_circle(round(self.SIZE[1]/2 * .82), (self.CENTER[0], self.CENTER[1]))
        unique, order = np.unique(solar_indices, axis = 1, return_index = True)
        order.sort()
        self.SOLAR_BAND = solar_indices[:, order]

    def calc_solar_pressure(self):
        x_carts, y_carts = calc_normal_carts_to_position(self.MGRID, ( self.SUN[0], self.SUN[1] ))
        x_carts = x_carts / 20
        y_carts = y_carts / 20
        self.SOLAR_PRESSURE = np.array([x_carts, y_carts])
        
    def calc_solar_pressure_and_distance(self):
        x_carts, y_carts, dist = calc_normal_carts_to_position(self.MGRID, ( self.SUN[0], self.SUN[1] ), return_distance = True)
        
        x_carts = x_carts / 20
        y_carts = y_carts / 20
        self.SOLAR_PRESSURE = np.array([x_carts, y_carts])
        self.DISTANCE_FROM_SUN = dist
        
        # return dist    
    
    
    def apply_pressure_winds(self):
        for band in [self.POLAR_BAND, self.INNER_EQ_BAND, self.INNER_POLAR_BAND]:
            self.WINDS[(band[0][0], band[0][1], 0)] += band[1][0]
            self.WINDS[(band[0][0], band[0][1], 1)] += band[1][1]
            
        self.WINDS[:,:,0] += self.SOLAR_PRESSURE[0]
        self.WINDS[:,:,1] += self.SOLAR_PRESSURE[1]
        
    def move_sun(self, idx):
        self.SUN = (self.SOLAR_BAND[0, idx], self.SOLAR_BAND[1, idx])
        
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
    
    def old_prop_pressure(self):
        for band in [self.POLAR_BAND, self.INNER_EQ_BAND, self.INNER_POLAR_BAND]:
            self.CURRENTS[(band[0][0], band[0][1], 0)] += band[1][0] * self.WIND_STRESS_FACTOR
            self.CURRENTS[(band[0][0], band[0][1], 1)] += band[1][1] * self.WIND_STRESS_FACTOR
            
        self.CURRENTS[:,:,0] += self.SOLAR_PRESSURE[0] * self.WIND_STRESS_FACTOR
        self.CURRENTS[:,:,1] += self.SOLAR_PRESSURE[1] * self.WIND_STRESS_FACTOR

        
        
        
    
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

    def sim_sun(self, count):
        self.apply_coriolis_force()
        # WORLD.apply_centrifugal_force()
        
        if count % self.SUN_FRAMES == 0:
            self.SUN_INDEX += 1
            if self.SUN_INDEX == self.SUN_INDEX_COUNT:
                self.SUN_INDEX = 0
            self.move_sun(self.SUN_INDEX)
            self.calc_solar_pressure_and_distance()

    def sim_winds(self):
        # before draw
        self.apply_pressure_winds()
        
        self.set_wind_thetas()
        self.propogate_array(array = 'winds')
        self.set_winds()
        self.apply_winds_to_currents()

        self.impact_land()
        self.set_current_thetas()  
    
    def sim_currents(self):
        # after draw
        self.propogate_array(array = 'currents')
        self.set_currents()

        self.apply_energy_loss()
        
        

    


    

if __name__ == '__main__': 
    world = World((300,300), 2)
    #world.LAND[...] = [[4],[6]]
    #world.WINDS[4,7,1] = 10
    
    # if count % 50 == 0:
    #     sun_index += 1
    #     if sun_index == sun_index_count:
    #         sun_index = 0
    #     world.move_sun(sun_index)
    


