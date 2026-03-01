# ship types - https://museum.wa.gov.au/maritime-archaeology-db/early-sailing-ships
#              https://www.realmofhistory.com/2023/08/11/historical-warships/#:~:text=These%20incredible%20warships%20ranged%20from,both%20solid%2Dshot%20and%20grapeshot.
# force calc - https://www.nautilusint.org/en/news-insight/telegraph/never-again-how-a-better-understanding-of-aerodynamics-and-hydrodynamics-could-help-prevent-another-ever-given-incident/
# sail/keel forces - https://www.phys.unsw.edu.au/~jw/sailing.html
# wind/wave forces - https://data.coaps.fsu.edu/eric_pub/RSMAS/GODAE_School/GODAE_Book/Chap23-Hackett.pdf
# weight/displacement - https://www.lifeofsailing.com/blogs/articles/how-much-does-a-sailboat-weigh
# righting/balance - https://www.quora.com/Is-it-true-that-ships-dont-roll-over-because-it-have-the-center-of-gravity-lower-than-center-of-buoyancy-and-ships-will-always-roll-over-if-the-center-of-gravity-higher-than-center-of-buoyancy
# inertia - https://phys.libretexts.org/Bookshelves/University_Physics/University_Physics_(OpenStax)/Book%3A_University_Physics_I_-_Mechanics_Sound_Oscillations_and_Waves_(OpenStax)/10%3A_Fixed-Axis_Rotation__Introduction/10.06%3A_Calculating_Moments_of_Inertia
# official force calculator - https://orc.org/organization/velocity-prediction-program-vpp
# CLR/CE estimation - https://usvmyg.org/articles/sailing/helm-balance-with-simple-calculations-of-center-of-effort-and-center-of-lateral-resistance/
# Aviation Formular; lots of math - https://edwilliams.org/avform147.htm#Clairaut

# 2240 lbs per ton
# 1016 kgs per ton


import numpy as np

from parameters import AIR_DENSITY, WATER_DENSITY, SAIL_INEFFICIENCY, KEEL_INEFFICIENCY
from basics.angles import clockwise_distance, clockwise_distance_prenorm_a2, normalize_angle




def decompose_force(force_x, force_y, comparison_theta): # force_x/y are force on ship, not accel or force on water/air
    '''
    comparison_theta: set to ship heading for driving/lateral decomposition or current/wave theta for lift/drag

    returns:
        ( driving, lateral ) or ( drag, lift )
    '''
    force_theta = np.arctan2(force_y, force_x)
    force_mag = np.sqrt(force_x**2 + force_y**2)
    theta = force_theta - comparison_theta
    x = np.cos(theta) * force_mag
    y = np.sin(theta) * force_mag
    return x, y

def calc_drag_coefficient(drag_force, area, fluid_density, flow_speed):
    return ( 2 * drag_force ) / ( fluid_density * flow_speed**2 * area )

def approximate_drag_force(density, area, velocity):
    return (1/2) * density * area * velocity**2 #newtons

def calc_sail_depth(point1, point2, width):
    chord_midpoint = (point2[0] - point1[0], point2[1] - point1[1])
    #TODO


class Mount:
    def __init__(self, owner, x = 0, y = 0, z = 0):
        self.owner = owner
        self.x = x # bow/stern
        self.y = y # port/starboard
        self.z = z # up/down

    @property
    def ship(self):
        return self.owner.ship

    def calc_heeling_arm(self):
        np.sqrt( (self.z - self.ship.cog[2])**2 + (self.y - self.cog[1]**2) )
    def calc_yawing_arm(self):
        np.sqrt( (self.y - self.ship.cog[1])**2 + (self.x - self.cog[0]**2) )
class Spar(Mount):
    def __init__(self, mount, length = 2, set = np.pi/2):
        super().__init__(mount.ship, mount.x, mount.y, mount.z)
        self.length = length
        self.set = set
        self.m1 = Mount(self, )
class Mast(Mount):
    def __init__(self, ship, x = 0, y = 0, height = 8):
        super().__init__(ship, x, y, 0)
        self.x = x
        self.y = y
        self.height = height
        self.top_mount = Mount(self, self.x, self.y, self.height) # top mount


