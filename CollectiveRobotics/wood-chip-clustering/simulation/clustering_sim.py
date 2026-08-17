import subprocess
import pygame
import numpy as np
import random
import matplotlib.pyplot as plt
import sys

#for capture.
RECORDING = False

#Adjust CELL_SIZE to scale PyGame-Window
CELL_SIZE = 15

#dont modify 
COLOR_BG = (80, 60, 40)
COLOR_OBJECT = (0, 128, 0)
COLOR_AGENT = (0, 255, 0)
COLOR_ANTI_AGENT = (255, 0, 0)
#60Hz max. Probably won't go a lot faster anyways.
SIM_STEPS_PER_SECOND = 1000

#begin modify
PERCENT_ANTI_AGENTS = 0.1
GRID_SIZE = 50
NUM_OBJECTS = 500
NUM_AGENTS = 50
SIM_STEPS = 100000 #10k and 100k respectively
P_PICK = 0.05
P_DROP = 0.95
VISION_RADIUS = 2
ITERRATION = 100
#end modify

#dont change this
NUM_ANTI_AGENTS = int(NUM_AGENTS * PERCENT_ANTI_AGENTS)
WINDOW_SIZE = GRID_SIZE * CELL_SIZE

grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

object_positions = random.sample([(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)], NUM_OBJECTS)
for x, y in object_positions:
    grid[x, y] = 1

class Agent:
    p_density = 0.15
    p_pick = P_PICK
    p_drop = P_DROP
    vision_r = VISION_RADIUS
    carrying = False
    
    def __init__(self, is_anti=False):
        self.x = random.randint(0, GRID_SIZE - 1)
        self.y = random.randint(0, GRID_SIZE - 1)
        self.is_anti = is_anti

    #move robot. we dont care about collision. Ants also crawl over each other :D and im lazy.
    #only use random movement.
    def move(self):
        #only move left/right
        dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])

        #python % operator actually makes sense so we can just use it. -1 % 3 = 2. Easy wrap around.
        self.x = (self.x + dx) % GRID_SIZE
        self.y = (self.y + dy) % GRID_SIZE
        return
        #non random movement makes things worse actually..... maybe because anti-agent have a different logic here...
        #we dont want seperate logics, just seperate probabilities.
        '''
        best_dx, best_dy = 0, 0
        max_count = -1

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                nx = (self.x + dx) % GRID_SIZE
                ny = (self.y + dy) % GRID_SIZE

                count = 0
                for i in [-1, 0, 1]:
                    for j in [-1, 0, 1]:
                        lx = (nx + i) % GRID_SIZE
                        ly = (ny + j) % GRID_SIZE
                        if grid[lx][ly] == 1:
                            count += 1

                if count > max_count:
                    max_count = count
                    best_dx = dx
                    best_dy = dy

        if max_count > 0 and random.randint(0, 99) < 70:
            self.x = (self.x + best_dx) % GRID_SIZE
            self.y = (self.y + best_dy) % GRID_SIZE
        else:
            moves = [(0,1), (0,-1), (1,0), (-1,0)]
            dx, dy = random.choice(moves)
            self.x = (self.x + dx) % GRID_SIZE
            self.y = (self.y + dy) % GRID_SIZE
        '''

    #look at all cells in vision range and check if they are populated.
    def local_density(self):
        grid_size = grid.shape[0]
        count = 0
        total_cells = (2 * self.vision_r + 1)**2 - 1

        for dx in range(-self.vision_r, self.vision_r + 1):
            for dy in range(-self.vision_r, self.vision_r + 1):
                nx = (self.x + dx) % grid_size
                ny = (self.y + dy) % grid_size
                if grid[nx, ny] == 1:
                    count += 1

        return count / total_cells
    
    #just some sugar
    def try_pick_up(self):
        if (grid[self.x, self.y] == 1) and (not self.carrying):
            grid[self.x, self.y] = 0
            self.carrying = True

    #just some sugar
    def try_drop(self):
        if (grid[self.x, self.y] == 0) and (self.carrying):
            grid[self.x, self.y] = 1
            self.carrying = False

    #just some sugar
    def pick_probability(self,density):
        return (self.p_pick / (self.p_pick + density)) ** 2

    #just some sugar
    def drop_probability(self,density):
        return (density / (self.p_drop + density)) ** 2

    #should i pick up or drop asked the ant to itself.
    def act(self):
        density = self.local_density()
            
        if not self.carrying:
            prob = self.pick_probability(density)
            if self.is_anti:
                prob = 1 - prob
            if random.random() < prob:
                self.try_pick_up()
        else:
            prob = self.drop_probability(density)
            if self.is_anti:
                prob = 1 - prob
            if random.random() < prob:
                self.try_drop()

