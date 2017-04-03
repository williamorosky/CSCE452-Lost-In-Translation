import socket
import sys
import sys
import math
import pygame as pg
from Tkinter import *
from tkFileDialog import askopenfilename
from tkColorChooser import askcolor

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

paint_on = True
image_attached = False
PLANK_LEN = [175, 175, 175]

global image_to_draw
scaled_down_image = pg.image.load("images/whitesquare.png")

root = Tk()
root.mainloop()

connectSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverSocket = ('localhost', 8000)
print >> sys.stderr, 'connecting to %s port %s' % serverSocket
connectSocket.connect(serverSocket)

class IKSolver():
    def __init__(self, screen):

        self.planknum = 3
        self.screen = screen
        self.FPS = 10 # frames per second setting
        self.fpsClock = pg.time.Clock()

        image1 = pg.image.load('images/greenarm2.png')
        image2 = pg.image.load('images/purplearm2.png')
        image3 = pg.image.load('images/yellowarm2.png')

        image1 = pg.transform.scale(image1, (349,20))
        image2 = pg.transform.scale(image2, (349,20))
        image3 = pg.transform.scale(image3, (349,20))

        self.images = [image1, image2, image3]
        self.plankWidth = image1.get_width()
        self.plankHeight = image1.get_height()
        self.plankScalars = [(int(self.plankWidth * l/175.0), self.plankHeight) for l in PLANK_LEN]

        print self.plankScalars
        self.targetImg = pg.image.load('images/target.png')
        self.endImg = pg.image.load('images/end.png').convert_alpha()
        self.plankAngles = [0]*3
        self.worldAngles = [0]*3
        self.plankPositions = [(0, 0)]*3
        self.plankEnds = [(175, 0)]*3
        self.goal = (-93, 93)

    # convert a point, (x, y) tuple, to a PyGame coordinate
    def pointDisplay(self, p):
        x, y = p
        return (SCREEN_WIDTH/2 + x, SCREEN_HEIGHT/2 - y)

    # convert a point on the screen, (x, y) tuple, to a point in world space
    def pointActual(self, p):
        x, y = p
        return (x - SCREEN_WIDTH/2, -y + SCREEN_HEIGHT/2)

    def cross(self, a, b):
        c = [a[1]*b[2] - a[2]*b[1],
             a[2]*b[0] - a[0]*b[2],
             a[0]*b[1] - a[1]*b[0]]

        return c

    def computeJacobianTranspose(self):
        endx, endy = self.plankEnds[-1]
        jt = []
        for startx, starty in self.plankPositions:
            dx = endx - startx
            dy = endy - starty
            js = self.cross((0, 0, 1), (dx, dy, 0))
            jt.append([js[0], js[1]])
        return jt

    def computeTargetVector(self):
        endx, endy = self.plankEnds[-1]
        targetx, targety = self.goal
        return [targetx-endx, targety-endy]

    def computeRotationVector(self, jacobianTranspose, targetVector):
        rv = []
        for row in jacobianTranspose:
            rv.append(row[0]*targetVector[0] + row[1]*targetVector[1])
        return rv

    def adjustForFramerate(self, v):
        for i in range(len(v)):
            v[i] = v[i] / (120 * float(self.FPS))

        return v

    def rotatePlanks(self, angles):
        for i in range(len(self.plankAngles)):
            self.plankAngles[i] += angles[i]

        self.worldAngles[0] = self.plankAngles[0]
        for a in range(1, len(self.worldAngles)):
            self.worldAngles[a] = self.worldAngles[a-1] + self.plankAngles[a]

        theta = math.radians(self.plankAngles[0])
        x = PLANK_LEN[0] * math.cos(theta)
        y = PLANK_LEN[0] * math.sin(theta)
        self.plankEnds[0] = (x, y)
        for j in range(1, len(self.plankPositions)):
            self.plankPositions[j] = self.plankEnds[j-1]
            x0, y0 = self.plankPositions[j]
            theta += math.radians(self.plankAngles[j])
            x = x0+PLANK_LEN[j] * math.cos(theta)
            y = y0+PLANK_LEN[j] * math.sin(theta)
            self.plankEnds[j] = (x, y)

        #print self.plankPositions
        #print self.plankEnds
        #print self.plankAngles

    def displayPlanks(self):
        for angle, position, scalar, image in zip(self.worldAngles, self.plankPositions, self.plankScalars, self.images):
            stretchedPlank = pg.transform.scale(image, scalar)
            rotatedPlank = pg.transform.rotate(stretchedPlank, angle)
            rotRect = rotatedPlank.get_rect()
            rotRect.center = self.pointDisplay(position)
            self.screen.blit(rotatedPlank, rotRect)
        endRect = self.endImg.get_rect()
        endRect.center = self.pointDisplay(self.plankEnds[-1])
        self.screen.blit(self.endImg, endRect)

    def displayTarget(self):
        x, y = self.goal
        rotRect = self.targetImg.get_rect()
        rotRect.center = self.pointDisplay((x, y))
        self.screen.blit(self.targetImg, rotRect)

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

    plus_x = screen.blit(buttons[2], (660, 133)); #plus_x
    minus_x = screen.blit(buttons[4], (590, 133)); #minus_x
    plus_y = screen.blit(buttons[3], (660, 228)); #plus_y
    minus_y = screen.blit(buttons[5], (590, 228)); #minus_y

    surface = pg.Surface((50,50))
    surface = surface.convert_alpha()
    surface.fill(DARKGREY)
    pg.draw.circle(surface, BLACK, (25, 25), 25)
    pg.draw.circle(surface, paint_color, (25, 25), 23)
    paint_select= screen.blit(surface, (107, 418))

    paint = screen.blit(buttons[6], (42, 418))
    if paint_on:
        paint = screen.blit(buttons[6], (42, 418))
    else:
        paint = screen.blit(buttons[7], (42, 418))

    rotation_buttons = [rotate_ccw_1, rotate_cw_1, rotate_ccw_2, rotate_cw_2, rotate_ccw_3, rotate_cw_3]
    translation_buttons = [plus_x, minus_x, plus_y, minus_y]
    paint_buttons = [paint, paint_select]

    return rotation_buttons, translation_buttons, paint_buttons

