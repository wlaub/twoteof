"""
From https://web.archive.org/web/20090705003938/http://properundead.com/2009/03/cave-generator.html
"""
import glob, os
import time
import random
import json

import torch
from model import Network

import pygame
import pygame.gfxdraw
from pygame.locals import *

pygame.init()

param_defaults = {
    'expand': 0.85,
    'die': 0.2,
    'decay': 5,
    'bias': 0.5,
}

with open('data.json', 'r') as fp:
    initials = json.load(fp)

class Kernel():
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.weights = {}
        for x in range(-w, w+1):
            for y in range(-h, h+1):
                dist = (abs(x)+abs(y))/(w+h)
                self.weights[(x,y)] = random.random()-dist
        self.normalize()

    def normalize(self):
        value = sum([x for x in self.weights.values() if x > 0])
        for k, v in self.weights.items():
            self.weights[k]/= value

    def compute(self, pos, cells):
        result = 0
        for k, v in self.weights.items():
            key = (k[0] + pos[0], k[1]+pos[1])
            if key in cells:
                result += v
        return result

    def render(self, scale):
        width = self.w*2+1
        height = self.h*2+1

        screen = pygame.Surface((width*scale, height*scale))
        norm = max(self.weights.values())
        nnorm = abs(min(self.weights.values()))
        norm = max(norm, nnorm)

        for (x,y), value in self.weights.items():
            if value > 0:
                color = (0,0,int(255*value/norm))
            else:
                color = (int(255*-value/norm),0,0)
            x += self.w
            y += self.h
            screen.fill(
                color,
                pygame.Rect(
                    x*scale, y*scale,
                    scale, scale)
                )
        return screen

def get_input_vector(pos, cells):
    size = 15
    vector = []
    for dx in range(-size, size+1):
        for dy in range(-size, size+1):
            dpos = (pos[0]+dx, pos[1]+dx)
            if dpos in cells:
                vector.append(1)
            else:
                vector.append(0)
    return vector

#model_2
#size:15
#3x512x512 hidden layers
#
#model_3
#size:15
#4x512x512 hidden layers
#


model = Network().to('cuda')
model.load_state_dict(torch.load('model_3.pth'))

