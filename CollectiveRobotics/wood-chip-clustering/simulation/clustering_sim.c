#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>
#include <math.h>

#define PYTHON_EQUIVALENT
#define CLUSTER_DIST (2)

/**
 * 
 * No need to look at this.
 * 1:1 Translation of the Python-Code.
 */

//2D Array [x,y]
static int **grid;
static int GRID_SIZE = 100;
static int NUM_OBJECTS = 100;
static int VISION_R = 5;
static double P_PICK = 0;
static double P_DROP = 0;

//Base Probability is not reversed. Reversed after calculation and before logic! (1- density_prob)
typedef struct {
    int x, y;
    int is_anti;
    double p_pick;
    double p_drop;
    int carrying;
} Agent;

//just some sugar
double pick_probability(double p_pick, double density) {
    return pow(p_pick / (p_pick + density), 2);
}

double drop_probability(double p_drop, double density) {
    return pow(density / (p_drop + density), 2);
}

void try_pick_up(Agent* agent) {
    if (grid[agent->x][agent->y] == 1 && !agent->carrying) {
        grid[agent->x][agent->y] = 0;
        agent->carrying = 1;
    }
}

void try_drop(Agent* agent) {
    if (grid[agent->x][agent->y] == 0 && agent->carrying) {
        grid[agent->x][agent->y] = 1;
        agent->carrying = 0;
    }
}

//python modulo
int mod_wrap_remaineder(int a, int b) {
    int r = a % b;
    // -3 % 2 = -1 -> -1 + 2 = 1
    return r < 0 ? r + b : r;
}

double local_density(int x, int y, int radius) {
    int count = 0;
    int total_cells = (2 * radius + 1) * (2 * radius + 1) - 1;

    for (int dx = -radius; dx <= radius; dx++) {
        for (int dy = -radius; dy <= radius; dy++) {
            int nx = mod_wrap_remaineder(x + dx, GRID_SIZE);
            int ny = mod_wrap_remaineder(y + dy, GRID_SIZE);
            if (grid[nx][ny] == 1) {
                count++;
            }
        }
    }

    return (double)count / total_cells;
}

void move_agent(Agent* agent) {
#ifdef PYTHON_EQUIVALENT
    int moves[4][2] = {{0,1},{0,-1},{1,0},{-1,0}};
    int r = rand() % 4;
    agent->x = mod_wrap_remaineder(agent->x + moves[r][0], GRID_SIZE);
    agent->y = mod_wrap_remaineder(agent->y + moves[r][1], GRID_SIZE);
#else
    int best_dx = 0, best_dy = 0;
    int max_count = -1;

    for (int dx = -1; dx <= 1; dx++) {
        for (int dy = -1; dy <= 1; dy++) {
            if (dx == 0 && dy == 0) continue;

            int nx = mod_wrap_remaineder(agent->x + dx, GRID_SIZE);
            int ny = mod_wrap_remaineder(agent->y + dy, GRID_SIZE);

            int count = 0;
            for (int i = -1; i <= 1; i++) {
                for (int j = -1; j <= 1; j++) {
                    int lx = mod_wrap_remaineder(nx + i, GRID_SIZE);
                    int ly = mod_wrap_remaineder(ny + j, GRID_SIZE);
                    if (grid[lx][ly] == 1) count++;
                }
            }

            if (count > max_count) {
                max_count = count;
                best_dx = dx;
                best_dy = dy;
            }
        }
    }

    if (max_count > 0 && (rand() % 100 < 70)) {
        agent->x = mod_wrap_remaineder(agent->x + best_dx, GRID_SIZE);
        agent->y = mod_wrap_remaineder(agent->y + best_dy, GRID_SIZE);
    } else {
        int moves[4][2] = {{0,1},{0,-1},{1,0},{-1,0}};
        int r = rand() % 4;
        agent->x = mod_wrap_remaineder(agent->x + moves[r][0], GRID_SIZE);
        agent->y = mod_wrap_remaineder(agent->y + moves[r][1], GRID_SIZE);
    }
#endif
}

//bfs joinked from stack overflow
int bfs_cluster(int start_x, int start_y, bool** visited, int max_empty) {
    int dx[] = {0, 0, -1, 1};
    int dy[] = {-1, 1, 0, 0};
    int queue_size = GRID_SIZE * GRID_SIZE;
    int queue_head = 0, queue_tail = 0;
    int cluster_size = 0;

    // (x, y, empty_used)
    int (*queue)[3] = malloc(queue_size * sizeof(int[3])); 

    queue[queue_tail][0] = start_x;
    queue[queue_tail][1] = start_y;
    queue[queue_tail][2] = 0;
    queue_tail++;

    int** local_visited = malloc(GRID_SIZE * sizeof(int*));
    for (int i = 0; i < GRID_SIZE; i++) {
        local_visited[i] = malloc(GRID_SIZE * sizeof(int));
        for (int j = 0; j < GRID_SIZE; j++)
            local_visited[i][j] = -1;
    }
    local_visited[start_x][start_y] = 0;

    while (queue_head < queue_tail) {
        int x = queue[queue_head][0];
        int y = queue[queue_head][1];
        int empty_used = queue[queue_head][2];
        queue_head++;

        if (visited[x][y]) continue;
        visited[x][y] = true;
        if (grid[x][y] == 1) cluster_size++;

        for (int i = 0; i < 4; i++) {
            int nx = mod_wrap_remaineder(x + dx[i], GRID_SIZE);
            int ny = mod_wrap_remaineder(y + dy[i], GRID_SIZE);
            int new_empty = empty_used + (grid[nx][ny] == 0 ? 1 : 0);

            if (new_empty > max_empty) continue;
            if (local_visited[nx][ny] != -1 && local_visited[nx][ny] <= new_empty) continue;

            local_visited[nx][ny] = new_empty;
            queue[queue_tail][0] = nx;
            queue[queue_tail][1] = ny;
            queue[queue_tail][2] = new_empty;
            queue_tail++;
        }
    }

    for (int i = 0; i < GRID_SIZE; i++)
        free(local_visited[i]);
    free(local_visited);
    free(queue);

    return cluster_size;
}

