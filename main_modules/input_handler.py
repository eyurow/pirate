import numpy as np
import pygame

from visuals.vis import *
from UI.ui import EscapeMenu, InfoBox


def wait_for_input(mouse_movement = False):
    waiting = True
    while waiting:
        event = pygame.event.wait()
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN):
            return 'quit'
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            return True
        
        elif event.type in [pygame.VIDEORESIZE, pygame.VIDEOEXPOSE]:
            return 'resize'
        # elif event.type == pygame.VIDEOEXPOSE:
        #     return 'resize'
            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            return 'text'
            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            return 'fill'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            return 'light'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            return 'sun'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
            return 'sun2'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            return 'ind'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            return 'red'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            return 'blue'
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print(f'DOWN: {event}')
            return event.pos
        elif event.type == pygame.MOUSEMOTION and mouse_movement:
            print(f'MOVE: {event}')
            return event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            print(f'UP: {event}')
            return 0


def receive_inputs(mouse_movement = False):
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN):
            return 'quit'
        
        elif event.type == pygame.VIDEORESIZE:
            return 'resize'
        elif event.type == pygame.VIDEOEXPOSE:
            return 'resize'
        
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'escape menu'
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            return 'text'
            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            return 'fill'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            return 'light'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            return 'sun'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
            return 'sun2'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            return 'ind'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            return 'red'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            return 'blue'
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print(f'DOWN: {event}')
            return event.pos
        elif event.type == pygame.MOUSEMOTION and mouse_movement:
            print(f'MOVE: {event}')
            return event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            print(f'UP: {event}')
            return 0
        

