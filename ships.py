# ship types - https://museum.wa.gov.au/maritime-archaeology-db/early-sailing-ships
#              https://www.realmofhistory.com/2023/08/11/historical-warships/#:~:text=These%20incredible%20warships%20ranged%20from,both%20solid%2Dshot%20and%20grapeshot.
# force calc - https://www.nautilusint.org/en/news-insight/telegraph/never-again-how-a-better-understanding-of-aerodynamics-and-hydrodynamics-could-help-prevent-another-ever-given-incident/
# sail/keel forces - https://www.phys.unsw.edu.au/~jw/sailing.html
# wind/wave forces - https://data.coaps.fsu.edu/eric_pub/RSMAS/GODAE_School/GODAE_Book/Chap23-Hackett.pdf
# weight/displacement - https://www.lifeofsailing.com/blogs/articles/how-much-does-a-sailboat-weigh

# 2240 lbs per ton
# 1016 kgs per ton


import numpy as np
from generics import clockwise_distance, DBZ, compare_angles

AIR_DENSITY = 1.225 # g/ml, 1.225 kg/m3 # TODO: world attribute
WATER_DENSITY = 1000 


class Sail:
    def __init__(self, ship = None, give = np.pi/6, set = np.pi/2, shape = 'square', height = 8, width = 8):
        self.give = give # in radians; maximum change in wind-angle sail will allow when fully taut; how much slack it has at rest; defined clockwise to set
        self.set = set # where leading edge of sail is pointing; pi/-pi has sail behind mast, -np.pi/2 has sail to the right of mast
        self.ship = ship
        self.calc_sail_area(shape, height, width)
        self.x = 0 # x-wise force on sail (relative to world directions)
        self.y = 0

    def calc_sail_area(self, shape, height, width):
        if shape == 'square':
            self.area = height * width
        elif shape == 'triangle':
            self.area = .5 * height * width

class Keel(Sail):
    def __init__(self, ship = None, give = 0, set = np.pi/2):
        super().__init__(ship = ship, give = give, set = set)
    


class Ship:
    def __init__(self, world = None, position = (0,0), heading = np.pi/4):
        self.world = world
        self.position = [position[0], position[1]]
        self.hull_length = 18
        self.hull_width = 4
        self.hull_height = 6
        self.hull_waterline = 3.5
        self.keel_height = 1
        self.heading = heading
        self.main_sail = Sail(ship = self)
        self.weight = 15*1016 # in kgs 
        self.x = 0 # present velocity
        self.y = 0

    def __str__(self):
        return f'Position: {self.position}; Heading: {self.heading}; Velocity: {self.x}, {self.y}; Sail: {self.main_sail.set}; Sail Force: {self.main_sail.x}, {self.main_sail.y}'
    
    def calc_apparent_wind(self):
        wind_x = self.world.WINDS[int(self.position[0]), int(self.position[1]), 0]
        wind_y = self.world.WINDS[int(self.position[0]), int(self.position[1]), 1]
        return (wind_x - self.x, wind_y - self.y)
    
    def calc_apparent_current(self):
        current_x = self.world.CURRENTS[int(self.position[0]), int(self.position[1]), 0]
        current_y = self.world.CURRENTS[int(self.position[0]), int(self.position[1]), 1]
        return (current_x - self.x, current_y - self.y)
    
    def sim(self, diagnostics = None):
        print(f'SPEED: {self.x, self.y}')
        print(f'WIND: {self.world.WINDS[int(self.position[0]), int(self.position[1])]}')
        print(f'CURR: {self.world.CURRENTS[int(self.position[0]), int(self.position[1])]}')
        apparent_wind = self.calc_apparent_wind()
        print(f'APP. WIND: {apparent_wind}')
        wind_impact_on_sail(apparent_wind, self.main_sail, diagnostics)

        apparent_current = self.calc_apparent_current()
        print(f'APP. CURR.: {apparent_current}')
        current_impact_on_ship(apparent_current, self, diagnostics)
        print('___________')
        self.position = [self.position[0] + (self.x / 1000), self.position[1] + (self.y / 1000)]
        if self.position[0] < 0:
            self.position[0] = self.world.SIZE[0] - 1
        if self.position[0] >= self.world.SIZE[0]:
            self.position[0] = 0
        if self.position[1] < 0:
            self.position[1] = self.world.SIZE[1] - 1
        if self.position[1] >= self.world.SIZE[1]:
            self.position[1] = 0
        print(f'NEW VELOCITY: {self.x}, {self.y}')
        print(f'NEW POSITION: {self.position}')
        print('____________')
        print('____________')


