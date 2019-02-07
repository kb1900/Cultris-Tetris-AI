from c2ai.base.field import Field
from c2ai.base.tetromino import Tetromino
from c2ai.base import settings
from operator import itemgetter


class Optimizer:
    @staticmethod
    def get_score(field, clears, row=0, n=0, combo_time=0, combo_counter=0):
        f = field

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
        heuristics = f.heuristics()

        # features = [heuristics[0], heuristics[1], heuristics[3],heuristics[4],heuristics[5],heuristics[6],heuristics[7], heuristics[8],heuristics[9],heuristics[10]]

        if settings.modes == True:
            if settings.train == True:
                if settings.mode == "upstack":
                    if clears > 0:
                        score = float("inf")
                    else:
                        score = sum(x * y for x, y in zip(heuristics, settings.upstack_model))
                elif settings.mode == "downstack":
                    score = sum(x * y for x, y in zip(heuristics, n))
            else:
                if settings.mode == "upstack":
                    if clears > 0:
                        score = float("inf")
                    else:
                        score = sum(
                            x * y for x, y in zip(heuristics, settings.upstack_model)
                        )
                elif settings.mode == "downstack":
                    score = sum(
                        x * y for x, y in zip(heuristics, settings.downstack_model)
                    )
                elif settings.mode == "test1":
                    score = sum(x * y for x, y in zip(heuristics, settings.test_model))

                elif settings.mode == "test2":
                    score = sum(
                        x * y for x, y in zip(heuristics, settings.downstack_model)
                    )
        else:
            score = sum(x * y for x, y in zip(heuristics, settings.test_model))

        if settings.combo == True:
            if combo_time < 1:
                combo_time += 1
            score = score / (combo_time)
        return float(score)

    @staticmethod
    def best_move(field, tetromino, next_tetromino, n=0, combo_time=0, combo_counter=0):
        # Here we should limit the number of rotations checked for symetric pieces like O, S, Z, I
        # O (only tetromino)
        # I (only tetromino + rotate_right)
        # S (only tetromino + rotate_right)
        # Z (only tetromino + rotate_right)
        rotations = [
            tetromino,
            tetromino.copy().rotate_right(),
            tetromino.copy().flip(),
            tetromino.copy().rotate_left(),
        ]
        if tetromino.state == Tetromino.O_Tetromino().state:
            # print('O DETECTED')
            rotations = [tetromino]
        if (
            tetromino.state == Tetromino.I_Tetromino().state
            or tetromino.state == Tetromino.S_Tetromino().state
            or tetromino.state == Tetromino.Z_Tetromino().state
        ):
            # print('I/S/Z DETECTED')
            rotations = [tetromino, tetromino.copy().rotate_right()]
        all_boards_first = []
        for rotation_counter, tetromino_rotation in enumerate(rotations):
            for column in range(Field.WIDTH):
                field_copy = field.copy()
                try:
                    clears1 = field_copy.drop(tetromino_rotation, column)[1]
                    score = Optimizer.get_score(
                        field=field_copy,
                        clears=clears1,
                        n=n,
                        combo_time=combo_time,
                        combo_counter=combo_counter,
                    )
                    # print(tetromino_rotation, " ",column, "score:", score)
                    # print(field_copy)
                    all_boards_first.append(
                        [field_copy, rotation_counter, column, score]
                    )
                except AssertionError:
                    # print(tetromino_rotation, column, "AssertionError")
                    continue

        all_boards_first.sort(
            key=itemgetter(3)
        )  # sort by first piece placed board scores

        # for i in all_boards_first:
        #   print(i[3])

        if (
            len(all_boards_first) > 1
        ):  # benchmarking suggests a linear increase of 0.02s per move for every increase in top current piece moves explored
            # 1 = 0.050; 2 = 0.073; 3 = 0.095; 4 = 0.114; 5 = 0.143; 6 = 0.163
            all_boards_first = all_boards_first[: settings.move_depth]

        # Again we should limit the number of rotations checked for symetric pieces like O, S, Z, I
        # O (only tetromino)
        # I (only tetromino + rotate_right)
        # S (only tetromino + rotate_right)
        # Z (only tetromino + rotate_right)
        next_rotations = [
            next_tetromino,
            next_tetromino.copy().rotate_right(),
            next_tetromino.copy().flip(),
            next_tetromino.copy().rotate_left(),
        ]
        if next_tetromino.state == Tetromino.O_Tetromino().state:
            next_rotations = [next_tetromino]
        if (
            next_tetromino.state == Tetromino.I_Tetromino().state
            or next_tetromino.state == Tetromino.S_Tetromino().state
            or next_tetromino.state == Tetromino.Z_Tetromino().state
        ):
            next_rotations = [next_tetromino, next_tetromino.copy().rotate_right()]
        for i in all_boards_first:
            second_scores = []
            for next_tetromino_rotation in next_rotations:
                for column in range(Field.WIDTH):
                    next_field_copy = i[0].copy()
                    try:
                        clears2 = next_field_copy.drop(next_tetromino_rotation, column)[
                            1
                        ]
                        score = Optimizer.get_score(
                            field=next_field_copy,
                            clears=clears2,
                            n=n,
                            combo_time=combo_time,
                            combo_counter=combo_counter,
                        )
                        second_scores.append(score)

                    except AssertionError:
                        # print(tetromino_rotation, column, "AssertionError")
                        score = float("inf")
                        second_scores.append(score)

            min_score_second = min(second_scores)
            i.append(min_score_second)
            if settings.combo == True and clears1 != 0:
                final_score = min_score_second + i[3]
            else:
                final_score = min_score_second
            i.append(final_score)

        all_boards_first.sort(
            key=lambda x: x[-1]
        )  # sort by minimum second piece placed board score

        # for i in all_boards_first:
        #     print('rotation', i[1], 'column', i[2], 'score1', round(i[3], 2), 'score2', round(i[4], 2), 'final_score', round(i[5], 2))
        # print('')
        return all_boards_first[0]

    @staticmethod
    def get_keystrokes(rotation, column, keymap, tetromino_name):

        keys = []
        ############# NO ROTATION ################

        if rotation == 0 or tetromino_name == "O":
            if tetromino_name == "O":
                # print("moving O piece to column #", column)
                if column == 4:
                    pass
                elif column > 4:
                    for i in range(column - 4):
                        keys.append(keymap["move_right"])
                elif column < 4:
                    for i in range(4 - column):
                        keys.append(keymap["move_left"])

            elif tetromino_name == "T" and rotation == 0:
                # print("moving T piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

            elif tetromino_name == "I" and rotation == 0:
                # print("moving I piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

            elif tetromino_name == "L" and rotation == 0:
                # print("moving L piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

            elif tetromino_name == "J" and rotation == 0:
                # print("moving J piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

            elif tetromino_name == "S" and rotation == 0:
                # print("moving S piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

            elif tetromino_name == "Z" and rotation == 0:
                # print("moving Z piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

                ############# 180 DEG ROTATION ################
        elif rotation == 2:
            keys.append(keymap["rotate_180"])

            if tetromino_name == "T":
                # print("moving T piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

            elif tetromino_name == "I":
                # print("moving I piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

            elif tetromino_name == "L":
                # print("moving L piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

            elif tetromino_name == "J":
                # print("moving J piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

                ############# TEST AREA ROTATION ################
        elif rotation == 1 and tetromino_name == "I":
            keys.append(keymap["rotate_right"])

            if tetromino_name == "I":
                # print("moving CW ROTATED I piece to column #", column)
                if column == 5:
                    pass
                elif column > 5:
                    for i in range(column - 5):
                        keys.append(keymap["move_right"])
                elif column < 5:
                    for i in range(5 - column):
                        keys.append(keymap["move_left"])

        elif rotation == 3 and tetromino_name == "I":
            keys.append(keymap["rotate_left"])

            if tetromino_name == "I":
                # print("moving CCW ROTATED I piece to column #", column)
                if column == 4:
                    pass
                elif column > 4:
                    for i in range(column - 4):
                        keys.append(keymap["move_right"])
                elif column < 4:
                    for i in range(4 - column):
                        keys.append(keymap["move_left"])

        elif rotation == 1 and tetromino_name == "T":
            keys.append(keymap["rotate_right"])

            if tetromino_name == "T":
                # print("moving CW ROTATED T piece to column #", column)
                if column == 4:
                    pass
                elif column > 4:
                    for i in range(column - 4):
                        keys.append(keymap["move_right"])
                elif column < 4:
                    for i in range(4 - column):
                        keys.append(keymap["move_left"])

        elif rotation == 3 and tetromino_name == "T":
            keys.append(keymap["rotate_left"])

            if tetromino_name == "T":
                # print("moving CCW ROTATED T piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

        elif rotation == 1 and tetromino_name == "S":
            keys.append(keymap["rotate_right"])

            if tetromino_name == "S":
                # print("moving CW ROTATED S piece to column #", column)
                if column == 4:
                    pass
                elif column > 4:
                    for i in range(column - 4):
                        keys.append(keymap["move_right"])
                elif column < 4:
                    for i in range(4 - column):
                        keys.append(keymap["move_left"])

        elif rotation == 3 and tetromino_name == "S":
            keys.append(keymap["rotate_left"])

            if tetromino_name == "S":
                # print("moving CCW ROTATED S piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

        elif rotation == 1 and tetromino_name == "Z":
            keys.append(keymap["rotate_right"])

            if tetromino_name == "Z":
                # print("moving CW ROTATED Z piece to column #", column)
                if column == 4:
                    pass
                elif column > 4:
                    for i in range(column - 4):
                        keys.append(keymap["move_right"])
                elif column < 4:
                    for i in range(4 - column):
                        keys.append(keymap["move_left"])

        elif rotation == 3 and tetromino_name == "Z":
            keys.append(keymap["rotate_left"])

            if tetromino_name == "Z":
                # print("moving CCW ROTATED Z piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

        elif rotation == 1 and tetromino_name == "J":
            keys.append(keymap["rotate_right"])

            if tetromino_name == "J":
                # print("moving CW ROTATED J piece to column #", column)
                if column == 4:
                    pass
                elif column > 4:
                    for i in range(column - 4):
                        keys.append(keymap["move_right"])
                elif column < 4:
                    for i in range(4 - column):
                        keys.append(keymap["move_left"])

        elif rotation == 3 and tetromino_name == "J":
            keys.append(keymap["rotate_left"])

            if tetromino_name == "J":
                # print("moving CCW ROTATED J piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])

        elif rotation == 1 and tetromino_name == "L":
            keys.append(keymap["rotate_right"])

            if tetromino_name == "L":
                # print("moving CW ROTATED L piece to column #", column)
                if column == 4:
                    pass
                elif column > 4:
                    for i in range(column - 4):
                        keys.append(keymap["move_right"])
                elif column < 4:
                    for i in range(4 - column):
                        keys.append(keymap["move_left"])

        elif rotation == 3 and tetromino_name == "L":
            keys.append(keymap["rotate_left"])

            if tetromino_name == "L":
                # print("moving CCW ROTATED L piece to column #", column)
                if column == 3:
                    pass
                elif column > 3:
                    for i in range(column - 3):
                        keys.append(keymap["move_right"])
                elif column < 3:
                    for i in range(3 - column):
                        keys.append(keymap["move_left"])
                ############# UNHANDELED FINESSE CASES ################
        else:
            print("UNFINISHED FINESSE CASE", tetromino_name)
            # First we orient the tetronimo
            if rotation == 1:
                keys.append(keymap["rotate_right"])
            elif rotation == 2:
                keys.append(keymap["rotate_180"])
            elif rotation == 3:
                keys.append(keymap["rotate_left"])
                # Then we move it all the way to the the left that we are guaranteed
                # that it is at column 0. The main reason for doing this is that when
                # the tetromino is rotated, the bottom-leftmost piece in the tetromino
                # may not be in the 3rd column due to the way Tetris rotates the piece
                # about a specific point. There are too many edge cases so instead of
                # implementing tetromino rotation on the board, it's easier to just
                # flush all the pieces to the left after orienting them.
            for i in range(5):
                keys.append(keymap["move_left"])
                # Now we can move it back to the correct column. Since pyautogui's
                # typewrite is instantaneous, we don't have to worry about the delay
                # from moving it all the way to the left.
            for i in range(column):
                keys.append(keymap["move_right"])

                ############# ADDING HARDDROP TO END OF KEYS ################
        keys.append(keymap["drop"])

        return keys


if __name__ == "__main__":
    f = Field()