class Sail:
    def __init__(self, ship = None, shape = 'square', height = 8, length = 8, _density = AIR_DENSITY, inefficiency_param = SAIL_INEFFICIENCY, mounting = (0,0,0), pivot = 0, give = np.pi/6, furling = 1):

        self.ship = ship

        self._density = _density
        self.INEFFICIENCY_PARAM = inefficiency_param

        self.x = 0 # x-wise acceleration on sail (relative to world directions)
        self.y = 0
        self.lat = 0
        self.driv = 0
        self.lift = 0
        self.drag = 0
        self.torque = 0

        self.mounting = mounting
        self.shape = shape
        self.height = height
        self.length = length

        # self.furling = furling
        # self.pivot = set
        # self.give = give

        self.calc_initial_properties(pivot, give, furling)

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f'''
        PivotSet: {self.pivot:.02f}; Give: {self.give:.02f}; EffSet: {self.set:.02f}; COE: {self.coe};
        Accel: {self.x:.03f}, {self.y:.03f}; LiftDrag = {self.lift:.02f}, {self.drag:.02f}; LatDriv = {self.lat:.02f}, {self.driv:.02f}; Torque: {self.torque:.03f}; 
        '''

        
    def calc_initial_properties(self, pivot, give, furling):
        self.pivot = pivot # skip for keel
        self.give = give # skip for rudder
        self.calc_area()
        self.calc_center_of_effort()
        self.calc_effective_set() # skip for keel/rudder
        self.calc_heeling_arm()
        self.calc_yawing_arm()


    def calc_area(self): # Standard definition for actual sail; redefined for Keel
        if self.shape == 'square':
            self.area = abs(self.height * self.length)
        elif self.shape == 'triangle':
            self.area = abs(.5 * self.height * self.length)

    def calc_center_of_effort(self):
        self.coe = [self.mounting[0] + self.length/2, 0, self.mounting[2] + self.height/2]
        # if self.shape == 'square': #mounting would be top left and top right on a spar, plus pivot point (could be same as m1 or m2 - three tuples - first tuple is mount point nearest to ship 0point or negative if equal distance
        #     self.m1_pivot_length = np.sqrt( (self.mounting[0][0] - self.mounting[2][0])**2 + (self.mounting[0][1] - self.mounting[2][1])**2 )
        #     self.m2_pivot_length = np.sqrt( (self.mounting[1][0] - self.mounting[2][0])**2 + (self.mounting[1][1] - self.mounting[2][1])**2 )
        #     port_mount = (np.cos(self.set + self.give / 4) * self.m1_pivot_length, np.sin(self.set + self.give / 4) * self.m2_pivot_length)
            
        #     x = mounting[0][0] + np.cos(self.set + self.give / 4) * (mounting[1][0] - mounting[0][0]) / 2 
        #     y = mounting[0][0] + np.sin(self.set + self.give / 4) * (mounting[1][1] - mounting[0][1]) / 2 
        #     z = (mounting[0][2] - self.height) / 2 
        # elif self.shape == 'triangle': # mounting is near mount where heel of sail is mounted, top mount along pivot arm, and far mount where setting arm - three tuple
        #     x = mounting[0][0] + np.cos(self.set + self.give / 4) * (mounting[0][0] - mounting[2][0]) / 3
        #     y = mounting[0][1] + np.sin(self.set + self.give / 4) * (mounting[0][1] - mounting[2][1]) / 3
        #     z = mounting[0][2] + (mounting[1][2] - mounting[0][2]) / 3

        # return x, y, z

    def calc_effective_set(self):
        self.set = self.pivot - (self.give / 2)
    def calc_heeling_arm(self):
        self.heel_arm_length = np.sqrt( (self.coe[1] - self.ship.cog[1])**2 + (self.coe[2] - self.ship.cog[2])**2 )
        self.heel_arm_theta = np.arctan2( (self.coe[1] - self.ship.cog[1]), (self.coe[2] - self.ship.cog[2]) ) # zerod on "up" or positive z-axis; additive with ship heel angle 
    def calc_yawing_arm(self): #mounting x and y
        self.yaw_arm_length = np.sqrt( (self.coe[0] - self.ship.cog[0])**2 + (self.coe[1] - self.ship.cog[1])**2 )
        self.yaw_arm_theta = np.arctan2( (self.coe[0] - self.ship.cog[0]) , (self.coe[1] - self.ship.cog[1]))



    ## Sim Funcs
    def compare_impact_force(self, wind): # Standard definition for actual sail; redefined for Keel
        zone = self.give - np.pi # sail give shouldn't eer be greater than pi so this is pre-normalized
        wind_diff = clockwise_distance_prenorm_a2(self.ship.heading + self.set, wind) #clockwise_distance(sail.ship.heading - sail.set, wind)

        if self.give >= 0: # zone is negative
            if wind_diff > -zone and wind_diff != 0: # 
                print('Wind is not Catching')
                # return None
                return wind, wind + np.pi
            else:
                half = -zone / 2
                if wind_diff < half:
                    print('Wind is closer to Set')
                    return wind, self.ship.heading + self.set + self.give
                else:
                    print('Wind is closer to Tip')
                    return wind, self.ship.heading + self.set + np.pi
    
        elif self.give < 0: # zone is supernegative (< -pi)
            _zone = np.pi*2 + zone # counterclockwise distance to zone
            if wind_diff < -zone and wind_diff != 0:
                print('Wind is not Catching')
                return wind, wind + np.pi
            else:
                half = -zone + ( _zone / 2 ) 
                if wind_diff >= half or wind_diff == 0:
                    print('Wind is closer to Set')
                    return wind, self.ship.heading + self.set + self.give
                else:
                    print('Wind is closer to Tip')
                    return wind, self.ship.heading + self.set + np.pi
    
    @staticmethod
    def calc_acceleration(initial_cart, final_theta):
        # initial force in cartesian and final in theta+mag
        final_wind_x = np.cos(final_theta[0]) * final_theta[1]
        final_wind_y = np.sin(final_theta[0]) * final_theta[1]

        return final_wind_x - initial_cart[0], final_wind_y - initial_cart[1]
    
    def calc_effective_area(self, force_theta):
        return self.area * max(np.sin(force_theta - (self.ship.heading + self.pivot)), .02)

    def calc_delta_force(self, velocity, theta, accel_x, accel_y, dt = 1):
        effective_area = self.calc_effective_area(theta) # m2
        mass = effective_area * velocity * self._density * dt # m2 * m/s * kg/m3 * s = kg
        # acceleration = np.sqrt(accel_x**2 + accel_y**2) * dt**2 # m/s2
        # force_on_sail = mass * acceleration # kg * m/s2
        force_sail_x = -accel_x * mass # per second
        force_sail_y = -accel_y * mass
        return force_sail_x, force_sail_y
    
    def calc_heeling_action(self, dt = 1):
        torque = self.lat * self.heel_arm_length * np.sin(np.pi/2 - (self.heel_arm_theta + self.ship.heeling_angle) ) / self.ship.heeling_inertia * dt #TODO: use fLat to get heeling force (youtube video on torque angles)
        # Newtons
        return torque
    
    def calc_yawing_action(self, dt = 1):
        force_theta = np.arctan2(self.y, self.x)
        force = np.sqrt(self.x**2 + self.y**2)
        torque = force * self.yaw_arm_length * np.sin(force_theta - (self.yaw_arm_theta + self.ship.heading) ) / self.ship.yawing_inertia * dt
        return torque

    def sim(self, wind, dt = 1):
        wind_theta = np.arctan2(wind[1], wind[0])
        wind_strength = np.sqrt(wind[0]**2 + wind[1]**2) #/ m/s
        wind_theta, final_wind = self.compare_impact_force(wind_theta)

        accel = self.calc_acceleration(wind, (final_wind, wind_strength * self.INEFFICIENCY_PARAM)) # x, y tuple; acceleration of wind/current hitting sail
        sail_force_x, sail_force_y = self.calc_delta_force(wind_strength, wind_theta, accel[0], accel[1], dt) # force on sail (opposite of force on wind/current)

        self.x = sail_force_x / self.ship.weight
        self.y = sail_force_y / self.ship.weight

        self.driv, self.lat = decompose_force(self.x, self.y, self.ship.heading)
        self.drag, self.lift = decompose_force(self.x, self.y, wind_theta)
        self.torque = self.calc_heeling_action()

        drag_coeff = calc_drag_coefficient(self.drag * self.ship.weight, self.area, self._density, wind_strength)
        lift_coeff = calc_drag_coefficient(self.lift * self.ship.weight, self.area, self._density, wind_strength)
        # print(f'{self.__class__} Drag Coeff.: {drag_coeff}')
        # print(f'{self.__class__} Lift Coeff.: {lift_coeff}')
        

