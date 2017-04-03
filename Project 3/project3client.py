import socket
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
rotatingArm = -1


paint_on = True
image_attached = False
PLANK_LEN = [175, 175, 175]

global image_to_draw
scaled_down_image = pg.image.load("images/whitesquare.png")

root = Tk()
root.mainloop()

# CLIENT
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

    images = [base, bob_ross]

    return images

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

    images = initialize()
    rotationVector = [0]*3

    while True:
        data = connectSocket.recv(1)

        # once the server closes, close the client
        # works, but causes issues when starting another game if not done properly
        """
        if data == "":
            connectSocket.close()
            pg.quit()
            sys.exit()
        """

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

        width = images[0].get_rect().width
        height = images[0].get_rect().height
        width = images[1].get_rect().width
        height = images[1].get_rect().height
        screen.blit(images[0], ((SCREEN_WIDTH/2)-(width/2),(SCREEN_HEIGHT/2)+(CANVAS_WIDTH_HEIGHT/2)-(height)))
        screen.blit(images[1], ((SCREEN_WIDTH/2)-(width/2),(SCREEN_HEIGHT/2)+(CANVAS_WIDTH_HEIGHT/2)-(height)))


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


        if data:
            if data == "0":
                rotatingArm = 2
                solver.plankAngles[2] = solver.plankAngles[2] + 1

            elif data == "1":
                rotatingArm = 2
                solver.plankAngles[2] = solver.plankAngles[2] - 1

            elif data == "2":
                rotatingArm = 1
                solver.plankAngles[1] = solver.plankAngles[1] + 1

            elif data == "3":
                rotatingArm = 1
                solver.plankAngles[1] = solver.plankAngles[1] - 1

            elif data == "4":
                rotatingArm = 0
                solver.plankAngles[0] = solver.plankAngles[0] + 1

            elif data == "5":
                rotatingArm = 0
                solver.plankAngles[0] = solver.plankAngles[0] - 1

            elif data == "6":
                rotatingArm = -1
                x, y = (solver.goal[0]+1, solver.goal[1])
                solver.goal = (x, y)

            elif data == "7":
                rotatingArm = -1
                x, y = (solver.goal[0]-1, solver.goal[1])
                solver.goal = (x, y)

            elif data == "8":
                rotatingArm = -1
                x, y = (solver.goal[0], solver.goal[1]+1)
                solver.goal = (x, y)

            elif data == "9":
                rotatingArm = -1
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

    connectSocket.close()
    pg.quit()
    sys.exit()
