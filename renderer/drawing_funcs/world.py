import numpy as np

from basics.arrays import shift_array

def screen_blur(pa):
    # shift pa array to calculate average 3x3 colors
    summ = pa[...].astype(float)
    y = True
    for pair in [(-1, 1),(1, 1),(1, -1),(-1, -1)]:  
        if y:
            cell = [(0, pair[0]), (pair[1], pair[0])]
        else:
            cell = [(pair[0], 0), (pair[0], pair[1])]
            
        ## Shift 1
        shift = shift_array(pa, pair[0], y = y, fill = 0)
        summ += shift

        ## Shift 2
        shift = shift_array(shift, pair[1], y = not y, fill = 0)
        summ += shift
    
        y = not y
    
    pa[...] = (summ / 9).astype(int)




def pa_random_color(pa, strengths, distance, cell_size, ref_size = (400,200)):
    shape = pa.shape[:2]
    
    #str_big = np.repeat(np.repeat(strengths, cell_size, axis = 1), cell_size, axis = 0)
    str_big = strengths.repeat(cell_size, axis = 1).repeat(cell_size, axis = 0)
    pa[:,:,2] = 190 - ( 100 * np.minimum(1, np.sqrt(str_big)/10) ) # make 10 a parameter
    #pa[:,:,1] = pa[:,:,2]
    #pa[:,:,1] = pa[:,:,2] * np.random.uniform(.57,1.2,shape)
    pa[:,:,1] = pa[:,:,2] * np.random.normal(.9, .1, shape)
    pa[:,:,0] = np.random.uniform(20,30,shape)
    

def pa_fill_color(pa, strengths, distance, cell_size, ref_size = (400,200)):
    scaled = np.arctan(strengths/2)
    percentile = scaled / (np.pi/2)
    
    blue = 209 - ( (209 - 48) * percentile )
    green = blue / 1.113537
    
    blue_big = np.repeat(np.repeat(blue, cell_size, axis = 1), cell_size, axis = 0)
    green_big = np.repeat(np.repeat(green, cell_size, axis = 1), cell_size, axis = 0)
    
    pa[:,:,2] = blue_big
    pa[:,:,1] = green_big #pa[:,:,2] / 1.113537
    pa[:,:,0] = 0
    

def funky1(pa, strengths, distance, cell_size, ref_size = (400,200)):
    scaled = np.arctan(strengths/2)
    percentile = scaled / (np.pi/2)
    
    blue = 209 - ( (209 - 48) * percentile * distance )
    green = blue / 1.113537
    
    blue_big = np.repeat(np.repeat(blue, cell_size, axis = 1), cell_size, axis = 0)
    green_big = np.repeat(np.repeat(green, cell_size, axis = 1), cell_size, axis = 0)
    
    pa[:,:,2] = blue_big
    pa[:,:,1] = pa[:,:,2] / 1.113537
    pa[:,:,0] = 0
    

    
def funky2(pa, strengths, distance, cell_size, ref_size = (400,200)):
    dist_big = np.repeat(np.repeat(distance, cell_size, axis = 1), cell_size, axis = 0)
    
    pa[:,:,2] = 209 - ( (209 - 48) * dist_big )     #(1 - dist_big / distance.max()) 
    pa[:,:,1] = pa[:,:,2] / 1.113537
    pa[:,:,0] = 0
    
    
    
