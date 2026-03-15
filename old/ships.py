import numpy as np
from basics.angles import clockwise_distance, clockwise_distance_prenorm_a2
from ships import Sail

from parameters import AIR_DENSITY, WATER_DENSITY, SAIL_INEFFICIENCY, KEEL_INEFFICIENCY



def compare_wind_and_sail3(wind, sail):
    print('SAIL-WIND: ', sail.ship.heading - sail.set, wind)
    zone = np.pi - sail.give 
    wind_diff = clockwise_distance_prenorm_a2(sail.ship.heading + sail.set, wind) #clockwise_distance(sail.ship.heading - sail.set, wind)
    if sail.give <= 0: # if sail.give >= 0: #TODOL flip to < 0 and else to >= so that sail give is consistent
        if wind_diff < zone and wind_diff != 0: # is wind in range of sail given give?
            return None
        else:
            print('wind wind is closer to set than tip')
            return (wind_diff - zone >= (np.pi + sail.give)/2) or wind_diff == 0# return (wind_diff - zone >= (np.pi - sail.give)/2) or wind_diff == 0 # True if wind is closer to set than end
    elif sail.give > 0:
        if wind_diff > zone:
            return None
        else:
            print('wind wind is closer to tip')
            return wind_diff <= zone / 2
        
def compare_wind_and_sail4(wind, sail):
    print('SAIL-WIND: ', sail.ship.heading - sail.set, wind)
    zone = sail.give - np.pi # sail give shouldn't eer be greater than pi so this is pre-normalized
    wind_diff = clockwise_distance_prenorm_a2(sail.ship.heading + sail.set, wind) #clockwise_distance(sail.ship.heading - sail.set, wind)

    if sail.give >= 0: # zone is negative
        if wind_diff > -zone and wind_diff != 0: # 
            print('Wind is not Catching')
            return None
        else:
            half = -zone / 2
            if wind_diff < half:
                print('Wind is closer to Set')
            else:
                print('Wind is closer to Tip')
            return wind_diff < half # True if wind is closer to set; False if wind is closer to tip
 
    elif sail.give < 0:
        _zone = np.pi*2 + zone
        if wind_diff < -zone and wind_diff != 0: # zone is supernegative (< -pi)
            return None
        else:
            half = -zone + ( _zone / 2 ) 
            if wind_diff >= half or wind_diff == 0:
                print('Wind is closer to Set')
            else:
                print('Wind is closer to Tip')
            return wind_diff >= half or wind_diff == 0



def wind_impact_on_sail(wind = (-7, 10), sail = Sail(), diagnostics = None):
    #print(wind)
    ship = sail.ship
    wind_theta = np.arctan2(wind[1], wind[0])
    wind_strength = np.sqrt(wind[0]**2 + wind[1]**2) #/ m/s

    wind_x = wind[0]
    wind_y = wind[1]

    wind_compare = compare_wind_and_sail4(wind_theta, sail)
    print('WIND COMPARE: ', wind_compare)
    if wind_compare is None:
        #ship.x += wind_x #sail.ship.x / 2
        #ship.y += wind_y #sail.ship.y / 2
        return
    # TODO: add ineffiency parameter?
    elif wind_compare:
        final_wind = sail.ship.heading + sail.set + sail.give
    else:
        final_wind = sail.ship.heading + sail.set + np.pi
    print(wind_theta, final_wind)

    # TODO: reduce strength based on length of sail wind travelled?
    final_wind_x = np.cos(final_wind) * wind_strength * .9
    final_wind_y = np.sin(final_wind) * wind_strength * .9

    delta_wind_x = final_wind_x - wind_x
    delta_wind_y = final_wind_y - wind_y
    print('DELTA WIND: ', final_wind_x, final_wind_y)

    air_volume = wind_strength * sail.area # m/s * m2 * s = m3. #TODO: wind-catching area should change with heeling angle - sin( heelAngle ) * sail area
    air_mass = air_volume * AIR_DENSITY # m3 * kg/m3 = kg
    air_acceleration = np.sqrt(delta_wind_x**2 + delta_wind_y**2) # m/s2
    force_on_air = air_mass * air_acceleration # kg * m/s2
    force_wind_x = delta_wind_x * air_mass # per second
    force_wind_y = delta_wind_y * air_mass

    sail.x = -force_wind_x / ship.weight
    sail.y = -force_wind_y / ship.weight
    print('SA: ', sail.x, sail.y)

    # print(f'WIND: {wind}')
    # try:
    #     diagnostics[-1]['F SAIL'] = (sail_x, sail_y)
    #     diagnostics[-1]['AIR MASS'] = air_mass
    # except:
    #     diagnostics[-1]['F SAIL'] = 'error'
    #     diagnostics[-1]['AIR MASS'] = 'error'


    # heeling action
    direction = ship.heading # current ship's direction
    force_on_ship_dir = np.arctan2(sail.y, sail.x)
    theta = direction - force_on_ship_dir
    fLat = np.cos(theta) * force_on_air #TODO: calc torque as if force was applied for a second or minute?
    torque = fLat * ( (sail.height/2) + ship.hull_height + ship.keel_height ) / ship.heeling_inertia #TODO: use fLat to get heeling force (youtube video on torque angles)

    ship.l = fLat
    ship.d = np.sin(theta) * force_on_air 
    ship.heeling_angle += torque
    print('S: ', torque)
    #return sail.set, final_wind[0], np.arctan2(sail_y, sail_x), np.sqrt(sail_x**2 + sail_y**2), sail_x, sail_y

