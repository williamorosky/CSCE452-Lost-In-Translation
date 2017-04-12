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
lights = []
rotation_angle = 0
K_matrix = [0, 0, 0, 0]

class Light():
    def __init__(self, image, position, angle, object_type, intensity = 100):
        self.velocity = 3
        self.path = []
        self.image = image
        self.position = position
        self.x, self.y = position
        self.angle = angle
        self.object_type = object_type
        self.intensity = float(intensity)
        
        
    def getIntensityOverDistance(self, x, y):
        distance = math.sqrt(math.pow(x-self.x,2) + math.pow(y-self.y,2))
        if distance == 0:
            return 100
        else:
            return self.intensity / distance

    def getLocation(self):
        return self.x, self.y

def getIntensities(lights, x, y):
    SensorVariable = 0
    for light in lights:
        SensorVariable += light.getIntensityOverDistance(x, y)
    return SensorVariable 

class Vehicle():

    def __init__(self, image, position, angle, object_type, k11, k12, k21, k22):
        self.velocity = 3
        self.path = []
        self.image = image
        self.position = position
        self.angle = angle
        self.object_type = object_type
        self.k11 = float(k11)
        self.k12 = float(k12)
        self.k21 = float(k21)
        self.k22 = float(k22)
        self.Lsensor_staticx = 26 
        self.Lsensor_staticy = 12
        self.Rsensor_staticx = 64
        self.Rsensor_staticy = 12

    def calculate_path(self):
        pass
        """
        w1 = k11 * s1 + k12 * s2
        w2 = k21 * s1 + k22 * s2
        
        rotation = math.degrees(math.atan((w2-w1)/(Rsensor_staticx-Lsensor_staticx)))

        self.angle = angle + rotation
        self.x, self.y = self.rotate(x,y-(w1+w2)/2, x, y)
        self.position = (x, y)
        """

    def simulate_path(self):
        pass

    def rotate(self, rx, ry, cx, cy):
        angle = -self.angle

        x = rx-cx
        y = ry-cy
        newx = (x*math.cos(math.radians(angle))) - (y*math.sin(math.radians(angle)))
        newy = (x*math.sin(math.radians(angle))) + (y*math.cos(math.radians(angle)))
        
        newx += cx
        newy += cy
        
        return newx,newy

    def move(self, lights):
        k11 = self.k11
        k12 = self.k12
        k21 = self.k21
        k22 = self.k22
        
        SensorLx, SensorLy = self.rotate(self.Lsensor_staticx, self.Lsensor_staticy, self.position[0], self.position[1])
        SensorRx, SensorRy = self.rotate(self.Rsensor_staticx, self.Rsensor_staticy, self.position[0], self.position[1])

        s1 = getIntensities(lights, SensorLx, SensorLy)
        s2 = getIntensities(lights, SensorRx, SensorRy)

        w1 = k11 * s1 + k12 * s2
        w2 = k21 * s1 + k22 * s2

        rotation = math.degrees(math.atan((w2-w1)/(self.Rsensor_staticx-self.Lsensor_staticx)))

        radians = math.radians(self.angle)
        x = self.position[0]+math.cos(radians)
        y = self.position[1]-math.sin(radians)
        self.position = (x, y)

        self.angle = self.angle + rotation
        self.x, self.y = self.rotate(x,y-(w1+w2)/2, x, y)
        self.position = (x, y)

def initialize():

    string = "images/vehicle_" + str(K_matrix[0]) + str(K_matrix[1]) + str(K_matrix[2]) + str(K_matrix[3]) + ".png"
    afraid = pg.image.load(string).convert_alpha()
    afraid = pg.transform.rotate(afraid, -90)
    afraid = pg.transform.scale(afraid, (43,43))

    close = pg.image.load("images/close.png").convert_alpha()
    close = pg.transform.scale(close, (29,29))

    light = pg.image.load("images/light.png").convert_alpha()
    light = pg.transform.scale(light, (43,43))

    selection = pg.image.load("images/selection.png").convert_alpha()
    selection = pg.transform.scale(selection, (65,15))

    buttons = [afraid, light]
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

    while True:
        
        buttons, toggles = initialize()

        screen.fill(LIGHTBLUE)
        screen.blit(surface, (0,0))

        bar = pg.draw.rect(screen, DARKGRAY, (0, 0, SCREEN_WIDTH, 100), 0)
        afraid = screen.blit(buttons[0], (334, 28))
        light = screen.blit(buttons[1], (410, 28))

        global close
        if selected_index > 0 :
            close = screen.blit(toggles[0], (740, 35))
            screen.blit(toggles[1], (323+((selected_index-1)*76), 78))

        for sprite in sprites:
            if sprite.object_type > 0:
                sprite.move(lights)
            selected_sprite = sprite.image
            image_rect = selected_sprite.get_rect(center=sprite.position)
            selected_sprite = pg.transform.rotate(selected_sprite, sprite.angle)
            image_rect = selected_sprite.get_rect(center=image_rect.center)
            screen.blit(selected_sprite, image_rect)

        matrix_00 = pg.draw.rect(screen, WHITE, (133, 29, 18, 18), 0)
        matrix_01 = pg.draw.rect(screen, WHITE, (156, 29, 18, 18), 0)
        matrix_10 = pg.draw.rect(screen, WHITE, (133, 52, 18, 18), 0)
        matrix_11 = pg.draw.rect(screen, WHITE, (156, 52, 18, 18), 0)

        myfont = pg.font.SysFont("Roboto", 14)
        label_00 = myfont.render(str(K_matrix[0]), 1, BLACK)
        label_01 = myfont.render(str(K_matrix[1]), 1, BLACK)
        label_10 = myfont.render(str(K_matrix[2]), 1, BLACK)
        label_11 = myfont.render(str(K_matrix[3]), 1, BLACK)

        screen.blit(label_00, (138, 30))
        screen.blit(label_01, (161, 30))
        screen.blit(label_10, (138, 53))
        screen.blit(label_11, (161, 53))

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
                elif light.collidepoint(mouse_pos):
                    rotation_angle = 0
                    if selected_index == 2:
                        selected_index = 0
                    else:
                        selected_index = 2
                elif matrix_00.collidepoint(mouse_pos):
                    K_matrix[0] = int(not K_matrix[0])
                elif matrix_01.collidepoint(mouse_pos):
                    K_matrix[1] = int(not K_matrix[1])
                elif matrix_10.collidepoint(mouse_pos):
                    K_matrix[2] = int(not K_matrix[2])
                elif matrix_11.collidepoint(mouse_pos):
                    K_matrix[3] = int(not K_matrix[3])
                elif mouse_pos[1] > 100:
                    if selected_index == 1:
                        sprite = Vehicle(buttons[0], mouse_pos, rotation_angle, 1, K_matrix[0], K_matrix[1], K_matrix[2], K_matrix[3])
                        sprites.append(sprite)
                    elif selected_index == 2:
                        sprite = Light(buttons[1], mouse_pos, rotation_angle, 0)
                        sprites.append(sprite)
                        lights.append(sprite)
                elif close.collidepoint(mouse_pos):
                        rotation_angle = 0
                        selected_index = 0
                    
                
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

            if keys[pg.K_r]:
                rotation_angle += 5
                rotation_angle = rotation_angle%360

        pg.display.flip()
        pg.display.update()

    pg.quit()
    sys.exit()