int find_largest_cluster_size(int empty_tiles) {
    bool** visited = malloc(GRID_SIZE * sizeof(bool*));
    for (int i = 0; i < GRID_SIZE; i++) {
        visited[i] = malloc(GRID_SIZE * sizeof(bool));
        for (int j = 0; j < GRID_SIZE; j++)
            visited[i][j] = false;
    }

    int max_cluster = 0;
    for (int x = 0; x < GRID_SIZE; x++) {
        for (int y = 0; y < GRID_SIZE; y++) {
            if (!visited[x][y] && grid[x][y] == 1) {
                int size = bfs_cluster(x, y, visited, empty_tiles);
                if (size > max_cluster)
                    max_cluster = size;
            }
        }
    }
    for (int i = 0; i < GRID_SIZE; i++)
        free(visited[i]);
    free(visited);

    return max_cluster;
}

double run_simulation(int num_agents, double percent_anti_agents, int sim_steps) {
    for (int i=0; i<GRID_SIZE; i++)
        for (int j=0; j<GRID_SIZE; j++)
            grid[i][j] = 0;

    srand((unsigned int)time(NULL));

    int total_cells = GRID_SIZE * GRID_SIZE;
    int* indices = (int*)malloc(total_cells * sizeof(int));
    for (int i=0; i<total_cells; i++) indices[i] = i;

    for (int i=0; i<NUM_OBJECTS; i++) {
        int r = i + rand() % (total_cells - i);
        int tmp = indices[i]; indices[i] = indices[r]; indices[r] = tmp;

        int pos = indices[i];
        int x = pos / GRID_SIZE;
        int y = pos % GRID_SIZE;
        grid[x][y] = 1;
    }
    free(indices);

    int num_anti_agents = (int)(num_agents * percent_anti_agents);
    int normal_agents = num_agents - num_anti_agents;
    Agent* agents = (Agent*)malloc(num_agents * sizeof(Agent));

    for (int i=0; i<num_agents; i++) {
        agents[i].x = rand() % GRID_SIZE;
        agents[i].y = rand() % GRID_SIZE;
        agents[i].carrying = 0;
        agents[i].is_anti = (i >= normal_agents) ? 1 : 0;
        agents[i].p_pick = P_PICK;
        agents[i].p_drop = P_DROP;
    }

    for (int step=0; step<sim_steps; step++) {
        for (int i=0; i<num_agents; i++) {
            Agent* a = &agents[i];
            move_agent(a);

            double density = local_density(a->x, a->y, VISION_R);
            if (!a->carrying) {
                double prob = pick_probability(a->p_pick, density);
                if(a->is_anti){
                    prob = 1 - prob;
                }
                if (((double)rand() / RAND_MAX) < prob) {
                    try_pick_up(a);
                }
            } else {
                double prob = drop_probability(a->p_drop, density);
                if(a->is_anti){
                    prob = 1 - prob;
                }
                if (((double)rand() / RAND_MAX) < prob) {
                    try_drop(a);
                }
            }
        }
    }

    free(agents);

    //replace this with loop using local_density for alternative to cluster size.
    return find_largest_cluster_size(CLUSTER_DIST);
}

int main(int argc, char** argv) {
    if (argc < 10) {
        fprintf(stderr, "Usage: p_pick p_drop num_agents percent_anti_agents sim_steps density_radius grid_size num_objects iterations\n");
        return 1;
    }

    P_PICK = atof(argv[1]);
    P_DROP = atof(argv[2]);
    int num_agents = atoi(argv[3]);
    double percent_anti_agents = atof(argv[4]);
    int sim_steps = atoi(argv[5]);
    VISION_R = atoi(argv[6]);
    GRID_SIZE = atoi(argv[7]);
    NUM_OBJECTS = atoi(argv[8]);
    int iter      = atoi(argv[9]);
    
    grid = malloc(GRID_SIZE * sizeof(int *));
    for (int i = 0; i < GRID_SIZE; i++) {
        grid[i] = malloc(GRID_SIZE * sizeof(int));
    }

    double avg = 0;
    for(int i=0; i <iter; i++){
        avg +=run_simulation(num_agents, percent_anti_agents, sim_steps);
    }
    printf("%f", avg/iter);
    return 0;
}
