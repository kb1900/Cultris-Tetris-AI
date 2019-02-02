from c2ai.base.tetromino import Tetromino
from c2ai.base.field import Field
from c2ai.base.optimizer import Optimizer
from c2ai.learning.deap.pso.downstack.tetris import Tetris
from c2ai import build_absolute_path

import random
import time
import pickle
import ast


lines_sent = {
    1: 0,
    2: 1,
    3: 2,
    4: 3,
    5: 5,
    6: 7,
    7: 10,
    8: 15,
    9: 22,
    10: 31,
    11: 42,
    12: 53,
    13: 64,
    14: 75,
}


def timer(combo_time=0, clears=0, combo_counter=0):
    combo_time = combo_time  # current timer
    clears = clears  # lines cleared (returns[1])

    # additional time per Line clear is Base(counter) + NumberOfClearedLines * Bonus(counter)

    if clears > 0 and combo_time >= 0:
        combo_counter += 1

    if combo_time >= 0:
        if clears == 0:  # punish for not clearing
            combo_time = combo_time - 0.4
        else:
            if combo_counter == 1:
                combo_time = combo_time + 2.4 + clears * 1.2
            elif combo_counter == 2:
                combo_time = combo_time + 1.1 + clears * 0.6
            elif combo_counter == 3:
                combo_time = combo_time + 0.4 + clears * 0.3
            elif combo_counter == 4:
                combo_time = combo_time + 0.05 + clears * 0.2
            elif combo_counter == 5:
                combo_time = combo_time + 0.0167 + clears * 0.1
            elif combo_counter == 6:
                combo_time = combo_time + 0.005 + clears * 0.05
            elif combo_counter > 9:
                # combo_time = combo_time + (-0.775 * combo_counter + 2.925) + clears * 1.2/(2^(combo_counter-1))
                # a + b*x + c*x^2 + d*x^3
                combo_time = (
                    combo_time
                    + (
                        4.55
                        - 2.6583 * (combo_counter)
                        + 0.55 * (combo_counter ^ 2)
                        - 0.042 * (combo_counter ^ 3)
                    )
                    + clears * 1.2 / (2 ^ (combo_counter - 1))
                )
                # y0 + a/x
                # combo_time = combo_time - 0.61 + 3.0677/combo_counter + clears * 1.2/(2^(combo_counter-1))

    return [combo_time, combo_counter]


def compute_score(combos):
    sents = []
    for i in combos:
        sents.append(lines_sent[i])

    return sum(sents)


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
            # sequence = sequence.strip("\n")

        piece_count = 1
        max_piece_count = 500
        exit = 1
        seed = random.randint(0, int(len(sequence) / 4))
        combo_counter = 0
        combo_time = 0
        combos = []
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
                        print(
                            "GETTING BEST DROP TOOK",
                            "{0:.4f}".format(t1 - t0),
                            "seconds",
                        )
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
                        # print(
                        #     "gaps",
                        #     heuristics[0],
                        #     "bumpiness",
                        #     heuristics[1],
                        #     "bog1",
                        #     heuristics[2],
                        #     "bog2",
                        #     heuristics[3],
                        #     "tall_holes",
                        #     heuristics[4],
                        #     "field_height",
                        #     heuristics[5],
                        #     "\n" + "stack gaps",
                        #     heuristics[6],
                        #     "stack height",
                        #     heuristics[7],
                        #     "sum_bumps_above_two",
                        #     heuristics[8],
                        #     "trans_above_gap1",
                        #     heuristics[9],
                        # )
                        # input()

                        ## PLACE BLOCK AND GET LINE CLEARS ##
                returns = field.drop(current_tetromino, column)
                if returns[1] > 0:
                    clears_count += returns[1]

                ct = timer(
                    combo_time=combo_time,
                    clears=returns[1],
                    combo_counter=combo_counter,
                )
                combo_time = ct[0]
                combo_counter = ct[1]
                print("combo_counter", combo_counter)

                ## SET UP NEXT INSTANCE ##
                previous_tetromino = current_tetromino
                current_tetromino = next_tetromino
                combo_time = (
                    combo_time
                    - 0.08914639647649374
                    - 0.028502932752664096
                    - 0.061450676715120355
                    - (t1 - t0)
                )

                if combo_time < 0:
                    combo_time = 0
                    if combo_counter != 0:
                        combos.append(combo_counter)
                    combo_counter = 0
                print("combo_time", combo_time)
                print("TOTAL LINES SENT:", compute_score(combos))

                if piece_count % 18 == 0:
                    for i in range(4):
                        field.add_garbage()

                        ## CHECK FOR GAME END ##
                    if field.height() > 20:
                        score = [piece_count]
                        return score
                        break

                if piece_count == max_piece_count:
                    score = compute_score(combos=combos)
                    return score
                    break

                piece_count += 1

            except IndexError:
                if render == True:
                    print(combos)
                    print("GAME OVER")
                score = compute_score(combos=combos)
                return score
                break
            # except:
            #     print("unhandeled error occured")
            #     break


def main():

    try:
        with open(
            build_absolute_path("learning/deap/pso/downstack/current_generation_dump"),
            "rb",
        ) as dump_file:
            dump = pickle.load(dump_file)
            current_generation = dump[0]
            n = current_generation[0]
            score = Tetris.run_game(n, render=True)
            print("loaded previous netowrk")
            print(score)
            print(n.wih)
            print(n.who)

    except:
        f_read = open("PSOoutput.txt", "r")
        n = ast.literal_eval(f_read.readlines()[-1])
        f_read.close()

        score = Tetris.run_game(n, render=True)

        print("")
        if score >= 250:
            print("UBER LEET COMPLETE")
            print("Lines Sent:", score)
        else:
            print("Remaining Lines:", 250 - score)

        print("")
        heuristics = [
            "count_gaps",
            "bumpiness",
            "blocks_over_gap1",
            "blocks_over_gap2",
            "tall_holes",
            "field_height",
            "stack_gaps",
            "stack_height",
            "sum_bumps_above_two",
            "row_trans_above_gap1",
        ]

        for index, heuristic in enumerate(heuristics):
            print(heuristic, ":", "{0:.2f}".format(n[index]))


if __name__ == "__main__":
    main()
