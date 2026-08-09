import numpy as np
import time
import matplotlib.pyplot as plt
from tkinter import *

W = 800     # window width
H = 800     # window height
N = 250     # swarm size
L = 50      # cycle length ("frames")
R = 5       # firefly icon radius
T_MAX = 2000
FPS_TARGET = 60
T_DELTA_MS = 1000 / FPS_TARGET

class Firefly:
    x: float = 0
    y: float = 0
    isFlashing = False
    c_offset: int = 0
    neighbours = []

swarm = []

def init_swarm(r = 0.05):
    swarm.clear()
    for _ in range(N):
        f = Firefly()
        f.x = np.random.random()
        f.y = np.random.random()
        f.c_offset = int(np.random.random()*50)
        swarm.append(f)

    # find neighbours in range
    n_count = 0
    for f in swarm:
        for n in swarm:
            if n == f: continue
            dist = np.sqrt(np.power(f.x - n.x, 2) + np.power(f.y - n.y, 2))
            if(dist <= r):
                f.neighbours.append(n)
                n_count += 1

def update_cycle_offset(f: Firefly = None):
    flashing_neighbours = 0
    for n in f.neighbours:
        if n.isFlashing:
            flashing_neighbours += 1
    flashing_percent = flashing_neighbours / len(f.neighbours)
    if flashing_percent > 0.5:
        f.c_offset += 1
    else:
        f.c_offset -= 1

def run_simulation_step(canvas: Canvas, cycle = 0, draw = False):
    if draw: canvas.delete("all")
    flashing_count = 0
    for f in swarm:
        f_c = (cycle + f.c_offset) % L
        f.isFlashing = f_c < (L/2)
        if f.isFlashing: flashing_count += 1
        if draw: canvas.create_oval(f.x*W-R, f.y*H-R, f.x*W+R, f.y*H+R, width=0, fill='orange' if f.isFlashing else 'black')
        if f_c == 0:
            update_cycle_offset(f)
    return flashing_count

def run_simulation(r = 0.05, draw = False):
    init_swarm(r)
    cycle = 0
    canvas: Canvas = None
    currently_flashing = []
    if draw:
        window = Tk()
        window.geometry(f'{W}x{H}')
        window.title("Firefly simulation")
        window.resizable(False, False)
        canvas = Canvas(window, width=W, height=H)
        canvas.pack(pady=20)
        canvas.config(bg='white')
    for t in range(T_MAX):
        currently_flashing.append(run_simulation_step(canvas, cycle, draw))
        cycle = (cycle + 1) % L
        if draw: 
            canvas.create_text(W/2,20,text=f'r={r}  t={t}, flashing: {currently_flashing[len(currently_flashing)-1]}', font=("Arial", 20))
            window.update()
            time.sleep(T_DELTA_MS / 1000)
    return currently_flashing

run_simulation(0.5, draw=True)
