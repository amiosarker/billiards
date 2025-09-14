import numpy as np
import pygame as pg
import sys
import random
import math
import PIL.Image as Image
pg.init()

framerate = 120

# 1. Set up 
width, height = 400,800
screen = pg.display.set_mode((width, height))
radius = 20

# 2. THEN load and convert your image
image1 = pg.image.load("sprites/1_ball.png").convert_alpha()
image2 = pg.image.load("sprites/2_ball.png").convert_alpha()
images = [image1, image2]
for i in range(len(images)):
    images[i] = pg.transform.scale(images[i], (2*radius, 2*radius))
clock = pg.time.Clock() 

# Draw circle function
def circle(color, pos, radius):
    for i in range(radius*radius*4):
        diameter = radius * 2
        x = i % diameter
        y = i // diameter
        if type(color) == tuple or type(color) == list:
            color2 = color
        else:       
            color2 = color.get_at((x, y))
        if (x-radius)**2 + (y-radius)**2 <= radius**2:
            screen.set_at((int(x+pos[0]), int(y+pos[1])), color2)

# Ball class
class Ball:
    
    def __init__(self, pos, vel, direction, radius, color):
        self.pos = pos
        self.vel = vel
        self.direction = direction  
        self.radius = radius
        self.color = color
        self.initially_pos = pos.copy()
    
    def move(self):
        self.initially_pos = self.pos.copy()  # Make a copy, not a reference
        self.pos[0] += self.vel * math.cos(self.direction)
        self.pos[1] += self.vel * math.sin(self.direction)
        if self.pos[0] <= self.radius or self.pos[0] >= width - self.radius:
            self.direction = math.pi - self.direction
            self.vel *= 0.67
        if self.pos[1] <= self.radius or self.pos[1] >= height - self.radius:
            self.direction = -self.direction
            self.vel *= 0.67
        
        self.pos[0] = max(self.radius, min(width - self.radius, self.pos[0]))
        self.pos[1] = max(self.radius, min(height - self.radius, self.pos[1]))
        self.vel *= 0.99
        if self.vel < 0.5:
            self.vel = 0

    def collide(self, list):
        for i in range(len(list)):
            if list[i] != self:
                dist = math.sqrt((self.pos[0] - list[i].pos[0])**2 + (self.pos[1] - list[i].pos[1])**2)
                if dist <= self.radius + list[i].radius:
                    angle = math.atan2(list[i].pos[1] - self.pos[1], list[i].pos[0] - self.pos[0])
                    total_vel = self.vel + list[i].vel
                    self.direction = angle + math.pi
                    list[i].direction = angle
                    self.vel = total_vel * 0.5
                    list[i].vel = total_vel * 0.5
    def distancecheck(self,position):
        dist = math.sqrt((self.pos[0] - position[0])**2 + (self.pos[1] - position[1])**2)
        return dist

#ballz
ball1 = Ball([300,300], 100, math.pi/4, radius, images[0])
ball2 = Ball([250,300], 0, 0, radius, images[1])

balllist = [ball1, ball2]

#screen
screen.fill((0,0,0))

# Main loop
while True:
    #for i in range(len(ballpos)):
        #circle(colors[i], (ballpos[i]), ballradius)
    mouse = pg.mouse.get_pos()

    for ball in balllist:
        ball.collide(balllist)
        ball.move()
        #print (ball.pos[0]-ball.initially_pos[0])
        circle([0,0,0], ball.initially_pos, ball.radius)
        circle(ball.color, ball.pos, ball.radius)
    pg.display.flip()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
    #print("hello world")
    
    clock.tick(framerate)