def compare_wind_and_sail(wind, sail):
    final_theta = sail.set - np.pi - sail.give
    if final_theta <= -np.pi:
        final_theta += 2*np.pi

    if sail.give >= 0:
        # final is counterclockwise around circle from set
        _wind = wind if wind >= 0 or sail.set < 0 else wind + 2*np.pi
        final_theta = final_theta if final_theta >= 0 or sail.set < 0 else final_theta + 2*np.pi
        #Notes - -pi sail set w/ pi wind should return True but doesn't
        return _wind >= sail.set and _wind <= final_theta

    elif sail.give < 0:
        _wind = wind + 2*np.pi if wind < 0 and final_theta > 0 else wind
        init_theta = sail.set + 2*np.pi if sail.set < 0 and _wind >= 0 else sail.set

        return _wind <= init_theta and _wind >= final_theta
    
def compare_wind_and_sail2(wind, sail):
    final_theta = sail.set - np.pi - sail.give
    if final_theta <= -np.pi:
        final_theta += 2*np.pi

    if sail.give >= 0:
        no_zone = compare_angles(sail.set, final_theta)
        wind_diff = compare_angles(sail.set, wind)
        return not wind_diff < no_zone
    
    elif sail.give < 0:
        no_zone = compare_angles(final_theta, sail.set)
        wind_diff = compare_angles(final_theta, wind)
        return not wind_diff < no_zone


def compare_wind_and_sail3(wind, sail):
    zone = np.pi + sail.give 
    if sail.give >= 0:
        wind_diff = clockwise_distance(sail.set, wind)
        if wind_diff < zone and wind_diff != 0: # is wind in range of sail given give?
            return None
        else:
            return (wind_diff - zone >= (np.pi - sail.give)/2) or wind_diff == 0 # True if wind is closer to set than end
    elif sail.give < 0:
        wind_diff = clockwise_distance(sail.set, wind)
        if wind_diff > zone:
            return None
        else:
            return wind_diff <= zone / 2


# sail = Sail()
# for give in [-np.pi/4]:#, -np.pi/6]:
#     sail.give = give
#     print('GIVE: ', sail.give)
#     for se in [0, 3*np.pi/4, np.pi, -3*np.pi/4, -np.pi/4]:
#         sail.set = se
#         print('SET: ', se)
#         for wind in [0, 3*np.pi/4, np.pi, -3*np.pi/4, -np.pi/4]:
#             print(wind, compare_wind_and_sail3(wind, sail))




