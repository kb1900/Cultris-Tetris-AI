from c2ai.base.field import Field
from c2ai.base.tetromino import Tetromino
from c2ai.base import settings
from operator import itemgetter
import multiprocessing as mp
import time


class Optimizer:
    @staticmethod
    def score_board(board, n=0):
        if board[0] == False:
            return float("inf")
        heuristics = board[0].heuristics()
        if settings.modes:
            if settings.train:
                model = n
            else:
                model = settings.downstack_model

        return sum(x * y for x, y in zip(heuristics, model))

    @staticmethod
    def get_all_boards_sequential(field, rotations, next_rotations, deep=True):
        # Returns a list of all_boards_shallow based on the first tetromino's placement options
        # Returns a lit of all_boards_deep based on the second tetromino's placement options for each board in all_boards_shallow
        all_boards_shallow = []
        # rotations = Optimizer.get_all_rotations(tetromino)

        # Iterate through rotations, columns
        for rotation_counter, tetromino_rotation in enumerate(rotations):
            for column in range(Field.WIDTH - tetromino_rotation.width() + 1):
                field_copy = field.copy()
                clears = field_copy.drop(tetromino_rotation, column)[1]
                # print(field_copy)
                all_boards_shallow.append(
                    [field_copy, rotation_counter, column, clears]
                )
        if deep == False:
            return all_boards_shallow

        all_boards_deep = []
        # next_rotations = Optimizer.get_all_rotations(next_tetromino)

        # Iterate through each board in all_boards_shallow, then iterate through rotations, columns
        for board in all_boards_shallow:
            for rotation_counter, tetromino_rotation in enumerate(next_rotations):
                for column in range(Field.WIDTH - tetromino_rotation.width() + 1):
                    field_copy = board[0].copy()
                    first_rotation = board[1]
                    first_column = board[2]
                    first_piece_clears = board[3]
                    second_piece_clears = field_copy.drop(tetromino_rotation, column)[1]
                    all_boards_deep.append(
                        [
                            field_copy,
                            first_rotation,
                            first_column,
                            first_piece_clears,
                            rotation_counter,
                            column,
                            second_piece_clears,
                        ]
                    )
        return all_boards_deep

    @staticmethod
    def get_all_rotations(tetromino):
        # Returns a list of tetrominos, rotated with pruning to avoid symetric rotations
        if tetromino.type == "O":
            rotations = [tetromino]
        elif tetromino.type in ("I", "S", "Z"):
            rotations = [tetromino.copy() for r in range(2)]
        else:
            rotations = [tetromino.copy() for r in range(4)]
        for i in range(len(rotations)):
            rotations[i].rotate(i)

        return rotations

    @staticmethod
    def get_first_board(field, tetromino_rotation, rotation_count, column):
        # given a rotation, column, next_rotation, next_column
        # returns [field, rotation, column, clears]
        field = field.copy()
        try:
            clears = field.drop(tetromino_rotation, column)[1]
        except AssertionError:
            field = False
            clears = 0
        return [field, rotation_count, column, clears]

    @staticmethod
    def get_second_board(
        field,
        first_rotation_count,
        first_column,
        first_clears,
        second_tetromino_rotation,
        second_rotation_count,
        second_column,
    ):
        # given a rotation, column, next_rotation, next_column
        # returns [field, rotation, column, clears]
        try:
            field = field.copy()
            clears = field.drop(second_tetromino_rotation, second_column)[1]
        except:
            field = False
            clears = 0
        return [
            field,
            first_rotation_count,
            first_column,
            first_clears,
            second_rotation_count,
            second_column,
            clears,
        ]

    def best_move(field, tetromino, next_tetromino, n=0, combo_time=0, combo_counter=0):
        print("WE HAVE ARRIVED HERE")

        # need to create a moves list of [field, tetromino_rotation, rotation_count, column] to feeed into get_board()
        rotations = Optimizer.get_all_rotations(tetromino)
        next_rotations = Optimizer.get_all_rotations(next_tetromino)
        first_moves = []
        # First piece moves
        for rotation_counter, tetromino_rotation in enumerate(rotations):
            for column in range(Field.WIDTH - tetromino_rotation.width() + 1):
                first_moves.append(
                    [field, tetromino_rotation, rotation_counter, column]
                )

        pool = mp.Pool(processes=4)
        first_boards = list(pool.starmap(Optimizer.get_first_board, first_moves))
        pool.close()
        print("WE HAVE ARRIVED HERE2")
        second_moves = []
        # Second piece moves
        for firstboard in first_boards:
            for rotation_counter, tetromino_rotation in enumerate(next_rotations):
                for column in range(Field.WIDTH - tetromino_rotation.width() + 1):
                    second_moves.append(
                        [
                            firstboard[0],  # first move field
                            firstboard[1],  # first move rotation counter
                            firstboard[2],  # first move column
                            firstboard[3],  # first move clears
                            tetromino_rotation,  # second move rotation
                            rotation_counter,  # second move rotation counter
                            column,  # second move columnm
                        ]
                    )
        pool = mp.Pool(processes=4)
        all_boards = list(pool.starmap(Optimizer.get_second_board, second_moves))
        pool.close()
        print("WE HAVE ARRIVED HERE3")

        pool = mp.Pool(processes=4)
        scores = list(pool.map(Optimizer.score_board, all_boards))
        pool.close()
        print("WE HAVE ARRIVED HERE4")
        for index, score in enumerate(scores):
            all_boards[index].append(score)

        all_boards.sort(key=lambda x: x[-1])
        return all_boards[0]

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
    try:
        mp.set_start_method("forkserver")
    except RuntimeError:
        pass
    f = Field()
    tetromino = Tetromino.J_Tetromino()
    next_tetromino = Tetromino.T_Tetromino()
    rotations = Optimizer.get_all_rotations(tetromino)
    next_rotations = Optimizer.get_all_rotations(next_tetromino)

    start = time.time()
    all_boards = Optimizer.get_all_boards_sequential(f, rotations, next_rotations)
    print("Total number of boards:", len(all_boards), "\n")
    print("Getting all boards linearly took", time.time() - start, "seconds")

    start = time.time()
    # need to create a moves list such that we have [field, tetromino_rotation, rotation_count, column] to feeed into get_board
    first_moves = []
    # First piece moves
    for rotation_counter, tetromino_rotation in enumerate(rotations):
        for column in range(Field.WIDTH - tetromino_rotation.width() + 1):
            first_moves.append([f, tetromino_rotation, rotation_counter, column])

    pool = mp.Pool(processes=4)
    first_boards = list(pool.starmap(Optimizer.get_first_board, first_moves))
    pool.close()

    second_moves = []
    # Second piece moves
    for firstboard in first_boards:
        for rotation_counter, tetromino_rotation in enumerate(next_rotations):
            for column in range(Field.WIDTH - tetromino_rotation.width() + 1):
                second_moves.append(
                    [
                        firstboard[0],  # first move field
                        firstboard[1],  # first move rotation counter
                        firstboard[2],  # first move column
                        firstboard[3],  # first move clears
                        tetromino_rotation,  # second move rotation
                        rotation_counter,  # second move rotation counter
                        column,  # second move columnm
                    ]
                )
    pool = mp.Pool(processes=4)
    all_boards = list(pool.starmap(Optimizer.get_second_board, second_moves))
    pool.close()
    print("Getting all boards with 2x starmap took", time.time() - start, "seconds \n")

    start = time.time()
    for board in all_boards:
        board.append(Optimizer.score_board(board))
    print("Scoring all boards linearly took", time.time() - start, "seconds")

    start = time.time()
    pool = mp.Pool(processes=4)
    scores = list(pool.map(Optimizer.score_board, all_boards))
    pool.close()
    for index, score in enumerate(scores):
        all_boards[index].append(score)
    print("Scoring all boards with map took:", time.time() - start, "seconds \n")

    start = time.time()
    all_boards.sort(key=lambda x: x[-1])
    print("Ranking boards took", time.time() - start, "seconds")
    print(all_boards[0])