class SquareRig(Sail):
    def __init__(self, ship = None, shape = 'square', height = 8, length = 8, _density = AIR_DENSITY, inefficiency_param = SAIL_INEFFICIENCY, mounting = (0,0,12), pivot = np.pi/2, give = np.pi/4, furling = 1):
        super().__init__(ship, shape, height, length, _density, inefficiency_param, mounting, pivot, give, furling)
        # Mounting is a single point on a mast; default pivot set is pi/2 or crosswise to ship

    def calc_initial_properties(self, pivot, give, furling):
        self.pivot = pivot # skip for keel
        self.give = give # skip for rudder
        self.furling = furling
        self.calc_area()
        self.calc_center_of_effort()
        self.calc_effective_set()
        self.calc_heeling_arm()
        self.calc_yawing_arm()

    def calc_area(self): # Standard definition for actual sail; redefined for Keel
        self.area = (self.height * self.furling) * self.length

    def calc_center_of_effort(self):
        x = self.mounting[0]
        y = self.mounting[1]
        z = self.mounting[2] - (self.height * self.furling)/2
        # TODO: x and y should be perpindicular to pivot set and slightly outwards depending on give; would then be included in pivot and trim methods
        self.coe = [x, y, z]
    
    def reset_coe_height(self):
        self.coe[2] = self.mounting[2] - (self.height * self.furling)
    
    def calc_effective_set(self):
        self.set = self.pivot - (self.give / 2)
    
    def tack(self, pivot):
        self.pivot = pivot
        self.calc_effective_set()
    def trim(self, give):
        self.give = give
        self.calc_effective_set()
    def furl(self, furling):
        self.furling = furling
        self.calc_area()
        self.reset_coe_height()
        self.calc_heeling_arm()


