import numpy as np

from UI.basics import Rectangle, Button
from renderer.drawing_funcs import *


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