class Cave():
    def __init__(self):
        self.cells = {(0,0)}
        self.dead_cells = set()
        self.bounds = [0,0,0,0]

        self.max_bounds = [-40,40, -40,40]

        self.expand = 0.25
        self.die = 0.2
        self.decay = 5
        self.bias = 0.5

        self.done = False

        self.make_kernels()

    def make_kernels(self):
        self.kernels = {}
        for direction in {(-1,0),(1,0),(0,-1),(0,1)}:
            self.kernels[direction] = Kernel(5,5)

        return

        factor = -0.05
        kernel = self.kernels[(-1,0)]
        for k,v in kernel.weights.items():
            if k[0] < 0 or k[1] != 0:
                kernel.weights[k] *= factor
        kernel.normalize()
        kernel = self.kernels[(1,0)]
        for k,v in kernel.weights.items():
            if k[0] > 0 or k[1] != 0:
                kernel.weights[k] *= factor
        kernel.normalize()
        kernel = self.kernels[(0,1)]
        for k,v in kernel.weights.items():
            if k[1] > 0 or k[0] != 0:
                kernel.weights[k] *= factor
        kernel.normalize()
        kernel = self.kernels[(0,-1)]
        for k,v in kernel.weights.items():
            if k[1] < 0 or k[0] != 0:
                kernel.weights[k] *=factor
        kernel.normalize()


    def expand_bounds(self, x,y):
        self.bounds[0] = min(x, self.bounds[0])
        self.bounds[1] = max(x, self.bounds[1])
        self.bounds[2] = min(y, self.bounds[2])
        self.bounds[3] = max(y, self.bounds[3])

    def test_maxbounds(self, x, y):
        return x <= self.max_bounds[0] or x>= self.max_bounds[1] or y<= self.max_bounds[2] or y >= self.max_bounds[3]

    def get_that_stuff(self):
        ref = initials['g-01']
        xoff = -min(ref, key=lambda x:x[0])[0]
        yoff = -min(ref, key=lambda x:x[1])[1]
        ref = [(x[0]+xoff, x[1]+yoff) for x in ref]

        for x,y in ref:
            self.starting_cells.add((x,y))

    def initialize(self, max_bounds):
        self.max_bounds = max_bounds
        cx = int((max_bounds[1]+max_bounds[0])/2)
        cy = int((max_bounds[2]+max_bounds[3])/2)
        self.iterations = 0
        self.starting_cells = set()
        self.fixed_cells = set()
        self.fixed_cells_ = {
            (43,31),
            (44,31),
            (41,31),
            (42,31),
            (43,32),
            (44,32),
            (41,32),
            (42,32),

            (26,27),
            (26,26),
            (25,27),
            (25,26),

            }

        self.get_that_stuff()

        if False:
            for i in range(-10,10):
                point = (cx+i, cy)
                self.starting_cells.add(point)
            for i in range(0,20):
                point = (cx+i, cy+10)
                self.starting_cells.add(point)
            for i in range(0,10):
                point = (cx+5, cy+i)
                self.starting_cells.add(point)

        self.bounds = [cx,cx,cy,cy]
        for x, y in self.starting_cells:
            self.expand_bounds(x,y)

        self.cells = set(self.starting_cells)

        self.dead_cells = set()


        self.done = False



    def generate(self, max_bounds):
        self.initialize(max_bounds)
        while not self.done:
            self.tick()

    def tick(self):
#        if self.done:
#            return

        pending = set()
        no_options = True
        operation_set = self.cells-self.dead_cells
        expand = self.expand
        die = self.die

        if len(operation_set) >0:
            expand = expand*(self.decay+1)/(self.decay+len(operation_set))

        for x,y in operation_set:
            if False and len(operation_set) > 1 and random.random() < die:
                self.dead_cells.add((x,y))
                continue
            kill_cell = True

            vector = get_input_vector((x,y), self.cells)
            probs = model.get_stuff(vector)

#            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            for (dx, dy), exp_eff in probs.items():
                    tx = x+dx
                    ty = y+dy
                    if (tx,ty) in self.cells: continue
                    if (tx, ty) in self.fixed_cells: continue
                    kill_cell = False
#                    if self.test_maxbounds(tx,ty): continue
                    no_options = False

#                    exp_eff = self.kernels[(dx,dy)].compute((x,y), self.cells)*expand
#                    exp_eff=exp_eff*expand

                    if random.random() < exp_eff*self.expand:
                        pending.add((tx,ty))
                        self.expand_bounds(tx, ty)
                        continue
            if kill_cell:
                self.dead_cells.add((x,y))

        self.cells.update(pending)
        self.iterations += 1
        if no_options or self.iterations > 1000:
            self.done = True
            return



    def render(self, screen, scale, ):
        offset = list(self.get_offset())
        wmax = self.max_bounds[1]-self.max_bounds[0]
        hmax = self.max_bounds[3]-self.max_bounds[2]
        w,h = self.get_size()
        centering = int((wmax-w)/2), int((hmax-h)/2)
        offset[0] += centering[0]
        offset[1] += centering[1]

        bg_color = (192,192,192)
        if not self.validate():
            bg_color = (192,0,0)

        screen.fill(
            bg_color,
            pygame.Rect(
                (centering[0]+1)*scale, (centering[1]+1)*scale,
                (w+1)*scale, (h+1)*scale)
            )

        for x,y in self.cells:
            x += offset[0] + 1
            y += offset[1] + 1
            color = (32,32,32)

            screen.fill(
                color,
                pygame.Rect(
                    x*scale, y*scale,
                    scale, scale)
                )

        for x,y in self.starting_cells:
            x += offset[0] + 1
            y += offset[1] + 1
            color= (128,32,32)

            screen.fill(
                color,
                pygame.Rect(
                    x*scale, y*scale,
                    scale, scale)
                )

        """
        for x,y in self.fixed_cells:
            x += offset[0] + 1
            y += offset[1] + 1
            color= (32,128,32)

            screen.fill(
                color,
                pygame.Rect(
                    x*scale, y*scale,
                    scale, scale)
                )
        """


        koff = scale*2
        for direction, kernel in self.kernels.items():
            kscreen = kernel.render(scale*2)
            kw, kh = kscreen.get_size()
