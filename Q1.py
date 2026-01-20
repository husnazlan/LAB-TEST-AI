import random
import numpy as np
import streamlit as st

POP_SIZE = 300         
CHROM_LEN = 80          
TARGET_ONES = 40       
MAX_FITNESS = 80       
N_GENERATIONS = 50    

def fitness(individual):
    ones = int(individual.sum())
    return MAX_FITNESS - abs(ones - TARGET_ONES)

def init_population():
    return np.random.randint(0, 2, size=(POP_SIZE, CHROM_LEN))

def run_ga():
    population = init_population()
    best = None
    best_fit = -1

    for _ in range(N_GENERATIONS):
        for ind in population:
            f = fitness(ind)
            if f > best_fit:
                best_fit = f
                best = ind.copy()

        new_pop = []
        while len(new_pop) < POP_SIZE:
            p1, p2 = random.sample(list(population), 2)
            point = random.randint(1, CHROM_LEN - 1)
            child = np.concatenate([p1[:point], p2[point:]])
            new_pop.append(child)
        population = np.array(new_pop)

    return best, best_fit

st.title("Genetic Algorithm Bit Pattern Generator")

if st.button("Run GA"):
    best_ind, best_fit = run_ga()
    st.write("Best Fitness:", best_fit)
    st.write("Number of Ones:", int(best_ind.sum()))
    st.code("".join(map(str, best_ind)))
