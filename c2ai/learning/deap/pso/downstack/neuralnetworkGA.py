import random
import collections
import pandas as pd
import numpy as np
from pathos.multiprocessing import ProcessingPool as Pool
from pathos import multiprocessing
from statistics import median
import dill
import time

from c2ai import build_absolute_path
from c2ai.learning.deap.pso.downstack.tetris import Tetris
from c2ai.base.tetromino import Tetromino
from c2ai.base.field import Field
from c2ai.base.optimizer import Optimizer
from c2ai.learning.deap.pso.downstack.plot import Regression
from c2ai.learning.deap.pso.downstack.NN import neuralNetwork


def generate_weight():
    """
	Generates a 1x29 array of random weights

	"""
    input_nodes = 6
    hidden_nodes = 1
    output_nodes = 1
    return neuralNetwork(input_nodes, hidden_nodes, output_nodes)


def factor_weight(WEIGHT):
    if factor_method == "NONE":
        # No normalization
        norm = WEIGHT

    elif factor_method == "VECTOR_LENGTH":
        # Vector Length normalization
        import math

        sq = []
        for i in range(len(WEIGHT)):
            sq.append((WEIGHT[i] * WEIGHT[i]))

        L = math.sqrt(sum(sq))
        norm = []
        for i in range(len(WEIGHT)):
            norm.append((WEIGHT[i] / L))

    elif factor_method == "MINMAX":
        # Min_max normalization

        minimum = min(WEIGHT)
        maximum = max(WEIGHT)

        if minimum == maximum:
            maximum = maximum + random.uniform(0.0000001, 0.00001)
        norm = []
        for i in range(len(WEIGHT)):
            Z = float((WEIGHT[i] - minimum) / (maximum - minimum))
            norm.append(Z)

    elif factor_method == "MAX":
        # Max normalization

        norm = []
        for i in WEIGHT:
            norm.append(float(i / max(WEIGHT)))

    elif factor_method == "SUM":
        # Max normalization

        norm = []
        for i in WEIGHT:
            norm.append(float(i / sum(WEIGHT)))

    return norm


def generate_random_population(size):
    """
	Generates a random population as a list of individuals in which each individual is a 1x29 array of random weights

	"""
    population = []
    i = 0
    while i < size:
        population.append(generate_weight())
        i += 1
    return population


def generate_fit_population(size):
    """
	Generates a fit population as a list of individuals in which each individual is a 1x29 array of random weights
	whose fitness() is below the fit_threshold

	"""
    if size >= 0:
        print("Generating FIT population of size:", size)
        print("This may take a while...")

    start_time = time.time()
    with multiprocessing.Pool(
        processes=max(multiprocessing.cpu_count() - 1, 1)
    ) as pool:

        population = pool.map(generate_helper, range(size))

    print("Took:", time.time() - start_time, "seconds")
    return population


def generate_helper(individual):
    return individual_fitness(attempts=game_attempts_fit_individual)


def fitness_helper(population):
    return fitness(population, attempts=game_attempts)


def compute_sort_population(population):
    """
	For each individual in a population, evaluate their fitness, and return a ordered dictionary of
	keys = list(scores)
	values = list(population)

	"""
    # population_scores = multiprocessing.Pool(processes=max(multiprocessing.cpu_count()-1,1)).map(fitness_helper, population)
    with multiprocessing.Pool(
        processes=max(multiprocessing.cpu_count() - 1, 1)
    ) as pool:
        population_scores = pool.map(fitness_helper, population)

    population_dict = dict(zip(population_scores, population))
    population_dict_sorted = collections.OrderedDict(sorted(population_dict.items()))

    return population_dict_sorted


def individual_fitness(attempts):
    """
	Takes an individual (weights array) and returns the average score of game_attempts of Tetris.run_game()

	"""
    while True:
        results = []
        individual = generate_weight()

        for x in range(attempts):  # plays game_attempts amound of games
            score = Tetris.run_game(individual, render=False)
            piece_count = score[0]

            fitness_score = 500 - piece_count

            results.append(fitness_score)

        avg_fitness = sum(results) / float(len(results))
        # median_fitness = median(results)

        if avg_fitness < fit_threshold:
            print("Created FIT individual:", "Score:", avg_fitness)
            return individual
            break
        else:
            continue


