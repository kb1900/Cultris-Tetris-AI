from c2ai.base.tetromino import Tetromino
from c2ai.base.field import Field
from c2ai.base.optimizer import Optimizer
from c2ai.learning.deap.pso.downstack.NN import neuralNetwork
from c2ai import build_absolute_path

import random
import time
import pickle
import ast


class Tetris:

    """
	Returns a ```Tetris Game``` with the given Weights, Piece Count

	"""

    def __init__(self):
        print("A Tetris Game was started")

    def run_game(n, render=False):
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
        max_piece_count = 500
        exit = 1
        seed = random.randint(0, int(len(sequence) / 4))
        # seed = 0
        sequence = sequence[seed:]

        current_tetromino = Tetromino.create(sequence[piece_count])
        clears_count = random.uniform(0.001, 1)

        while exit == 1:
            try:
                next_tetromino = Tetromino.create(sequence[piece_count + 1])

                ## GET BEST MOVE ##
                t0 = time.time()
                best_drop = Optimizer.best_move(
                    field, current_tetromino, next_tetromino, n
                )
                t1 = time.time()

                rotation = best_drop[1]
                column = best_drop[2]
                current_tetromino.rotate(rotation)

                ## RENDER & DEBUG ##
                if render == True:
                    if piece_count % 1 == 0:
                        print(field)
                        print("GETTING BEST DROP TOOK", t1 - t0, "seconds")
                        print(
                            "Current Piece:",
                            sequence[piece_count],
                            "NEW Best Rotation:",
                            rotation,
                            "NEW Best Column:",
                            column,
                        )
                        print("Next Piece:", sequence[piece_count + 1])
                        print(
                            "piece_count:", piece_count, "clears_count:", clears_count
                        )
                        heuristics = field.heuristics()
                        print(
                            "gaps",
                            heuristics[0],
                            "bumpiness",
                            heuristics[1],
                            "bog1",
                            heuristics[2],
                            "bog2",
                            heuristics[3],
                            "tall_holes",
                            heuristics[4],
                            "field_height",
                            heuristics[5],
                            "stack gaps",
                            heuristics[6],
                            "stack height",
                            heuristics[7],
                            "sum_bumps_above_two",
                            heuristics[8],
                            "trans_above_gap1",
                            heuristics[9],
                        )
                        # input()

                        ## PLACE BLOCK AND GET LINE CLEARS ##
                returns = field.drop(current_tetromino, column)
                if returns[1] > 0:
                    clears_count += returns[1]

                    ## SET UP NEXT INSTANCE ##
                previous_tetromino = current_tetromino
                current_tetromino = next_tetromino

                if piece_count % 18 == 0:
                    for i in range(4):
                        field.add_garbage()

                        ## CHECK FOR GAME END ##
                    if field.height() > 20:
                        score = [piece_count]
                        return score
                        break

                if piece_count == max_piece_count:
                    score = [piece_count]
                    return score
                    break

                piece_count += 1

            except IndexError:
                if render == True:
                    print("GAME OVER: best_drop[0] didnt exist")
                score = [piece_count]
                return score
                break
            # except:
            #     print("unhandeled error occured")
            #     break

def main():

    try:
        with open(build_absolute_path("learning/deap/pso/downstack/current_generation_dump"), "rb") as dump_file:
            dump = pickle.load(dump_file)
            current_generation = dump[0]
            n = current_generation[0]
            score = Tetris.run_game(n, render=True)
            print("loaded previous netowrk")
            print(score)
            print(n.wih)
            print(n.who)
    except:
        """
		heuristics[0] = count_gaps()
		heuristics[1] = bumpiness
		heuristics[2] = blocks_over_gap1
		heuristics[3] = blocks_over_gap2
		heuristics[4] = tall_holes
		heuristics[5] = field_height
		heuristics[6] = stack_gaps
		heuristics[7] = stack_height
		heuristics[8] = sum_bumps_above_two
		heuristics[9] = row_trans_above_gap1
		"""
        f_read = open("PSOoutput.txt", "r")
        n = ast.literal_eval(f_read.readlines()[-1])
        f_read.close()

        score = Tetris.run_game(n, render=True)
        print(score)
        print(n)

if __name__ == '__main__':
    main()
