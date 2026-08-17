import random
import math
import matplotlib.pyplot as plt

NUM_LOCUSTS = 20
ITERATIONS = 500
PERCEPTION_RANGE = 0.045
PERCEPTION_RANGE_HIGH = 0.2
MOVE_SPEED = 0.001 # arc length that a locust moves in one iteration
SWITCH_PROBABILITY = 0.015

CIRCUMFERENCE = 1
RADIUS = CIRCUMFERENCE / (2 * math.pi)
ANGULAR_SPEED = MOVE_SPEED / RADIUS
LEFT = 'L'
RIGHT = 'R'

NUM_PLOTS = 5

class Locust:
    def __init__(self, direction, angle):
        self.direction = direction  # Direction can be 'left' or 'right'
        self.angle = angle  # Angle in degrees

    def switch(self):
        self.direction = LEFT if self.direction == RIGHT else RIGHT

def create_locusts(biased = False) -> list:
    locusts = []
    for i in range(NUM_LOCUSTS):
        direction = LEFT if i % 2 == 0 or (biased and i < 4) else RIGHT
        angle = random.uniform(0.0, 2.0 * math.pi)  # Random angle in radians
        locusts.append(Locust(direction, angle))
    return locusts

def simulate(locusts: list, highViewDist = False) -> None:
    for locust in locusts:
        # movement
        locust.angle += ANGULAR_SPEED * (1 if locust.direction == RIGHT else -1)
        locust.angle %= 2 * math.pi  # Keep angle within [0, 2π)
        # perception
        neighbours_count = 0
        opposite_neighbours = 0
        for other in locusts:
            if other == locust: continue
            angular_distance = abs(other.angle - locust.angle)
            if angular_distance > math.pi:
                angular_distance = 2 * math.pi - angular_distance
            arc_distance = RADIUS * angular_distance
            if arc_distance < (PERCEPTION_RANGE_HIGH if highViewDist else PERCEPTION_RANGE):
                neighbours_count += 1
                if other.direction != locust.direction:
                    opposite_neighbours += 1
        # switch direction if majority of neighbours are opposite
        condition1 = neighbours_count > 0 and opposite_neighbours > neighbours_count / 2
        # switch with a random probability
        condition2 = random.random() < SWITCH_PROBABILITY
        if condition1 or condition2:
            locust.switch()

def count_left(locusts: list) -> int:
    return sum(1 for locust in locusts if locust.direction == LEFT)

def plot_locust_trajectories(biased = False, highViewDist = False):
    plt.clf()
    for _ in range(NUM_PLOTS):
        # simulate
        locusts = create_locusts(biased)
        num_left = []
        num_left.append(count_left(locusts))
        for i in range(ITERATIONS):
            simulate(locusts, highViewDist)
            num_left.append(count_left(locusts))
        # plot result
        plt.plot(num_left)
    plt.xlabel('Iteration')
    plt.ylabel('#Left Locusts')
    plt.title('Locust Direction-Alignment Simulation')
    suffix = f"{'_biased' if biased else ''}{'_high_view_dist' if highViewDist else ''}"
    plt.savefig(f'locust_trajectories{suffix}_result.png')
    #plt.show()  

def run_multi_simulation(num_simulations: int, biased = False, highViewDist = False) -> tuple:
    transitions = [[0 for _ in range(NUM_LOCUSTS+1)] for _ in range(NUM_LOCUSTS+1)]
    occurrences = [0 for _ in range(NUM_LOCUSTS+1)]
    for sim in range(num_simulations):
        if sim % 100 == 0: print(f'Simulation {sim} of {num_simulations}')
        locusts = create_locusts(biased)
        num_left = count_left(locusts)
        #occurrences[num_left] += 1
        for i in range(ITERATIONS):
            old_left = num_left
            simulate(locusts, highViewDist)
            num_left = count_left(locusts)
            transitions[old_left][num_left] += 1
            occurrences[old_left] += 1
    return transitions, occurrences

def plot_transition_histogram(biased = False, highViewDist = False) -> tuple:
    plt.clf()
    transitions, occurrences = run_multi_simulation(1000, biased, highViewDist)
    # plot transitions as 2d histogram
    plt.imshow(transitions, cmap='hot', interpolation='nearest')
    plt.colorbar()
    plt.xlabel('#L_t')
    plt.ylabel('#L_t+1')
    plt.title('Left-Locust State-Transition Histogram over 1000 simulations')
    suffix = f"{'_biased' if biased else ''}{'_high_view_dist' if highViewDist else ''}"
    plt.savefig(f'transition_histogram{suffix}_result.png')
    #plt.show()

def plot_predicted_trajectories(biased = False, highViewDist = False):
    plt.clf()
    transitions, occurrences = run_multi_simulation(1000, biased, highViewDist)
    # normalize transitions
    for i in range(NUM_LOCUSTS+1):
        for j in range(NUM_LOCUSTS+1):
            if occurrences[i] > 0:
                transitions[i][j] /= occurrences[i]
    # plot possible trajectories of left locusts over time based on the normalized transition probabilities
    for _ in range(NUM_PLOTS):
        trajectory = [0] * (ITERATIONS + 1)
        trajectory[0] = count_left(create_locusts(biased))
        for i in range(ITERATIONS):
            trajectory[i + 1] = random.choices(range(NUM_LOCUSTS+1), weights=transitions[trajectory[i]])[0]
        # plot trajectory
        plt.plot(trajectory)
    plt.xlabel('Iteration')
    plt.ylabel('#Left Locusts')
    plt.title('Predicted Trajectories from Transition-Probability Model')
    plt.rcParams['figure.figsize'] = (20, 12)
    suffix = f"{'_biased' if biased else ''}{'_high_view_dist' if highViewDist else ''}"
    plt.savefig(f'predicted_trajectories{suffix}_result.png')
    #plt.show()

if __name__ == "__main__":
    plot_locust_trajectories(biased=False)
    plot_locust_trajectories(biased=True)
    plot_locust_trajectories(biased=False, highViewDist=True)
    plot_transition_histogram(biased=False)
    plot_transition_histogram(biased=True)
    plot_transition_histogram(biased=False, highViewDist=True)
    plot_predicted_trajectories(biased=False)
    plot_predicted_trajectories(biased=True)
    plot_predicted_trajectories(biased=False, highViewDist=True)
