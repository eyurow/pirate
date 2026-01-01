import numpy as np
import pygame
import pygame.surfarray as sa
from vis import pa_fill_color, fill_color_light, fill_color_sun, fill_ind_colors
from generics import DBZ, get_margin
from shapes import generate_compass, generate_patterned_line



class Context:
    def __init__(self, owner):
        self.owner = owner
        self.button_context = PositionContext(owner)
        self.hover_context = PositionContext(owner)

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

    def register_component(self, component):
        # add top-left (0,1) and bottom-right (2,3) corners of rectangle (button, dropdown) and key (4)
        # Most recently registered component at top of list

        add = np.zeros((5, 1), dtype = int)
        add[0] = self.owner.pos[0] + component.pos[0]
        add[1] = self.owner.pos[1] + component.pos[1]
        add[2] = self.owner.pos[0] + component.pos[0] + component.size[0]
        add[3] = self.owner.pos[1] + component.pos[1] + component.size[1]
        add[4] = self.key_idx

        self.map = np.concatenate([add, self.map], axis = 1)
        self.key[self.key_idx] = component
        component.register_context(self.key_idx)

        self.key_idx += 1

class KeyContext:
    def __init__(self, owner):
        self.owner = owner
        self.reset()

    def __str__(self):
        return f"map: {self.map}, base: {self.base}, key: {self.key}, idx: {self.key_idx}, active: {self.active}"
        
    def reset(self):
        self.map = np.zeros((2,0), dtype = object) # top-left (idx 0,1) and bottom-right (2,3) corner of component and component id (4)
        self.base = np.zeros((2,0), dtype = int) # base layer of map - to be recovered when overlays deactivate
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

    def register_component(self, component):
        # add top-left (0,1) and bottom-right (2,3) corners of rectangle (button, dropdown) and key (4)
        # Most recently registered component at top of list

        add = np.zeros((5, 1), dtype = int)
        add[0] = self.owner.pos[0] + component.pos[0]
        add[1] = self.owner.pos[1] + component.pos[1]
        add[2] = self.owner.pos[0] + component.pos[0] + component.size[0]
        add[3] = self.owner.pos[1] + component.pos[1] + component.size[1]
        add[4] = self.key_idx

        self.map = np.concatenate([add, self.map], axis = 1)
        self.key[self.key_idx] = component
        component.register_context(self.key_idx)

        self.key_idx += 1



class Rectangle:
    def __init__(self, pos, size, color = None, border_color = (0,0,0), owner = None):
        self.pos = pos # position relative to container 
        self.size = size
        self.color = color
        self.border_color = border_color
        self.owner = owner # pointer to container, e.g. EscapeMenu
        self.pa_pos = (self.owner.pa_pos[0] + self.pos[0], self.owner.pa_pos[1] + self.pos[1]) # absolute position within PA
        # self.generate()

    def generate(self, pos = None, size = None):
        # self.size = new_size
        # TODO: reset pa_pos
        if pos:
            self.pos = pos
        if size:
            self.size = size
        self.pa_pos = (self.owner.pa_pos[0] + self.pos[0], self.owner.pa_pos[1] + self.pos[1])


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


class Menu:
    def __init__(self, renderer):
        pass
class EscapeMenu(Rectangle):
    def __init__(self, pos, owner, size = (1000,550), color = (166,93,7), border_color = (0,0,0), font = pygame.font.SysFont('chicago', size = 30)):
        super().__init__(pos, size, color, border_color, owner)
        self.context = Context(self)    
        self.font = font
        size = self.font.render('Display View Display ***', 0, (0,0,0)).get_size()
        self.button_size = (size[0], round(size[1] * (1 + .25)))
        
        self.view_button = ViewButton('Display View', (30,20), self.button_size, font = self.font, color = (150,150,150), border_color = (0,0,0), owner = self) # position given relative to menu
        # self.resize() # TODO: rename as generate

    @property
    def bcontext(self):
        return self.context.button_context

    def generate(self, **kwargs):
        super().generate(**kwargs)

        self.bcontext.reset()
        self.generate_buttons() # TODO: resize/position buttons
        self.bcontext.register_component(self.view_button)
        self.bcontext.store_base()

    def refresh_base(self):
        # remove overlays from context/screen
        self.bcontext.restore_base()
        self.display()

    def display(self):
        self.owner.draw_rectangle(self)
        self.draw_buttons()

    def draw_buttons(self, buttons = None):
        if not buttons:
            buttons = [self.view_button]
        for button in buttons:
            self.owner.draw_button(button, self.pa_pos)
        self.owner.update_display()
    
    def generate_buttons(self):
        self.view_button.generate()




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
  
        