class InputHandler:
    def __init__(self, screen, renderer, world = None):
        self.screen = screen
        self.renderer = renderer
        self.world = world

        self.ESC_MENU = EscapeMenu(owner = self.renderer, pos = ((self.renderer.PA_SIZE[0] - 1000)//2, (self.renderer.PA_SIZE[1] - 550)//2))
        self.info_box = InfoBox(owner = self.renderer)

        self.context = 'run'
        self.queue = []
        self.mouse_movement = False
        self.lmb_mode = False
        self.rmb_mode = False
        self.add_land = []
        self.pa_pos = (0,0)
        

    def generate_info_box(self, pos):
        world_pos = ( (pos[0] - self.renderer.START_PIXEL_X) // self.renderer.CELL_SIZE + self.renderer.WORLD_SLICER_X.start, 
                          (pos[1] - self.renderer.START_PIXEL_X) // self.renderer.CELL_SIZE + self.renderer.WORLD_SLICER_Y.start )
            
        current_x = self.world.CURRENTS[world_pos[0], world_pos[1], 0]
        current_y = self.world.CURRENTS[world_pos[0], world_pos[1], 1]
        winds_x = self.world.WINDS[world_pos[0], world_pos[1], 0]
        winds_y = self.world.WINDS[world_pos[0], world_pos[1], 1]
        r = self.renderer.PA[pos[0] - self.renderer.START_PIXEL_X, pos[1] - self.renderer.START_PIXEL_Y, 0]
        g = self.renderer.PA[pos[0] - self.renderer.START_PIXEL_X, pos[1] - self.renderer.START_PIXEL_Y, 1]
        b = self.renderer.PA[pos[0] - self.renderer.START_PIXEL_X, pos[1] - self.renderer.START_PIXEL_Y, 2]

        posx, posy = pos[0] + 4 - self.renderer.START_PIXEL_X, pos[1] - self.renderer.START_PIXEL_Y
        if posx + self.info_box.size[0] >= self.renderer.PA_SIZE[0]:
            posx = posx - self.info_box.size[0]
        if posy + self.info_box.size[1] >= self.renderer.PA_SIZE[1]:
            posy = posy - self.info_box.size[1]
    
        self.info_box.generate((posx, posy))
        self.info_box.generate_info(current_x, current_y, winds_x, winds_y, r, g, b) # TODO: call generate info from generate??
        
        self.renderer.add_post(self.renderer.draw_info_box, self.info_box)

    def default_handle(self, event, mouse_press = None):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            self.renderer.set_draw(pa_fill_color)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            self.renderer.set_draw(fill_color_light)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            self.renderer.set_draw(fill_color_sun)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
            self.renderer.set_draw(fill_color_sun2)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            self.renderer.set_draw(fill_ind_colors)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.renderer.set_draw(fill_ind_red)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            self.renderer.set_draw(fill_fluc_blue)

        elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3): # or mouse_press[2] == 1:
            self.generate_info_box(event.pos)
        
        elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
            modified_pos = (event.pos[0] - self.renderer.START_PIXEL_X + self.renderer.WORLD_SLICER_X.start * self.renderer.CELL_SIZE,
                            event.pos[1] - self.renderer.START_PIXEL_Y + self.renderer.WORLD_SLICER_Y.start * self.renderer.CELL_SIZE)
            same_pos_size = self.world.LAND[:, (self.world.LAND[0] == modified_pos[0]//self.renderer.CELL_SIZE)& 
                                          (self.world.LAND[1] == modified_pos[1]//self.renderer.CELL_SIZE)].size
            if same_pos_size == 0 and modified_pos not in self.add_land:
                self.add_land.append(modified_pos)
            self.lmb_mode = 'add land'
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            add_land_array = np.array(self.add_land).T // self.renderer.CELL_SIZE
            self.world.LAND = np.concatenate([self.world.LAND, add_land_array], axis = 1) #, dtype = int)
            self.lmb_mode = False

    def end_handle(self, mouse_press):
        if mouse_press[2] == 1: # and self.rmb_mode == 'info':
            self.generate_info_box(pygame.mouse.get_pos())
        
        if mouse_press[0] == 1 and self.lmb_mode == 'add land':
            pos = pygame.mouse.get_pos()
            modified_pos = (pos[0] - self.renderer.START_PIXEL_X + self.renderer.WORLD_SLICER_X.start * self.renderer.CELL_SIZE,
                            pos[1] - self.renderer.START_PIXEL_Y + self.renderer.WORLD_SLICER_Y.start * self.renderer.CELL_SIZE)
            
            same_pos_size = self.world.LAND[:, (self.world.LAND[0] == modified_pos[0]//self.renderer.CELL_SIZE)& 
                                          (self.world.LAND[1] == modified_pos[1]//self.renderer.CELL_SIZE)].size
            if same_pos_size == 0 and modified_pos not in self.add_land:
                self.add_land.append(modified_pos)

    
    def handle(self):
        # global WORLD

        handling = True
        events = []
        # events = pygame.event.get()
        if pygame.event.peek(pygame.QUIT):
            return 'quit' # self.quit()
        if pygame.event.peek([pygame.VIDEORESIZE, pygame.VIDEOEXPOSE]):
            self.resize()

        while handling:
            match self.context:
                case 'run':
                    handling = False # set to False, will be intercepted below if need be (quit, EscapeMenu, pause)
                    events = pygame.event.get()
                    mouse_press = pygame.mouse.get_pressed()
                    # for event in events:
                    for _ in range(len(events)):
                        event = events.pop(0)
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            self.ESC_MENU.display()
                            self.context = 'escape menu'
                            handling = True
                            break
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                            self.context = 'pause'
                            handling = True
                        else:
                            self.default_handle(event, mouse_press)
                    self.end_handle(mouse_press)
                            
                case 'pause':
                    waiting = True
                    while waiting:
                        if events:
                            event = events.pop(0)
                        else:
                            event = pygame.event.wait()
                        if event.type == pygame.QUIT:
                            return self.quit()
                        elif event.type in [pygame.VIDEORESIZE, pygame.VIDEOEXPOSE]:
                            self.resize()
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            self.ESC_MENU.display()
                            self.context = 'escape menu'
                            waiting = False
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                            self.context = 'run'
                            waiting = False
                            handling = False
                        else:
                            self.default_handle(event, mouse_press = [])

                case 'escape menu':
                    waiting = True
                    while waiting:
                        event = pygame.event.wait()
                        if event.type == pygame.QUIT:
                            return self.quit()
                        elif event.type in [pygame.VIDEORESIZE, pygame.VIDEOEXPOSE]:
                            self.resize()
                            self.ESC_MENU.display()
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: # reset context, close menu and continue frame
                            self.ESC_MENU.bcontext.restore_base()
                            self.context = 'run'
                            waiting = False
                            handling = False
                        
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            pos = (event.pos[0] - self.renderer.START_PIXEL_X, event.pos[1] - self.renderer.START_PIXEL_Y)
                            ctx = self.ESC_MENU.context.button_context
                            check = ctx.map[4, (ctx.map[0] <= pos[0])&(ctx.map[1] <= pos[1])&(ctx.map[2] >= pos[0])&(ctx.map[3] >= pos[1])] # return any buttons on context map where click was within button borders
                            if check.size > 0:
                                button = ctx.key[check[0]]
                                button.press(self)
                            else:
                                if self.ESC_MENU.bcontext.active:
                                    self.ESC_MENU.refresh_base()
                
    def quit(self):
        # global RUN
        # RUN = False
        # pygame.display.quit()
        return 'quit'
    
    def resize(self):
        self.renderer.refresh_PA()
        self.renderer.set_pixelarray()
        self.ESC_MENU.generate(pos = ((self.renderer.PA_SIZE[0] - 1000)//2, (self.renderer.PA_SIZE[1] - 550)//2))      
