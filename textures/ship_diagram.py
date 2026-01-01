import sys
sys.path.append('..')

import numpy as np
from shapes import generate_thick_circle, generate_perpendicular_line, generate_solid_line
from indices import index_range, get_pixel_indices
from ships import Ship, Sail
from textures.textures import rotate_index_array



def xy_diagram(ship, size = 'small'):
    if size == 'small':
        length = 100
        thick = 2
    elif size == 'large':
        length = 380
        thick = 4
    width = (ship.hull_width / ship.hull_length) * length

    x_range = (round(-length/2*1.3), round(length/2*1.3)) # x bounds for border
    y_range = (round(-length/2*1.3), round(length/2*1.3)) # y bounds for border

    bow_point = (round(length/2), 0)
    port_point = (0, round(width/2))
    starboard_point = (0, round(-width/2))
    stern_point = (round(-length/2), 0)
    boat = np.concatenate([generate_solid_line(bow_point, port_point, thick), 
                                   generate_solid_line(port_point, stern_point, thick),
                                   generate_solid_line(stern_point, starboard_point, thick),
                                   generate_solid_line(starboard_point, bow_point, thick)], axis = 1)
    boat[0, boat[0] < -length/2 * .8] = -length/2 * .8
    
    sail_length = (ship.main_sail.width / ship.hull_length) * length
    sail_end = (round(np.cos(ship.main_sail.set) * sail_length * .65), round(np.sin(ship.main_sail.set) * sail_length * .65))
    curve_end = (round(sail_end[0] + np.cos(ship.main_sail.set + ship.main_sail.give) * sail_length * .15), 
                 round(sail_end[1] + np.sin(ship.main_sail.set + ship.main_sail.give) * sail_length * .15))
    sail = np.concatenate([generate_solid_line((0,0), sail_end, thick), 
                           generate_solid_line(sail_end, curve_end, thick)], axis = 1)
    
    wind = ship.apparent_wind
    
    
    rotate = np.concatenate([boat, sail], axis = 1)
    # zero outputs
    rotate[0] += x_range[1]
    rotate[1] += y_range[1]
    x_range = (x_range[0] + x_range[1], x_range[1] + x_range[1])
    y_range = (y_range[0] + y_range[1], y_range[1] + y_range[1])

    return x_range, y_range, rotate


def zx_diagram(ship, size = 'small'):
    if size == 'small':
        radius = 50
        thick = 2
    elif size == 'large':
        radius = 190
        thick = 4

    mast_height = radius * 1.3 #(ship.main_sail.height / ship.hull_height) * radius
    total_height = radius + round(mast_height)

    x_range = (round(-radius*1.3), round(radius*1.3)) # x bounds for border
    y_range = (round(-radius*1.3), round(radius*1.3)) # y bounds for border

    hull_offset = radius/10
    circle = generate_thick_circle(radius = radius, thick = thick, offset = (0, hull_offset))
    hull = circle[:, circle[1] >= hull_offset] # bottom half of circle
    hull_top = generate_perpendicular_line((-radius, hull_offset), (radius, hull_offset), thick) # top line of hull
    waterline = -radius * (ship.hull_waterline / ship.hull_height) # y-direction
    
    mast_l = generate_perpendicular_line((-radius * .095, hull_offset), (-radius * .095, hull_offset-mast_height), thick)
    mast_r = generate_perpendicular_line((radius * .095, hull_offset), (radius * .095, hull_offset-mast_height), thick) 

    static_shape = np.concatenate([hull, hull_top, mast_l, mast_r], axis = 1)

    cob = ( radius * (ship.cob[0] / ship.hull_height), hull_offset + radius * (1 - (ship.cob[1] / ship.hull_height)) )
    cog = ( radius * (ship.cog[0] / ship.hull_height), hull_offset + radius * (1 - (ship.cog[1] / ship.hull_height)) )

    cob_idx = np.array(get_pixel_indices( ( np.array([cob[0] - (radius * .04)], dtype = int),
                                            np.array([cob[1] - (radius * .04)], dtype = int) ), 
                                        round(radius * .04 * 2 )))
    
    cog_idx = np.array(get_pixel_indices( ( np.array([cog[0] - (radius * .04)], dtype = int),
                                            np.array([cog[1] - (radius * .04)], dtype = int) ), 
                                        round(radius * .04 * 2 )))
    
    rotate = rotate_index_array(np.concatenate([static_shape, cob_idx, cog_idx], axis = 1), ship.heeling_angle)
    # zero outputs
    rotate[0] += x_range[1]
    rotate[1] += y_range[1]
    x_range = (x_range[0] + x_range[1], x_range[1] + x_range[1])
    y_range = (y_range[0] + y_range[1], y_range[1] + y_range[1])

    return x_range, y_range, rotate
    
    





ship = Ship(world = None, position = (350,115), heading = np.pi/2)