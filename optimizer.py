from field import Field
import settings
from operator import itemgetter
import threading
import queue


def get_current_rotations(tetromino, que):

    # Here we should limit the number of rotations checked for symmetric pieces like O, S, Z, I
    if tetromino.type == "O":
        rotations = [tetromino]
    elif tetromino.type in ("I", "S", "Z"):
        rotations = [tetromino.copy() for r in range(2)]
    else:
        rotations = [tetromino.copy() for r in range(4)]

    return que.put(rotations)


def get_next_rotations(next_tetromino, que):
    if next_tetromino.type == "O":
        next_rotations = [next_tetromino]
    elif next_tetromino.type in ("I", "S", "Z"):
        next_rotations = [next_tetromino.copy() for r in range(2)]
    else:
        next_rotations = [next_tetromino.copy() for r in range(4)]

    return que.put(next_rotations)


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

        if settings.modes:
            if settings.train:
                if settings.mode == "upstack":
                    if clears > 0:
                        score = float("inf")
                    else:
                        score = sum(
                            x * y for x, y in zip(heuristics, settings.upstack_model)
                        )
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
                    score = sum(
                        x * y for x, y in zip(heuristics, settings.test_model))

                elif settings.mode == "test2":
                    score = sum(
                        x * y for x, y in zip(heuristics, settings.downstack_model)
                    )
        else:
            score = sum(x * y for x, y in zip(heuristics, settings.test_model))

        if settings.combo:
            if combo_time < 1:
                combo_time += 1
            score = score / (combo_time)
        return float(score)

    @staticmethod
    def best_move(field, tetromino, next_tetromino, n=0, combo_time=0, combo_counter=0):
        node = 0
        combo_priority = False

        cur_que = queue.Queue()
        next_que = queue.Queue()

        t1 = threading.Thread(
            target=get_current_rotations, args=(tetromino, cur_que))

        t2 = threading.Thread(
            target=get_next_rotations, args=(next_tetromino, next_que))

        t1.start()
        t2.start()

        rotations = cur_que.get()
        # Here we should limit the number of rotations checked for symmetric pieces like O, S, Z, I
        # rotations = get_current_rotations(tetromino)
        for i in range(len(rotations)):
            rotations[i].rotate(i)

        # Again we should limit the number of rotations checked for symmetric pieces like O, S, Z, I
        next_rotations = next_que.get()
        for i in range(len(next_rotations)):
            next_rotations[i].rotate(i)

        all_boards_first = []
        for rotation_counter, tetromino_rotation in enumerate(rotations):
            for column in range(Field.WIDTH - tetromino_rotation.width() + 1):
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

                    if clears1:
                        if settings.combo and combo_counter > 5:
                            score = score / clears1
                            combo_priority = True

                    # print(tetromino_rotation, " ",column, "score:", score)
                    # print(field_copy)
                    all_boards_first.append(
                        [field_copy, rotation_counter, column, score]
                    )
                except AssertionError:
                    # print(tetromino_rotation, column, "AssertionError")
                    continue
                node += 1

        # benchmarking suggests a linear increase of 0.02s per move for every increase in top current piece moves explored
        all_boards_first.sort(
            key=itemgetter(3)
        )  # sort by first piece placed board scores
        # 1 = 0.050; 2 = 0.073; 3 = 0.095; 4 = 0.114; 5 = 0.143; 6 = 0.163
        all_boards_first = all_boards_first[: settings.move_depth]

        for i in all_boards_first:
            if combo_priority == True:
                print("Priority active for combo!! \n")
                break
            second_scores = []
            for next_tetromino_rotation in next_rotations:
                for column in range(Field.WIDTH - next_tetromino_rotation.width() + 1):
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

                        if combo_counter > 8:
                            if clears2:
                                combo_priority = True
                                score = score / clears2
                                break

                        second_scores.append(score)

                    except AssertionError:
                        # print(tetromino_rotation, column, "AssertionError")
                        score = float("inf")
                        second_scores.append(score)
                    node += 1

            min_score_second = min(second_scores)
            i.append(min_score_second)
            ## This makes no sense - fix it ##
            if settings.combo:
                if clears1:
                    final_score = min_score_second + i[3]
                elif clears2:
                    final_score = min_score_second + i[3] + 75
                else:
                    final_score = min_score_second + i[3] + 150
            else:
                final_score = min_score_second
            i.append(final_score)
            if node > settings.max_nodes:
                break

        all_boards_first.sort(
            key=lambda x: x[-1]
        )  # sort by minimum second piece placed board score

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

            for i in range(5):
                keys.append(keymap["move_left"])

            for i in range(column):
                keys.append(keymap["move_right"])

        ############# ADDING HARDDROP TO END OF KEYS ################
        keys.append(keymap["drop"])

        return keys


if __name__ == "__main__":
    f = Field()
