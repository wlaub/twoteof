import sys, os
import math
import time
import json
from collections import defaultdict

import tuw
from tuw import render

runs = []
#infile = sys.argv[1]
for infile in {'pristine_1.dump', 'pristine_2.dump'}:
    start_time = time.time()
    states = tuw.StateDump(infile)
    end_time = time.time()

    print(f'{len(states.states)} states loaded in {end_time-start_time:.2f} s')
    print(states.map)
    print(states.chapter)
    print(states.rooms)

    runs.extend(states.extract_sequences(tuw.RoomCompleteRun))

print(f'{len(runs)} total runs')

#for run in runs:
#    print(run.control_flags)

if len(sys.argv) <= 2: exit()
room = sys.argv[2]
filename = None
if len(sys.argv) > 3:
    filename = sys.argv[3]
if room == 'all': room = True

plotter = render.Plotter()

def _filter(x):
    return room is True or x.room == room

room_offsets = {
'g-00': (-355, 469),
'g-01': (-457, 469),
'g-02': (-586, 456),
'g-03b': (-750,388),
'g-04': (-846,456),
'g-05': (-980,419),
'g-06': (-1095,379),
'g-07': (-1141,441),
'g-08': (-1321,522),
#'g-09': (-1455,527),
'g-10': (-1589,502),
'g-11': (-1746,460),
'g-12': (-1838,440),
'g-13': (-1960,547),
}

room_offsets = {k:(v[0]*8, v[1]*8) for k,v in room_offsets.items()}

lock_blocks = {
'g-00': [(560,240),(752,232),(752,264)],
'g-01': [(608,24), (120,160)],
'g-03b': [(384,416)],
'g-05': [(88,0)],
'g-06': [(56,520),(80,656)],
'g-07': [(144,48),(0,1000)],
'g-08': [(1368,176),(888,304),(304,144)],
'g-10': [(320,256),(432,256)],
'g-11': [(184,320)],
'g-12': [(368,320)],
'g-13': [(152,176)],
}

open_blocks = {
'g-01':[
    (808,40,8,56),
    (0,136,8,24),
    ],
'g-03b':[
    (1360,536,40,8),
    (160,536,64,8),
    ],
'g-05':[
    (1056,384,16,16),
    ],
'g-06':[
    (912,384,8,80),
    (912,352,8,24),
    ],
'g-07':[
    (360,72,8,64),
    (0,1056,8,16),
    (0,824,8,40),
    (112,1072,32,40),
    (240,1072,32,40),
    ],
'g-10':[
    (1056,208,16,80),
    ],
'g-11': [
    (1240,488,16,32),
    (1192,528,16,32),
    (1248,560,8,13),
    (72,408,8,24),
    ],
'g-12':[
    (728,536,8,24),
    (728,504,8,24),
    (672,568,8,21),
    (728,616,8,24),
    (360,792,8,24),
    (456,792,8,24),
    (328,296,16,128),
    (336,312,112,16),
    ],
}

fixed_blocks = {
'g-00': [
    (312,320,32,16),
    (200,248,16,16),
    (352,104,32,16),
    (720,336,48,16),
    (0,96,48,16),
    (720,224,48,16),
    ],
'g-01': [
    (600,272,32,16),
    (456,568,32,16),
    (248,472,32,16),
    (400,424,16,16),
    (352,320,16,16),
    (400,272,16,16),
    (328,256,16,16),
    (376,232,16,16),
    (304,216,16,16),
    (360,200,16,16),
    (312,176,16,16),
    (360,152,32,16),
    (768,96,48,16),
    (768,248,16,160),
    (768,512,16,16),
    (0,160,48,16),
    (0,0,16,136),
    (760,32,56,16),
    ],
'g-03b': [
    (1328,432,32,16),
    (1224,352,32,16),
    (1312,280,32,16),
    (1184,208,32,16),
    (1304,128,32,16),
    (992,136,32,16),
    (456,208,32,16),
    (552,192,32,16),
    (784,120,16,16),
    (688,104,32,16),
    (456,208,32,16),
    (304,392,32,16),
    (1312,512,48,32),
    (1408,120,16,72),
    (104,504,56,32),
    (144,504,16,40),
    (0,528,160,16),
    (224,496,16,48),
    (224,528,1096,16),
    (1400,512,16,32),
    (1400,528,80,16),
    ],
'g-05': [
    (824,456,32,16),
    (496,496,32,16),
    (1064,152,16,16),
    (760,192,32,16),
    (416,264,32,16),
    (272,416,16,16),
    (1032,400,40,16),
    (1056,296,16,88),
    (0,144,40,16),
    (24,144,16,88),
    (336,32,32,512),
    ],
'g-06': [
    (768,360,32,16),
    (544,272,32,16),
    (544,496,32,16),
    (208,512,32,16),
    (880,464,48,16),
#   (456,512,128,32),
    (456,512,128,8),
    (128,312,32,232),
    (0,632,40,72),
    (912,376,8,8),
    (912,104,8,246),
    ],
'g-07': [
    (312,136,56,32),
    (312,240,56,32),
#    (240,152,32,192),
#    (112,136i),
    (336,432,32,104),
    (336,616,32,64),
    (240,648,32,16),
    (336,824,32,32),
    (0,1072,112,40),
    (296,944,72,32),
#    (0,624,8,408),
    (0,864,8,192),
    (0,640,8,184),
    (360,0,8,72),
    ],
'g-08': [
    (1384,424,56,32),
    (1208,256,32,32),
    (1208,352,32,32),
    (1320,296,32,32),
    (1384,120,56,56),
    (1080,152,32,32),
    (1384,536,56,32),
    (1112,448,32,16),
    (1112,544,32,16),
    (1112,616,32,32),
    (840,400,32,32),
    (736,360,32,16),
    (704,560,32,16),
    (488,280,16,16),
    (416,264,16,16),
    (896,88,32,16),
    (600,128,32,16),
    (504,88,32,16),
    (400,144,32,16),
    (416,184,16,16),
    (480,208,16,16),
    (400,216,16,16),
    (464,240,16,16),
    (0,144,64,32),
    (0,0,8,128),
    (0,104,24,24),
    ],
'g-10': [
    (1008,288,64,32),
    (880,232,16,72),
    (816,288,32,16),
    (0,184,48,16),
    (1056,184,16,24),
    ],
'g-11': [
    (1208,520,48,16),
    (0,400,72,16),
    (656,600,16,16),
    (664,344,16,16),
    (904,752,32,16),
    (1000,456,32,16),
    (384,416,32,16),
    (1240,328,16,160),
    (1248,520,8,40),
    ],
'g-12': [
    (680,560,56,16),
    (368,784,80,16),
    (288,464,16,16),
    (272,576,32,16),
    (312,168,16,16),
    (728,560,8,56),
    (728,152,8,352),
    ],
'g-13':[
    (1280,104,72,16),
    (1327,385,32,16),
    (1007,121,32,16),
    (1535,313,32,16),
    ],
}

