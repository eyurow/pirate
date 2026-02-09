import numpy as np
import pygame
import pygame.surfarray as sa

from UI.basics import Rectangle

from basics.generics import DBZ, get_margin
from basics.shapes import generate_patterned_line, generate_solid_line, generate_perpendicular_line, generate_compass, generate_arrow, generate_thick_circle
from basics.IndexArray import IndexArray
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
    def __init__(self, pos = (0,0), size = 'small', color = (100,100,100), border_color = (0,0,0), owner = None, 
                 text_color = (255,255,255), ship_color = (255,255,255), sail_color = (255,255,255), wind_arrow_color = (255,255,255), current_arrow_color = (255,255,255),
                 font = pygame.font.SysFont('chicago', size = 15), ship = None):
        if size == 'small':
            self.ship_length = 100
            self.line_thick = 2

        elif size == 'large':
            self.ship_length = 380
            self.line_thick = 4
        self.size = (self.ship_length*1.3, self.ship_length*1.3)
        self.pi_margin = get_margin(self.size[0], self.ship_length)
        super().__init__(pos, self.size, color, border_color, owner)
        self.text_color = text_color
        self.font = font
        self._ship = ship

    def draw(self):
        # super().draw(). TODO: add draw func for ui objects
        self.generate()


    def generate(self):
        ship = self.generate_ship()
        sail = self.generate_sail()
        wind_arrow = self.generate_wind_arrow()
        self.pixel_index = IndexArray.from_array(np.concatenate([ship, sail, wind_arrow], axis = 1))
        # TODO: self.rotate() before wind arrow

        # rezero to left-corner
        self.pixel_index.get_stats()
        x_min = self.pixel_index.xmin
        y_min = self.pixel_index.ymin
        self.pixel_index.offset((x_min, y_min))

        # get pa pos
        x_rng = self.pixel_index.xrng
        y_rng = self.pixel_index.yrng
        x_margin = get_margin(self.size[0], x_rng)
        y_margin = get_margin(self.size[1], y_rng)
        self.pixel_index.offset((self.pa_pos[0] + x_margin[0], self.pa_pos[1] + y_margin[1]))


    def generate_ship(self):
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

    def generate_sail(self):
        sail_length = (self._ship.main_sail.width / self._ship.hull_length) * self.ship_length
        sail_end = (round(np.cos(self._ship.main_sail.set) * sail_length * .65), round(np.sin(self._ship.main_sail.set) * sail_length * .65))
        curve_end = (round(sail_end[0] + np.cos(self._ship.main_sail.set + self._ship.main_sail.give) * sail_length * .15), 
                     round(sail_end[1] + np.sin(self._ship.main_sail.set + self._ship.main_sail.give) * sail_length * .15))
        sail = np.concatenate([generate_solid_line((0,0), sail_end, self.line_thick), 
                               generate_solid_line(sail_end, curve_end, self.line_thick)], axis = 1)
        return sail
        
    def generate_wind_arrow(self):
        wind = self._ship.APP_WIND
        wind_theta = np.arctan2(wind[1], wind[0])
        wind_str = np.sqrt(wind[1]**2 + wind[0]**2)

        line_start = (np.cos(wind_theta + np.pi) * (self.ship_length / 2) * 1.2, np.sin(wind_theta + np.pi) * (self.ship_length / 2) * 1.2)
        line_end = (np.cos(wind_theta + np.pi) * (self.ship_length / 2) * .8, np.sin(wind_theta + np.pi) * (self.ship_length / 2) * .8)
        wind_arrow = generate_arrow(line_start, line_end, 2, 7) # TODO pdate length/thickness of line based on strength
        return wind_arrow

    def generate_current_arrow(self):
        pass

    def recenter(self):
        self.pixel_index.offset()


class ZXDiagram:
    def __init__(self, pos = (0,0), size = 'small', color = (100,100,100), border_color = (0,0,0), owner = None, 
                 text_color = (255,255,255), ship_color = (255,255,255), sail_color = (255,255,255), wind_arrow_color = (255,255,255), current_arrow_color = (255,255,255),
                 font = pygame.font.SysFont('chicago', size = 15), ship = None):
        if size == 'small':
            self.hull_radius = 50
            self.line_thick = 2
        elif size == 'large':
            self.hull_radius = 190
            self.line_thick = 4
        self.size = (self.hull_radius*2*1.3, self.hull_radius*2*1.3)
        # self.pi_margin = get_margin(self.size[0], self.hull_radius * 2)
        super().__init__(pos, self.size, color, border_color, owner)
        self.text_color = text_color
        self.font = font
        self._ship = ship
        self.hull_offset = self.hull_radius/10
        self.generate_static_index()

    def generate(self):
        cob = self.generate_cob()
        self.pixel_index = IndexArray(np.concatenate([self.static_index, cob], axis = 1))
        self.pixel_index.rotate(self._ship.heeling_angle)

        # rezero to left-corner
        self.pixel_index.get_stats()
        x_min = self.pixel_index.xmin
        y_min = self.pixel_index.ymin
        self.pixel_index.offset((x_min, y_min))

        # get pa pos
        x_rng = self.pixel_index.xrng
        y_rng = self.pixel_index.yrng
        x_margin = get_margin(self.size[0], x_rng)
        y_margin = get_margin(self.size[1], y_rng)
        self.pixel_index.offset((self.pa_pos[0] + x_margin[0], self.pa_pos[1] + y_margin[1]))

    def generate_static_index(self):
        hull = self.generate_hull()
        mast = self.generate_mast()
        self.static_index = IndexArray(np.concatenate([hull, mast], axis = 1))

    def generate_hull(self):
        circle = generate_thick_circle(radius = self.hull_radius, thick = self.line_thick)
        hull = circle[:, circle[1] >= 0] # bottom half of circle
        hull_top = generate_perpendicular_line((-self.hull_radius, 0), (self.hull_radius, 0), self.line_thick) # top line of hull
    # TODO: generate_waterline = -radius * (ship.hull_waterline / ship.hull_height) # y-direction
    def generate_mast(self):
        mast_height = self.hull_radius * 1.3 #(ship.main_sail.height / ship.hull_height) * radius
        mast_l = generate_perpendicular_line((-self.hull_radius * .095, 0), (-self.hull_radius * .095, -mast_height), self.line_thick)
        mast_r = generate_perpendicular_line((self.hull_radius * .095, 0), (self.hull_radius * .095, -mast_height), self.line_thick) 
        pass
    def generate_cob(self):
        cob = ( self.hull_radius * (self._ship.cob[0] / self._ship.hull_height), self.hull_radius * (1 - (self._ship.cob[1] / self._ship.hull_height)) )
        cog = ( self.hull_radius * (self._ship.cog[0] / self._ship.hull_height), self.hull_radius * (1 - (self._ship.cog[1] / self._ship.hull_height)) )

        cob_idx = np.array(get_pixel_indices( ( np.array([cob[0] - (self.hull_radius * .04)], dtype = int),
                                                np.array([cob[1] - (self.hull_radius * .04)], dtype = int) ), 
                                            round(self.hull_radius * .04 * 2 )))
        
        cog_idx = np.array(get_pixel_indices( ( np.array([cog[0] - (self.hull_radius * .04)], dtype = int),
                                                np.array([cog[1] - (self.hull_radius * .04)], dtype = int) ), 
                                            round(self.hull_radius * .04 * 2 )))
        pass
    def generate_cog(self):
        pass
    def generate_wind_arrow(self):
        pass
    def generate_current_arrow(self):
        pass
