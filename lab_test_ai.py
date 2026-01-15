import streamlit as st
import numpy as np
import random

# Fixed parameters
POP_SIZE = 300
CHROM_LEN = 80
TARGET_ONES = 40
MAX_FITNESS = 80
N_GENERATIONS = 50

# Fitness: max when ones == 40
def fitness(ind):
    ones = np.sum(ind)
    return MAX_FITNESS - abs(ones - TARGET_ONES)

# Initialize population
def init_population():
    return np.random.randint(0, 2, size=(POP_SIZE, CHROM_LEN))

# Tournament selection
def select(pop, fits):
    i1, i2 = random.randint(0, POP_SIZE-1), random.randint(0, POP_SIZE-1)
    return pop[i1] if fits[i1] > fits[i2] else pop[i2]

# Crossover
def crossover(p1, p2):
    point = random.randint(1, CHROM_LEN-1)
    c1 = np.concatenate((p1[:point], p2[point:]))
    c2 = np.concatenate((p2[:point], p1[point:]))
    return c1, c2

# Mutation (flip 1 random bit)
def mutate(ind):
    idx = random.randint(0, CHROM_LEN-1)
    ind[idx] = 1 - ind[idx]
    return ind

# ==== MAIN EXECUTION ====
pop = init_population()

for _ in range(N_GENERATIONS):
    fits = np.array([fitness(ind) for ind in pop])

    new_pop = []
    for _ in range(POP_SIZE // 2):
        p1 = select(pop, fits)
        p2 = select(pop, fits)
        c1, c2 = crossover(p1, p2)
        new_pop.append(mutate(c1))
        new_pop.append(mutate(c2))

    pop = np.array(new_pop)

# Final evaluation
fits = np.array([fitness(ind) for ind in pop])
best = pop[np.argmax(fits)]
best_fitness = np.max(fits)
ones_count = int(np.sum(best))

print("=== Genetic Algorithm Result ===")
print("Best Fitness:", best_fitness)
print("Ones Count:", ones_count)
print("First 50 bits of Best Pattern:", best[:50])
