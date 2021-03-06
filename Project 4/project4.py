import sys
import math
import pygame as pg
import numpy as np

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTBLUE = (118, 213, 255)
DARKBLUE = (61, 170, 214)
DARKGRAY = (48, 48, 48)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700

selected_index = 0
lights = []
vehicles = []
sprites = []
rotation_angle = 0
matrices = []
K_matrix = [0, 0, 0, 0]

class Vehicle():

    def __init__(self, image, position, angle, object_type, matrix):
        self.velocity = 3
        self.path = []
        self.image = image
        self.position = position
        self.angle = angle
        self.object_type = object_type
        self.matrix = matrix
        radians = math.radians(self.angle+90)
        self.sensor_one = (self.position[0] + 15*math.cos(radians), self.position[1] - 15*math.sin(radians))
        self.sensor_two = (self.position[0] - 15*math.cos(radians), self.position[1] + 15*math.sin(radians))

    def calculate_path(self):
        pass

    def simulate_path(self):
        pass

    def move(self):
        self.angle = self.angle + self.angular_velocity
        radians = math.radians(self.angle)
        x = self.position[0]+math.cos(radians)
        y = self.position[1]-math.sin(radians)
        self.position = (x, y)
        radians_plus90 = math.radians(self.angle+90)
        self.sensor_one = (self.position[0] + 15*math.cos(radians_plus90), self.position[1] - 15*math.sin(radians_plus90))
        self.sensor_two = (self.position[0] - 15*math.cos(radians_plus90), self.position[1] + 15*math.sin(radians_plus90))

    def calculate_angular_velocity(self):
        velocity_matrix = [0, 0]
        intensity_one = 0
        intensity_two = 0
        for light in lights:
            intensity_one += light.getIntensityOverDistance(self.sensor_one[0], self.sensor_one[1])
            intensity_two += light.getIntensityOverDistance(self.sensor_two[0], self.sensor_two[1])
        sensor_matrix = np.matrix([[intensity_one], [intensity_two]])
        matrix_k = np.matrix([[self.matrix[0], self.matrix[1]], [self.matrix[2], self.matrix[3]]])
        velocity_matrix = matrix_k * sensor_matrix
        self.angular_velocity = math.degrees(math.atan(velocity_matrix[0] - velocity_matrix[1]) / 38)

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
        distance = math.sqrt(float((self.x - x) **2 + (self.y - y)**2))
        return self.intensity / distance

    def getLocation(self):
        return self.x, self.y

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

        for index, v in enumerate(vehicles):
            v.matrix = matrices[index] 
            print(matrices[index])
            v.calculate_angular_velocity()
            v.move()
            selected_sprite = v.image
            image_rect = selected_sprite.get_rect(center=v.position)
            selected_sprite = pg.transform.rotate(selected_sprite, v.angle)
            image_rect = selected_sprite.get_rect(center=image_rect.center)
            screen.blit(selected_sprite, image_rect)

        for l in lights:
            selected_sprite = l.image
            image_rect = selected_sprite.get_rect(center=l.position)
            selected_sprite = pg.transform.rotate(selected_sprite, l.angle)
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
                        print("ADDED")
                        sprite = Vehicle(buttons[0], mouse_pos, rotation_angle, 1, K_matrix)
                        vehicles.append(sprite)
                        sprites.append(sprite)
                        new_list = list(K_matrix)
                        matrices.append(new_list)
                    elif selected_index == 2:
                        sprite = Light(buttons[1], mouse_pos, rotation_angle, 0)
                        lights.append(sprite)
                        sprites.append(sprite)
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
