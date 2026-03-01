import numpy as np
import pygame
import pygame.surfarray as sa

from UI.basics import Rectangle

from basics.generics import DBZ, get_margin
from basics.shapes import generate_patterned_line, generate_solid_line, generate_perpendicular_line, generate_compass, generate_arrow, generate_thick_circle
from basics.IndexArray import IndexArray, PixelIndex
from basics.indices import get_pixel_indices




class InfoBox(Rectangle):
    def __init__(self, pos = (0,0), size = (170,62), color = (100,100,100), border_color = (0,0,0), owner = None, text_color = (255,255,255), font = pygame.font.SysFont('chicago', size = 15)):
        super().__init__(pos, size, color, border_color, owner)
        self.text_color = text_color
        self.font = font
        self.currents_compass = generate_compass(radius = 13, offset = (20,25))
        # self.generate()

    def generate_info(self, current_x, current_y, winds_x, winds_y, r, g, b):
        self.xcurrents_text = sa.pixels2d(self.font.render(f'CURRENTS: {current_x:.2f}', 0, self.text_color))
        self.ycurrents_text = sa.pixels2d(self.font.render(f'          {current_y:.2f}', 0, self.text_color))
        self.xwinds_text = sa.pixels2d(self.font.render(   f'WINDS:    {winds_x:.2f}', 0, self.text_color))
        self.ywinds_text = sa.pixels2d(self.font.render(   f'          {winds_y:.2f}', 0, self.text_color))
        self.r_text = sa.pixels2d(self.font.render(        f'RED:      {r}', 0, self.text_color))
        self.g_text = sa.pixels2d(self.font.render(        f'GREEEN:   {g}', 0, self.text_color))
        self.b_text = sa.pixels2d(self.font.render(        f'BLUE:     {b}', 0, self.text_color))

        current_str = np.sqrt(current_y**2 + current_x**2)
        adjusted_curr_str = np.arctan(current_str) / (np.pi/2)
        current_line_len = 13 * adjusted_curr_str
        current_point = (round(20 + DBZ(current_x, current_str) * current_line_len), round(25 - DBZ(current_y, current_str) * current_line_len))
        self.current_line = generate_patterned_line((20,25), current_point, thick = 5)
        # self.current_arrow

        # return xcurrents_text, ycurrents_text, xwinds_text, ywinds_text, r_text, g_text, b_text



