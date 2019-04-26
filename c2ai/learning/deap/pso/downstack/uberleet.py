from c2ai.base.tetromino import Tetromino
from c2ai.base.field import Field
from c2ai.base.optimizer import Optimizer
from c2ai.base import settings
from c2ai.learning.deap.pso.downstack.tetris import Tetris
from c2ai import build_absolute_path

import random
import time
import pickle
import ast


lines_sent = {
    0: 0,
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
    if clears:
        combo_counter += 1

    # additional time per Line clear is Base(counter) + NumberOfClearedLines * Bonus(counter)
    if combo_time >= 0:
        if not clears:  # punish for not clearing
            combo_time = combo_time - 0.42
            if 1 < combo_counter < 5:
                combo_time += (1 - combo_counter) * 0.015
            else:
                combo_time += (1 - combo_counter) * 0.03
        else:
            if combo_counter == 1:
                combo_time += 2.4 + clears * 1.2
            elif combo_counter == 2:
                combo_time += 1.1 + clears * 0.6
            elif combo_counter == 3:
                combo_time += 0.4 + clears * 0.3
            elif combo_counter == 4:
                combo_time += 0.05 + clears * 0.15
            elif combo_counter == 5:
                combo_time += clears * 0.075
            elif combo_counter == 6:
                combo_time += clears * 0.0375
            elif combo_counter == 7:
                combo_time += clears * 0.01875 - 0.2
            elif combo_counter == 8:
                combo_time += clears * 0.009375 - 0.3
            elif combo_counter == 9:
                combo_time += clears * 0.0046875 - 0.4
            elif combo_counter == 10:
                combo_time += -0.6
            elif combo_counter == 11:
                combo_time += -0.8
            else:
                combo_time += -1

    return combo_time, combo_counter


def compute_score(detailed_combos):
    sent_from_combos = sum(lines_sent[len(combo)] for combo in detailed_combos)
    sent_from_clears = sum(sum(combo) - len(combo) for combo in detailed_combos)
    # print("Lines Sent From Combos: ", sent_from_combos)
    # print("Lines Sent From Clears: ", sent_from_clears)
    # print("Lines Sent", sent_from_clears + sent_from_combos)
    return sent_from_clears + sent_from_combos


class Tetris:

    """
    Returns a ```Tetris Game``` with the given Weights, Piece Count

    """

    def __init__(self):
        print("A Tetris Game was started")

    def run_game(n, render=False):
        """
        Runs a Tetris simulation until either:
        1) The max piece count is reached
        2) The game was lost

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
        detailed_combos = [[]]
        # seed = 0
        sequence = sequence[seed:]

        current_tetromino = Tetromino.create(sequence[piece_count])
        clears_count = random.uniform(0.001, 1)

        while exit == 1:
            try:
                next_tetromino = Tetromino.create(sequence[piece_count + 1])

                if settings.mode == "upstack":
                    if (
                        field.height() > 12
                        or field.count_gaps() > 2
                        or field.max_bump() > 6
                    ):
                        # print(
                        #     "MODE SWITCH TO DOWNSTACK",
                        #     # field.height(),
                        #     # field.count_gaps(),
                        # )
                        settings.mode = "downstack"
                if settings.mode == "downstack":
                    if combo_counter > 6 or combo_counter + combo_time > 8.5:
                        settings.combo = True
                        # print("COMBO ACTIVE")
                    else:
                        settings.combo = False
                    if (
                        field.height() < 4
                        and field.count_gaps() < 3
                        and combo_counter < 3
                    ):
                        # print(
                        #     "MODE SWITCH TO UPSTACK",
                        #     # field.height(),
                        #     # field.count_gaps(),
                        # )
                        settings.mode = "upstack"

                ## GET BEST MOVE ##
                t0 = time.time()
                best_drop = Optimizer.best_move(
                    field=field,
                    tetromino=current_tetromino,
                    next_tetromino=next_tetromino,
                    n=n,
                    combo_time=combo_time,
                    combo_counter=combo_counter,
                )
                t1 = time.time()

                rotation = best_drop[1]
                column = best_drop[2]
                current_tetromino.rotate(rotation)

                ## RENDER & DEBUG ##
                if render:
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
                    detailed_combos[-1].append(returns[1])

                combo_time, combo_counter = timer(combo_time, returns[1], combo_counter)

                ## SET UP NEXT INSTANCE ##
                current_tetromino = next_tetromino
                combo_time = (
                    combo_time
                    - 0.0900634319213337  # Average compute time for executing moves
                    - 0.024662579271626208  # Average compute time for field image processing
                    - 0.007466887216673049  # time to check game over
                    - (t1 - t0) # time to get/compute best move based on nodes + depth
                )

                if combo_time < 0:
                    combo_time = 0
                    if combo_counter:
                        combos.append(combo_counter)
                    if detailed_combos[-1]:
                        detailed_combos.append([])
                    combo_counter = 0
                # print("combo_time", combo_time)
                # print("TOTAL LINES SENT:", compute_score(combos))

                if piece_count % 21 == 0:
                    for i in range(4):
                        field.add_garbage()

                    ## CHECK FOR GAME END ##
                    if field.height() > 20:
                        return piece_count

                if piece_count == max_piece_count:
                    return compute_score(detailed_combos)

                piece_count += 1

            except IndexError:
                if render:
                    print("GAME OVER")
                    print("Combos: ", combos)
                    print("Detailed Combos: ", detailed_combos)
                return compute_score(detailed_combos)


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
