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

        self.context = Context(self)

    @property
    def PA_SIZE(self):
        return self.renderer.PA_SIZE
    
    def generate_components(self):
        self.ESC_MENU = EscapeMenu(owner = self.renderer, pos = ((self.PA_SIZE[0] - 1000)//2, (self.PA_SIZE[1] - 550)//2))
        self.info_box = InfoBox(owner = self.renderer)
        self.XYDiagram = XYDiagram(owner = self.renderer, pos = (self.PA_SIZE[0] - 130 - 10, self.PA_SIZE[1] - 130 - 10), size = 'small', ship = self.ship)
        self.ZYDiagram = ZYDiagram(owner = self.renderer, pos = (self.PA_SIZE[0] - 260 - 20, self.PA_SIZE[1] - 130 - 10), size = 'small', color = (0,0,0), ship = self.ship)