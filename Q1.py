import random
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# ---- Fixed GA Parameters (as required by Question 1) ----
POP_SIZE = 300          # population
CHROM_LEN = 80          # chromosome length
TARGET_ONES = 40        # fitness peaks at ones = 40
MAX_FITNESS = 80        # max fitness == 80
N_GENERATIONS = 50      # generations

# ---- GA Hyperparameters ----
TOURNAMENT_K = 3
CROSSOVER_RATE = 0.9
MUTATION_RATE = 1.0 / CHROM_LEN

# ---- Fitness Function ----
def fitness(individual: np.ndarray) -> float:
    ones = int(individual.sum())
    return MAX_FITNESS - abs(ones - TARGET_ONES)

# ---- GA Operators ----
def init_population(pop_size: int, chrom_len: int):
    return np.random.randint(0, 2, size=(pop_size, chrom_len), dtype=np.int8)

def tournament_selection(pop, fits, k):
    idxs = np.random.randint(0, len(pop), size=k)
    best_idx = idxs[np.argmax(fits[idxs])]
    return pop[best_idx].copy()

def single_point_crossover(p1, p2):
    if np.random.rand() > CROSSOVER_RATE:
        return p1.copy(), p2.copy()
    point = np.random.randint(1, CHROM_LEN)
    c1 = np.concatenate([p1[:point], p2[point:]])
    c2 = np.concatenate([p2[:point], p1[point:]])
    return c1, c2

def mutate(individual):
    mask = np.random.rand(CHROM_LEN) < MUTATION_RATE
    individual[mask] = 1 - individual[mask]
    return individual

def evolve(pop, generations):
    best_fitness_per_gen = []
    best_individual = None
    best_f = -9999

    for _ in range(generations):
        fits = np.array([fitness(ind) for ind in pop])

        gen_best_idx = np.argmax(fits)
        gen_best = pop[gen_best_idx]
        gen_best_f = fits[gen_best_idx]
        best_fitness_per_gen.append(gen_best_f)

        if gen_best_f > best_f:
            best_f = gen_best_f
            best_individual = gen_best.copy()

        new_pop = []
        while len(new_pop) < len(pop):
            p1 = tournament_selection(pop, fits, TOURNAMENT_K)
            p2 = tournament_selection(pop, fits, TOURNAMENT_K)
            c1, c2 = single_point_crossover(p1, p2)
            new_pop.append(mutate(c1))
            new_pop.append(mutate(c2))

        pop = np.array(new_pop[:len(pop)], dtype=np.int8)

    return best_individual, best_f, best_fitness_per_gen

# ---- UI ----
st.title("Genetic Algorithm - Bit Pattern Generator (Q1)")
seed = st.number_input("Random Seed", min_value=0, value=42)
run = st.button("Run GA")

if run:
    random.seed(seed)
    np.random.seed(seed)

    pop = init_population(POP_SIZE, CHROM_LEN)
    best_ind, best_fit, curve = evolve(pop, N_GENERATIONS)

    ones = int(best_ind.sum())
    zeros = CHROM_LEN - ones
    bitstring = "".join(map(str, best_ind.tolist()))

    st.subheader("Best Result Found")
    st.write(f"Ones = {ones}, Zeros = {zeros}, Length = {CHROM_LEN}")
    st.write(f"Best Fitness = {best_fit}")
    st.code(bitstring)

    st.subheader("Convergence Curve")
    fig, ax = plt.subplots()
    ax.plot(range(1, len(curve)+1), curve)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best Fitness")
    st.pyplot(fig)

    if best_fit == MAX_FITNESS:
        st.success("Perfect match achieved!")
    else:
        st.info("Near optimal solution achieved.")
