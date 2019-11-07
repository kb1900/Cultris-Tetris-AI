from tetromino import Tetromino
from field import Field
from optimizer import Optimizer
import settings


import random
import time
import ast

import requests


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
        with open(("pieces.txt"), "r") as file:
            sequence = file.read().replace("\n", "")

        piece_count = 1
        max_piece_count = 500
        seed = random.randint(0, int(len(sequence) / 4))
        combo_counter = 0
        combo_time = 0
        combos = []
        detailed_combos = [[]]
        sequence = sequence[seed:]

        current_tetromino = Tetromino.create(sequence[piece_count])

        current_tetromino = Tetromino.create("L")
        # print(current_tetromino.state)
        # print([[" ", " ", "x"], ["x", "x", "x"]])
        # time.sleep(100)

        clears_count = random.uniform(0.001, 1)

        while 1:
            try:
                next_tetromino = Tetromino.create(sequence[piece_count + 1])

                r0 = time.time()
                r = requests.get(
                    "http://localhost:9876/mode/{}/{}/{}/{}/{}/{}".format(
                        settings.mode,
                        field.height(),
                        field.count_gaps(),
                        field.max_bump(),
                        combo_counter,
                        combo_time,
                    )
                )
                print("Requests took", time.time() - r0)

                settings.mode = r.json()["mode"]
                # tries to get the value for combo if the key is invalid sets it to false
                settings.combo = r.json().get("combo", False)

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
                            "\n" + "stack gaps",
                            heuristics[6],
                            "stack height",
                            heuristics[7],
                            "sum_bumps_above_two",
                            heuristics[8],
                            "trans_above_gap1",
                            heuristics[9],
                        )
                        input()

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
                    # time to get/compute best move based on nodes + depth
                    - (t1 - t0)
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
