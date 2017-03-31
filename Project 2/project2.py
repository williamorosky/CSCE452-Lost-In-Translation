import sys
import math
import pygame as pg

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTBLUE = (118, 213, 255)
DARKBLUE = (61, 170, 214)
GREEN = (56, 211, 169)
PURPLE = (123, 79, 214)
YELLOW = (255, 232, 131)
DARKGREY = (85, 85, 85)

SCREEN_WIDTH = 750
SCREEN_HEIGHT = 600
CANVAS_WIDTH_HEIGHT = 350

rotation_speed = 1
paint_color = WHITE

class Rotator(object):
    def __init__(self,center,origin,image_angle=0):
        x_mag = center[0]-origin[0]
        y_mag = center[1]-origin[1]
        self.radius = math.hypot(x_mag,y_mag)
        self.start_angle = math.atan2(-y_mag,x_mag)-math.radians(image_angle)

    def __call__(self,angle,origin):
        new_angle = math.radians(angle)+self.start_angle
        new_x = origin[0] + self.radius*math.cos(new_angle)
        new_y = origin[1] - self.radius*math.sin(new_angle)
        return (new_x,new_y)

class Joint(pg.sprite.DirtySprite):
    def __init__(self,image,location,pivot_point="center"):
        self.original_image = image
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=location)
        self.angle = 0
        self.hasLink = False
        self.draw_point = self.rect.midtop

        try:
            self.set_pivot_point(getattr(self.rect,pivot_point))
        except TypeError:
            self.set_pivot_point(pivot_point)
        self.speed = 3
        self.speed_ang = 1
        return super(pg.sprite.DirtySprite, self).__init__()

    def set_pivot_point(self,point):
        self.pivot_point = list(point)
        self.pivot_rotator = Rotator(self.rect.center,point,self.angle)
        
        if self.hasLink:
            self.link_rotator = Rotator(self.linkedJoint.rect.center, point, self.angle)
            if self.linkedJoint.hasLink:
                self.link_link_rotator = Rotator(self.linkedJoint.linkedJoint.rect.center, point, self.angle)

    def set_link_center(self,point):
        self.link_rotator = Rotator(self.linkedJoint.rect.center, point, self.angle)
        if self.linkedJoint.hasLink:
                self.link_link_rotator = Rotator(self.linkedJoint.linkedJoint.rect.center, point, self.angle)

    def rotateCCW(self):
        self.speed_ang = abs(rotation_speed)
        if self.speed_ang:
            self.angle = (self.angle+self.speed_ang)%360
            new_center = self.pivot_rotator(self.angle, self.pivot_point)
            self.image = pg.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=new_center)
            if self.hasLink:
                self.update_end_point()
                self.linkedJoint.set_pivot_point((self.end_point[0], self.end_point[1]))
                new_link_center = self.link_rotator(self.angle, self.pivot_point)
                self.linkedJoint.rect = self.linkedJoint.image.get_rect(center=new_link_center)
                self.rotateLinkCCW()


    def rotateCW(self):
        self.speed_ang = -1*abs(rotation_speed)
        if self.speed_ang:
            self.angle = (self.angle+self.speed_ang)%360
            new_center = self.pivot_rotator(self.angle,self.pivot_point)
            self.image = pg.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=new_center)
            if self.hasLink:
                self.update_end_point()
                self.linkedJoint.set_pivot_point((self.end_point[0], self.end_point[1]))
                new_link_center = self.link_rotator(self.angle, self.pivot_point)
                self.linkedJoint.rect = self.linkedJoint.image.get_rect(center=new_link_center)
                self.rotateLinkCW()

    def rotateLinkCCW(self):
        link = self.linkedJoint
        link.speed_ang = abs(rotation_speed)
        if link.speed_ang:
            link.angle = (link.angle+link.speed_ang)%360
            link.image = pg.transform.rotate(link.original_image, link.angle)

            if link.hasLink:
                link.update_end_point()
                link.linkedJoint.set_pivot_point((link.end_point[0], link.end_point[1]))
                new_link_center = self.link_link_rotator(self.angle, self.pivot_point)
                link.linkedJoint.rect = link.linkedJoint.image.get_rect(center=new_link_center)
                link.rotateLinkCCW()
           
    def rotateLinkCW(self):
        link = self.linkedJoint
        link.speed_ang = -1*abs(rotation_speed)
        if link.speed_ang:
            link.angle = (link.angle+link.speed_ang)%360
            link.image = pg.transform.rotate(link.original_image, link.angle)

            if link.hasLink:
                link.update_end_point()
                link.linkedJoint.set_pivot_point((link.end_point[0], link.end_point[1]))
                new_link_center = self.link_link_rotator(self.angle, self.pivot_point)
                link.linkedJoint.rect = link.linkedJoint.image.get_rect(center=new_link_center)
                link.rotateLinkCW()

    def update_end_point(self):
        dx = self.rect.center[0] - self.pivot_point[0]
        dy = self.rect.center[1] - self.pivot_point[1]
        self.end_point = list((self.rect.center[0]+dx, self.rect.center[1]+dy))

    def update_draw_point(self):
        self.update_end_point()
        dx = self.rect.center[0] - self.pivot_point[0]
        dy = self.rect.center[1] - self.pivot_point[1]
        addx = (dx/abs(dx))*10
        addy = (dx/abs(dx))*10
        self.draw_point = list((self.end_point[0]+addx, self.end_point[1]+addy))

    def linkJoint(self, Joint):
        self.linkedJoint = Joint
        self.hasLink = True

