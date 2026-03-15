import numpy as np
import pygame

from UI.basics import Context
from UI.esc_menu import EscapeMenu
from UI.live import InfoBox, XYDiagram, ZYDiagram


class UserInterface:
    def __init__(self, world, ship):
        self.renderer = None # defined at renderer init
        self.input_handler = None # defined at inp_handler init
        self.world = world
        self.ship = ship

        self.pa_pos = (0,0)

        # self.key_context.register_key(pygame.K_ESCAPE, self.open_escape_menu)
        # self.key_context.register_key(pygame.K_SPACE, self.pause)

    # @property
    # def key_context(self):
    #     return self.context.key_context

    @property
    def PA_SIZE(self):
        return self.renderer.PA_SIZE
    
    def generate_components(self, settings = None): # do this after UI is registered with renderer
        self.ESC_MENU = EscapeMenu(owner = self, pos = ((self.PA_SIZE[0] - 1000)//2, (self.PA_SIZE[1] - 550)//2))
        self.info_box = InfoBox(owner = self.renderer)
        self.XYDiagram = XYDiagram(owner = self.renderer, pos = (self.PA_SIZE[0] - 130 - 10, self.PA_SIZE[1] - 130 - 10), size = 'small', ship = self.ship)
        self.ZYDiagram = ZYDiagram(owner = self.renderer, pos = (self.PA_SIZE[0] - 260 - 20, self.PA_SIZE[1] - 130 - 10), size = 'small', color = (0,0,0), ship = self.ship)

    def resize(self):
        pass
        #TODO: regenerate all components with new size/layout after screen resize
        self.ESC_MENU.generate(pos = ((self.PA_SIZE[0] - 1000)//2, (self.PA_SIZE[1] - 550)//2))   

    def open_escape_menu(self):
        pass
        self.ESC_MENU.display()
        self.input_handler._context = self.ESC_MENU.context

        
    def close_escape_menu(self):
        pass
        self.input_handler._context = self.input_handler.live_context
        pass

    def pause(self):
        pass