def fill_color_light(pa, strengths, distance, cell_size, ref_size = (400,200)):
    #adjusted_strength = np.maximum(( 70 * (strengths**(1/3)) ), 200)
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = np.minimum(distance / 282, 1) #np.sqrt(300**2 + 300**2)
    
    blue = (240 - (240) * adjusted_strength) * (1 - adjusted_distance)**2
    green = blue / 1.113537
    red = blue * .6315789 * (1 - adjusted_distance)**2 # np.zeros(blue.shape) #
    
    blue_big = np.repeat(np.repeat(blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big
    
    
def fill_color_sun(pa, strengths, distance, cell_size, ref_dist = 200):
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = np.minimum(distance / 200, 1) #np.sqrt(300**2 + 300**2)
    
    base_blue = (240 - (240) * adjusted_strength) * (1 - adjusted_distance)**2
    base_green = base_blue * .898039 # blue / 1.113 as base; increased when near sun
    base_red = np.zeros(base_blue.shape)
    
    # Under sun slightly yellow
    base_green[adjusted_distance <= .3] = base_blue[adjusted_distance <= .3] * \
                                            ( .898039 + (.992157 - .898039) * (1 - \
                                                        ( adjusted_distance[adjusted_distance <= .3]/.3) ) )
    
    base_red[adjusted_distance <= .3] = base_blue[adjusted_distance <= .3] * .866071 * \
                                                        ( 1 - (adjusted_distance[adjusted_distance <= .3]/.3) )
                                                        
    blue_big = np.repeat(np.repeat(base_blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(base_green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(base_red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big
                                                        
                                                        

def fill_color_sun2(pa, strengths, distance, cell_size, ref_size = (400,200)):
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = distance / np.sqrt(ref_size[0]**2 + ref_size[1]**2) #np.sqrt(300**2 + 300**2)
    
    base_blue = 240 - ( (240) * adjusted_strength * (1 - adjusted_distance)**2 )
    base_green = base_blue * .992157 * (1 - np.maximum(0, adjusted_distance - .28))**2 # blue / 1.113 as base; increased when near sun
    
    #base_red = np.zeros(base_blue.shape)
    #base_red[adjusted_distance > .5] = 40
    base_red = base_blue * (1 - np.absolute(adjusted_distance - .4))**3
    #base_red = base_blue * 2 * (np.maximum((adjusted_distance - .45), 0))
    # base_red[adjusted_distance <= .3] = base_blue[adjusted_distance <= .3] * .866071 * \
    #                                                     ( 1 - (adjusted_distance[adjusted_distance <= .3]/.3) )

    blue_big = np.repeat(np.repeat(base_blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(base_green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(base_red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big
    
    
def fill_ind_colors(pa, strengths, distance, cell_size, ref_size = (400,200)):
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = distance / np.sqrt(ref_size[0]**2 + ref_size[1]**2) #np.sqrt(300**2 + 300**2)
    
    #base_blue = 30 + ( 210 * (1 - adjusted_strength) * (1 - adjusted_distance)**2 )
    base_blue = 30 + ( 210 * (1 - adjusted_strength) * (1 - adjusted_distance)**2 * (np.absolute(.5 - adjusted_distance) / .5)**2 )
    
    base_green = 245 * (1 - adjusted_strength) * (1 - adjusted_distance)**2 * (np.absolute(.5 - adjusted_distance) / .5)**2
    base_red = 50 * (1 - adjusted_strength) * (1 - np.absolute(.55 - adjusted_distance))**7
    
    blue_big = np.repeat(np.repeat(base_blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(base_green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(base_red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big    
    
def fill_ind_red(pa, strengths, distance, cell_size, ref_size = (400,200)):
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = distance / np.sqrt(ref_size[0]**2 + ref_size[1]**2) #np.sqrt(300**2 + 300**2)

    base_blue = 230 * (1 - adjusted_strength) * (1 - adjusted_distance)**2 * ( np.minimum(.07,np.absolute(.52 - adjusted_distance)) / .07)
    
    base_green = 300 * (1 - adjusted_strength) * (.9 - adjusted_distance)**2 * ( np.minimum(.07,np.absolute(.58 - adjusted_distance)) / .07)
    # base_red = 60 * (1 - adjusted_strength) * (1 - np.absolute(.55 - adjusted_distance))**7
    base_red = 50 * (1 - adjusted_strength) * (1 - np.absolute(.55 - adjusted_distance))**7
    
    blue_big = np.repeat(np.repeat(base_blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(base_green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(base_red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big       
    
    
def fill_fluc_blue(pa, strengths, distance, cell_size, ref_size = (400,200)):
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = distance / np.sqrt(ref_size[0]**2 + ref_size[1]**2) #np.sqrt(300**2 + 300**2)
    
    base_blue = ( 60 * adjusted_distance**3 ) + 240 * (1 - adjusted_strength) * \
                (1 - adjusted_distance)**2 * ( np.minimum(.2, np.absolute(adjusted_distance - .6)) / .2 )
    
    base_green = 250 * (1 - adjusted_strength) * (1 - adjusted_distance)**2
    # base_red = np.maximum(0, 120 * np.sin(10 * adjusted_distance - 3.4) * (1 - adjusted_strength))
    base_red = 120 * ( 1 - np.minimum(.1, np.absolute(.55-adjusted_distance)) / .1 )
    
    blue_big = np.repeat(np.repeat(base_blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(base_green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(base_red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big      
    
    
def fill_parabola(pa, strengths, distance, cell_size, ref_size = (400,200)):
    adjusted_strength = np.arctan(strengths) / (np.pi/2)
    adjusted_distance = distance / np.sqrt(ref_size[0]**2 + ref_size[1]**2) #np.sqrt(300**2 + 300**2)
    
    base_blue = 60 * (1 - adjusted_strength) * (2 - adjusted_distance)**2 * ( np.minimum(.07, np.absolute(adjusted_distance - .52)) / .07 )
    
    base_green = 77 * (1 - adjusted_strength) * (1.8 - adjusted_distance)**2 * ( np.minimum(.07, np.absolute(adjusted_distance - .58)) / .07 )
    base_red = np.maximum(0,140 + -7000 * (.55-adjusted_distance)**2) * (1 - adjusted_strength)
    
    blue_big = np.repeat(np.repeat(base_blue, cell_size, axis = 1), cell_size, axis = 0) 
    green_big = np.repeat(np.repeat(base_green, cell_size, axis = 1), cell_size, axis = 0) 
    red_big = np.repeat(np.repeat(base_red, cell_size, axis = 1), cell_size, axis = 0) 
    
    pa[:,:,2] = blue_big    #(1 - dist_big / distance.max()) 
    pa[:,:,1] = green_big
    pa[:,:,0] = red_big