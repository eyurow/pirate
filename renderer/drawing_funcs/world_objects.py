import numpy as np

from renderer.textures.world_objects import particle, ship
from basics.indices import get_start_pixels, get_pixel_indices, index_shape
from basics.indices import rotate2, rotate_texture

def draw_land(pa, land, cell_size, world_slicers, color = (255,0,0)):
    visible_land = land[:,  (land[0] >= world_slicers[0].start)&
                            (land[0] < world_slicers[0].stop)&
                            (land[1] >= world_slicers[1].start)&
                            (land[1] < world_slicers[1].stop)]
    visible_land[0] -= world_slicers[0].start
    visible_land[1] -= world_slicers[1].start
        
    start_pixels = get_start_pixels(visible_land, cell_size)
    pixels = get_pixel_indices(start_pixels, cell_size)
    
    pa[pixels] = color

def draw_sun(pa, sun, cell_size, world_slicers, color = (200,100,100)):
    if sun[0] >= world_slicers[0].start and sun[1] < world_slicers[0].stop \
        and sun[1] >= world_slicers[1].start and sun[1] < world_slicers[1].stop:
            
        drawn_sun = (sun[0] - world_slicers[0].start, sun[1] - world_slicers[1].start)
            
        start_pixels = get_start_pixels(drawn_sun, cell_size)
        pixels = np.mgrid[start_pixels[0]:start_pixels[0] + cell_size,
                          start_pixels[1]:start_pixels[1] + cell_size]
        
        pa[(pixels[0], pixels[1])] = color

def draw_particles(pa, particles, pa_size, cell_size, world_slicers, start_pixels, color = (0,0,0)):
    world_idx = particles[:2,   (particles[0] >= world_slicers[0].start)&
                                (particles[0] < world_slicers[0].stop)&
                                (particles[1] >= world_slicers[1].start)&
                                (particles[1] < world_slicers[1].stop)]
    # print('WORLD_IDX 1: ', world_idx.T)
    world_idx[0] -= world_slicers[0].start # Get world index zerod on displayed world
    world_idx[1] -= world_slicers[1].start
    # print('WORLD_IDX 2: ', world_idx.T)
    
    draw_idx = world_idx * cell_size # convert to pixel index
    # print('DRAW_IDX 1: ', draw_idx.T)

    draw_idx[0] -= start_pixels[0]
    draw_idx[1] -= start_pixels[1]
    # print('DRAW_IDX 2: ', draw_idx.T)

    texture = particle()
    pixels = (  index_shape(draw_idx[0], texture[0]).ravel(), 
                index_shape(draw_idx[1], texture[1]).ravel() )
    on_screen = (pixels[0] >= 0)&(pixels[0] < pa_size[0])&(pixels[1] >= 0)&(pixels[1] < pa_size[1])

    
    asint = (pixels[0][on_screen].astype(int), pixels[1][on_screen].astype(int))
    # print('DRAW_IDX 3: ', draw_idx.astype(int).T)
    # print('_____________________________')
    pa[asint] = (0,0,0)


def draw_ship(pa, _ship, pa_size, cell_size, world_slicers, start_pixels, color = (0,0,0)):
    x = (_ship.position[0] - world_slicers[0].start) * cell_size - start_pixels[0]
    y = (_ship.position[1] - world_slicers[1].start) * cell_size - start_pixels[1]

    texture = rotate2(ship, _ship.heading)
    #texture = rotate_texture(ship, _ship.heading)
    # TODO: rotate texture

    pixels = (  index_shape(np.array([x], dtype = int), texture[0]).ravel(), 
                index_shape(np.array([y], dtype = int), texture[1]).ravel() )

    in_bounds = ((pixels[0] >= 0)&
                       (pixels[0] < pa_size[0])&
                       (pixels[1] >= 0)&
                       (pixels[1] < pa_size[1]))
    pa[(pixels[0][in_bounds], pixels[1][in_bounds])] = color