#            res = screen.blit(kscreen, (koff,scale*2))
            koff += kw+scale

    def get_size(self):
        return self.bounds[1] - self.bounds[0], self.bounds[3]-self.bounds[2]

    def get_offset(self):
        return -self.bounds[0], -self.bounds[2]

    def validate(self):
        w,h = self.get_size()
        if w < 40 or h < 23:
            return False
        return True

    def generate_valid(self, bounds, timeout = 100):
        count = 0
        count = 0
        while not self.validate() and count < timeout:
            self.generate(bounds)
            count += 1
        print(f'{count}/{timeout} iterations')

    def export(self):
        offset = list(self.get_offset())
        w,h = self.get_size()
        w+= 1
        h += 1

        tile = 'U'

        lines = [[tile]*w for _ in range(h)]
        for x,y in self.cells:
            x += offset[0]
            y += offset[1]
            try:
                lines[y][x] = '0'
            except:
                print(x,y,w,h)
                raise
        lines = [''.join(l) for l in lines]


        return '\n'.join(lines)

class Slider():
    def __init__(self, x, y, w, h, vmin, vmax, value):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vmin = vmin
        self.vmax = vmax
        self.value = value

    def get_hit(self, x, y):
        if x < self.x or x > self.x+self.w:
            return False
        if y < self.y or y > self.y+self.h:
            return False
        return True

    def on_mouse(self, x, y):
        if not self.get_hit(x,y):
            return False

        alpha = 1-(y-self.y)/self.h
        self.value = self.vmin + alpha*(self.vmax-self.vmin)

    def render(self, screen, indicator=None):
        bg_color = (0,0,0)
        fg_color = (255,255,255)
        line_color = (0,0,0)
        ind_color = (255,0,0)
        screen.fill(
            line_color,
            rect=pygame.Rect(
                self.x-1, self.y-1,
                self.w+2, self.h+2
                )
            )

        screen.fill(
            bg_color,
            rect=pygame.Rect(
                self.x, self.y,
                self.w, self.h
                )
            )

        hfill = int(self.h * (self.value-self.vmin)/(self.vmax-self.vmin))
        screen.fill(
            fg_color,
            rect=pygame.Rect(
                self.x, self.y+self.h-hfill,
                self.w, hfill
                )
            )

        if indicator is None:
            return

        hind = int(self.h * (indicator-self.vmin)/(self.vmax-self.vmin))
        screen.fill(
            ind_color,
            rect = pygame.Rect(
                self.x, self.y+self.h-hind,
                self.w, 1
                )
            )

class Button():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.active = False

    def render(self, screen):
        line_color = (0,0,0)
        bg_color = (128,128,128)
        if self.active:
            bg_color = (255,0,0)
        screen.fill(
            line_color,
            rect=pygame.Rect(
                self.x-1, self.y-1,
                self.w+2, self.h+2
                )
            )

        screen.fill(
            bg_color,
            rect=pygame.Rect(
                self.x, self.y,
                self.w, self.h
                )
            )

    def get_hit(self, x, y):
        if x < self.x or x > self.x+self.w:
            return False
        if y < self.y or y > self.y+self.h:
            return False
        return True

    def on_mouse_down(self, x, y):
        if not self.get_hit(x,y):
            return False
        self.active=True
        return True

    def on_mouse(self, x, y):
        if not self.active:
            return False
        if not self.get_hit(x,y):
            self.active = False
            return False
        return True

    def on_mouse_up(self, x, y):
        if not self.active:
            return False
        self.active = False
        if not self.get_hit(x,y):
            return False
        return True

