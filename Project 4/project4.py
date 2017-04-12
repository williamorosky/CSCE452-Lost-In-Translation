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
rotation_angle = 0

class Vehicle():

    def __init__(self, image, position, angle, object_type):
        self.velocity = 3
        self.path = []
        self.image = image
        self.position = position
        self.angle = angle
        self.object_type = object_type
        

    def calculate_path(self):
        pass

    def simulate_path(self):
        pass

    def move(self):
        radians = math.radians(self.angle)
        x = self.position[0]+math.cos(radians)
        y = self.position[1]-math.sin(radians)
        self.position = (x, y)

class Light():

    def __init__(self, image, position, angle, object_type, intensity = 100):
        self.velocity = 3
        self.path = []
        self.image = image
        self.position = position
        self._x, self._y = position
        self.angle = angle
        self.object_type = object_type
        self._intensity = float(intensity)
        
    def getIntensityOverDistance(self, x, y):
        distance = sqrt(float((self._x - x) **2 + (self._y - y)**2) )
        return self._intensity / distance

    def getLocation(self):
        return self._x, self._y

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
            if sprite.object_type > 0:
                sprite.move()
            selected_sprite = sprite.image
            image_rect = selected_sprite.get_rect(center=sprite.position)
            selected_sprite = pg.transform.rotate(selected_sprite, sprite.angle)
            image_rect = selected_sprite.get_rect(center=image_rect.center)
            screen.blit(selected_sprite, image_rect)

        pg.event.pump()
        keys = pg.key.get_pressed()
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():

            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONUP:

                if afraid.collidepoint(mouse_pos):
                    rotation_angle = 0
                    if selected_index == 1:
                        selected_index = 0
                    else:
                        selected_index = 1
                elif attracted.collidepoint(mouse_pos):
                    rotation_angle = 0
                    if selected_index == 2:
                        selected_index = 0
                    else:
                        selected_index = 2
                elif light.collidepoint(mouse_pos):
                    rotation_angle = 0
                    if selected_index == 3:
                        selected_index = 0
                    else:
                        selected_index = 3
                elif close.collidepoint(mouse_pos):
                    rotation_angle = 0
                    selected_index = 0
                elif mouse_pos[1] > 100:
                    if selected_index == 1:
                        sprite = Vehicle(buttons[0], mouse_pos, rotation_angle, 1)
                        sprites.append(sprite)
                    elif selected_index == 2:
                        sprite = Vehicle(buttons[1], mouse_pos, rotation_angle, 2)
                        sprites.append(sprite)
                    elif selected_index == 3:
                        sprite = Light(buttons[2], mouse_pos, rotation_angle, 0)
                        sprites.append(sprite)

        if mouse_pos[1] > 100:

            if selected_index == 1:
                transparent = buttons[0].copy()
                transparent.fill((255, 255, 255, 128), None, pg.BLEND_RGBA_MULT)
                image_rect = transparent.get_rect(center=mouse_pos)
                transparent = pg.transform.rotate(transparent, rotation_angle)
                image_rect = transparent.get_rect(center=image_rect.center)
                selected_sprite = screen.blit(transparent, image_rect)
            elif selected_index == 2:
                transparent = buttons[1].copy()
                transparent.fill((255, 255, 255, 128), None, pg.BLEND_RGBA_MULT)
                image_rect = transparent.get_rect(center=mouse_pos)
                transparent = pg.transform.rotate(transparent, rotation_angle)
                image_rect = transparent.get_rect(center=image_rect.center)
                selected_sprite = screen.blit(transparent, image_rect)
            elif selected_index == 3:
                transparent = buttons[2].copy()
                transparent.fill((255, 255, 255, 128), None, pg.BLEND_RGBA_MULT)
                image_rect = transparent.get_rect(center=mouse_pos)
                transparent = pg.transform.rotate(transparent, rotation_angle)
                image_rect = transparent.get_rect(center=image_rect.center)
                selected_sprite = screen.blit(transparent, image_rect)

            if keys[pg.K_r]:
                rotation_angle += 5
                rotation_angle = rotation_angle%360

        pg.display.flip()
        pg.display.update()

    pg.quit()
    sys.exit()
