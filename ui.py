import numpy as np
import pygame
import pygame.surfarray as sa
from vis import *
from generics import get_margin



class Context:
    def __init__(self, owner):
        self.owner = owner
        self.button_context = PositionContext(owner)
        self.hover_context = PositionContext(owner)

class PositionContext: # For button and hover maps
    def __init__(self, owner):
        self.owner = owner
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




class Menu:
    def __init__(self, renderer):
        pass
class EscapeMenu():
    def __init__(self, renderer):
        self.renderer = renderer

        self.font = pygame.font.SysFont('chicago', size = 30)
        size = self.font.render('Display View Display ***', 0, (0,0,0)).get_size()
        self.button_size = (size[0], round(size[1] * (1 + .25)))
        self.context = Context(self)
        
        self.view_button = ViewButton('Display View', (30,20), self.button_size, font = self.font, color = (150,150,150), border_color = (0,0,0), owner = self) # position given relative to menu

    @property
    def bcontext(self):
        return self.context.button_context

    def resize(self, scale = .9):
        self.bcontext.reset()

        # TODO: set font size and button size
        self.left_marg = int(self.renderer.PA.shape[0] * (1 - scale))
        self.right_marg = int(self.renderer.PA.shape[0] * scale)
        self.top_marg = int(self.renderer.PA.shape[1] * (1 - scale))
        self.bot_marg = int(self.renderer.PA.shape[1] * scale)
        self.size = (self.right_marg - self.left_marg, self.bot_marg - self.top_marg)
        self.pos = (self.left_marg, self.top_marg)

        # TODO: resize/position buttons
        self.generate_buttons()
        self.bcontext.register_component(self.view_button)
        self.bcontext.store_base()

    def refresh_base(self):
        # remove overlays from context/screen
        self.bcontext.restore_base()
        self.display()

    def display(self):
        self.renderer.draw_menu(self)
        self.draw_buttons()

    def draw_buttons(self, buttons = None):
        if not buttons:
            buttons = [self.view_button]
        for button in buttons:
            self.renderer.draw_button(button, self.pos)
        self.renderer.update_display()
    
    def generate_buttons(self):
        self.view_button.generate()




class Button:
    def __init__(self, text, pos, size, color = None, text_color = (0,0,0), border_color = None, font = None, owner = None, context_type = 'base'):
        self.text = text
        self.pos = pos #position relative to container 
        self.size = size
        self.color = color
        self.text_color = text_color
        self.border_color = border_color
        if font:
            self.font = font
        else:
            self.font = pygame.font.SysFont('chicago', size = 30)
        self.owner = owner # pointer to container, e.g. EscapeMenu
        self.context_type = context_type
        self.b_context_key = None
        self.h_context_key = None

    @property
    def context(self):
        return self.owner.context.button_context
    
    @property
    def hover_context(self):
        return self.owner.context.hover_context

    def generate(self):
        # self.size = size
        self.generate_text()
        self.generate_array()

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

    def generate_array(self):
        if self.color:
            self.type = 'array'
            ar = np.zeros((*self.size, 3))
            ar[:, :] = self.color
            ar[self.text_ind] = self.text_color
            if self.border_color:
                ar[0] = self.border_color
                ar[-1] = self.border_color
                ar[:, 0] = self.border_color
                ar[:, -1] = self.border_color
            self.array = ar
        
        elif self.border_color:
            self.type = 'index'
            border_ind_horiz = np.arange(self.pos[0], self.pos[0] + self.size[0] + 1, dtype = 'int')
            border_ind_vert = np.arange(self.pos[1], self.pos[1] + self.size[1] + 1, dtype = 'int')

            border_ind_t = (border_ind_horiz, np.zeros((border_ind_horiz.size), dtype = 'int') + self.pos[1]) #top border line
            border_ind_b = (border_ind_horiz, np.zeros((border_ind_horiz.size), dtype = 'int') + self.pos[1] + self.size[1]) # bottom border line
            
            border_ind_l = (np.zeros((border_ind_vert.size - 2), dtype = 'int') + self.pos[0], border_ind_vert[1:-1])
            border_ind_r = (np.zeros((border_ind_vert.size - 2), dtype = 'int') + self.pos[0] + self.size[0], border_ind_vert[1:-1])

            self.border_ind = (np.concatenate([border_ind_t[0], border_ind_b[0], border_ind_l[0], border_ind_r[0]]),
                               np.concatenate([border_ind_t[1], border_ind_b[1], border_ind_l[1], border_ind_r[1]]))
            
        else:
            self.type = 'text'

    def register_context(self, key):
        self.b_context_key = key

    def press(self):
        pass
  
        

class ViewButton(Button):
    def __init__(self, text, pos, size, color = None, text_color = (0,0,0), border_color = None, font = None, owner = None, context_type = 'base'):
        super().__init__(text, pos, size, color, text_color, border_color, font, owner, context_type)

        self.orig_view_butt = OrigViewButton('Original', (pos[0]+20, pos[1] + size[1]), (size[0]-10, size[1]), color, text_color, border_color, font, owner = owner, context_type = 'overlay')
        self.light_view_butt = LightViewButton('Light', (pos[0]+20, pos[1] + self.size[1]*2), (size[0]-10, size[1]), color, text_color, border_color, font, owner = owner, context_type = 'overlay')
        self.sun_view_butt = SunViewButton('Sun', (pos[0]+20, pos[1] + self.size[1]*3), (size[0]-10, size[1]), color, text_color, border_color, font, owner = owner, context_type = 'overlay')
        self.drama_view_butt = DramaViewButton('Dramatic', (pos[0]+20, pos[1] + self.size[1]*4), (size[0]-10, size[1]), color, text_color, border_color, font, owner = owner, context_type = 'overlay')

    def press(self, handler):
        # open dropdown
        print('Press VB: ')
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
        super().__init__(text, pos, size, color, text_color, border_color, font, owner, context_type)
    # def generate(self):
    #     super().generate()
    def press(self, handler):
        print('orig press')
        self.owner.renderer.set_draw(pa_fill_color)
        self.owner.refresh_base()

class LightViewButton(Button):
    def __init__(self, text, pos, size, color = None, text_color = (0,0,0), border_color = None, font = None, owner = None, context_type = 'base'):
        super().__init__(text, pos, size, color, text_color, border_color, font, owner, context_type)
    def press(self, handler):
        print('light press')
        self.owner.renderer.set_draw(fill_color_light)
        self.owner.refresh_base()

class SunViewButton(Button):
    def __init__(self, text, pos, size, color = None, text_color = (0,0,0), border_color = None, font = None, owner = None, context_type = 'base'):
        super().__init__(text, pos, size, color, text_color, border_color, font, owner, context_type)
    def press(self, handler):
        print('sun press')
        self.owner.renderer.set_draw(fill_color_sun)
        self.owner.refresh_base()

class DramaViewButton(Button):
    def __init__(self, text, pos, size, color = None, text_color = (0,0,0), border_color = None, font = None, owner = None, context_type = 'base'):
        super().__init__(text, pos, size, color, text_color, border_color, font, owner, context_type)
    def press(self, handler):
        print('drama press')
        self.owner.renderer.set_draw(fill_ind_colors)
        self.owner.refresh_base()



        
        