def setupButtons(screen, buttons):
    rotate_ccw_1 = screen.blit(buttons[0], (42, 133))
    rotate_cw_1 = screen.blit(buttons[1], (107, 133))
    rotate_ccw_2 = screen.blit(buttons[0], (42, 228))
    rotate_cw_2 = screen.blit(buttons[1], (107, 228))
    rotate_ccw_3 = screen.blit(buttons[0], (42, 323))
    rotate_cw_3 = screen.blit(buttons[1], (107, 323))
    screen.blit(buttons[6], (42, 418))
    
    #Currently just placing images, turning into buttons later.
    plus_x = screen.blit(buttons[2], (590, 133)); #plus_x
    minus_x = screen.blit(buttons[4], (660, 133)); #minus_x
    plus_y = screen.blit(buttons[3], (590, 228)); #plus_y
    minus_y = screen.blit(buttons[5], (660, 228)); #minus_y
    
    surface = pg.Surface((50,50))
    surface = surface.convert_alpha()
    surface.fill(DARKGREY)
    pg.draw.circle(surface, paint_color, (25, 25), 25)
    pg.draw.circle(surface, paint_color, (25, 25), 23)
    screen.blit(surface, (107, 418))

    button_list = [rotate_ccw_1, rotate_cw_1, rotate_ccw_2, rotate_cw_2, rotate_ccw_3, rotate_cw_3]

    translate_buttons = [plus_x, minus_x, plus_y, minus_y]

    buttons_setup = button_list + translate_buttons
    return buttons_setup


def initialize():

    base = pg.image.load("images/base.png").convert_alpha()
    base = pg.transform.scale(base, (60,20))
    bob_ross = pg.image.load("images/bobross.png").convert_alpha()
    bob_ross = pg.transform.scale(bob_ross, (55,65))
    button_backgrounds = pg.image.load("images/buttonbackground.png").convert_alpha()
    button_backgrounds = pg.transform.scale(button_backgrounds, (690,350))

    rotate_ccw = pg.image.load("images/rotateccw.png").convert_alpha()
    rotate_ccw = pg.transform.scale(rotate_ccw, (50,50))
    rotate_cw = pg.image.load("images/rotatecw.png").convert_alpha()
    rotate_cw = pg.transform.scale(rotate_cw, (50,50))

    plus_x = pg.image.load("images/plusx.png").convert_alpha()
    plus_x = pg.transform.scale(plus_x, (50,50))
    plus_y = pg.image.load("images/plusy.png").convert_alpha()
    plus_y = pg.transform.scale(plus_y, (50,50))
    minus_x = pg.image.load("images/minusx.png").convert_alpha()
    minus_x = pg.transform.scale(minus_x, (50,50))
    minus_y = pg.image.load("images/minusy.png").convert_alpha()
    minus_y = pg.transform.scale(minus_y, (50,50))

    paint_on = pg.image.load("images/painton.png").convert_alpha()
    paint_on = pg.transform.scale(paint_on, (50,50))
    paint_off = pg.image.load("images/paintoff.png").convert_alpha()
    paint_off = pg.transform.scale(paint_off, (50,50))

    link1 = pg.image.load("images/greenarm.png").convert_alpha()
    link1 = pg.transform.scale(link1, (20,185))
    green_arm = Joint(link1, (SCREEN_WIDTH/2, (SCREEN_HEIGHT/2)+82.5), "midbottom")

    link2 = pg.image.load("images/purplearm.png").convert_alpha()
    link2 = pg.transform.scale(link2, (185,20))
    purple_arm = Joint(link2, ((SCREEN_WIDTH/2)+82.5, SCREEN_HEIGHT/2), "midbottom")

    link3 = pg.image.load("images/yellowarm.png").convert_alpha()
    link3 = pg.transform.scale(link3, (20,185))
    yellow_arm = Joint(link3, ((SCREEN_WIDTH/2)+165, (SCREEN_HEIGHT/2)-82.5), "midbottom")

    green_arm.linkJoint(purple_arm)
    purple_arm.linkJoint(yellow_arm)
    green_arm.set_pivot_point((SCREEN_WIDTH/2, 465))
    green_arm.update_end_point()
    purple_arm.set_pivot_point((green_arm.end_point[0], green_arm.end_point[1]))
    purple_arm.update_end_point()
    yellow_arm.set_pivot_point((purple_arm.end_point[0], purple_arm.end_point[1]))

    sprites = [green_arm, purple_arm, yellow_arm]
    images = [base, bob_ross, button_backgrounds]
    buttons = [rotate_ccw, rotate_cw, plus_x, plus_y, minus_x, minus_y, paint_on, paint_off]

    return green_arm, purple_arm, yellow_arm, images, buttons, pg.sprite.RenderPlain(sprites)