def fitness(individual, attempts):
    """
	Takes an individual (weights array) and returns the average score of game_attempts of Tetris.run_game()

	"""
    results = []
    for x in range(attempts):  # plays game_attempts amound of games
        score = Tetris.run_game(individual, render=False)
        piece_count = score[0]

        fitness_score = 500 - piece_count

        results.append(fitness_score)

    avg_fitness = sum(results) / float(len(results))
    # median_fitness = median(results)
    return avg_fitness


def create_child(individual1, individual2):
    """
	Produces a new individual given two breeding individuals.
	crossover_method specifies method of determining new weights of child:
		EITHER_OR: 50/50 chance of either allele
		AVERAGE: average of both alleles

	"""

    if crossover_method == "EITHER_OR":

        if int(100 * random.random()) < 50:
            return individual1
        else:
            return individual2

    elif crossover_method == "AVERAGE":
        child = generate_weight()
        wih1 = individual1.wih
        wih2 = individual2.wih
        who1 = individual1.who
        who2 = individual2.who

        child.wih = np.mean([wih1, wih2], axis=0)
        child.who = np.mean([who1, who2], axis=0)

        return child


def create_children(sorted_population, breeders, number_of_child):
    """
	Given a population of breeders the children generating the next population is returned
	50% of the next population is produced by creating child() using 2 randomly selected breeders
	The rest of the next population is produced by takign the top remaining individuals from the sorted_population
	"""
    next_population = []
    for x in range(int(number_of_child / 2)):
        individual1 = random.choice(breeders)
        individual2 = random.choice(breeders)
        # next_population.append(create_child(breeders[i], breeders[len(breeders) -1 -i]))
        next_population.append(create_child(individual1, individual2))
    for x in range((number_of_child) - len(next_population)):
        next_population.append(sorted_population[x])

    return next_population


def mutate_individual(individual):
    """
	For each individual in a population
		for each weight in each individual
			if random.random() * 100 is lower than the mutation rate:
				mutate that weight by a random factor between 0.001 and 1000
			factor that individual's weights
	return individual
	"""
    # if np.random.randint(101) < mutation_rate:
    mutated_individual = individual

    if np.random.randint(101) < mutation_rate:
        # print(individual.wih)

        x = np.random.randint(len(individual.wih))
        y = np.random.randint(len(individual.wih[0]))

        mutated_individual.wih[x][y] = np.random.rand() * individual.wih[x][y]

        # print(mutated_individual.wih)

    if np.random.randint(101) < mutation_rate:
        # print(individual.wih)

        x = np.random.randint(len(individual.who))
        y = np.random.randint(len(individual.who[0]))

        mutated_individual.who[x][y] = np.random.rand() * individual.who[x][y]

        # print(mutated_individual.wih)

    return mutated_individual


def select_breeders(population_sorted):
    """
	Given a sorted population, returns chosen breeders (parents)

	The resulting population of breeders (parents) contains:
		- the top 'best_individuals' of the sorted population
		- 'lucky_few' number of random individuals from the sorted population
		- 'random_new' number of FIT individuals generated using generate_fit_population()
	"""
    breeders = []
    for i in range(best_individuals):
        breeders.append(population_sorted[i])
    for i in range(lucky_few):
        breeders.append(random.choice(population_sorted))
    random_new_population = generate_fit_population(random_new)
    for i in range(len(random_new_population)):
        breeders.append(random_new_population[i])
    random.shuffle(breeders)
    return breeders


def mutate_population(population):
    """
	For each individual in a population
		for each weight in each individual
			mutate_indvidual()
	return population
	"""
    for i in range(len(population)):
        population[i] = mutate_individual(population[i])
    return population


def first_generation(type):
    """
	Generates the first population of individuals

	"""
    if type == "random":
        return generate_random_population(population_size)

    elif type == "fit":
        return generate_fit_population(population_size)


def next_generation(sorted_population):
    """
	Using a sorted population:
		1) selects + creates the breeders
		2) creates the children of the next generation
		3) mutates the children
	And returns the next_population

	"""
    # print('Creating next generation')
    breeders = select_breeders(sorted_population)
    children = create_children(sorted_population, breeders, population_size)
    next_population = mutate_population(children)

    return next_population


