import numpy as np
import pygame as pg
import sys
import random
import math
import PIL.Image as Image
pg.init()

# 1. Set up display FIRST
width, height = 600,1200
screen = pg.display.set_mode((width, height))

# 2. THEN load and convert your image
image1 = pg.image.load("sprites/1_ball.png").convert_alpha()
images = [image1]
clock = pg.time.Clock() 

# Draw circle function
ballradius = 20
ballpos = [[100,100], [200,100], [300,100], [400,100], [500,100], [600,100]]
def circle(image, pos, radius):
    px, py = int(pos[0]), int(pos[1])
    for y in range(-radius, radius):
        for x in range(-radius, radius):
            if x*x + y*y <= radius*radius:
                ix = x + radius
                iy = y + radius
                if 0 <= ix < image.get_width() and 0 <= iy < image.get_height():
                    color = image.get_at((ix, iy))
                    sx = px + x
                    sy = py + y
                    if 0 <= sx < width and 0 <= sy < height:
                        screen.set_at((sx, sy), color)

#physics variables
ballvel = [0,0,0,0,0,0]
balldirection = [0,0,0,0,0,0]
balllist = []

class Ball:
    def __init__(self, pos, vel, direction, radius, color):
        self.pos = pos
        self.vel = vel
        self.direction = direction  
        self.radius = radius
        self.color = color
    def move(self):
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

testball = Ball([400,300], 100, math.pi/4, 20, images[0])
balllist.append(testball)
ball2 = Ball([500,300], 0, 0, 20, images[0])
balllist.append(ball2)


# Main loop
while True:
    screen.fill((0,0,0))
    #for i in range(len(ballpos)):
        #circle(colors[i], (ballpos[i]), ballradius)
    for ball in balllist:
        ball.collide(balllist)
        ball.move()
        circle(ball.color, ball.pos, ball.radius)
    pg.display.flip()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
    #print("hello world")
    clock.tick(120)