def setDrawColor():
    (RGB, hexstr) = askcolor()
    if RGB:
        global paint_color
        paint_color = RGB

def setImageToDraw(screen):
    file_name = askopenfilename()
    print(file_name)
    image_to_draw = pg.image.load(file_name).convert_alpha()
    global scaled_down_image
    scaled_down_image = pg.transform.scale(image_to_draw, (40,40))
    screen.blit(scaled_down_image, (650,387))


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

try:
    """
    message = 'This is the message. It will be repeated.'
    print >> sys.stderr, 'sending "%s"' % message
    connectSocket.sendall(message)

    received = 0
    expected = len(message)

    while(received < expected):
        data = connectSocket.recv(16)
        received += len(data)
        print >> sys.stderr, 'received "%s"' % dat
    """


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
    solver = IKSolver(screen)


    green_arm, purple_arm, yellow_arm, images, buttons, allsprites = initialize()
    rotationVector = [0]*3

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

        print(solver.pointDisplay((int(solver.goal[0]),int(solver.goal[1]))))

        if paint_on:
            pg.draw.circle(surface,paint_color,yellow_arm.end_point, 10)
            pg.draw.circle(surface,paint_color,solver.pointDisplay((int(solver.goal[0]),int(solver.goal[1]))), 10)


        screen.fill(LIGHTBLUE)
        canvas_surface.fill(WHITE)
        screen.blit(surface, (0,0))

        allsprites.update()
        allsprites.draw(screen)
        myfont = pg.font.SysFont("Roboto-Bold", 40)
        label = myfont.render("roBOB ROSS", 1, WHITE)
        screen.blit(label, (295, 22))

        myfont = pg.font.SysFont("Roboto", 20)
        label = myfont.render("A happy little mistake", 1, WHITE)
        screen.blit(label, (285, 500))

        for i, image in enumerate(images):
            width = image.get_rect().width
            height = image.get_rect().height
            if i < 2 :
                screen.blit(image, ((SCREEN_WIDTH/2)-(width/2),(SCREEN_HEIGHT/2)+(CANVAS_WIDTH_HEIGHT/2)-(height)))
            else:
                screen.blit(image, ((SCREEN_WIDTH/2)-(width/2),(SCREEN_HEIGHT/2)-(height/2)))

        rotation_buttons, translation_buttons, paint_buttons = setupButtons(screen, buttons)

        myfont = pg.font.SysFont("Roboto", 14)
        global image_button
        if not image_attached:
            label = myfont.render("Upload", 1, WHITE)
            image_button = screen.blit(label, (628, 434))
        else:
            label = myfont.render("Paint It!", 1, WHITE)
            image_button = screen.blit(label, (622, 434))

        button_list = setupButtons(screen, buttons)
        mouse = pg.mouse.get_pressed()
        pos = pg.mouse.get_pos()

        # move the joints by how much we decided
        solver.rotatePlanks(rotationVector)
        # print the target to the screen
        solver.displayTarget()
        # calculate plank position in real space and display to screen
        solver.displayPlanks()

        # compute the Jacobian Transpose
        jt = solver.computeJacobianTranspose()
        # compute the target vector
        tv = solver.computeTargetVector()
        # compute how far to rotate each joint
        rotationVector = solver.computeRotationVector(jt, tv)
        # adjust for framerate
        rotationVector = solver.adjustForFramerate(rotationVector)

        if mouse[0]:
            if rotation_buttons[0].collidepoint(pos):
                yellow_arm.rotateCCW()
                purple_arm.set_link_center((purple_arm.pivot_point[0], purple_arm.pivot_point[1]))
                green_arm.set_link_center((green_arm.pivot_point[0], green_arm.pivot_point[1]))

            elif rotation_buttons[1].collidepoint(pos):
                yellow_arm.rotateCW()
                purple_arm.set_link_center((purple_arm.pivot_point[0], purple_arm.pivot_point[1]))
                green_arm.set_link_center((green_arm.pivot_point[0], green_arm.pivot_point[1]))

            elif rotation_buttons[2].collidepoint(pos):
                purple_arm.rotateCCW()
                green_arm.set_link_center((green_arm.pivot_point[0], green_arm.pivot_point[1]))

            elif rotation_buttons[3].collidepoint(pos):
                purple_arm.rotateCW()
                green_arm.set_link_center((green_arm.pivot_point[0], green_arm.pivot_point[1]))

            elif rotation_buttons[4].collidepoint(pos):
                green_arm.rotateCCW()

            elif rotation_buttons[5].collidepoint(pos):
                green_arm.rotateCW()

            elif translation_buttons[0].collidepoint(pos):
                print("PLUS X")
                x, y = (solver.goal[0]+1, solver.goal[1])
                solver.goal = (x, y)

            elif translation_buttons[1].collidepoint(pos):
                print("MINUS X")
                x, y = (solver.goal[0]-1, solver.goal[1])
                solver.goal = (x, y)

            elif translation_buttons[2].collidepoint(pos):
                print("PLUS Y")
                x, y = (solver.goal[0], solver.goal[1]+1)
                solver.goal = (x, y)

            elif translation_buttons[3].collidepoint(pos):
                print("MINUS Y")
                x, y = (solver.goal[0], solver.goal[1]-1)
                solver.goal = (x, y)

            elif paint_buttons[0].collidepoint(pos):
                if paint_on:
                    paint_on = False
                else:
                    paint_on = True

            elif paint_buttons[1].collidepoint(pos):
                setDrawColor()

            elif image_button.collidepoint(pos):
                if image_attached:
                    image_attached = False
                else:
                    setImageToDraw(screen)
                    image_attached = True

        if image_attached:
            scaled_down_image = pg.transform.scale(scaled_down_image, (50,50))
            screen.blit(scaled_down_image, (624,360))

        pg.display.flip()

        pg.display.update()
        solver.fpsClock.tick(solver.FPS)


    pg.quit()
    sys.exit()

finally:
    print >> sys.stderr, 'closing socket'
    connectSocket.close()