def several_generations(epochs):
    """
	Evaluates and logs the results of several generations.

	Parameters:
		epochs:
			the number of loops of evolution to be performed on the current_generation
		current_generation:
			the starter population. Loaded from an existing current_generation_dump file
			or created new using first_generation()

	"""
    for epoch in range(epochs):

        # Attempt to load a previous current_generation and the epoch # if available
        try:
            with open(
                build_dotted_path(
                    "learning/deap/pso/downstack/current_generation_dump"
                ),
                "rb",
            ) as dump_file:
                dump = dill.load(dump_file)
                most_recent_generation = dump[0]
                current_generation = most_recent_generation[:population_size]
                # Pick up where we left off previously
                epochs = epochs + dump[1]
                epoch = dump[1] + 1
            dump_file.close()

        except:
            # If a previous dump is not available, create a first generation
            print("Did not find a current_generation_dump object file")
            print("Creating first generation starter population")
            current_generation = first_generation(type="fit")

        if epoch != 0:
            next_population = next_generation(current_generation)
        else:
            next_population = current_generation

        start_time = time.time()
        print("Computing fitness for individuals in Epoch:", epoch + 1)
        population_dict = compute_sort_population(next_population)
        print(
            "Computing fitness for Epoch",
            epoch + 1,
            "took",
            float((time.time() - start_time) / 60),
            "minutes",
        )

        sorted_population = list(population_dict.values())
        scores = list(population_dict.keys())

        avg_score = sum(scores) / float(len(scores))
        median_score = median(scores)
        min_score = min(scores)
        top_5_scores = scores[:5]
        avg_top_5 = sum(top_5_scores) / float(len(top_5_scores))

        data = [
            [
                epoch + 1,
                avg_score,
                median_score,
                avg_top_5,
                min_score,
                sorted_population[:5],
                float((time.time() - start_time) / 60),
            ]
        ]
        temp_df = pd.DataFrame(
            data,
            columns=[
                "Epoch",
                "Average Score",
                "Median Score",
                "Top 5 Average score",
                "Minimum Score",
                "Top 5 Chromosomes",
                "Evaluation Time",
            ],
        )

        if epoch == 0:
            temp_df.to_csv("log.csv", header=True, mode="a")
        else:
            temp_df.to_csv("log.csv", header=False, mode="a")

        current_generation = sorted_population

        print("Epoch", epoch + 1, "stats:")
        print("Average Score:", data[0][1])
        print("Median Score:", data[0][2])
        print("Top 5 Average Score:", data[0][3])

        df = pd.read_csv("log.csv")
        ind = max(df["Epoch"]) + 100
        regression = Regression.linear_regression(
            x=df["Epoch"], y=df["Median Score"], ind=ind
        )
        print("Slope:", regression[0])
        print("y-Intercept:", regression[1])
        print("R squared:", regression[2])
        print("Epoch", ind, "Prediction score:", regression[3])
        print("")

        Regression.plot(x=df["Epoch"], y=df["Average Score"], y1=df["Median Score"])

        current_generation_dump = (current_generation, epoch)
        with open(
            build_absolute_path("learning/deap/pso/downstack/current_generation_dump"),
            "wb",
        ) as dump_file:
            dill.dump(current_generation_dump, dump_file)
        dump_file.close()

    return current_generation


"""
############ GA PARAMATERS ############
population_size
	type: int
	is number of individuals in population
	must be equal to best_individuals + lucky_few + random_new
mutation rate
	is chance of mutating a weight in an individual
	must be between 0 and 100
game attempts
	type: int
	is number of games played to determine fitness score (average)
	more games will take longer to compute fitness of each indvidiual
game_attempts_fit_individual
	type: int
	is number of games played to determine if a newly generated individual qualifies as fit
fit_threshold
	is the maximum score to qualify as fit (score = 10000 - pieces placed before death)
	lower threshold will take longer to create fit individuals
crossover_method
	is EITHER_OR or AVERAGE for create_child()
factor_method
	is NONE, VECTOR_LENGTH, MINMAX, or MAX for factoring weights of an individual
"""

population_size = 100
mutation_rate = 5
game_attempts = 1
game_attempts_fit_individual = 1
best_individuals = 80
lucky_few = 15
random_new = 5
fit_threshold = 497
crossover_method = "AVERAGE"
factor_method = "NONE"
iterations = 1000


if __name__ == "__main__":
    result_population = several_generations(epochs=iterations)
