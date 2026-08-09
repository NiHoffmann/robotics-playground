#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define W 800
#define H 800
#define N 250
#define L 50
#define RADIUS 5
#define T_MAX 5000
#define ITERATIONS 50

typedef struct Firefly {
    float x;
    float y;
    int isFlashing;
    int c_offset;
    struct Firefly** neighbours;
    int neighbour_count;
} Firefly;

Firefly swarm[N];

float rand_float() {
    return rand() / (float)RAND_MAX;
}

float distance(Firefly* a, Firefly* b) {
    float dx = a->x - b->x;
    float dy = a->y - b->y;
    return sqrt(dx*dx + dy*dy);
}

void init_swarm(float r) {
    for (int i = 0; i < N; i++) {
        swarm[i].x = rand_float();
        swarm[i].y = rand_float();
        swarm[i].c_offset = rand() % 50;
        swarm[i].isFlashing = 0;
        swarm[i].neighbours = malloc(N * sizeof(Firefly*));
        swarm[i].neighbour_count = 0;
    }

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            if (i == j) continue;
            if (distance(&swarm[i], &swarm[j]) <= r) {
                swarm[i].neighbours[swarm[i].neighbour_count++] = &swarm[j];
            }
        }
    }
}

void update_cycle_offset(Firefly* f) {
    int flashing_neighbours = 0;
    for (int i = 0; i < f->neighbour_count; i++) {
        if (f->neighbours[i]->isFlashing)
            flashing_neighbours++;
    }

    float flashing_percent = f->neighbour_count > 0 ? 
        (float)flashing_neighbours / f->neighbour_count : 0;

    if (flashing_percent > 0.5) f->c_offset++;
    else f->c_offset--;
}

int run_simulation_step(int cycle) {
    int flashing_count = 0;
    for (int i = 0; i < N; i++) {
        int f_c = (cycle + swarm[i].c_offset + L) % L;
        swarm[i].isFlashing = (f_c < (L / 2));
        if (swarm[i].isFlashing)
            flashing_count++;
    }

    for (int i = 0; i < N; i++) {
        int f_c = (cycle + swarm[i].c_offset + L) % L;
        if (f_c == 0)
            update_cycle_offset(&swarm[i]);
    }

    return flashing_count;
}

void run_simulation(float r, int* flashing_data) {
    init_swarm(r);
    int cycle = 0;
    for (int t = 0; t < T_MAX; t++) {
        flashing_data[t] = run_simulation_step(cycle);
        cycle = (cycle + 1) % L;
    }
}

void compute_amplitude_sweep() {
    float r;
    float min_val, max_val;
    float amplitudes[1000];
    float r_values[1000];
    int idx = 0;

    for (r = 0.05f; r < 1.4f; r += 0.025f) {
        min_val = 0;
        max_val = 0;

        for (int i = 0; i < ITERATIONS; i++) {
            int flashing_data[T_MAX];
            run_simulation(r, flashing_data);

            int local_min = flashing_data[T_MAX - 50];
            int local_max = flashing_data[T_MAX - 50];
            for (int j = T_MAX - 50; j < T_MAX; j++) {
                if (flashing_data[j] < local_min) local_min = flashing_data[j];
                if (flashing_data[j] > local_max) local_max = flashing_data[j];
            }
            min_val += local_min;
            max_val += local_max;
        }

        min_val /= ITERATIONS;
        max_val /= ITERATIONS;

        float amplitude = (max_val - min_val) / 2.0;
        amplitudes[idx] = amplitude;
        r_values[idx] = r;
        idx++;

        printf("%.3f,%.3f\n", r, amplitude);
        fflush(stdout);
    }
}

int main() {
    srand(time(NULL));
    compute_amplitude_sweep();
    return 0;
}
