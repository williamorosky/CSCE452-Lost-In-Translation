import sys
import math
import pygame as pg

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTBLUE = (118, 213, 255)
DARKBLUE = (61, 170, 214)
DARKGRAY = (48, 48, 48)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700

selected_index = 0
sprites = []

def initialize():

    afraid = pg.image.load("images/afraid.png").convert_alpha()
    afraid = pg.transform.scale(afraid, (43,43))

    attracted = pg.image.load("images/attracted.png").convert_alpha()
    attracted = pg.transform.scale(attracted, (43,43))

    close = pg.image.load("images/close.png").convert_alpha()
    close = pg.transform.scale(close, (29,29))

    light = pg.image.load("images/light.png").convert_alpha()
    light = pg.transform.scale(light, (43,43))

    selection = pg.image.load("images/selection.png").convert_alpha()
    selection = pg.transform.scale(selection, (65,15))

    buttons = [afraid, attracted, light]
    toggles = [close, selection]

    return buttons, toggles


if __name__ == "__main__":

    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    screen.fill(LIGHTBLUE)
    surface = pg.Surface(screen.get_size())
    surface = surface.convert()
    surface.fill(LIGHTBLUE)

    pg.display.set_caption('Lost in Translation')

    buttons, toggles = initialize()

    while True:
        
        screen.fill(LIGHTBLUE)
        screen.blit(surface, (0,0))

        bar = pg.draw.rect(screen, DARKGRAY, (0, 0, SCREEN_WIDTH, 100), 0)
        afraid = screen.blit(buttons[0], (280, 28))
        attracted = screen.blit(buttons[1], (372, 28))
        light = screen.blit(buttons[2], (464, 28))

        global close
        if selected_index > 0 :
            close = screen.blit(toggles[0], (740, 35))
            screen.blit(toggles[1], (270+((selected_index-1)*92), 78))

        for sprite in sprites:
            screen.blit(sprite[0], sprite[1])

        pg.event.pump()
        keys = pg.key.get_pressed()
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():

            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONUP:

                if afraid.collidepoint(mouse_pos):
                    if selected_index == 1:
                        selected_index = 0
                    else:
                        selected_index = 1
                elif attracted.collidepoint(mouse_pos):
                    if selected_index == 2:
                        selected_index = 0
                    else:
                        selected_index = 2
                elif light.collidepoint(mouse_pos):
                    if selected_index == 3:
                        selected_index = 0
                    else:
                        selected_index = 3
                elif close.collidepoint(mouse_pos):
                    selected_index = 0
                elif mouse_pos[1] > 100:
                    if selected_index == 1:
                        # afraid_copy = screen.blit(buttons[0], mouse_pos)
                        sprites.append((buttons[0],mouse_pos))
                    elif selected_index == 2:
                        # attracted_copy = screen.blit(buttons[1], mouse_pos)
                        sprites.append((buttons[1],mouse_pos))
                    elif selected_index == 3:
                        sprites.append((buttons[2],mouse_pos))

                    
            if mouse_pos[1] > 100:
                # transparent = pg.Surface((43,43))
                # transparent = transparent.set_alpha(128)
                if selected_index == 1:
                    transparent = buttons[0].copy()
                    transparent.fill((255, 255, 255, 128), None, pg.BLEND_RGBA_MULT)
                    afraid_copy = screen.blit(transparent, mouse_pos)
                elif selected_index == 2:
                    transparent = buttons[1].copy()
                    transparent.fill((255, 255, 255, 128), None, pg.BLEND_RGBA_MULT)
                    attracted_copy = screen.blit(transparent, mouse_pos)
                elif selected_index == 3:
                    transparent = buttons[2].copy()
                    transparent.fill((255, 255, 255, 128), None, pg.BLEND_RGBA_MULT)
                    light_copy = screen.blit(transparent, mouse_pos)

        pg.display.flip()
        pg.display.update()

    pg.quit()
    sys.exit()