class XYDiagram(Rectangle):
    def __init__(self, pos = (0,0), size = 'small', color = (150,150,150), border_color = (0,0,0), owner = None, 
                 text_color = (255,255,255), ship_color = (61,31,6), sail_color = (255,255,255), 
                 sail_force_color = (216,58,222), keel_force_color = (58,222,112), wind_arrow_color = (222,222,58), current_arrow_color = (58,222,216),
                 font = pygame.font.SysFont('chicago', size = 15), ship = None):
        if size == 'small':
            self.ship_length = 100
            self.line_thick = 2

        elif size == 'large':
            self.ship_length = 380
            self.line_thick = 4
        self.size = (int(self.ship_length*1.3), int(self.ship_length*1.3))

        super().__init__(pos, self.size, color, border_color, owner) # rectangle initial generate
        self.x_min = self.pa_pos[0]; self.x_max = self.pa_pos[0] + self.size[0]
        self.y_min = self.pa_pos[1]; self.y_max = self.pa_pos[1] + self.size[1]
        self.mid_x = self.x_min + ( (self.x_max - self.x_min) // 2); self.mid_y = self.y_min + ( (self.y_max - self.y_min) // 2) # for preplaced PixelIndexes

        self.text_color = text_color
        self.font = font
        self.ship_color = ship_color
        self.sail_color = sail_color
        self.wind_arrow_color = wind_arrow_color
        self.current_arrow_color = current_arrow_color
        self.sail_force_color = sail_force_color
        self.keel_force_color = keel_force_color

        self._ship = ship


    def generate_static(self):
        ship = self.generate_ship()
        sail = self.generate_sail()
        wind_arrow = self.generate_wind_arrow()
        sail_force_arrow = self.generate_sail_force_arrow()
        self.pixel_index = IndexArray(np.concatenate([ship, sail, wind_arrow, sail_force_arrow], axis = 1))
        # TODO: self.rotate() before wind arrow

        # rezero to left-corner
        x_min, x_max, y_min, y_max, mid_x, mid_y, x_rng, y_rng = self.pixel_index.get_stats()
        # xmin = self.pixel_index.xmin
        # ymin = self.pixel_index.ymin
        self.pixel_index.offset((-x_min, -y_min))

        # get pa pos
        x_margin = get_margin(self.size[0], x_rng)
        y_margin = get_margin(self.size[1], y_rng)
        self.pixel_index.offset((self.pa_pos[0] + x_margin[0], self.pa_pos[1] + y_margin[0]))

    def generate_abs(self):
        self.ship = self.generate_ship_abs_heading()
        self.sail = self.generate_sail_abs_heading()
        self.wind_arrow = self.generate_wind_arrow()
        self.current_arrow = self.generate_current_arrow()
        self.sail_force_arrow = self.generate_sail_force_arrow()
        self.keel_force_arrow = self.generate_keel_force_arrow()
        # self.pixel_index = IndexArray(np.concatenate([self.ship, self.sail, self.wind_arrow, 
        #                                               self.current_arrow, self.sail_force_arrow, self.keel_force_arrow], axis = 1))

        ## rezero to middle of rectangle
        # x_min = self.pa_pos[0]; x_max = self.pa_pos[0] + self.size[0]
        # y_min = self.pa_pos[1]; y_max = self.pa_pos[1] + self.size[1]

        # mid_x = x_min + ( (x_max - x_min) // 2); mid_y = y_min + ( (y_max - y_min) // 2)
        # self.pixel_index.offset((mid_x, mid_y))
        # self.pixel_index.trim(x_min, x_max, y_min, y_max)

    
    def draw(self, renderer):
        renderer.draw_rectangle(self)
        renderer.draw_pixel_index(self.ship)
        renderer.draw_pixel_index(self.sail)
        renderer.draw_pixel_index(self.wind_arrow)
        renderer.draw_pixel_index(self.current_arrow)
        renderer.draw_pixel_index(self.sail_force_arrow)
        renderer.draw_pixel_index(self.keel_force_arrow)


    def generate_ship(self): #static
        width = (self._ship.hull_width / self._ship.hull_length) * self.ship_length # TODO: precalc this given ship? or set to standard
        bow_point = (round(self.ship_length/2), 0)
        port_point = (0, round(width/2))
        starboard_point = (0, round(-width/2))
        stern_point = (round(-self.ship_length/2), 0)

        boat = np.concatenate([generate_solid_line(bow_point, port_point, self.line_thick), 
                               generate_solid_line(port_point, stern_point, self.line_thick),
                               generate_solid_line(stern_point, starboard_point, self.line_thick),
                               generate_solid_line(starboard_point, bow_point, self.line_thick)], axis = 1)

        boat[0, boat[0] < -self.ship_length/2 * .8] = -self.ship_length/2 * .8 # cut off a bit from stern

        return boat
    
    def generate_ship_abs_heading(self):
        width = (self._ship.hull_width / self._ship.hull_length) * self.ship_length / 2 # TODO: precalc this given ship? or set to standard
        length = self.ship_length/2
        heading_x = np.cos(self._ship.heading)
        heading_y = -np.sin(self._ship.heading)

        bow_point = (heading_x * length, heading_y * length)
        stern_point = (-heading_x * length, -heading_y * length)
        port_point = (-heading_y * width, heading_x * width)
        starboard_point = (heading_y * width, -heading_x * width)

        stern = np.concatenate([generate_solid_line(stern_point, starboard_point, self.line_thick + 2), generate_solid_line(port_point, stern_point, self.line_thick + 2)], axis = 1)
        lens = np.sqrt(stern[0]**2 + stern[1]**2)
        excess = lens > length * .8
        thetas = np.arctan2(stern[1], stern[0])
        stern[:, excess] = (np.cos(thetas[excess]) * length * .8, np.sin(thetas[excess]) * length * .8)

        boat = PixelIndex(np.concatenate([generate_solid_line(bow_point, port_point, self.line_thick + 2), 
                                          stern,
                                          generate_solid_line(starboard_point, bow_point, self.line_thick + 2)], axis = 1),
                          color = self.ship_color)
        boat.offset((self.mid_x, self.mid_y))
        boat.trim(self.x_min, self.x_max, self.y_min, self.y_max)

        return boat

    def generate_sail(self):
        sail_length = (self._ship.main_sail.length / self._ship.hull_length) * self.ship_length
        sail_end = (round(np.cos(self._ship.main_sail.set) * sail_length * .65), round(np.sin(-self._ship.main_sail.set) * sail_length * .65))
        curve_end = (round(sail_end[0] - np.cos(self._ship.main_sail.set - self._ship.main_sail.give) * sail_length * .15), 
                     round(sail_end[1] - np.sin(self._ship.main_sail.set - self._ship.main_sail.give) * sail_length * .15))
        sail = PixelIndex(np.concatenate([generate_solid_line((0,0), sail_end, self.line_thick), 
                                          generate_solid_line(sail_end, curve_end, self.line_thick)], axis = 1),
                          color = self.sail_color)
        
        sail.offset((self.mid_x, self.mid_y))
        sail.trim(self.x_min, self.x_max, self.y_min, self.y_max)
        return sail
    
    def generate_sail_abs_heading(self):
        sail_length = (self._ship.main_sail.length / self._ship.hull_length) * self.ship_length
        sail_end = (round(np.cos(self._ship.heading + self._ship.main_sail.set) * sail_length * .65), round(-np.sin(self._ship.heading + self._ship.main_sail.set) * sail_length * .65))
        curve_end = (round(sail_end[0] + np.cos(self._ship.heading + self._ship.main_sail.set + self._ship.main_sail.give) * sail_length * .15), 
                     round(sail_end[1] - np.sin(self._ship.heading + self._ship.main_sail.set + self._ship.main_sail.give) * sail_length * .15))
        
        sail = PixelIndex(np.concatenate([generate_solid_line((0,0), sail_end, self.line_thick), 
                                          generate_solid_line(sail_end, curve_end, self.line_thick)], axis = 1),
                          color = self.sail_color)
        sail.offset((self.mid_x, self.mid_y))
        sail.trim(self.x_min, self.x_max, self.y_min, self.y_max)
        return sail
        
    def generate_wind_arrow(self):
        wind = self._ship.APP_WIND
        wind_theta = np.arctan2(wind[1], wind[0])
        wind_str = np.sqrt(wind[1]**2 + wind[0]**2)

        line_start = (-np.cos(wind_theta) * (self.ship_length / 2) * 1.2, np.sin(wind_theta) * (self.ship_length / 2) * 1.2)
        line_end = (-np.cos(wind_theta) * (self.ship_length / 2) * .8, np.sin(wind_theta) * (self.ship_length / 2) * .8)
        arrow = PixelIndex(generate_arrow(line_start, line_end, 2, 7), color = self.wind_arrow_color)

        arrow.offset((self.mid_x, self.mid_y))
        arrow.trim(self.x_min, self.x_max, self.y_min, self.y_max)
        return arrow

    def generate_current_arrow(self):
        current = self._ship.APP_CURR
        curr_theta = np.arctan2(current[1], current[0])
        curr_str = np.sqrt(current[1]**2 + current[0]**2)

        line_start = (-np.cos(curr_theta) * (self.ship_length / 2) * 1.2, np.sin(curr_theta) * (self.ship_length / 2) * 1.2)
        line_end = (-np.cos(curr_theta) * (self.ship_length / 2) * .8, np.sin(curr_theta) * (self.ship_length / 2) * .8)
        arrow = PixelIndex(generate_arrow(line_start, line_end, 2, 7), color = self.current_arrow_color)

        arrow.offset((self.mid_x, self.mid_y))
        arrow.trim(self.x_min, self.x_max, self.y_min, self.y_max)
        return arrow

    def generate_sail_force_arrow(self):
        theta = np.arctan2(self._ship.main_sail.y, self._ship.main_sail.x)
        mag = np.sqrt(self._ship.main_sail.y**2 +  self._ship.main_sail.x**2)

        line_len = min( int(self.ship_length/2), max( int(self.ship_length/4), int(np.sqrt(mag)) ))
        line_thick = min( int(self.line_thick*4), max( self.line_thick, round(np.sqrt(mag) - line_len * 8) ))
        head_thick = min( int(self.line_thick*9), max( int(self.line_thick*2.5), round(np.log(mag + 1)) )) 

        line_end = ( np.cos(theta) * line_len, 
                    -np.sin(theta) * line_len ) 
        
        arrow = PixelIndex(generate_arrow((0,0), line_end, line_thick, head_thick), color = self.sail_force_color)
        arrow.offset((self.mid_x, self.mid_y))
        arrow.trim(self.x_min, self.x_max, self.y_min, self.y_max)
        return arrow
    
    def generate_keel_force_arrow(self):
        theta = np.arctan2(self._ship.keel.y, self._ship.keel.x)
        mag = np.sqrt(self._ship.keel.y**2 + self._ship.keel.x**2)

        line_len = min( int(self.ship_length/2), max( int(self.ship_length/4), int(np.sqrt(mag)) ))
        line_thick = min( int(self.line_thick*4), max( self.line_thick, round(np.sqrt(mag) - line_len * 8) ))
        head_thick = min( int(self.line_thick*9), max( int(self.line_thick*2.5), round(np.log(mag + 1)) )) 

        line_end = ( np.cos(theta) * line_len, 
                    -np.sin(theta) * line_len ) 
        
        arrow = PixelIndex(generate_arrow((0,0), line_end, line_thick, head_thick), color = self.keel_force_color)
        arrow.offset((self.mid_x, self.mid_y))
        arrow.trim(self.x_min, self.x_max, self.y_min, self.y_max)
        return arrow
    



class ZYDiagram(Rectangle):
    def __init__(self, pos = (0,0), size = 'small', color = (100,100,100), border_color = (0,0,0), owner = None, 
                 text_color = (255,255,255), ship_color = (255,255,255), sail_color = (255,255,255), wind_arrow_color = (255,255,255), current_arrow_color = (255,255,255),
                 font = pygame.font.SysFont('chicago', size = 15), ship = None):
        if size == 'small':
            self.hull_radius = 50
            self.line_thick = 2
        elif size == 'large':
            self.hull_radius = 190
            self.line_thick = 4
        self.size = (round(self.hull_radius*2*1.3), round(self.hull_radius*2*1.3))
        # self.pi_margin = get_margin(self.size[0], self.hull_radius * 2)
        super().__init__(pos, self.size, color, border_color, owner)
        self.text_color = text_color
        self.font = font
        self.ship_color = ship_color
        self.sail_color = sail_color
        self.wind_arrow_color = wind_arrow_color
        self.current_arrow_color = current_arrow_color

        self._ship = ship
        self.hull_offset = self.hull_radius/10
        self.generate_static_index()
        

    def generate_index(self):
        cob = self.generate_cob()
        self.pixel_index = IndexArray(np.concatenate([self.static_index, cob], axis = 1), rounding = np.round)
        self.pixel_index.rotate_around(-self._ship.heeling_angle, (self.cog[0], self.cog[1])) # self.pixel_index.rotate(self._ship.heeling_angle)
        # print('Class: ', self.static_index)

        ## rezero to middle of rectangle
        x_min = self.pa_pos[0]; x_max = self.pa_pos[0] + self.size[0]
        y_min = self.pa_pos[1]; y_max = self.pa_pos[1] + self.size[1]

        mid_x = x_min + ( (x_max - x_min) // 2); mid_y = y_min + ( (y_max - y_min) // 2)
        self.pixel_index.offset((mid_x, mid_y + round(self.cog[1]) + 5))
        self.pixel_index.trim(x_min, x_max, y_min, y_max)

    def generate_static_index(self):
        hull = self.generate_hull()
        mast = self.generate_mast()
        cog, cog_idx = self.generate_cog()
        self.cog = cog
        self.static_index = IndexArray(np.concatenate([hull, mast, cog_idx], axis = 1))

    def reset_cog(self):
        cog, cog_idx = self.generate_cog()
        self.cog = cog
        self.static_index[:,-cog_idx.shape[1]:] = cog_idx

    def generate_hull(self):
        circle = generate_thick_circle(radius = self.hull_radius, thick = self.line_thick)
        hull = circle[:, circle[1] >= 0] # bottom half of circle
        hull_top = generate_perpendicular_line((-self.hull_radius, 0), (self.hull_radius, 0), self.line_thick) # top line of hull
        return np.concatenate([hull, hull_top], axis = 1)
    # TODO: generate_waterline = -radius * (ship.hull_waterline / ship.hull_height) # y-direction

    def generate_mast(self):
        mast_height = self.hull_radius * 1.3 #(ship.main_sail.height / ship.hull_height) * radius
        mast_l = generate_perpendicular_line((-self.hull_radius * .095, 0), (-self.hull_radius * .095, -mast_height), self.line_thick)
        mast_r = generate_perpendicular_line((self.hull_radius * .095, 0), (self.hull_radius * .095, -mast_height), self.line_thick) 
        return np.concatenate([mast_l, mast_r], axis = 1)
    
    def generate_cob(self):
        cob = ( self.hull_radius * (-self._ship.cob[1] / self._ship.hull_height), self.hull_radius * (-self._ship.cob[2] / self._ship.hull_height) ) 

        cob_idx = np.array(get_pixel_indices( ( np.array([cob[0] - (self.hull_radius * .04)], dtype = int),
                                                np.array([cob[1] - (self.hull_radius * .04)], dtype = int) ), 
                                            round(self.hull_radius * .04 * 2 )))
        return cob_idx

    def generate_cog(self):
        cog = ( self.hull_radius * (-self._ship.cog[1] / self._ship.hull_height), self.hull_radius * (-self._ship.cog[2] / self._ship.hull_height) ) 
        cog_idx = np.array(get_pixel_indices( ( np.array([cog[0] - (self.hull_radius * .04)], dtype = int),
                                                np.array([cog[1] - (self.hull_radius * .04)], dtype = int) ), 
                                    round(self.hull_radius * .04 * 2 )))
        return cog, cog_idx
    
    def generate_wind_arrow(self):
        pass
    def generate_current_arrow(self):
        pass
