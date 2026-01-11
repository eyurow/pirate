import numpy as np
from algorithms.generics import DBZ, DBZArray, get_margin


def generate_perpendicular_line(p1, p2, thick = 1):
    # Use if line will always be perpendicular to the x/y axes
    x_diff = p1[0] - p2[0]
    y_diff = p1[1] - p2[1]
    step = -x_diff / abs(x_diff) if abs(x_diff) >= abs(y_diff) else -y_diff / abs(y_diff)
    back, front = get_margin(thick, 1) # offsets from start pixel for thickness, e.g. (0,1) for thick2, (1,1) for thick3

    if y_diff == 0:
        xs = np.arange(p1[0], p2[0] + step, step, dtype = int)
        if thick > 1:
            xs = xs[None].repeat(thick, axis = 0).flatten()
            ys = np.arange(p1[1] - back, p1[1] + front + 1).repeat(xs.size//thick)
        else:
            ys = np.full(abs(x_diff) + 1, p1[1], dtype = int)
        
    elif x_diff == 0:
        ys = np.arange(p1[1], p2[1] + step, step, dtype = int)
        if thick > 1:
            ys = ys[None].repeat(thick, axis = 0).flatten()
            xs = np.arange(p1[0] - back, p1[0] + front + 1).repeat(ys.size//thick)
        else:
            xs = np.full(abs(y_diff) + 1, p1[0], dtype = int)

    return np.array([xs, ys], dtype = int)


def generate_line(p1, p2, thick = 1, thick_quotient = .5, thick_offset = -1, num_lines = 1, even_offset = 0):
    '''
    THICKNESS PARAMETERS

    base line -                 perpendicular to the line between p1 and p2, and intersecting at p1
    antiline:                   non-dominant axis step length along base line to form one boundary of thickness 
    antislope:                  slope of base line
    thick_offset_front/back:    points which form boundaries along base line from which !num_lines are drawn

    thick:                      number of non-dom pixels to draw per dominant pixel given an x/y-perpendicular line
    thick_param:                permutation of !thick for calculation of !antiline
    num_lines:                  number of lines to draw against base line when calculating pixels
    thick_offset:               addition/reduction to !thick when calculating !thick_param
    thick_quotient:             multiple applied to !thick when calculating !thick_param
    even_offset:                offset applied to !num_lines for even numbered thickness

    '''
    if p1 == p2:
        return np.empty((2,0), dtype = int)
    x_diff = p1[0] - p2[0]
    y_diff = p1[1] - p2[1]
    slope = DBZ(y_diff, x_diff)
    step = -x_diff / abs(x_diff) if abs(x_diff) >= abs(y_diff) else -y_diff / abs(y_diff) # -1 or 1 cell along dominant axis

    if abs(x_diff) >= abs(y_diff):
        step = -x_diff / abs(x_diff)
        slope = DBZ(y_diff, x_diff)
        d_len = x_diff
        nd_len = y_diff
        d = (p1[0], p2[0])
        nd = (p1[1], p2[1])
        direction = 'x'
    else:
        step = -y_diff / abs(y_diff)
        slope = DBZ(x_diff, y_diff)
        d_len = y_diff
        nd_len = x_diff
        d = (p1[1], p2[1])
        nd = (p1[0], p2[0])
        direction = 'y'

    if thick == 1:
        ds = np.arange(d[0], d[1] + step, step)
        nds = np.rint(nd[0] + (ds - d[0]) * slope) #TODO: Use y1 + linspace method here instead?
    else:
        d_range = np.arange(stop = -d_len + step, step = step) # range from 0 to dominant diff (to be added to p1; e.g p1 = 3 and -x_diff = 3 gives range 3:6)

        ## Thickness Base Line ##
        thick_param = (thick + thick_offset) * thick_quotient
        antislope = DBZ(-1, slope) # S
        antiline = np.sqrt( thick_param**2 / (DBZ(1, antislope**2) + 1) ) # L
        offset = ((1 - (thick%2)) * DBZ(antiline, antislope) * even_offset, (1 - (thick%2)) * antiline * even_offset)
        thick_offset_front = (d[0] - DBZ(antiline, antislope) - offset[0], nd[0] - antiline - offset[1]) # C1
        thick_offset_back = (d[0] + DBZ(antiline, antislope) - offset[0], nd[0] + antiline - offset[1]) # C2

        d_start = np.linspace(thick_offset_back[0], thick_offset_front[0], num_lines) # + (1 - thick%2))
        nd_start = np.linspace(thick_offset_back[1], thick_offset_front[1], num_lines) # + (1 - thick%2))

        ds = np.rint(d_start[:, None] + d_range).flatten()
        nds = np.rint(nd_start[:, None] + np.linspace(0, -nd_len, d_range.size)).flatten()
    
    if direction == 'x':
        ar = np.array([ds, nds], dtype = int)
    else:
        ar = np.array([nds, ds], dtype = int)
    return np.unique(ar, axis = 1)


def generate_solid_line(p1, p2, thick = 2):
    # Gives patterned line for odd thicknesses > 1
    thick_quotient = .5
    thick_offset = -1
    num_lines = thick
    even_offset = .5
    return generate_line(p1, p2, thick, thick_quotient, thick_offset, num_lines, even_offset)

def generate_patterned_line(p1, p2, thick = 2):
    # Gives patterned line for odd thicknesses > 1
    thick_quotient = .5
    thick_offset = 0
    num_lines = thick + (1 - thick%2)
    even_offset = 0
    return generate_line(p1, p2, thick, thick_quotient, thick_offset, num_lines, even_offset)
 



def generate_circle(radius = 5, offset = (0,0)):
    x = radius 
    y = 0
    
    xs = []
    ys = []
    while y <= x:
        if (x**2) + (y**2) <= radius**2:
            xs.append(x)
            ys.append(y)
            y += 1
        else:
            x -= 1
            xs.append(x)
            ys.append(y)
            y += 1
    
    oct_len = len(xs)
    arr = np.empty((2, oct_len * 8), dtype = int)
    arr[0, :oct_len] = xs
    arr[1, :oct_len] = ys
    
    arr[0, oct_len:2*oct_len] = ys[::-1] #arr[1, :oct_len] # second octant
    arr[1, oct_len:2*oct_len] = xs[::-1] #arr[0, :oct_len]
    
    arr[0, 2*oct_len:4*oct_len] = np.flip(-arr[0, :2*oct_len]) # second quadrant
    arr[1, 2*oct_len:4*oct_len] = np.flip(arr[1, :2*oct_len])
    
    arr[0, 4*oct_len:8*oct_len] = np.flip(arr[0, :4*oct_len]) # second half
    arr[1, 4*oct_len:8*oct_len] = np.flip(-arr[1, :4*oct_len])
    
    arr[0] += int(offset[0])
    arr[1] += int(offset[1])
    
    return arr

def generate_thick_circle(radius = 5, thick = 2, offset = (0,0)):
    outer = generate_circle(radius = radius, offset = offset)
    for x in range(1, thick):
        append = generate_circle(radius = radius - x, offset = offset)
        outer = np.concatenate([outer, append], axis = 1, dtype = int)
    outer = np.unique(outer, axis = 1)
        
    return outer


def generate_compass(radius = 10, offset = (0,0)):
    # two crossed horizontal and vertical lines within circle
    circle = generate_circle(radius = radius, offset = offset)

    x_line = generate_perpendicular_line((offset[0] + radius, offset[1]), (offset[0] - radius, offset[1]), thick = 2)
    y_line = generate_perpendicular_line((offset[0], offset[1] + radius), (offset[0], offset[1] - radius), thick = 2)

    return np.concatenate([circle, x_line, y_line], axis = 1)


def generate_arrow(p1, p2, line_thick, head_thick):
    line = generate_solid_line(p1, p2, line_thick)


def generate_curve(radius = 5, xy_ratio = 2, offset = (0,0)):
    # xy_ratio: # of x-steps per y-step
    x = radius 
    y = 0
    
    xs = []
    ys = []
    while y <= x / xy_ratio:
        if (x**2) + (y**2) <= x * (x / xy_ratio):
            xs.append(x)
            ys.append(y)
            y += 1
        else:
            x -= 1
            xs.append(x)
            ys.append(y)
            y += 1
        
    return np.array([xs, ys], dtype = int)