class Keel(Sail):
    def __init__(self, ship = None, shape = 'square', height = -1, length = 18, _density = WATER_DENSITY, inefficiency_param = KEEL_INEFFICIENCY, mounting = (-9, 0, -6)):
        super().__init__(ship, shape, height, length, _density, inefficiency_param, mounting)

    def __repr__(self):
        return f'''
        COE: {self.coe}; 
        Accel: {self.x:.03f}, {self.y:.03f}; LiftDrag = {self.lift:.02f}, {self.drag:.02f}; LatDriv = {self.lat:.02f}, {self.driv:.02f}; Torque: {self.torque:.03f}; 
        '''
    
    @property
    def pivot(self):
        return self.ship.heading
    @property
    def set(self):
        return self.ship.heading

    def calc_initial_properties(self, pivot, give, furling):
        self.calc_area()
        self.calc_center_of_effort()
        self.calc_heeling_arm()
        self.calc_yawing_arm()


    def compare_impact_force(self, current_theta):
        distance = clockwise_distance(self.ship.heading, current_theta)
        if distance >= np.pi/2 and distance < 3*np.pi/2:
            final_current = self.ship.heading + np.pi
        else:
            final_current = self.ship.heading
        return current_theta, final_current

    
class Rudder(Sail):
    def __init__(self, ship = None, shape = 'square', height = -4, length = -1, _density = WATER_DENSITY, inefficiency_param = KEEL_INEFFICIENCY, mounting = (-9, 0, -3), pivot = np.pi):
        super().__init__(ship, shape, height, length, _density, inefficiency_param, mounting, pivot)

    def __repr__(self):
        return f'''
        PivotSet: {self.pivot:.02f}; COE: {self.coe};
        Accel: {self.x:.03f}, {self.y:.03f}; LiftDrag = {self.lift:.02f}, {self.drag:.02f}; LatDriv = {self.lat:.02f}, {self.driv:.02f}; Torque: {self.torque:.03f}; 
        '''

    def calc_initial_properties(self, pivot, give, furling):
        self.pivot = pivot
        self.calc_area()
        self.calc_center_of_effort()
        self.calc_heeling_arm()
        self.calc_yawing_arm()
    
    # TODO: recalc COE, yawing arm - should always be small in scale

    def compare_impact_force(self, current_theta):
        distance = clockwise_distance(self.ship.heading, current_theta)
        if distance >= np.pi/2 and distance < np.pi:
            if self.pivot >= 0:
                initial_current = self.ship.heading + np.pi
                final_current = self.ship.heading + self.pivot
                print('Keel is catching Rudder')
            else:
                initial_current = self.ship.heading + np.pi
                final_current = self.ship.heading + np.pi
                print('Rudder not Catching')

        elif distance >= np.pi and distance < 3*np.pi/2:
            if self.pivot < 0:
                initial_current = self.ship.heading + np.pi
                final_current = self.ship.heading + self.pivot
                print('Keel is catching Rudder')
            else:
                initial_current = self.ship.heading + np.pi
                final_current = self.ship.heading + np.pi
                print('Rudder not Catching')

        else:
            initial_current = current_theta
            distance = clockwise_distance(self.ship.heading + self.pivot, current_theta)
            if distance >= np.pi/2 and distance < 3*np.pi/2:
                final_current = self.ship.heading + self.pivot + np.pi
            else:
                final_current = self.ship.heading + self.pivot
            
        return initial_current, final_current

    def tack(self, pivot):
        self.pivot = pivot


