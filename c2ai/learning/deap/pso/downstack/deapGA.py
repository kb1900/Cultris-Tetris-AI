import random

from deap import base
from deap import creator
from deap import tools
from scoop import futures

from c2ai import build_absolute_path
from c2ai.learning.deap.pso.downstack.tetris import Tetris
import numpy as np


# ----------

population_size = 500
game_attempts = 3
CXPB = 0.35  # CXPB  is the probability with which two individuals are crossed
MUTPB = 0.2  # MUTPB is the probability for mutating an individual
NGEN = 10 # number of generations to run
RCALCGEN = 5



creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Attribute generator
#                      define 'attr_bool' to be an attribute ('gene')
#                      which corresponds to integers sampled uniformly
#                      from the range [0,1] (i.e. 0 or 1 with equal
#                      probability)
toolbox.register("attr_bool", random.uniform, -10, 30)

# Structure initializers
#                         define 'individual' to be an individual
#                         consisting of 100 'attr_bool' elements ('genes')
toolbox.register(
    "individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 10
)

# define the population to be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("map", futures.map)
# toolbox.register("map", map)

# the goal ('fitness') function to be maximized
def evalOneMax(individual):

    scores = []
    for attempt in range(game_attempts):
        scores.append(Tetris.run_game(n=individual, render=False))

    print("Individual had fitness of", np.mean(scores))
    return (np.mean(scores),)

# ----------
# Operator registration
# ----------
# register the goal / fitness function
toolbox.register("evaluate", evalOneMax)

# register the crossover operator
toolbox.register("mate", tools.cxTwoPoint)

# register a mutation operator with a probability to
# flip each attribute/gene of 0.05
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)

# operator for selecting individuals for breeding the next
# generation: each individual of the current generation
# is replaced by the 'fittest' (best) of tournsize individuals
# drawn randomly from the current generation.
toolbox.register("select", tools.selTournament, tournsize=int(population_size*0.01))


def main():
    random.seed(64)

    # create an initial population of population_size individuals (where
    # each individual is a list of integers)
    pop = toolbox.population(population_size)

    print("Start of evolution")

    # Evaluate the entire population
    fitnesses = list(toolbox.map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
        
    print("  Evaluated %i individuals" % len(pop))

    # Extracting all the fitnesses of
    fits = [ind.fitness.values[0] for ind in pop]

    # Variable keeping track of the number of generations
    g = 0

    # Begin the evolution
    while max(fits) < 100000 and g < NGEN:
        # A new generation
        g = g + 1
        print("-- Generation %i --" % g)

        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):

            # cross two individuals with probability CXPB
            if random.random() < CXPB:
                toolbox.mate(child1, child2)

                # fitness values of the children
                # must be recalculated later
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:

            # mutate an individual with probability MUTPB
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        if g % RECALCGEN == 0:

            # recalculate all individuals fitness every kth generation
            for ind in offspring:
                del ind.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        print("  Evaluated %i individuals" % len(invalid_ind))

        # The population is entirely replaced by the offspring
        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)
        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual so far is %s, %s" % (best_ind, best_ind.fitness.values))
        with open(
            build_absolute_path("learning/deap/pso/downstack/GAoutput.txt"), "a"
        ) as text_file:
            text_file.writelines(["\n", str(best_ind)])

    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))


if __name__ == "__main__":
    main()
