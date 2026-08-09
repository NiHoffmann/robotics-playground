import numpy as np
import time
import matplotlib.pyplot as plt

W = 800     # window width
H = 800     # window height
N = 250     # swarm size
L = 50      # cycle length ("frames")
R = 5       # firefly icon radius
T_MAX = 5000
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

def run_simulation_step(cycle = 0, draw = False):
    flashing_count = 0
    for f in swarm:
        f_c = (cycle + f.c_offset) % L
        f.isFlashing = f_c < (L/2)
        if f.isFlashing: flashing_count += 1
    #time-step "after", aka. all other fireflies already updated
    for f in swarm:
        f_c = (cycle + f.c_offset) % L
        if f_c == 0:
            update_cycle_offset(f)
            
    return flashing_count

def run_simulation(r = 0.05, draw = False):
    init_swarm(r)
    cycle = 0
    currently_flashing = []
    for t in range(T_MAX):
        currently_flashing.append(run_simulation_step(cycle, draw))
        cycle = (cycle + 1) % L
    return currently_flashing

#run_simulation(0.05, draw=True)

distances = [0.05, 0.1, 0.5, 1.4]

def plot_synchronization_over_time():
    for r in distances:
        flashing_data = run_simulation(r, draw = False)
        plt.clf()
        plt.ylim(0, N+1)
        plt.xlabel('Time')
        plt.ylabel('Currently flashing fireflies')
        plt.title('Firefly synchronization simulation')
        plt.plot(range(0, T_MAX), flashing_data, linestyle='-', label = f'r:{r}')
        plt.legend()
        plt.savefig(f'sync_over_time_{r}.png')
        print("sync_over_time.png saved")

#don't execute this. We use C for this - better performance. See amplitude_sweep.c / amplitude_sweep_plot.py
def analyze_sync_amplitude():
    amplitudes = []
    distances = np.arange(0.05, 1.4, 0.025)
    for r in distances:
        minimum = 0
        maximum = 0
        for i in range(0,50):
            flashing_data = run_simulation(r, draw = False)
            last_50 = flashing_data[-50:]
            minimum += min(last_50)
            maximum += max(last_50)
        minimum /= 50
        maximum /= 50
        amplitudes.append((maximum - minimum) / 2)
        print(r)

    plt.clf()
    plt.xlabel('Distance (r)')
    plt.ylabel('Amplitude')
    plt.title('Amplitude Plot')
    plt.plot(distances, amplitudes, linestyle='-')
    plt.savefig(f'sync_amplitude.png')

plot_synchronization_over_time()
analyze_sync_amplitude()
