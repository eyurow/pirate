import numpy as np
import pygame.surfarray as sa

from algorithms.generics import get_margin
from algorithms.shapes import generate_line, generate_patterned_line, generate_perpendicular_line
from visuals.vis import *
from visuals.textures.ship_diagram import zx_diagram, xy_diagram

class Renderer:
    def __init__(self, screen, world, cell_size):
        self.screen = screen
        self.world = world
        self.PA = None
        self.PA_SIZE = (0,0)
        self.CELL_SIZE = cell_size
        self.WORLD_SLICER_X = slice(0, self.world.SIZE[0])
        self.WORLD_SLICER_Y = slice(0, self.world.SIZE[0])
        self.START_PIXEL_X = 0
        self.START_PIXEL_Y = 0
        self.pa_pos = (0,0)
        self.DRAW = pa_fill_color
        self.post = []

        self.refresh_PA()
        self.set_pixelarray()

    def refresh_PA(self):
        self.PA = sa.pixels3d(self.screen.WIN)
        self.screen.WIDTH, self.screen.HEIGHT = self.PA.shape[:2]

    def update_display(self):
        self.screen.update_display()
    
    def set_draw(self, func): # set world-current drawing function
        self.DRAW = func
    
    def draw_world(self):
        self.DRAW(self.PA, self.world.THETAS[self.WORLD_SLICER_X, self.WORLD_SLICER_Y, 1], self.world.DISTANCE_FROM_SUN[self.WORLD_SLICER_X, self.WORLD_SLICER_Y], self.CELL_SIZE, self.world.SIZE)
        draw_land(self.PA, self.world.LAND, self.CELL_SIZE, (self.WORLD_SLICER_X, self.WORLD_SLICER_Y))
        draw_sun(self.PA, self.world.SUN, self.CELL_SIZE, (self.WORLD_SLICER_X, self.WORLD_SLICER_Y))
        # self.update_display()

    def draw_post(self):
        for item in self.post:
            func = item[0]
            func(*item[1:])


    def draw_menu(self, menu):
        # screen_blur(PA)
        self.PA[menu.left_marg:menu.right_marg, menu.top_marg:menu.bot_marg] = (166, 93, 7)
        self.PA[menu.left_marg, menu.top_marg:menu.bot_marg] = (0,0,0)
        self.PA[menu.right_marg, menu.top_marg:menu.bot_marg] = (0,0,0)
        self.PA[menu.left_marg:menu.right_marg, menu.top_marg] = (0,0,0)
        self.PA[menu.left_marg:menu.right_marg, menu.bot_marg] = (0,0,0)

    def draw_button(self, button, menu_pos = (0,0)):
        self.draw_rectangle(button)
        if button.text:
            self.PA[(button.pa_pos[0] + button.text_ind[0], button.pa_pos[1] + button.text_ind[1])] = button.text_color

    def draw_particles(self, particles):
        draw_particles(self.PA, particles, self.PA_SIZE, self.CELL_SIZE, (self.WORLD_SLICER_X, self.WORLD_SLICER_Y), (self.START_PIXEL_X, self.START_PIXEL_Y))

    def draw_ship(self, ship):
        draw_ship(self.PA, ship, self.PA_SIZE, self.CELL_SIZE, (self.WORLD_SLICER_X, self.WORLD_SLICER_Y), (self.START_PIXEL_X, self.START_PIXEL_Y))


    def draw_rectangle(self, rect):
        if rect.color:
            self.PA[rect.pa_pos[0]:rect.pa_pos[0] + rect.size[0], rect.pa_pos[1]:rect.pa_pos[1] + rect.size[1]] = rect.color
        if rect.border_color:
            self.PA[rect.pa_pos[0], rect.pa_pos[1]:rect.pa_pos[1] + rect.size[1]] = rect.border_color
            self.PA[rect.pa_pos[0] + rect.size[0], rect.pa_pos[1]:rect.pa_pos[1] + rect.size[1]] = rect.border_color
            self.PA[rect.pa_pos[0]:rect.pa_pos[0] + rect.size[0], rect.pa_pos[1]] = rect.border_color
            self.PA[rect.pa_pos[0]:rect.pa_pos[0] + rect.size[0], rect.pa_pos[1] + rect.size[1]] = rect.border_color

    def draw_info_box(self, info_box):
        self.draw_rectangle(info_box)

        row = 4
        for info in [info_box.xcurrents_text, info_box.ycurrents_text, info_box.xwinds_text, info_box.ywinds_text]:
            idx = np.where(info == 1)
            adjusted = (idx[0] + info_box.pa_pos[0] + 5, idx[1] + info_box.pa_pos[1] + row)
            self.PA[adjusted] = info_box.text_color
            row += 15

        row = 10
        for info in [info_box.r_text, info_box.g_text, info_box.b_text]:
            idx = np.where(info == 1)
            adjusted = (idx[0] + info_box.pa_pos[0] + 95, idx[1] + info_box.pa_pos[1] + row)
            self.PA[adjusted] = info_box.text_color
            row += 15

        idx = info_box.currents_compass
        adjusted = (idx[0] + info_box.pa_pos[0], idx[1] + info_box.pa_pos[1])
        self.PA[adjusted] = (0,0,0)

        idx = info_box.current_line
        adjusted = (idx[0] + info_box.pa_pos[0], idx[1] + info_box.pa_pos[1])
        self.PA[adjusted] = (50,150,175)

    def draw_ship_zx_diagram(self, ship):
        x_range, y_range, zx_diag = zx_diagram(ship, 'small')
        start_x = x_range[0] + self.PA_SIZE[0] - (x_range[1] * 2) - (10 * 2) # two diagrams from bottom right corner, 10 pix buffer
        start_y = y_range[0] + self.PA_SIZE[1] - y_range[1] - 10
       
        print(self.PA_SIZE)        
        print(x_range, y_range)
        print(zx_diag[0].min(), zx_diag[0].max())
        print(zx_diag[1].min(), zx_diag[1].max())

        self.PA[start_x:start_x + x_range[1],start_y:start_y + y_range[1]] = (0,0,0)
        self.PA[(zx_diag[0] + start_x, zx_diag[1] + start_y)] = (255,255,255)

    def draw_ship_xy_diagram(self, ship):
        x_range, y_range, xy_diag = xy_diagram(ship, 'small')
        start_x = x_range[0] + self.PA_SIZE[0] - x_range[1] - 10 # one diagram from bottom right corner, 10 pix buffer
        start_y = y_range[0] + self.PA_SIZE[1] - y_range[1] - 10

        self.PA[start_x:start_x + x_range[1],start_y:start_y + y_range[1]] = (0,0,0)
        self.PA[(xy_diag[0] + start_x, xy_diag[1] + start_y)] = (255,255,255)


    def draw_line(self, p1, p2, thick, thick_quotient = .5, thick_offset = -1, num_lines = 1, even_offset = 0, color = (0,0,0)):
        line = generate_line(p1, p2, thick, thick_quotient, thick_offset, num_lines, even_offset)
        self.PA[tuple(line)] = color
    def draw_perp_line(self, p1, p2, thick, color = (0,0,0)):
        line = generate_perpendicular_line(p1, p2, thick)
        self.PA[tuple(line)] = color
    def draw_patterned_line(self, p1, p2, thick, color = (0,0,0)):
        line = generate_patterned_line(p1, p2, thick)
        self.PA[tuple(line)] = color
    
    def add_post(self, func, *args):
        self.post.append((func, *args))

    def clear_post(self):
        self.post = []

    
    def set_pixelarray(self):
        if self.screen.WIDTH > self.world.SIZE[0] * self.CELL_SIZE:
            start, end = get_margin(self.screen.WIDTH, self.world.SIZE[0] * self.CELL_SIZE)
            self.PA[:start] = (0,0,0)
            self.PA[-end:] = (0,0,0)
            self.PA = self.PA[start:-end]
            self.START_PIXEL_X = start
            self.WORLD_SLICER_X = slice(0, self.world.SIZE[0])
        elif self.screen.WIDTH < self.world.SIZE[0] * self.CELL_SIZE:
            # get WORLD slicer
            start, end = get_margin(self.world.SIZE[0], self.screen.WIDTH // self.CELL_SIZE)
            self.WORLD_SLICER_X = slice(start, self.world.SIZE[0] - end)
            # get pixel slicer
            if self.screen.WIDTH > self.CELL_SIZE * (self.world.SIZE[0] - start - end): # if screen WIDTH greater than sliced WORLD size
                start, end = get_margin(self.screen.WIDTH, self.CELL_SIZE * (self.world.SIZE[0] - start - end))
                self.PA[:start] = (0,0,0)
                self.PA[-end:] = (0,0,0)
                self.PA = self.PA[start:-end]
                self.START_PIXEL_X = start
        elif self.screen.WIDTH == self.world.SIZE[0] * self.CELL_SIZE:
            self.START_PIXEL_X = 0
            self.WORLD_SLICER_X = slice(0, self.world.SIZE[0])
        
        if self.screen.HEIGHT > self.world.SIZE[1] * self.CELL_SIZE:
            start, end = get_margin(self.screen.HEIGHT, self.world.SIZE[1] * self.CELL_SIZE)
            self.PA[:, :start] = (0,0,0)
            self.PA[:, -end:] = (0,0,0)
            self.PA = self.PA[:, start:-end]
            self.START_PIXEL_Y = start
            self.WORLD_SLICER_Y = slice(0, self.world.SIZE[1])
        elif self.screen.HEIGHT < self.world.SIZE[1] * self.CELL_SIZE:
            # get WORLD slicer
            start, end = get_margin(self.world.SIZE[1], self.screen.HEIGHT // self.CELL_SIZE)
            self.WORLD_SLICER_Y = slice(start, self.world.SIZE[1] - end)
            # get pixel slicer
            if self.screen.HEIGHT > self.CELL_SIZE * (self.world.SIZE[1] - start - end): # if screen WIDTH greater than sliced WORLD size
                start, end = get_margin(self.screen.HEIGHT, self.CELL_SIZE * (self.world.SIZE[1] - start - end))
                self.PA[:, :start] = (0,0,0)
                self.PA[:, -end:] = (0,0,0)
                self.PA = self.PA[:, start:-end]
                self.START_PIXEL_Y = start
        elif self.screen.HEIGHT == self.world.SIZE[1] * self.CELL_SIZE:
            self.START_PIXEL_Y = 0
            self.WORLD_SLICER_Y = slice(0, self.world.SIZE[1])

        self.PA_SIZE = self.PA.shape[:2]

