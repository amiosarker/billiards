import numpy as np
import pygame as pg
import sys
import random
import math
import PIL.Image as Image
import os, re
pg.init()
os.chdir("/Users/amiosarker/dev/Programing/python/billiards/indexed_sprites")
win = False
framerate = 120
frame = 0
time_frame = 0
power = 0
pressed = False
gameover = False
totalvel = False
lose = False
win = False

# 1. Set up 
screeninfo = pg.display.Info()
screenwidth, screenheight = screeninfo.current_w, screeninfo.current_h
width, height = 464,864
edgecoliderx, edgecolidery = 400,800
screen = pg.display.set_mode((screenwidth, screenheight), pg.RESIZABLE)
radius = 20
hole_radius = 20
playareaoffset = [int(screenwidth/2 - width/2), int(screenheight/2 - height/2)]
filelist = []

for file in os.listdir():
    if file.endswith(".png"):
        filelist.append(file)

def natural_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

filelist.sort(key=natural_key)

for i in range(len(filelist)):
    filename = filelist[i]
    img = pg.image.load(filename).convert_alpha()
    if "ball" in filename:
        img = pg.transform.scale(img, (2*radius, 2*radius))
    filelist[i] = img

temp_surface = pg.Surface(screen.get_size(), pg.SRCALPHA)

filelist[19]=pg.transform.scale(filelist[19],(int(filelist[19].get_width()/3),int(filelist[19].get_height()/3)))

