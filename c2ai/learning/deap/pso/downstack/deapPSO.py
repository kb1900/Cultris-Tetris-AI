from deap import base
from deap import creator
from deap import tools
from scoop import futures
from c2ai import build_absolute_path
from c2ai.learning.deap.pso.downstack.uberleet import Tetris
import numpy as np
import time
import operator
import random
import pickle

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create(
    "Particle",
    list,
    fitness=creator.FitnessMax,
    speed=list,
    smin=None,
    smax=None,
    best=None,
)


def generate(size, pmin, pmax, smin, smax):
    part = creator.Particle(random.uniform(pmin, pmax) for _ in range(size))
    part.speed = [random.uniform(smin, smax) for _ in range(size)]
    part.smin = smin
    part.smax = smax
    return part


def updateParticle(part, best, phi1, phi2):
    u1 = (random.uniform(0, phi1) for _ in range(len(part)))
    u2 = (random.uniform(0, phi2) for _ in range(len(part)))
    v_u1 = map(operator.mul, u1, map(operator.sub, part.best, part))
    v_u2 = map(operator.mul, u2, map(operator.sub, best, part))
    part.speed = list(map(operator.add, part.speed, map(operator.add, v_u1, v_u2)))
    for i, speed in enumerate(part.speed):
        if speed < part.smin:
            part.speed[i] = part.smin
        elif speed > part.smax:
            part.speed[i] = part.smax
    part[:] = list(map(operator.add, part, part.speed))


def evalOneMax(individual):
    scores = []
    for i in range(game_attempts):
        scores.append(Tetris.run_game(n=individual, render=False))

    print("Particle had fitness of", scores, "Mean:", int(np.mean(scores)))

    return (np.average(scores),)


toolbox = base.Toolbox()
toolbox.register("particle", generate, size=10, pmin=-3, pmax=25, smin=-0.5, smax=0.5)
toolbox.register("population", tools.initRepeat, list, toolbox.particle)
toolbox.register("update", updateParticle, phi1=2.0, phi2=2.0)
toolbox.register("evaluate", evalOneMax)


def main(checkpoint):
    try:
        # A file name has been given, then load the data from the file
        with open(checkpoint, "rb") as cp_file:
            cp = pickle.load(cp_file, encoding="bytes")
            pop = cp["population"]
            g = cp["generation"]
            best = cp["best"]
    except:
        # Start a new evolution
        # random.seed(64)
        pop = toolbox.population(n=population_size)
        g = 0
        print("Start of evolution")
        best = None

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    logbook = tools.Logbook()
    logbook.header = ["gen", "evals"] + stats.fields

    while g < NGEN:
        g += 1
        start_time = time.time()
        print("-- Generation %i --" % g)

        for part in pop:
            part.fitness.values = toolbox.evaluate(part)
            if not part.best or part.best.fitness < part.fitness:
                part.best = creator.Particle(part)
                part.best.fitness.values = part.fitness.values
            if not best or best.fitness < part.fitness:
                best = creator.Particle(part)
                best.fitness.values = part.fitness.values

        for part in pop:
            toolbox.update(part, best)

        # Gather all the fitnesses in one list and print the stats
        logbook.record(gen=g, evals=len(pop), **stats.compile(pop))
        log = logbook.stream

        print(log)
        print(
            "Generation",
            g,
            "took:",
            time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)),
        )
        print(best, "\n")

        with open(
            build_absolute_path("learning/deap/pso/downstack/PSOoutput.txt"), "a"
        ) as text_file:
            text_file.writelines([log, "\n", str(best)])

        if g % FREQ == 0:
            # Fill the dictionary using the dict(key=value[, ...]) constructor
            cp = dict(population=pop, generation=g, best=best)

            with open("PSO_checkpoint.pkl", "wb") as cp_file:
                pickle.dump(cp, cp_file)

    return pop, logbook, best


NGEN = 500
population_size = 100
game_attempts = 5
FREQ = 1

if __name__ == "__main__":
    main(
        checkpoint=build_absolute_path("learning/deap/pso/downstack/PSO_checkpoint.pkl")
    )
