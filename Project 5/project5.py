import sys
import math
import pygame as pg
import numpy as np

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTBLUE = (118, 213, 255)
DARKBLUE = (61, 170, 214)
LIGHTGREEN = (122, 226, 198)
GREEN = (56, 211, 169)
DARKGREEN = (42, 158, 127)
DARKGRAY = (48, 48, 48)

SCREEN_WIDTH = 572
SCREEN_HEIGHT = 500

selected_index = 0
obstacles = []
endpoints = []

class Obstacle():

    def __init__(self, image, position, size, color):
        self.image = image
        self.position = position
        self.size = size
        self.color = color

class Endpoint():
    def __init__(self, image, position, is_start):
        self.image = image
        self.position = position
        self.is_start = is_start

def draw(surface, start, end):
    pg.draw.line(surface, DARKBLUE, start.position, end.position, 4)


def find_path(surface):
    if (len(endpoints) == 2):
        if (startpoint.is_start == True for startpoint in endpoints):
            start = [startpoint for startpoint in endpoints if startpoint.is_start == True]
            if (endpoint.is_start == False for endpoint in endpoints):
                end = [endpoint for endpoint in endpoints if endpoint.is_start == False]
                draw(surface, start[0], end[0])

def initialize():
    run = pg.image.load("images/run.png").convert_alpha()
    run = pg.transform.scale(run, (36,36))

    start = pg.image.load("images/start.png").convert_alpha()
    start = pg.transform.scale(start, (11,11))
    end = pg.image.load("images/end.png").convert_alpha()
    end = pg.transform.scale(end, (11,11))

    small = pg.image.load("images/small.png").convert_alpha()
    small = pg.transform.scale(small, (19,19))
    medium = pg.image.load("images/medium.png").convert_alpha()
    medium = pg.transform.scale(medium, (27,27))
    large = pg.image.load("images/large.png").convert_alpha()
    large = pg.transform.scale(large, (36,36))

    buttons = [run, start, end, small, medium, large]

    return buttons