def wind_impact_on_sail(wind = (-7, 10), sail = Sail(), diagnostics = None):
    wind_theta = np.arctan2(wind[1], wind[0])
    wind_strength = np.sqrt(wind[0]**2 + wind[1]**2)

    wind_x = wind[0]
    wind_y = wind[1]

    wind_compare = compare_wind_and_sail3(wind_theta, sail)
    if wind_compare is None:
        # sail.x = wind[0] / 4 / sail.ship.weight
        # sail.y = wind[1] / 4 / sail.ship.weight
        # sail.ship.x += sail.x
        # sail.ship.y += sail.y
        # print(f'WIND: {wind}')
        # try:
        #     diagnostics[-1]['NO SAIL'] = (wind[0] / 4 / sail.ship.weight, wind[1] / 4 / sail.ship.weight)
        # except NameError:
        #     pass
        sail.ship.x = sail.ship.x / 2
        sail.ship.y = sail.ship.y / 2
        return
    # TODO: add ineffiency parameter?
    elif wind_compare:
        final_wind = sail.set - sail.give
    else:
        final_wind = sail.set + np.pi

    # TODO: reduce strength based on length of sail wind travelled?
    final_wind_x = np.cos(final_wind) * wind_strength
    final_wind_y = np.sin(final_wind) * wind_strength

    delta_wind_x = final_wind_x - wind_x
    delta_wind_y = final_wind_y - wind_y

    air_volume = wind_strength * sail.area # m/s * m2 * s = m3
    air_mass = air_volume * AIR_DENSITY # m3 * kg/m3 = kg
    air_acceleration = np.sqrt(delta_wind_x**2 + delta_wind_y**2) # m/s2
    force_on_air = air_mass * air_acceleration # kg * m/s2
    force_wind_x = delta_wind_x * air_mass
    force_wind_y = delta_wind_y * air_mass

    sail_x = -force_wind_x / sail.ship.weight
    sail_y = -force_wind_y / sail.ship.weight

    # print(f'WIND: {wind}')
    try:
        diagnostics[-1]['F SAIL'] = (sail_x, sail_y)
        diagnostics[-1]['AIR MASS'] = air_mass
    except NameError:
        pass
    except:
        print((sail_x, sail_y))
        print(air_mass)


    sail.x = sail_x
    sail.y = sail_y
    sail.ship.x += sail_x
    sail.ship.y += sail_y
    print(f'F WIND: {sail_x, sail_y}')
    #return sail.set, final_wind[0], np.arctan2(sail_y, sail_x), np.sqrt(sail_x**2 + sail_y**2), sail_x, sail_y

def current_impact_on_ship(current = (10,0), ship = Ship(), diagnostics = None):
    current_theta = np.arctan2(current[1], current[0])
    current_strength = np.sqrt(current[0]**2 + current[1]**2)

    current_x = current[0] # DBZ(current[0], current_strength)
    current_y = current[1] # DBZ(current[1], current_strength)

    distance = clockwise_distance(ship.heading, current_theta)
    if distance >= np.pi/2 and distance < 3*np.pi/2:
        final_current = ship.heading + np.pi
    else:
        final_current = ship.heading

    # TODO: reduce strength based on length of sail wind travelled?
    final_current_x = np.cos(final_current) * current_strength * 1
    final_current_y = np.sin(final_current) * current_strength * 1

    delta_current_x = final_current_x - current_x
    delta_current_y = final_current_y - current_y

    delta_current_theta = final_current - current_theta #np.arctan2(delta_current_y, delta_current_x)

    water_volume = current_strength * ship.hull_length * ship.hull_waterline
    water_mass = water_volume * WATER_DENSITY
    water_acceleration = np.sqrt(delta_current_x**2 + delta_current_y**2)
    force_on_water = water_mass * water_acceleration
    force_current_x = delta_current_x * water_mass
    force_current_y = delta_current_y * water_mass

    print(f'F CURRENT: {-force_current_x / ship.weight, -force_current_y / ship.weight}')
    try:
        diagnostics[-1]['F SHIP'] = (-force_current_x / ship.weight, -force_current_y / ship.weight)
        diagnostics[-1]['WATER MASS'] = water_mass
    except NameError:
        pass
    except:
        print(-force_current_x / ship.weight, -force_current_y / ship.weight)
        print(water_mass)

    ship.x += -force_current_x / ship.weight
    ship.y += -force_current_y / ship.weight