class Ship:
    '''
    coordinate system:
    a. default has point (0,0) in x/y center point
        a1. point (length/2,0) is therefore bow
    b. 
    '''

    def __init__(self, world = None, position = (0,0), heading = np.pi/4):
        self.world = world
        self.position = [position[0], position[1]]
        self.hull_length = 18 # meters
        self.hull_width = 4 # meters
        self.hull_height = 6 # meters
        self.hull_waterline = 3.5 # meters
        self.keel_height = 1 # meters
        self.block_coefficient = .4
        self.volume = self.hull_length * self.hull_width * self.hull_height * self.block_coefficient
        self.weight = 15*1016 # tons -> kgs 

        self.heading = heading
        self.x_accel = 0
        self.y_accel = 0
        self.x = 0 # velocity-x
        self.y = 0 # velocity-y
        self.driv = 0 # forward (driving) acceleration in reference to heading
        self.lat = 0 # lateral acceleration relative to heading
        self.torque = 0

        self.APP_WIND = (0,0)
        self.WIND = (0,0)
        self.APP_CURR = (0,0)
        self.CURR = (0,0)

        self.heeling_angle = 0 # straight up
        self.cog = [0, 0, -.45 * self.hull_height] # TODO: make 3d; x is inplicitly 0 now - OLD: (0, .55)
        self.cob = [0, 0, -.65 * self.hull_height] # y and z; OLD: (0, .35)
        self.metacenter = self.hull_waterline - self.hull_height # z; x y zerod
        self.metacenter_length = self.metacenter - self.cob[2] # z

        # self.main_mast = Mast(self, 0, 0, height = 8)
        
        self.main_sail = SquareRig(ship = self, shape = 'square', height = 6, length = 6, mounting = (0, 0, 8))
        self.keel = Keel(ship = self, length = self.hull_length, height = -1, mounting = (-self.hull_length/2, 0, -self.hull_height))
        self.rudder = Rudder(ship = self, height = -4, length = -1, mounting = (-self.hull_length/2, 0, -self.hull_height * 3/4))

        self.heeling_inertia = ((self.hull_width + (self.hull_height + self.main_sail.height)) / 2)**2
        self.righting_inertia = ((self.hull_width + self.hull_height) / 2)**2
        self.yawing_inertia = ((self.hull_width + self.hull_width) / 2)**2

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f'''
        Position: {self.position}; Heading: {self.heading:.02f}; Velocity: {self.x:.02f}, {self.y:.02f}; Heel: {self.heeling_angle:.02f}; COG: {self.cog}; COB: {self.cob};
        Wind: {self.WIND}, Current: {self.CURR}; AppWind: {self.APP_WIND}, AppCurrent: {self.APP_CURR}; 
        Accel: {self.x_accel:.03f}, {self.y_accel:.03f}; RighingTorque: {self.torque:.03f}; NetTorque: {self.main_sail.torque+self.keel.torque+self.torque:.03f};
        Sail Set: {self.main_sail.pivot:.02f}, Sail Give: {self.main_sail.give:.02f}
        '''
    

    @property
    def ship(self): # For component ownership heirarchy to end here
        return self

    @property
    def apparent_wind(self):
        wind_x = self.world.WINDS[int(self.position[0]), int(self.position[1]), 0]
        wind_y = self.world.WINDS[int(self.position[0]), int(self.position[1]), 1]
        self.APP_WIND = (wind_x - self.x, wind_y - self.y)
        self.WIND = (wind_x, wind_y)
        return (wind_x - self.x, wind_y - self.y)
    
    @property
    def apparent_current(self):
        current_x = self.world.CURRENTS[int(self.position[0]), int(self.position[1]), 0]
        current_y = self.world.CURRENTS[int(self.position[0]), int(self.position[1]), 1]
        self.APP_CURR = (current_x - self.x, current_y - self.y)
        self.CURR = (current_x, current_y)
        return (current_x - self.x, current_y - self.y)
    
    def find_center_of_balance(self):
        return [0, np.sin(self.heeling_angle) * self.metacenter_length, self.metacenter - np.cos(self.heeling_angle) * self.metacenter_length]
    
    def calc_righting_action(self, dt = 1):
        b = np.sqrt((self.cob[1] - self.cog[1])**2 + (self.cob[2] - self.cog[2])**2)
        b_angle = np.arctan2(self.cog[1] - self.cob[1], self.cog[2] - self.cob[2]) # y coords first so 0rad is 'up' in zy space - zerod on gravitational force angle
        buoyant_torque = 9.8 * b * np.sin(self.heeling_angle + b_angle) / self.righting_inertia * dt # inertia * mass (kg) * grav. accel (m/s2) * lever arm

        self.torque = buoyant_torque

    def reset_acceleration_vectors(self):
        self.x_accel = 0
        self.y_accel = 0
        self.driv = 0
        self.lat = 0
    
    def sim(self, diagnostics = None, world_cell_size = 1000, dt = 1):
        '''
        world cell size: square meters per world cell
        dt: seconds per sim step
        '''
        self.reset_acceleration_vectors()

        self.main_sail.sim(self.apparent_wind, dt)
        '''
        TO SIM ALL SAILS WITH SAME APPARENT WIND/CURRENT

        self.keel.sim(self.apparent_current, dt)
        self.rudder.sim(self.APP_CURR, dt)

        self.x += self.main_sail.x + self.keel.x + self.rudder.x
        self.y += self.main_sail.y + self.keel.y + self.rudder.x
        self.x_accel += self.main_sail.x + self.keel.x + self.rudder.x
        self.y_accel += self.main_sail.y + self.keel.y + self.rudder.x
        self.driv += self.main_sail.driv + self.keel.driv + self.rudder.driv
        self.lat += self.main_sail.lat + self.keel.lat + self.rudder.lat
        self.heeling_angle += self.main_sail.torque + self.keel.torque + self.rudder.torque

        yaw_torque = self.rudder.calc_yawing_action()
        self.heading = normalize_angle(self.heading + yaw_torque)
        '''

        self.x += self.main_sail.x #+ self.keel.x + self.x_accel
        self.y += self.main_sail.y #+ self.keel.y # + self.y_accel
        self.x_accel += self.main_sail.x
        self.y_accel += self.main_sail.y
        self.driv += self.main_sail.driv #+ self.keel.driv # + self.x_accel
        self.lat += self.main_sail.lat #+ self.keel.lat # + self.y_accel
        self.heeling_angle += self.main_sail.torque #+ self.keel.torque

        print('SHIP: ', self.APP_CURR)
        print('SAIL: ', self.main_sail)

        self.keel.sim(self.apparent_current, dt)

        self.x += self.keel.x # + self.x_accel
        self.y += self.keel.y # + self.y_accel
        self.x_accel += self.keel.x
        self.y_accel += self.keel.y
        self.driv += self.keel.driv # + self.x_accel
        self.lat += self.keel.lat # + self.y_accel
        self.heeling_angle += self.keel.torque

        print('SHIP: ', self.APP_CURR)
        print('KEEL: ', self.keel)

        self.rudder.sim(self.apparent_current, dt)

        self.x += self.rudder.x # + self.x_accel
        self.y += self.rudder.y # + self.y_accel
        self.x_accel += self.rudder.x
        self.y_accel += self.rudder.y
        self.driv += self.rudder.driv # + self.x_accel
        self.lat += self.rudder.lat # + self.y_accel
        self.heeling_angle += self.rudder.torque
        yaw_torque = self.rudder.calc_yawing_action()
        self.heading = normalize_angle(self.heading + yaw_torque)


        self.cob = self.find_center_of_balance()
        self.calc_righting_action(dt)
        self.heeling_angle += self.torque

        print('RUDDER: ', self.rudder)
        print('YAW: ', yaw_torque)
        print('SHIP: ', self)

        self.position = [self.position[0] + (self.x / world_cell_size) * dt, self.position[1] - (self.y / world_cell_size) * dt]
        if self.position[0] < 0:
            self.position[0] = self.world.SIZE[0] - 1
        if self.position[0] >= self.world.SIZE[0]:
            self.position[0] = 0
        if self.position[1] < 0:
            self.position[1] = self.world.SIZE[1] - 1
        if self.position[1] >= self.world.SIZE[1]:
            self.position[1] = 0

        # print('SHIP: ', self)
        # print('SAIL: ', self.main_sail)
        # print('KEEL: ', self.keel)
        # print('RUDDER: ', self.rudder)
        if abs(self.heeling_angle) > np.pi/2:
            self.heeling_angle = 0