if __name__ == "__main__":

    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    screen.fill(LIGHTBLUE)
    surface = pg.Surface(screen.get_size())
    surface = surface.convert()
    surface.fill(LIGHTBLUE)

    pg.display.set_caption('Lost in Translation')

    while True:

        buttons = initialize()

        screen.fill(LIGHTBLUE)
        screen.blit(surface, (0,0))

        bar = pg.draw.rect(screen, DARKGRAY, (0, 0, 72, SCREEN_HEIGHT), 0)
        run = screen.blit(buttons[0], (18, 40))
        start = screen.blit(buttons[1], (30, 151))
        end = screen.blit(buttons[2], (30, 205))
        small = screen.blit(buttons[3], (26, 431))
        medium = screen.blit(buttons[4], (22, 379))
        large = screen.blit(buttons[5], (18, 318))

        for obstacle in obstacles:
            selected_sprite = obstacle.image
            bar = pg.draw.rect(screen, obstacle.color, (obstacle.position[0], obstacle.position[1], obstacle.size[0], obstacle.size[1]), 0)

        for endpoint in endpoints:
            selected_sprite = endpoint.image
            image_rect = selected_sprite.get_rect(center=endpoint.position)
            screen.blit(selected_sprite, image_rect)

        my_font = pg.font.SysFont("Roboto", 14)
        run_label = my_font.render(("Run"), 1, WHITE)
        start_label = my_font.render(("Start"), 1, WHITE)
        end_label = my_font.render(("End"), 1, WHITE)

        screen.blit(run_label, (23, 81))
        screen.blit(start_label, (22, 167))
        screen.blit(end_label, (23, 222))

        pg.event.pump()
        keys = pg.key.get_pressed()
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():

            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONUP:
                if run.collidepoint(mouse_pos):
                    selected_index = 0
                    find_path(surface)

                elif start.collidepoint(mouse_pos):
                    if selected_index == 1:
                        selected_index = 0
                    else:
                        selected_index = 1
                elif end.collidepoint(mouse_pos):
                    if selected_index == 2:
                        selected_index = 0
                    else:
                        selected_index = 2
                elif large.collidepoint(mouse_pos):
                    if selected_index == 3:
                        selected_index = 0
                    else:
                        selected_index = 3
                elif medium.collidepoint(mouse_pos):
                    if selected_index == 4:
                        selected_index = 0
                    else:
                        selected_index = 4
                elif small.collidepoint(mouse_pos):
                    if selected_index == 5:
                        selected_index = 0
                    else:
                        selected_index = 5

                elif mouse_pos[0] > 100:
                    if selected_index == 1:
                        if any(endpoint.is_start == True for endpoint in endpoints):
                            end = [endpoint for endpoint in endpoints if endpoint.is_start == True]
                            endpoints.remove(end[0])
                            sprite = Endpoint(buttons[1], mouse_pos, True)
                            endpoints.append(sprite)
                        else:
                            sprite = Endpoint(buttons[1], mouse_pos, True)
                            endpoints.append(sprite)
                    elif selected_index == 2:
                        if any(endpoint.is_start == False for endpoint in endpoints):
                            end = [endpoint for endpoint in endpoints if endpoint.is_start == False]
                            endpoints.remove(end[0])
                            sprite = Endpoint(buttons[2], mouse_pos, False)
                            endpoints.append(sprite)
                        else:
                            sprite = Endpoint(buttons[2], mouse_pos, False)
                            endpoints.append(sprite)
                    elif selected_index == 3:
                        if any(obstacle.size[0] == 200 for obstacle in obstacles):
                            obs = [obstacle for obstacle in obstacles if obstacle.size[0] == 200]
                            obstacles.remove(obs[0])
                            bar = pg.draw.rect(screen, DARKGREEN, (mouse_pos[0]-100, mouse_pos[1]-100, 200, 200), 0)
                            sprite = Obstacle(buttons[5], (mouse_pos[0]-100,mouse_pos[1]-100), (200,200), DARKGREEN)
                            obstacles.append(sprite)
                        else: 
                            bar = pg.draw.rect(screen, DARKGREEN, (mouse_pos[0]-100, mouse_pos[1]-100, 200, 200), 0)
                            sprite = Obstacle(buttons[5], (mouse_pos[0]-100,mouse_pos[1]-100), (200,200), DARKGREEN)
                            obstacles.append(sprite)
                    elif selected_index == 4:
                        if any(obstacle.size[0] == 150 for obstacle in obstacles):
                            obs = [obstacle for obstacle in obstacles if obstacle.size[0] == 150]
                            obstacles.remove(obs[0])
                            bar = pg.draw.rect(screen, GREEN, (mouse_pos[0]-75, mouse_pos[1]-75, 150, 150), 0)
                            sprite = Obstacle(buttons[4], (mouse_pos[0]-75,mouse_pos[1]-75), (150,150), GREEN)
                            obstacles.append(sprite)
                        else:
                            bar = pg.draw.rect(screen, GREEN, (mouse_pos[0]-75, mouse_pos[1]-75, 150, 150), 0)
                            sprite = Obstacle(buttons[4], (mouse_pos[0]-75,mouse_pos[1]-75), (150,150), GREEN)
                            obstacles.append(sprite)
                    elif selected_index == 5:
                        if any(obstacle.size[0] == 100 for obstacle in obstacles):
                            obs = [obstacle for obstacle in obstacles if obstacle.size[0] == 100]
                            obstacles.remove(obs[0])
                            bar = pg.draw.rect(screen, LIGHTGREEN, (mouse_pos[0]-50, mouse_pos[1]-50, 100, 100), 0)
                            sprite = Obstacle(buttons[3], (mouse_pos[0]-50,mouse_pos[1]-50), (100,100), LIGHTGREEN)
                            obstacles.append(sprite)
                        else:
                            bar = pg.draw.rect(screen, LIGHTGREEN, (mouse_pos[0]-50, mouse_pos[1]-50, 100, 100), 0)
                            sprite = Obstacle(buttons[3], (mouse_pos[0]-50,mouse_pos[1]-50), (100,100), LIGHTGREEN)
                            obstacles.append(sprite)


        if mouse_pos[0] > 100:
            if selected_index == 1:
                transparent = buttons[1].copy()
                transparent.fill((255, 255, 255, 128), None, pg.BLEND_RGBA_MULT)
                image_rect = transparent.get_rect(center=mouse_pos)
                selected_sprite = screen.blit(transparent, image_rect)
            elif selected_index == 2:
                transparent = buttons[2].copy()
                transparent.fill((255, 255, 255, 128), None, pg.BLEND_RGBA_MULT)
                image_rect = transparent.get_rect(center=mouse_pos)
                selected_sprite = screen.blit(transparent, image_rect)
            elif selected_index == 3:
                large = pg.transform.scale(buttons[5], (200,200))
                transparent = large.copy()
                transparent.fill((255, 255, 255, 128), None, pg.BLEND_RGBA_MULT)
                image_rect = transparent.get_rect(center=mouse_pos)
                selected_sprite = screen.blit(transparent, image_rect)
            elif selected_index == 4:
                medium = pg.transform.scale(buttons[4], (150,150))
                transparent = medium.copy()
                transparent.fill((255, 255, 255, 128), None, pg.BLEND_RGBA_MULT)
                image_rect = transparent.get_rect(center=mouse_pos)
                selected_sprite = screen.blit(transparent, image_rect)
            elif selected_index == 5:
                small = pg.transform.scale(buttons[3], (100,100))
                transparent = small.copy()
                transparent.fill((255, 255, 255, 128), None, pg.BLEND_RGBA_MULT)
                image_rect = transparent.get_rect(center=mouse_pos)
                selected_sprite = screen.blit(transparent, image_rect)

        pg.display.flip()
        pg.display.update()

    pg.quit()
    sys.exit()