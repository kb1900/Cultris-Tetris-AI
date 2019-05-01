import random

from deap import base
from deap import creator
from deap import tools
from scoop import futures

from c2ai import build_absolute_path
from c2ai.learning.deap.pso.downstack.uberleet import Tetris
import numpy as np
import pickle


# ----------

population_size = 500
game_attempts = 5
CXPB = 0.35  # CXPB  is the probability with which two individuals are crossed
MUTPB = 0.25  # MUTPB is the probability for mutating an individual
NGEN = 600  # number of generations to run
RECALCGEN = (
    100
)  # how often to reclaculate fitness of entire population (unecessary with higher game_attempts)
FREQ = 1  # how often to pickle dump the progress


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

    print("Individual had fitness of", scores, "Mean:", int(np.mean(scores)))
    return (np.mean(scores),)


# ----------
# Operator registration
# ----------
# register the goal / fitness function
toolbox.register("evaluate", evalOneMax)

# register the crossover operator
toolbox.register("mate", tools.cxBlend, alpha=0.5)

# register a mutation operator with a probability to
# flip each attribute/gene of 0.05
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)

# operator for selecting individuals for breeding the next
# generation: each individual of the current generation
# is replaced by the 'fittest' (best) of tournsize individuals
# drawn randomly from the current generation.
toolbox.register("select", tools.selTournament, tournsize=10)


def main(checkpoint=None):
    try:
        # A file name has been given, then load the data from the file
        with open(checkpoint, "rb") as cp_file:
            cp = pickle.load(cp_file, encoding="bytes")
            pop = cp["population"]
            g = cp["generation"]
            best_ind = cp["best_ind"]
            random.setstate(cp["rndstate"])
            fits = [ind.fitness.values[0] for ind in pop]
    except:
        # Start a new evolution
        # random.seed(64)
        pop = toolbox.population(population_size)
        g = 0
        print("Start of evolution")

        # Evaluate the entire population
        fitnesses = list(toolbox.map(toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        print("  Evaluated %i individuals" % len(pop))

        # Extracting all the fitnesses of
        fits = [ind.fitness.values[0] for ind in pop]

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

        if g % FREQ == 0:
            # Fill the dictionary using the dict(key=value[, ...]) constructor
            cp = dict(
                population=pop,
                generation=g,
                best_ind=best_ind,
                rndstate=random.getstate(),
            )

            with open("GA_checkpoint.pkl", "wb") as cp_file:
                pickle.dump(cp, cp_file)

    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))


if __name__ == "__main__":

    main(
        checkpoint=build_absolute_path("learning/deap/pso/downstack/GA_checkpoint.pkl")
    )