def sail_impact_on_ship(sail, ship):
    #convert sail x and y to be relative to ship heading
    force_on_sail_theta = np.arctan2(sail.y, sail.x)
    force_on_sail_strength = np.sqrt(sail.x**2 + sail.y**2)
    crosswise_ship_theta = ship.heading - np.pi/2 # TODO: add pi/2 if sail is on other side of mast
    relative_sail_theta = force_on_sail_theta - crosswise_ship_theta
    relative_sail_x = np.cos(relative_sail_theta) * force_on_sail_strength
    relative_sail_y = np.sin(relative_sail_theta) * force_on_sail_strength

    relative_force_on_keel_theta = ship.heading + np.pi/2
    relative_keel_x = -relative_sail_x # Equal to strength as force on keel has no y in ship-relative composition

    ship.x = np.cos(relative_force_on_keel_theta) * relative_sail_x
    ship.y = np.sin(relative_force_on_keel_theta) * relative_sail_x

def calc_sail_depth(point1, point2, width):
    chord_midpoint = (point2[0] - point1[0], point2[1] - point1[1])

def force_of_impact(impacting_force = (0, 10), impacted_object = (-np.pi/2, 0)):
    water_density = 1.026 #seawater density; freshwater = 1
    ldc = 1 # lengthwise drag coefficient
    wdc = 1 # widthhwise drag coefficient

    impacted_object = (-np.pi, 0)
    impacting_force = (0, 10)

    current_theta = impacting_force[0]
    current_strength = impacting_force[1]
    ship_theta = impacted_object[0]
    ship_strength = impacted_object[1]
    ship_x = ship_strength * np.cos(ship_theta)
    ship_y = ship_strength * np.sin(ship_theta)
    ship_length = 10
    ship_width = 1

    # lw_drag_force = .5 * water_density * current_strength * ldc * ship_length
    # ww_drag_force = .5 * water_density * current_strength * wdc * ship_width

    current_90 = current_theta - np.pi/2
    theta = ship_theta - current_90

    perpendicular_strength = current_strength * np.cos(theta) * ldc
    perpendicular_theta = ship_theta + np.pi/2
    perpendicular_x = perpendicular_strength * np.cos(perpendicular_theta)
    perpendicular_y = perpendicular_strength * np.sin(perpendicular_theta)

    parallel_strength = current_strength * np.sin(theta) * wdc
    parallel_theta = ship_theta
    parallel_x = parallel_strength * np.cos(parallel_theta)
    parallel_y = parallel_strength * np.sin(parallel_theta)

    # normal_strength = 


    net_x = parallel_x + perpendicular_x + ship_x
    net_y = parallel_y + perpendicular_y + ship_y

    return net_x, net_y


if __name__ == '__main__':
# Position: [70.01842392323705, 90.02729013457169]; Heading: 2.106194490192345; Velocity: -4.416054258232779, 0.22129272587548798; Sail: -0.7853981633974483; Sail Force: 0.026684449114727466, 0.028744423136780294
# SPEED: (-4.416054258232779, 0.22129272587548798)
# WIND: [2.5 0. ]
# CURR: [1. 0.]
# APP. WIND: (6.916046775344396, -0.22129272587548798)
# F WIND: (0.18243819815387377, 0.23004496843871758)
# APP. CURR.: (5.205552171499232, -0.45133769431420556)
# F CURRENT: (54.859071656666195, 87.31860196566832)
    class World:
        def __init__(self):
            self.WINDS = np.zeros((500,300,2))
            self.CURRENTS = np.zeros((500,300,2))
    world = World()
    world.WINDS[:,:] = (2.5, 0)
    world.CURRENTS[:,:] = (1, 0)

    ship = Ship(position = (70.01842392323705, 90.02729013457169), heading = 2.106194490192345, world = world)
    ship.main_sail.set = -np.pi/4
    ship.x = -4.416054258232779
    ship.y = 0.22129272587548798

    app_wind = ship.calc_apparent_wind()
    wind_impact_on_sail(app_wind, ship.main_sail)
    app_current = ship.calc_apparent_current()
    current_impact_on_ship(app_current, ship)