room_tiles = defaultdict(set)
fixed_tiles = defaultdict(set)

room_plotters = defaultdict(render.Plotter)

def map_tile(x,y):
    return math.floor(x/8), math.floor(y/8)

durations = defaultdict(list)
events = defaultdict(lambda: defaultdict(set))

for run in runs:
    if tuw.ControlFlags.dead in run.control_flags:
        continue

    run_room = run.room_order[0]

    durations[run_room].append(run.states[-1].timestamp-run.states[0].timestamp)

    not_dashing = True
    for state in run.states:
        box = render.Plotter._state_box(state)
        center = [box[0] + box[2]/2, box[1]-box[3]/2]
#        center = [box[0] + box[2]/2, box[1]]
        center = map_tile(*center)
        room_tiles[run_room].add(tuple(center))

        if state.state == tuw.PlayerState.dash:
            if not_dashing:
                not_dashing=False
                events[run_room]['dash'].add(center)
        else:
            not_dashing = True


    room_plotters[run_room].add_run(run, lambda x: True)

for room_name, tiles in room_tiles.items():
    xoff, yoff = room_offsets.get(room_name, (0,0))
    for x, y in lock_blocks.get(room_name, []):
        for dx in [8,16]:
            for dy in [8,16]:
                pos = map_tile(xoff+x+dx, yoff+y+dy)
                tiles.add(pos)

    for x, y, w, h in open_blocks.get(room_name, []):
        for dx in range(w):
            for dy in range(h):
                pos = map_tile(xoff+x+dx, yoff+y+dy)
                tiles.add(pos)

    for x, y, w, h in fixed_blocks.get(room_name, []):
        for dx in range(w):
            for dy in range(h):
                pos = map_tile(xoff+x+dx, yoff+y+dy)
                fixed_tiles[room_name].add(pos)
                try:
                    tiles.remove(pos)
                except KeyError: pass

if filename is not None:
    print(f'dumping to {filename}')
    room_tiles = {k:list(v) for k,v in room_tiles.items()}
    fixed_tiles = {k:list(v) for k,v in fixed_tiles.items()}
    event_data = {}
    for room, room_events in events.items():
        event_data[room] = {k:list(v) for k,v in room_events.items()}

    data = {k: {
        'initial_tiles':room_tiles[k],
        'fixed_tiles':fixed_tiles.get(k, []),
        'events': event_data.get(k, {}),
        } for k in room_tiles.keys()}
    with open(filename, 'w') as fp:
        json.dump(data, fp)

for room_name, plotter in room_plotters.items():
    if not room_name in {'g-00'}:
        continue
    plotter.finalize()
    plotter.render(f'{room_name}.png', show=False)

total = 0
print('Durations:')
for room_name, durs in durations.items():
    if not 'g' in room_name: continue
    if '14' in room_name: continue

    avg = sum(durs)/len(durs)
    avg = max(durs)
    total += avg
    print(f'{room_name}: {avg:.2f} ({durs})')
print(f'\nTotal: {total:.2f} s')