def mapvalues(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

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
    
    def __init__(self, pos, vel, direction, radius, color,list):
        self.pos = pos
        self.vel = vel
        self.direction = direction  
        self.radius = radius
        self.color = color
        self.initially_pos = pos.copy()
        self.list = list
        self.bool = False
        
    
    def move(self):
        self.initially_pos = self.pos.copy()  # Make a copy, not a reference
        self.pos[0] += self.vel * math.cos(self.direction)
        self.pos[1] += self.vel * math.sin(self.direction)
        if self.pos[0] <= self.radius or self.pos[0] >= width:
            self.direction = math.pi - self.direction
            self.vel *= 0.45
        if self.pos[1] <= self.radius or self.pos[1] >= height:
            self.direction = -self.direction
            self.vel *= 0.45
        
        
        self.pos[0] = max(self.radius+32, min(edgecoliderx+self.radius, self.pos[0]))
        self.pos[1] = max(self.radius+32, min(edgecolidery + self.radius, self.pos[1]))
        self.vel *= 0.95
        if self.vel < 0.5:
            self.vel = 0

    def collide(self, list):
        global win
        for i in range(len(list)):
            if list[i] != self:
                dist = math.sqrt((self.pos[0] - list[i].pos[0])**2 + (self.pos[1] - list[i].pos[1])**2)
                if dist <= self.radius + list[i].radius:
                    angle = math.atan2(list[i].pos[1] - self.pos[1], list[i].pos[0] - self.pos[0])
                    total_vel = self.vel + list[i].vel
                    self.direction = angle + math.pi
                    list[i].direction = angle
                    self.vel = total_vel * 0.45
                    list[i].vel = total_vel * 0.45
                    
                    
    
    def distancecheck(self,position):
        dist2 = math.sqrt((self.pos[0] - position[0])**2 + (self.pos[1] - position[1])**2)
        return dist2
    
    def weirdcollison(self, balls):
        ax, ay = self.initially_pos
        bx, by = self.pos
        for ball in balls:
            if ball is self:
                continue

            px, py = ball.pos

            # Vector AB (ball's path) and AP (to other ball)
            ABx, ABy = bx - ax, by - ay
            APx, APy = px - ax, py - ay

            AB_len_sq = ABx**2 + ABy**2
            if AB_len_sq == 0:
                continue  # ball didn't move

            # Project AP onto AB → find t in [0,1]
            t = max(0, min(1, (APx*ABx + APy*ABy) / AB_len_sq))

            # Closest point on the segment to P
            closest_x = ax + t * ABx
            closest_y = ay + t * ABy

            # Distance from ball center to path segment
            dx = px - closest_x
            dy = py - closest_y
            distance = (dx**2 + dy**2) ** 0.5

            if distance <= self.radius + ball.radius:
                # Collision!
                angle = math.atan2(ball.pos[1] - self.pos[1],
                                ball.pos[0] - self.pos[0])
                total_vel = self.vel + ball.vel

                self.direction = angle + math.pi
                ball.direction = angle
                self.vel = total_vel * 0.45
                ball.vel = total_vel * 0.45
                self.bool = True
                break

class hole:
    def __init__(self, pos,hradius,tolerence,offset):
        self.pos = pos
        self.pocketed = False
        self.radius = hradius
        self.tolerence = tolerence
        self.clock = 0
        self.offset = offset
    def pocket(self,cueball, eightball,ball):
        global gameover, lose, time_frame, win, balllist
        if ball.distancecheck([self.pos[0]+self.radius, self.pos[1]+self.radius]) < self.radius * self.tolerence:

            if ball != eightball:
                balllist.remove(ball)
                if ball != cueball:
                    self.pocketed = True
                print("pocketed")
            else:  # ball == eightball
            # count how many object balls are still left
                object_balls_left = [b for b in balllist if b not in (cueball, eightball)]

                if len(object_balls_left) > 0:
                    print("you lose")
                    gameover = True
                    lose = False
                    time_frame = 0   # reset fade counter
                else:
                    balllist.remove(ball)
                    print("you win")
                    gameover = False
                    win = True

                    setuop()
    def imagefadein (self,drawnimage):
        mainbool = False
        global screen,playareaoffset
        if self.pocketed:
            
            if self.clock < 255:
                self.clock +=15
                mainbool = True
            if self.clock >= 255:
                self.clock = 0
                self.pocketed = False
            drawnimage.set_alpha(min(self.clock, 255))
            screen.blit(drawnimage, (self.pos[0]-int(drawnimage.get_width()/2)+25+playareaoffset[0],self.pos[1]-int(drawnimage.get_height()/2)+15+playareaoffset[1]))
            #screen.blit(drawnimage, (self.pos[0]+self.offset[0],self.pos[1]+self.offset[1]))
            

balllist = []

rack_positions = [
    # Row 1
    
    # Row 2
    [207, 329], [257, 329],
    # Row 3
    [182, 286], [282, 286],
    # Row 4
    [157, 243], [207, 243], [257, 243], [307, 243],
    # Row 5
    [132, 200], [182, 200], [232, 200], [282, 200], [332, 200],[232, 372], [232, 286]
]

initial_rack_positions = rack_positions.copy()
cue_ball_pos = [232, 664]

topl = hole([45-radius,47-radius],hole_radius,1.5,[25,15])
topr = hole([419-radius,47-radius],hole_radius,1.5,[0,0])
bottoml = hole([45-radius,817-radius],hole_radius,1.5,[50,-50])
bottomr = hole([419-radius,817-radius],hole_radius,1.5,[25,15])
middlel = hole([45-radius,432-radius],hole_radius,1.5,[25,15])
middler = hole([419-radius,432-radius],hole_radius,1.5,[-50,0])
holes = [topl,topr,bottoml,bottomr,middlel,middler,]
#ballz

ball1 = Ball(rack_positions[0], 0, 0, radius, filelist[1],balllist)
ball2 = Ball(rack_positions[1], 0, 0, radius, filelist[2],balllist)
ball3 = Ball(rack_positions[2], 0, 0, radius, filelist[3],balllist)
ball4 = Ball(rack_positions[3], 0, 0, radius, filelist[4],balllist)
ball5 = Ball(rack_positions[4], 0, 0, radius, filelist[5],balllist)
ball6 = Ball(rack_positions[5], 0, 0, radius, filelist[6],balllist)
ball7 = Ball(rack_positions[6], 0, 0, radius, filelist[7],balllist)
ball8 = Ball(rack_positions[12], 0, 0, radius, filelist[8],balllist)
ball9 = Ball(rack_positions[7], 0, 0, radius, filelist[9],balllist)
ball10 = Ball(rack_positions[8], 0, 0, radius, filelist[10],balllist)   
ball11 = Ball(rack_positions[9], 0, 0, radius, filelist[11],balllist)
ball12 = Ball(rack_positions[10], 0, 0, radius, filelist[12],balllist)
ball13 = Ball(rack_positions[11], 0, 0, radius, filelist[13],balllist)
ball14 = Ball(rack_positions[13], 0, 0, radius, filelist[14],balllist)
ball15 = Ball(rack_positions[14], 0, 0, radius, filelist[15],balllist)  

cue_ball = Ball(cue_ball_pos, 0, 0, radius, filelist[0],balllist)

balllist = [ ball1,ball2, ball3, ball4, ball5, ball6, ball7, ball9, ball10, ball11, ball12, ball13, ball14, ball15,ball8, cue_ball]



def setuop():
    global balllist  # we will update the global list in-place / make sure it's the current one

    # defensive deep-ish copy of initial positions (so nested lists aren't aliased)
    available_positions = [pos.copy() for pos in initial_rack_positions]

    # reserve the fixed positions for ball1 and ball8 (remove them from available pool)
    reserved1 = [232, 372]
    reserved8 = [232, 286]
    if reserved1 in available_positions:
        available_positions.remove(reserved1)
    if reserved8 in available_positions:
        available_positions.remove(reserved8)

    random.shuffle(available_positions)

    # the balls we want to randomly place (13 of them)
    normal_balls = [ball2, ball3, ball4, ball5, ball6, ball7,
                    ball9, ball10, ball11, ball12, ball13, ball14, ball15]

    # sanity check: lengths must match
    if len(available_positions) < len(normal_balls):
        raise RuntimeError("Not enough available positions to place normal_balls")

    # assign shuffled positions
    for i, ball in enumerate(normal_balls):
        pos = available_positions[i]
        ball.pos = pos.copy()
        ball.initially_pos = pos.copy()
        ball.vel = 0
        ball.direction = 0

    # assign fixed positions for ball1 and ball8
    ball1.pos = reserved1.copy()
    ball1.initially_pos = reserved1.copy()
    ball1.vel = 0
    ball1.direction = 0

    ball8.pos = reserved8.copy()
    ball8.initially_pos = reserved8.copy()
    ball8.vel = 0
    ball8.direction = 0

    # cue ball
    cue_ball.pos = cue_ball_pos.copy()
    cue_ball.initially_pos = cue_ball_pos.copy()
    cue_ball.vel = 0
    cue_ball.direction = 0

    # rebuild global balllist in the order you prefer
    # (make sure this order matches everywhere else in your code)
    balllist = [
        ball1, ball2, ball3, ball4, ball5, ball6, ball7,
        ball8, ball9, ball10, ball11, ball12, ball13, ball14, ball15,
        cue_ball
    ]
    # no return — we've updated the global balllist
#screen
background = filelist[16]
screen.fill((0,0,255))
screen.blit(background, (0,0))
pocket_time = 0

cue_ball.vel = 0

mouse_on_cueball = False
active_image =18
setuop()
# Main loop

while True:
    playareaoffset = [int(screenwidth/2 - width/2), int(screenheight/2 - height/2)]
    normalmouse = pg.mouse.get_pos()
    mouse = (normalmouse[0]-playareaoffset[0],normalmouse[1]-playareaoffset[1])

    mouse_buttons = pg.mouse.get_pressed()
    if gameover:
        # Fade in the "you lose" image
        if time_frame < 255:
            time_frame += 5
        if win :
            active_image = 17
        if lose:
            active_image = 18
        filelist[active_image].set_alpha(time_frame)
        
        for i in range(len(balllist)):
            circle(balllist[i].color, [balllist[i].pos[0]-balllist[i].radius+playareaoffset[0], balllist[i].pos[1]-balllist[i].radius+playareaoffset[1]], balllist[i].radius)
        screen.blit(filelist[active_image], (width/2 - 150+playareaoffset[0], height/2 - 150+playareaoffset[1]))

        if time_frame >= 255:
            # Wait a bit, then reset
            pg.time.delay(1000)  # 1 second pause
            setuop()
            gameover = False
    if cue_ball.distancecheck(mouse) < 2*radius:
        mouse_on_cueball = True
    if not gameover:
        if not totalvel:
            angle = (math.atan2(mouse[1] - cue_ball.pos[1], mouse[0] - cue_ball.pos[0]))+math.pi
            cue_ball.direction = angle
        
            if mouse_buttons[0] and mouse_on_cueball:
                pressed = True
                frame += 0.5
                power = (cue_ball.distancecheck(mouse)/2)+frame
                color = (cue_ball.distancecheck(mouse)/2)+frame

                temp_surface.fill((0, 0, 0, 0))  # <-- Clear the temp_surface here

                pg.draw.line(screen, (255,255,255), (cue_ball.pos[0]+playareaoffset[0], cue_ball.pos[1]+playareaoffset[1]), (mouse[0]+playareaoffset[0], mouse[1]+playareaoffset[1]), int(mapvalues(power,0,100,5,14)))
                pg.draw.line(screen, (min(color,255),0,0), (cue_ball.pos[0]+playareaoffset[0], cue_ball.pos[1]+playareaoffset[1]), (mouse[0]+playareaoffset[0], mouse[1]+playareaoffset[1]), int(mapvalues(power,0,100,4,10)))
                line_length = ((power - frame)*1.5)+frame
                
                end_x = cue_ball.pos[0] + line_length * math.cos(cue_ball.direction)
                end_y = cue_ball.pos[1] + line_length * math.sin(cue_ball.direction)

                pg.draw.line(
                    temp_surface, 
                    (255, 255, 255, 128), 
                    (cue_ball.pos[0]+playareaoffset[0], cue_ball.pos[1]+playareaoffset[1]), 
                    (end_x+playareaoffset[0], end_y+playareaoffset[1]), 
                    5
                )
                power = min(power, 100)
                mouse_on_cueball = True
                screen.blit(temp_surface, (0, 0))
            else:
                cue_ball.vel = power 
                mouse_on_cueball = False
                if power != 0:
                    print("power:", power)  
                power = 0
                frame = 0
                pressed = False
        if frame > 0 and not pressed:
            frame = 0
            power = 0
        #ballz
        for ball in balllist:
            
            ball.collide(balllist)
            ball.move()
            ball.weirdcollison(balllist)
            #print (ball.pos[0]-ball.initially_pos[0])
            #circle([0,0,255], [ball.initially_pos[0]-ball.radius,ball.initially_pos[1]-ball.radius], ball.radius)
            circle(ball.color, [ball.pos[0]-ball.radius+playareaoffset[0],ball.pos[1]-ball.radius+playareaoffset[1]], ball.radius)
            topl.pocket(cue_ball,ball8,ball)  
            topr.pocket(cue_ball,ball8,ball) 
            bottoml.pocket(cue_ball,ball8,ball) 
            bottomr.pocket(cue_ball,ball8,ball) 
            middlel.pocket(cue_ball,ball8,ball) 
            middler.pocket(cue_ball,ball8,ball)  
            
            if ball.vel > 0:
                totalvel = True
            else:
                totalvel = False

        # control cue ball   

            
            #print(cue_ball.vel) 

        cueball_pocketed = cue_ball not in balllist  

    # only reset when all balls have stopped AND cueball is missing
        if cueball_pocketed and not totalvel:
            screen.blit(background, playareaoffset)
            for i in range(len(balllist)):
                circle(balllist[i].color, [balllist[i].pos[0]-balllist[i].radius+playareaoffset[0],balllist[i].pos[1]-balllist[i].radius+playareaoffset[1]], balllist[i].radius)
            # short pause so the pocket feels real
            balllist.append(cue_ball)
            cue_ball.pos = cue_ball_pos.copy()
            cue_ball.initially_pos = cue_ball_pos.copy()
            cue_ball.vel = 0
            cue_ball.direction = 0
            print("cue ball added back")
        

    if balllist == [cue_ball]:
        screen.blit(background, playareaoffset)
        screen.blit(filelist[17],playareaoffset)
        screen.blit(filelist[17],(width/2-150+playareaoffset,height/2-150+playareaoffset))
        pg.time.delay(500)
        win = True
        setuop()
        print("you win")
    for i in range(len(holes)):
        holes[i].imagefadein(filelist[19])
    # reset
    pg.display.flip()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:  # press ESC to exit fullscreen
                running = False
        elif event.type == pg.VIDEORESIZE:
            screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
            screenwidth,screenheight = event.w,event.h
    #print("hello world")
   
    
    screen.fill((0,0,0))
    screen.blit(background, playareaoffset)
    
    clock.tick(framerate)
    