#populate agents array. Total agents = ANTI+NORMAL
agents = [Agent(False) for _ in range(NUM_AGENTS)] + [Agent(True) for _ in range(NUM_ANTI_AGENTS)]

def draw_grid(screen, grid, agents, draw_vision):
    screen.fill(COLOR_BG)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if grid[x, y] == 1:
                pygame.draw.rect(screen, COLOR_OBJECT,
                                 (y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for agent in agents:
        color = COLOR_ANTI_AGENT if agent.is_anti else COLOR_AGENT
        pygame.draw.circle(screen, color,
                           (agent.y * CELL_SIZE + CELL_SIZE // 2, agent.x * CELL_SIZE + CELL_SIZE // 2),
                           CELL_SIZE // 2)
        if draw_vision:
            pygame.draw.circle(screen, (0, 0, 0), (agent.y * CELL_SIZE + CELL_SIZE // 2, agent.x * CELL_SIZE + CELL_SIZE // 2), agent.vision_r * CELL_SIZE,
                           2)

    #only update the portion needed to update.
    #might result in weird artefacts but its faster.
    pygame.display.flip()

def simulate(run_visualization=True, draw_vision=True):
    if run_visualization:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Wood Chip Clustering Simulation")
        clock = pygame.time.Clock()

    for step in range(SIM_STEPS):
        print(step)

        #pygame exit handler.
        for event in pygame.event.get() if run_visualization else []:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        for agent in agents:
            agent.move()
            agent.act()

        if run_visualization:
            draw_grid(screen, grid, agents, draw_vision)
            #limit frame rate. like a wait but from pygames.
            clock.tick(SIM_STEPS_PER_SECOND)

    if run_visualization:
        while(RECORDING):
            pass
        pygame.quit()

    return np.argwhere(grid == 1)

def plot_final_objects(initial_positions, final_positions):
    #x_i, y_i = zip(*initial_positions)
    x, y = zip(*final_positions)
    plt.figure(figsize=(6,6))
    #plt.scatter(y_i, x_i, s=10, c='blue')
    plt.scatter(y, x, s=10, c='red')
    plt.title("Final Object Clustering")
    #since we use PyGame data. Flip it all (0,0) is top left corner.
    plt.gca().invert_yaxis()
    plt.savefig("final_clustering.png")

#call c-script from python
def run_c_sim(p_pick, p_drop, num_agents, percent_anti_agents, sim_steps, density_radius, grid_size, num_obj, iter):
    result = subprocess.run(
            ["./clustering_sim",str(p_pick), str(p_drop), str(num_agents), str(percent_anti_agents), str(sim_steps), str(density_radius), str(grid_size), str(num_obj), str(iter)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
    return float(result.stdout.strip().split('\n')[0])

def run_animated_simulation(run_visualization, draw_vision):
    #modify at top of file.
    initial_positions = np.argwhere(grid == 1)
    final_positions = simulate(run_visualization=run_visualization, draw_vision=draw_vision)
    #initial position is uncommented in the script, add back in to see starting conditions.
    plot_final_objects(initial_positions, final_positions)

def sweep_anti_agent_percentage():
    cluster_sizes = []
    percent_anti_agents_values = [0, 0.05, 0.1, 0.15]

    for p in percent_anti_agents_values:
        print(f"percent_anti_agents = {p:.3f}")
        c_size = run_c_sim(P_PICK, P_DROP, NUM_AGENTS, p, SIM_STEPS, VISION_RADIUS, GRID_SIZE, NUM_OBJECTS, ITERRATION)
        if c_size is None:
            c_size = 0
        cluster_sizes.append(c_size)

    plt.figure(figsize=(8,5))
    plt.plot(percent_anti_agents_values, cluster_sizes, marker='o')
    plt.xlabel('Percent Anti Agents')
    plt.ylabel('Cluster Size')
    plt.title('Cluster Size vs Percent Anti Agents')
    plt.grid(True)
    plt.savefig("cluster_size_vs_anti_agent_percent.png")
    
run_animated_simulation(run_visualization = True, draw_vision = True)
sweep_anti_agent_percentage()
