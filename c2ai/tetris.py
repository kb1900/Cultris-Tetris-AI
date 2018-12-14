from c2ai.base.tetromino import Tetromino
from c2ai.base.field import Field
from c2ai.base.optimizer import Optimizer
from c2ai import build_absolute_path

import random
import time
import pickle


class Tetris:

    """
	Returns a ```Tetris Game``` with the given Weights, Piece Count

	"""

    def __init__(self):
        print("A Tetris Game was started")

    def run_game(weights, render=False):
        """
		Runs a Tetris simulation until either 1) The max piece count is reached or 2) The game was lost

		Parameters: weights: scoring function weights array (1x29)
		Returns: piece_count: pieces placed prior to game end

		"""
        field = Field()
        with open(build_absolute_path("base/pieces.txt"), "r") as file:
            sequence = file.read().replace("\n", "")
            # print(sequence)
            # sequence = sequence.strip('\n')

        piece_count = 1
        max_piece_count = 100000
        exit = 1
        seed = random.randint(0, int(len(sequence) / 4))
        sequence = sequence[seed:]

        current_tetromino = Tetromino.create(sequence[piece_count])

        clears_count = random.uniform(0.001, 1)

        while exit == 1:
            try:
                next_tetromino = Tetromino.create(sequence[piece_count + 1])

                best_drop = Optimizer.get_best_drop(
                    field, current_tetromino, next_tetromino, weights
                )
                # best_drop = Optimizer.get_optimal_drop(field, current_tetromino, next_tetromino, weights)
                # opt = best_drop[0]

                rotation = best_drop[1]
                column = best_drop[2]

                current_tetromino.rotate(rotation)
                returns = field.drop(current_tetromino, column)
                if returns[1] > 0:
                    clears_count += 1

                previous_tetromino = current_tetromino
                current_tetromino = next_tetromino

                if piece_count == max_piece_count:
                    score = [piece_count + random.uniform(0.001, 1), clears_count]
                    return score
                    break

                if render == True:
                    if piece_count % 10 == 0:
                        print(field)
                        print(
                            "piece_count:", piece_count, "clears_count:", clears_count
                        )
                        # time.sleep(0.040)

                piece_count += 1

            except:
                score = [piece_count + random.uniform(0.001, 1), clears_count]
                return score
                break


if __name__ == "__main__":

    def generate_weight():
        WEIGHT = []
        n = 0
        while n < 8:
            i = round(random.uniform(0, 1000), 4)
            WEIGHT.append(i)
            n += 1
        return WEIGHT

    try:
        with open("current_generation_dump", "rb") as dump_file:
            dump = pickle.load(dump_file)
            current_generation = dump[0]
            w0 = current_generation[0]
    except:
        w0 = generate_weight()

    score = Tetris.run_game(w0, render=True)
    print(score)
