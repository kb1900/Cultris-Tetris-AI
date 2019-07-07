from c2ai.base.tetromino import Tetromino
from c2ai.base.field import Field
from c2ai.base.optimizer import Optimizer
from c2ai.base import settings
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


def compute_sent(detailed_combos):
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

    def one_step(
        n,
        field,
        current_tetromino,
        next_tetromino,
        garbage=0,
        combo_counter=0,
        combo_time=0,
        combos=[],
        detailed_combos=[[]],
    ):
        """
        Run 1 step of a Tetris game

        Parameters: n = weights: scoring function weights array (1x29). garbage = garbage to recieve
        Returns: Game Over, Lines Sent if Combo complete, Field, combo_counter, combo_time, combos, detailed combos
        """

        for i in range(garbage):
            field.add_garbage()
        if field.height() > 20:
            print("GAMEOVER - garbage to add", garbage)
            return False

        if settings.mode == "upstack":
            if field.height() > 12 or field.count_gaps() > 2 or field.max_bump() > 6:
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
            if field.height() < 4 and field.count_gaps() < 3 and combo_counter < 3:
                # print(
                #     "MODE SWITCH TO UPSTACK",
                #     # field.height(),
                #     # field.count_gaps(),
                # )
                settings.mode = "upstack"

        ## GET BEST MOVE ##
        t0 = time.time()
        try:
            best_drop = Optimizer.best_move(
                field=field,
                tetromino=current_tetromino,
                next_tetromino=next_tetromino,
                n=n,
                combo_time=combo_time,
                combo_counter=combo_counter,
            )
        except IndexError:
            print("GAMEOVER")
            return False

        t1 = time.time()

        rotation = best_drop[1]
        column = best_drop[2]
        current_tetromino.rotate(rotation)

        print(field)
        print("GETTING BEST DROP TOOK", "{0:.4f}".format(t1 - t0), "seconds")

        ## PLACE BLOCK AND GET LINE CLEARS ##
        returns = field.drop(current_tetromino, column)
        if returns[1] > 0:
            detailed_combos[-1].append(returns[1])

        combo_time, combo_counter = timer(combo_time, returns[1], combo_counter)

        ## SET UP NEXT INSTANCE ##
        combo_time = (
            combo_time
            - 0.0900634319213337  # Average compute time for executing moves
            - 0.024662579271626208  # Average compute time for field image processing
            - 0.007466887216673049  # time to check game over
            - (t1 - t0)  # time to get/compute best move based on nodes + depth
        )

        sent = False
        if combo_time < 0:
            combo_time = 0
            if combo_counter:
                combos.append(combo_counter)
                sent = True
            if detailed_combos[-1]:
                detailed_combos.append([])
            combo_counter = 0

        return [field, combo_counter, combo_time, combos, detailed_combos, sent]


if __name__ == "__main__":

    ## Initialize piece sequence
    with open(build_absolute_path("base/pieces.txt"), "r") as file:
        sequence = file.read().replace("\n", "")
        # print(sequence)
        # sequence = sequence.strip("\n")
    seed = random.randint(0, int(len(sequence) / 4))

    piece_count = 1
    current_tetromino = Tetromino.create(sequence[piece_count])

    while True:
        next_tetromino = Tetromino.create(sequence[piece_count + 1])

        if piece_count == 1:
            ## Initialize Player 1
            player1_recieved_garbage = 0
            player1_combo_counter = 0
            player1_combo_time = 0
            player1_combos = []
            player1_detailed_combos = [[]]
            player1_field = Field()

            ## Initialize Player 2
            player2_recieved_garbage = 0
            player2_combo_counter = 0
            player2_combo_time = 0
            player2_combos = []
            player2_detailed_combos = [[]]
            player2_field = Field()

        player1_returns = Tetris.one_step(
            n=[17.27, 2.78, 6.76, 0.787, 12.4, 1.5, 17.85, 8.53, 1.511, 4.5],
            field=player1_field,
            current_tetromino=current_tetromino,
            next_tetromino=next_tetromino,
            garbage=player1_recieved_garbage,
            combo_counter=player1_combo_counter,
            combo_time=player1_combo_time,
            combos=player1_combos,
            detailed_combos=player1_detailed_combos,
        )
        if not player1_returns:
            print("GAMEOVER player 2 won")
            break

        print("P1 Returns", player1_returns)
        player1_field = player1_returns[0]
        player1_combo_counter = player1_returns[1]
        player1_combo_time = player1_returns[2]
        player1_combos = player1_returns[3]
        player1_detailed_combos = player1_returns[4]
        sent = player1_returns[5]

        if sent == True:  # Sent is True
            combo = player1_detailed_combos[-2]
            # print('DC', player1_detailed_combos)
            # print('COMBO', combo)
            sent_from_combos = lines_sent[len(combo)]
            sent_from_clears = lines_sent[sum(combo) - len(combo)]
            player2_recieved_garbage = sent_from_clears + sent_from_combos
        else:
            player2_recieved_garbage = 0

        print("player2_recieved_garbage", player2_recieved_garbage)

        player2_returns = Tetris.one_step(
            n=[22.5, 1.88, 6.75, -0.631, 6.579, 1.79, 0.716, 11.69, -0.993, 14.3],
            field=player2_field,
            current_tetromino=current_tetromino,
            next_tetromino=next_tetromino,
            garbage=player2_recieved_garbage,
            combo_counter=player2_combo_counter,
            combo_time=player2_combo_time,
            combos=player2_combos,
            detailed_combos=player2_detailed_combos,
        )
        if not player2_returns:
            print("GAMEOVER player 1 won")
            break

        print("P2 Returns", player2_returns)
        player2_field = player2_returns[0]
        player2_combo_counter = player2_returns[1]
        player2_combo_time = player2_returns[2]
        player2_combos = player2_returns[3]
        player2_detailed_combos = player2_returns[4]
        sent = player2_returns[5]

        if sent == True:  # Sent is True
            combo = player2_detailed_combos[-2]
            # print('DC', player2_detailed_combos)
            # print('COMBO', combo)
            sent_from_combos = lines_sent[len(combo)]
            sent_from_clears = lines_sent[sum(combo) - len(combo)]
            player1_recieved_garbage = sent_from_clears + sent_from_combos
        else:
            player1_recieved_garbage = 0

        print("player1_recieved_garbage", player1_recieved_garbage)

        piece_count += 1
        current_tetromino = next_tetromino