def current_impact_on_ship(current = (10,0), ship = Ship(), diagnostics = None):
    current_theta = np.arctan2(current[1], current[0])
    current_strength = np.sqrt(current[0]**2 + current[1]**2) #/ 1000
    #print(current, current_strength)

    current_x = current[0] # DBZ(current[0], current_strength)
    current_y = current[1] # DBZ(current[1], current_strength)

    distance = clockwise_distance(ship.heading, current_theta)
    if distance >= np.pi/2 and distance < 3*np.pi/2:
        final_current = ship.heading + np.pi
    else:
        final_current = ship.heading

    # TODO: reduce strength based on length of sail wind travelled?
    final_current_x = np.cos(final_current) * current_strength * .7
    final_current_y = np.sin(final_current) * current_strength * .7

    delta_current_x = final_current_x - current_x
    delta_current_y = final_current_y - current_y
    print('DELTA CURR: ', delta_current_x, delta_current_y)

    delta_current_theta = final_current - current_theta #np.arctan2(delta_current_y, delta_current_x)

    water_volume = current_strength * ship.hull_length * ship.hull_waterline * .5 #TODO better calc area of ship shown to current
    water_mass = water_volume * WATER_DENSITY
    water_acceleration = np.sqrt(delta_current_x**2 + delta_current_y**2)
    force_on_water = water_mass * water_acceleration
    force_current_x = delta_current_x * water_mass
    force_current_y = delta_current_y * water_mass


    # drag coefficient



    # try:
    #     diagnostics[-1]['F SHIP'] = (-force_current_x / ship.weight, -force_current_y / ship.weight)
    #     diagnostics[-1]['WATER MASS'] = water_mass
    # except:
    #     diagnostics[-1]['F SHIP'] = 'error'
    #     diagnostics[-1]['WATER MASS'] = 'error'

    ship.x_accel = -force_current_x / ship.weight
    ship.y_accel = -force_current_y / ship.weight
    print('HA: ', ship.x_accel, ship.y_accel)

    # heeling action
    direction = np.arctan2(ship.y, ship.x) # current ship's direction
    force_on_ship_dir = np.arctan2(ship.x_accel, ship.y_accel)
    theta = direction - force_on_ship_dir
    fLat = np.cos(theta) * force_on_water #TODO: calc torque as if force was applied for a second or minute?
    torque = fLat * ( ship.hull_height + ship.keel_height ) / ship.heeling_inertia #TODO: use fLat to get heeling force (youtube video on torque angles)

    ship.lat += fLat
    ship.driv += np.sin(theta) * force_on_water 
    ship.heeling_angle += torque
    print('K: ', torque)


