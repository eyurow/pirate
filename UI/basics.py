import numpy as np
import pygame
import pygame.surfarray as sa

from basics.generics import get_margin



class Context:
    def __init__(self, owner, run_func):
        self.owner = owner
        self.run_func = run_func

        self.button_context = PositionContext(owner) # for UI Buttons
        self.hover_context = PositionContext(owner) # mouse hover
        self.key_context = KeyContext(owner) # keyboard keys
        self.lmb_context = PositionContext(owner)
        self.rmb_context = PositionContext(owner)
        self.event_context = KeyContext(owner) # pygame special events (QUIT, RESIZE)

    def store_base(self):
        self.button_context.store_base()
        self.hover_context.store_base()
        self.key_context.store_base()
        self.lmb_context.store_base()
        self.rmb_context.store_base()
        self.event_context.store_base()
    def restore_base(self):
        self.button_context.restore_base()
        self.hover_context.restore_base()
        self.key_context.restore_base()
        self.lmb_context.restore_base()
        self.rmb_context.restore_base()
        self.event_context.restore_base()

    def check_input(self, event):
        if event.type in [pygame.QUIT, pygame.VIDEORESIZE, pygame.VIDEOEXPOSE]:
            self.event_context.check(inp)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.lmb_context.check(event)
        

class BaseContext:
    def __init__(self, owner):
        self.owner = owner
        self.reset()
        self.map_size = 0

    def __str__(self):
        return f"map: {self.map}, base: {self.base}, key: {self.key}, idx: {self.key_idx}, active: {self.active}"
    
    def reset(self):
        self.map = np.zeros((self.map_size,0), dtype = int) # top-left (idx 0,1) and bottom-right (2,3) corner of component and component id (4)
        self.base = np.zeros((self.map_size,0), dtype = int) # base layer of map - to be recovered when overlays deactivate
        self.key = {}
        self.key_idx = 0
        self.base_idx = 0
        self.active = []
    
    def store_base(self):
        self.base = self.map.copy()
        self.base_idx = self.key_idx

    def restore_base(self):
        self.map = self.base.copy()
        self.key_idx = self.base_idx
        self.active = []

    
        

class PositionContext: # For button and hover maps
    def __init__(self, owner):
        self.owner = owner
        self.map_size = 5
        self.reset()

    def __str__(self):
        return f"map: {self.map}, base: {self.base}, key: {self.key}, idx: {self.key_idx}, active: {self.active}"
        
    def reset(self):
        self.map = np.zeros((5,0), dtype = int) # top-left (idx 0,1) and bottom-right (2,3) corner of component and component id (4)
        self.base = np.zeros((5,0), dtype = int) # base layer of map - to be recovered when overlays deactivate
        self.key = {}
        self.key_idx = 0
        self.base_idx = 0
        self.active = []

    def store_base(self):
        self.base = self.map.copy()
        self.base_idx = self.key_idx

    def restore_base(self):
        self.map = self.base.copy()
        self.key_idx = self.base_idx
        self.active = []

    def register_func(self, pos, size, func):
        add = np.zeros((5, 1), dtype = int)
        add[0] = pos[0]
        add[1] = pos[1]
        add[2] = pos[0] + size[0]
        add[3] = pos[1] + size[1]
        add[4] = self.key_idx

        self.map = np.concatenate([add, self.map], axis = 1)
        self.key[self.key_idx] = func

        self.key_idx += 1

    def register_component(self, component):
        # add top-left (idx 0,1) and bottom-right (2,3) corners of rectangle (button, dropdown) and id (4)
        # Most recently registered component at front of list

        add = np.zeros((5, 1), dtype = int)
        add[0] = component.pa_pos[0]
        add[1] = component.pa_pos[1]
        add[2] = component.pa_pos[0] + component.size[0]
        add[3] = component.pa_pos[1] + component.size[1]
        add[4] = self.key_idx

        self.map = np.concatenate([add, self.map], axis = 1)
        self.key[self.key_idx] = component
        component.register_context(self.key_idx)

        self.key_idx += 1

    def register_null(self, func):
        self.null = func

    def overlay(self, context):
        self.map = context.map
        self.key_idx = context.key_index

class KeyContext:
    def __init__(self, owner):
        self.owner = owner
        self.reset()

    def __str__(self):
        return f"map: {self.map}, base: {self.base}, active: {self.active}"
        
    def reset(self):
        self.map = {} # key: function
        self.base = {}
        self.active = []

    def store_base(self):
        self.base = self.map.copy()

    def restore_base(self):
        self.map = self.base.copy()
        self.active = []

    def register(self, key, func):
        self.map[key] = func

    def register_null(self, func):
        self.null = func

    def overlay(self, context):
        self.map = context.map




class Rectangle:
    def __init__(self, pos = (0,0), size = (10,10), color = (100,100,100), border_color = (0,0,0), owner = None):
        self.pos = pos # position relative to container 
        self.size = size
        self.color = color
        self.border_color = border_color
        self.owner = owner # pointer to container, e.g. EscapeMenu
        if owner:
            self.pa_pos = (self.owner.pa_pos[0] + self.pos[0], self.owner.pa_pos[1] + self.pos[1]) # absolute position within PA
        else:
            self.pa_pos = (self.pos[0], self.pos[1])
        # self.generate()

    @property
    def renderer(self):
        return self.owner.renderer

    def generate(self, pos = None, size = None):
        # self.size = new_size
        # TODO: reset pa_pos
        if pos:
            self.pos = pos
        if size:
            self.size = size
        self.pa_pos = (self.owner.pa_pos[0] + self.pos[0], self.owner.pa_pos[1] + self.pos[1])



class Button(Rectangle):
    def __init__(self, text, pos, size, color = None, border_color = None, owner = None, text_color = (0,0,0), font = pygame.font.SysFont('chicago', size = 30), context_type = 'base'):
        super().__init__(pos, size, color, border_color, owner)
        self.text = text
        self.text_color = text_color
        self.font = font
        self.context_type = context_type
        self.b_context_key = None
        self.h_context_key = None

    @property
    def context(self):
        return self.owner.context.button_context
    @property
    def hover_context(self):
        return self.owner.context.hover_context

    def generate(self, **kwargs):
        super().generate(**kwargs)
        if self.text:
            self.generate_text()

    def generate_text(self):
        # Set text index tuple and offset
        text = self.font.render(self.text, 0, (0,0,0))
        pix = sa.pixels2d(text)
        ind = np.where(pix == 1)

        text_size = pix.shape
        w_start, w_end = get_margin(self.size[0], text_size[0])
        h_start, h_end = get_margin(self.size[1], text_size[1])
        # self.text_offset = (w_start, h_start)
        self.text_ind = (ind[0] + w_start, ind[1] + h_start) # indices relative to container and centered in button box

    def register_context(self, key):
        self.b_context_key = key

    def press(self):
        pass
  