class ViewButton(Button):
    def __init__(self, text, pos, size, color = None, text_color = (0,0,0), border_color = None, font = None, owner = None, context_type = 'base'):
        super().__init__(text, pos, size, color, border_color, owner, text_color, font, context_type)

        self.orig_view_butt = OrigViewButton('Original', (pos[0]+20, pos[1] + size[1]), (size[0]-10, size[1]), color, text_color, border_color, font, owner = owner, context_type = 'overlay')
        self.light_view_butt = LightViewButton('Light', (pos[0]+20, pos[1] + self.size[1]*2), (size[0]-10, size[1]), color, text_color, border_color, font, owner = owner, context_type = 'overlay')
        self.sun_view_butt = SunViewButton('Sun', (pos[0]+20, pos[1] + self.size[1]*3), (size[0]-10, size[1]), color, text_color, border_color, font, owner = owner, context_type = 'overlay')
        self.drama_view_butt = DramaViewButton('Dramatic', (pos[0]+20, pos[1] + self.size[1]*4), (size[0]-10, size[1]), color, text_color, border_color, font, owner = owner, context_type = 'overlay')

    def press(self, handler):
        # open dropdown
        if self not in self.context.active: # if not self.pressed:
            self.context.active.append(self)
            for button in [self.orig_view_butt, self.light_view_butt, self.sun_view_butt, self.drama_view_butt]:
                self.context.register_component(button)
            self.display()
        else:
            self.owner.refresh_base()
    
    def display(self):
        self.owner.draw_buttons([self.orig_view_butt, self.light_view_butt, self.sun_view_butt, self.drama_view_butt])

    def generate(self):
        super().generate()
        self.generate_dropdown()

    def generate_dropdown(self):
        # OPTION 2 - scrap buttons; directly add dropdown context to ESC-MENU with pseudobuttons (only have press method)
        self.orig_view_butt.generate()
        self.light_view_butt.generate()
        self.sun_view_butt.generate()
        self.drama_view_butt.generate()




### OPTION 1 - indiv buttons for each dropdown option
class OrigViewButton(Button):
    def __init__(self, text, pos, size, color = None, text_color = (0,0,0), border_color = None, font = None, owner = None, context_type = 'base'):
        super().__init__(text, pos, size, color, border_color, owner, text_color, font, context_type)
    # def generate(self):
    #     super().generate()
    def press(self, handler):
        self.owner.owner.set_draw(pa_fill_color)
        self.owner.refresh_base()

class LightViewButton(Button):
    def __init__(self, text, pos, size, color = None, text_color = (0,0,0), border_color = None, font = None, owner = None, context_type = 'base'):
        super().__init__(text, pos, size, color, border_color, owner, text_color, font, context_type)
    def press(self, handler):
        self.owner.owner.set_draw(fill_color_light)
        self.owner.refresh_base()

class SunViewButton(Button):
    def __init__(self, text, pos, size, color = None, text_color = (0,0,0), border_color = None, font = None, owner = None, context_type = 'base'):
        super().__init__(text, pos, size, color, border_color, owner, text_color, font, context_type)
    def press(self, handler):
        self.owner.owner.set_draw(fill_color_sun)
        self.owner.refresh_base()

class DramaViewButton(Button):
    def __init__(self, text, pos, size, color = None, text_color = (0,0,0), border_color = None, font = None, owner = None, context_type = 'base'):
        super().__init__(text, pos, size, color, border_color, owner, text_color, font, context_type)
    def press(self, handler):
        self.owner.owner.set_draw(fill_ind_colors)
        self.owner.refresh_base()



        
        