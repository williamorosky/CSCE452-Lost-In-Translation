import socket
import sys
import time

import math
import pygame as pg
from Tkinter import *
from tkFileDialog import askopenfilename
from tkColorChooser import askcolor

# default delay is turned off.
# when true, delay is approximately 2 seconds
#delay = False

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
rotatingArm = -1


paint_on = True
image_attached = False
PLANK_LEN = [175, 175, 175]

global image_to_draw
scaled_down_image = pg.image.load("images/whitesquare.png")

root = Tk()
root.mainloop()

# SERVER
connectSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverSocket = ('localhost', 8000)
print >> sys.stderr, 'initializing server socket on %s port %s' % serverSocket
connectSocket.bind(serverSocket)

connectSocket.listen(5)

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

    def rotatePlanks(self, angles, rotating):
        if rotating == -1:
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
        else:
            self.plankAngles[0] += angles[0]
            if rotating == 0:
                self.worldAngles[0] = self.plankAngles[0]
                for i in range(1, len(self.worldAngles)):
                    self.worldAngles[i] = self.worldAngles[i-1] + self.plankAngles[i]
            else:
                for rotating in range(1, len(self.worldAngles)):
                    self.worldAngles[rotating] = self.worldAngles[rotating-1] + self.plankAngles[rotating]

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

    images = [base, bob_ross, button_backgrounds]
    buttons = [rotate_ccw, rotate_cw, plus_x, plus_y, minus_x, minus_y, paint_on, paint_off]

    return images, buttons

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
    solver = IKSolver(screen)


    images, buttons = initialize()
    rotationVector = [0]*3

    print >> sys.stderr, 'awaiting connection'
    (clientSocket, clientAddress) = connectSocket.accept()

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

        if paint_on:
            pg.draw.circle(surface,paint_color,solver.pointDisplay((int(solver.goal[0]),int(solver.goal[1]))), 10)
            if not rotatingArm == -1:
                pg.draw.circle(surface,paint_color,solver.pointDisplay((int(solver.plankEnds[2][0]),int(solver.plankEnds[2][1]))), 10)

        screen.fill(LIGHTBLUE)
        canvas_surface.fill(WHITE)
        screen.blit(surface, (0,0))

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
        solver.rotatePlanks(rotationVector, rotatingArm)
        # print the target to the screen
        solver.displayTarget()
            # calculate plank position in real space and display to screen
        solver.displayPlanks()

        if rotatingArm == -1:
            # compute the Jacobian Transpose
            jt = solver.computeJacobianTranspose()
            # compute the target vector
            tv = solver.computeTargetVector()
            # compute how far to rotate each joint
            rotationVector = solver.computeRotationVector(jt, tv)
            # adjust for framerate
            rotationVector = solver.adjustForFramerate(rotationVector)
        else:
            solver.goal = solver.plankEnds[2]
            # solver.computeTargetVector()


        if mouse[0]:
            if rotation_buttons[0].collidepoint(pos):
                rotatingArm = 2
                solver.plankAngles[2] = solver.plankAngles[2] + 1
                clientSocket.send("0")
                """
                Serverside Delay code if we need it.
                if delay == True:
                    time.sleep(2)
                    clientSocket.send("0")
                elif delay == False:
                    clientSocket.send("0")
                """
            elif rotation_buttons[1].collidepoint(pos):
                rotatingArm = 2
                solver.plankAngles[2] = solver.plankAngles[2] - 1
                clientSocket.send("1")

            elif rotation_buttons[2].collidepoint(pos):
                rotatingArm = 1
                solver.plankAngles[1] = solver.plankAngles[1] + 1
                clientSocket.send("2")

            elif rotation_buttons[3].collidepoint(pos):
                rotatingArm = 1
                solver.plankAngles[1] = solver.plankAngles[1] - 1
                clientSocket.send("3")

            elif rotation_buttons[4].collidepoint(pos):
                rotatingArm = 0
                solver.plankAngles[0] = solver.plankAngles[0] + 1
                clientSocket.send("4")

            elif rotation_buttons[5].collidepoint(pos):
                rotatingArm = 0
                solver.plankAngles[0] = solver.plankAngles[0] - 1
                clientSocket.send("5")

            elif translation_buttons[0].collidepoint(pos):
                rotatingArm = -1
                x, y = (solver.goal[0]+1, solver.goal[1])
                solver.goal = (x, y)
                clientSocket.send("6")

            elif translation_buttons[1].collidepoint(pos):
                rotatingArm = -1
                x, y = (solver.goal[0]-1, solver.goal[1])
                solver.goal = (x, y)
                clientSocket.send("7")

            elif translation_buttons[2].collidepoint(pos):
                rotatingArm = -1
                x, y = (solver.goal[0], solver.goal[1]+1)
                solver.goal = (x, y)
                clientSocket.send("8")

            elif translation_buttons[3].collidepoint(pos):
                rotatingArm = -1
                x, y = (solver.goal[0], solver.goal[1]-1)
                solver.goal = (x, y)
                clientSocket.send("9")

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

    clientSocket.close();
    pg.quit()
    sys.exit()