if __name__ == "__main__":

    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    screen.fill(LIGHTBLUE)
    surface = pg.Surface(screen.get_size())
    surface = surface.convert()
    surface.fill(LIGHTBLUE)

    canvas_surface = pg.Surface((CANVAS_WIDTH_HEIGHT,CANVAS_WIDTH_HEIGHT))
    canvas_surface = canvas_surface.convert()
    canvas_surface.fill(LIGHTBLUE)

    pg.display.set_caption('Lost in Translation')

    green_arm, purple_arm, yellow_arm, images, buttons, allsprites = initialize()

    while True:

        pg.event.pump()
        keys = pg.key.get_pressed()

        for event in pg.event.get():

            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        
        if keys[pg.K_EQUALS] or keys[pg.K_KP_PLUS]:
            rotation_speed += 1
        elif keys[pg.K_MINUS] or keys[pg.K_KP_MINUS]:
            rotation_speed -= 1
            
        yellow_arm.update_end_point()

        pg.draw.circle(surface,paint_color,yellow_arm.end_point, 10)

        screen.fill(LIGHTBLUE)
        canvas_surface.fill(WHITE)
        screen.blit(surface, (0,0))

        allsprites.update()
        allsprites.draw(screen)

        for i, image in enumerate(images):
            width = image.get_rect().width
            height = image.get_rect().height
            if i < 2 :
                screen.blit(image, ((SCREEN_WIDTH/2)-(width/2),(SCREEN_HEIGHT/2)+(CANVAS_WIDTH_HEIGHT/2)-(height)))
            else:
                screen.blit(image, ((SCREEN_WIDTH/2)-(width/2),(SCREEN_HEIGHT/2)-(height/2)))

        button_list = setupButtons(screen, buttons)
        mouse = pg.mouse.get_pressed()
        pos = pg.mouse.get_pos()
        if mouse[0]:
            if button_list[0].collidepoint(pos):
                yellow_arm.rotateCCW()
                purple_arm.set_link_center((purple_arm.pivot_point[0], purple_arm.pivot_point[1]))
                green_arm.set_link_center((green_arm.pivot_point[0], green_arm.pivot_point[1]))

            elif button_list[1].collidepoint(pos):
                yellow_arm.rotateCW()
                purple_arm.set_link_center((purple_arm.pivot_point[0], purple_arm.pivot_point[1]))
                green_arm.set_link_center((green_arm.pivot_point[0], green_arm.pivot_point[1]))

            elif button_list[2].collidepoint(pos):
                purple_arm.rotateCCW()
                green_arm.set_link_center((green_arm.pivot_point[0], green_arm.pivot_point[1]))

            elif button_list[3].collidepoint(pos):
                purple_arm.rotateCW()
                green_arm.set_link_center((green_arm.pivot_point[0], green_arm.pivot_point[1]))

            elif button_list[4].collidepoint(pos):
                green_arm.rotateCCW()

            elif button_list[5].collidepoint(pos):
                green_arm.rotateCW()

            elif button_list[6].collidepoint(pos): #plus x
                print("PLUS X")

        pg.display.flip()

        pg.display.update()

    pg.quit()
    sys.exit()
