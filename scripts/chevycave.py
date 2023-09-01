"""
From https://web.archive.org/web/20090705003938/http://properundead.com/2009/03/cave-generator.html
"""

import time
import random

class Cave():


    def __init__(self):
        self.cells = {(0,0)}
        self.dead_cells = set()
        self.bounds = [0,0,0,0]

        self.max_bounds = [-40,40, -40,40]

    def expand_bounds(self, x,y):
        self.bounds[0] = min(x, self.bounds[0])
        self.bounds[1] = max(x, self.bounds[1])
        self.bounds[2] = min(y, self.bounds[2])
        self.bounds[3] = max(y, self.bounds[3])

    def test_maxbounds(self, x, y):
        return x <= self.max_bounds[0] or x>= self.max_bounds[1] or y<= self.max_bounds[2] or y >= self.max_bounds[3]

    def generate(self, max_bounds):
        self.max_bounds = max_bounds
        cx = int((max_bounds[1]+max_bounds[0])/2)
        cy = int((max_bounds[2]+max_bounds[3])/2)
        iterations = 0
        self.cells = {(cx,cy)}
        self.dead_cells = set()
        self.bounds = [cx,cx,cy,cy]


        while True:
            pending = set()
            no_options = True
            operation_set = self.cells-self.dead_cells
            expand = 0.3
            die = 0.2

            if len(operation_set) >0:
                a = 5
                expand = (a+1)/(a+len(operation_set))

            for x,y in operation_set:
                if len(operation_set) > 1 and random.random() < die:
                    self.dead_cells.add((x,y))
                    continue
                for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                        tx = x+dx
                        ty = y+dy
                        if (tx,ty) in self.cells: continue
                        if self.test_maxbounds(tx,ty): continue
                        no_options = False
                        if tx != 0:
                            exp_eff = expand
                        else:
                            exp_eff = expand/4
                        if random.random() < exp_eff:
                            pending.add((tx,ty))
                            self.expand_bounds(tx, ty)

            self.cells.update(pending)
            iterations+= 1
            if no_options or iterations > 1000:
                break

    def render(self, screen, scale):
        offset = self.get_offset()
        for x,y in self.cells:
            x += offset[0]
            y += offset[1]

            screen.fill(
                (128,128,128),
                pygame.Rect(
                    x*scale, y*scale,
                    scale, scale)
                )

    def get_size(self):
        return self.bounds[1] - self.bounds[0], self.bounds[3]-self.bounds[2]

    def get_offset(self):
        return -self.bounds[0], -self.bounds[2]

    def validate(self):
        w,h = self.get_size()
        if w < 40 or h < 23:
            return False
        return True

bounds = [0, 80, 0, 80]
c= Cave()
c.generate(bounds)
count = 0
while not c.validate() and count < 100:
    c.generate(bounds)
    print(count)
    count += 1
print(len(c.cells))
print(c.bounds)

import pygame
import pygame.gfxdraw
from pygame.locals import *

pygame.init()

w,h = c.get_size()
scale = 8

width, height = w*scale, h*scale
screen = pygame.display.set_mode((width+8, height+8))

screen.fill((255,255,255))


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
    screen.fill((255,255,255))
    c.render(screen, scale)
    pygame.display.update()
    time.sleep(0.1)