def get_next_file():
    files = glob.glob('*.cave')
    if len(files) == 0:
        return '0.cave'

    idx = max((int(x.split('.')[0]) for x in files))+1
    return f'{idx}.cave'


bounds = [0, 160, 0, 160]
c= Cave()
c.initialize(bounds)

w,h = 150,150
bounds = [0,w,0,h]
scale = 3

wbase = w*scale
hbase = h*scale

slider_width = 10
slider_height = hbase-80

sliders = {}
sliders['expand'] = Slider(
    wbase + 16 + slider_width, 8,
    slider_width, slider_height,
    0,1,param_defaults['expand']
    )
sliders['die'] = Slider(
    wbase + 16 + slider_width*3, 8,
    slider_width, slider_height,
    0,1,param_defaults['die']
    )
sliders['decay'] = Slider(
    wbase + 16 + slider_width*5, 8,
    slider_width, slider_height,
    1,10,param_defaults['decay']
    )
sliders['bias'] = Slider(
    wbase + 16 + slider_width*7, 8,
    slider_width, slider_height,
    0,1,param_defaults['bias']
    )



buttons = {}
buttons['gen'] = Button(
    wbase + 16+slider_width, 8+slider_height+8,
    slider_width*(2*len(sliders)-1), 20
    )
buttons['export'] = Button(
    wbase + 16+slider_width, 8+slider_height+8+48,
    slider_width*(2*len(sliders)-1), 20
    )



width = wbase + slider_width*(1+2*len(sliders))
height = hbase
screen = pygame.display.set_mode((width+16, height+16))

screen.fill((255,255,255))


while True:
    buttons_hit = set()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                for name, button in buttons.items():
                    button.on_mouse_down(*event.pos)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                for name, button in buttons.items():
                    if button.on_mouse_up(*event.pos):
                        buttons_hit.add(name)


    mleft, mmid, mright = pygame.mouse.get_pressed()
    mpos = pygame.mouse.get_pos()

    if mleft:
        for name, slider in sliders.items():
            slider.on_mouse(*mpos)
        for name, button in buttons.items():
            button.on_mouse(*mpos)

    if 'gen' in buttons_hit:
#        c = Cave()
        c.expand = sliders['expand'].value
        c.die = sliders['die'].value
        c.decay = sliders['decay'].value
        c.bias = sliders['bias'].value
        c.initialize(bounds)
#        c.generate_valid(bounds)
#        print(c.bounds)
#        print(f'{c.expand=}\n{c.die=}\n{c.decay=}\n{c.bias=}')
    if not c.done:
        for _ in range(3):
            c.tick()
        print(c.iterations)

    if 'export' in buttons_hit:
        tilestring = c.export()
        filename = get_next_file()
        with open(filename, 'w') as fp:
            fp.write(tilestring)
        print(f'Wrote {filename}')

    screen.fill((128,128,128))

    sliders['expand'].render(screen, c.expand)
    sliders['die'].render(screen, c.die)
    sliders['decay'].render(screen, c.decay)
    sliders['bias'].render(screen, c.bias)

    for name, button in buttons.items():
        button.render(screen)

    screen.fill(
        (64,64,64),
        pygame.Rect(
            0,0,
            wbase+16, hbase+16,
            )
        )
    screen.fill(
        (255,255,255),
        pygame.Rect(
            8,8,
            wbase, hbase,
            )
        )



    c.render(screen, scale)
    pygame.display.update()
    time.sleep(0.05)
