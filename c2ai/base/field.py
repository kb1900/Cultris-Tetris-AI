from c2ai.base.tetromino import Tetromino
import random
import numpy as np
from operator import xor


class Field:

    WIDTH = 10
    HEIGHT = 20

    def __init__(self, state=None):
        if state:
            self.state = state
        else:
            self.state = [
                [" " for cols in range(Field.WIDTH)] for rows in range(Field.HEIGHT)
            ]

    def __str__(self):
        BAR = (
            "   "
            + "-" * (Field.WIDTH * 2 + 1)
            + "\n    "
            + " ".join(map(str, range(Field.WIDTH)))
            + "\n"
        )
        return (
            BAR
            + "\n".join(
                [
                    "{:2d} |".format(i) + " ".join(row) + "|"
                    for i, row in enumerate(self.state)
                ]
            )
            + "\n"
            + BAR
        )

    def _test_tetromino(self, tetromino, row, column):
        """
		Tests to see if a tetromino can be placed at the specified row and
		column. It performs the test with the bottom left corner of the
		tetromino at the specified row and column.
		"""
        assert column >= 0
        assert column + tetromino.width() <= Field.WIDTH
        assert row - tetromino.height() + 1 >= 0
        assert row < Field.HEIGHT
        for ti, si in list(enumerate(range(row - tetromino.height() + 1, row + 1)))[
            ::-1
        ]:
            for tj, sj in enumerate(range(column, column + tetromino.width())):
                if tetromino[ti][tj] != " " and self.state[si][sj] != " ":
                    return False
        return True

    def _place_tetromino(self, tetromino, row, column):
        """
		Place a tetromino at the specified row and column.
		The bottom left corner of the tetromino will be placed at the specified
		row and column. This function does not perform checks and will overwrite
		filled spaces in the field.
		"""
        assert column >= 0
        assert column + tetromino.width() <= Field.WIDTH
        assert row - tetromino.height() + 1 >= 0
        assert row < Field.HEIGHT
        for ti, si in list(enumerate(range(row - tetromino.height() + 1, row + 1)))[
            ::-1
        ]:
            for tj, sj in enumerate(range(column, column + tetromino.width())):
                if tetromino[ti][tj] != " ":
                    self.state[si][sj] = tetromino[ti][tj]

    def _place_null_tetromino(self, tetromino, row, column):
        """
		Place a tetromino at the specified row and column.
		The bottom left corner of the tetromino will be placed at the specified
		row and column. This function does not perform checks and will overwrite
		filled spaces in the field.
		"""
        for ti, si in list(enumerate(range(row - tetromino.height() + 1, row + 1)))[
            ::-1
        ]:
            for tj, sj in enumerate(range(column, column + tetromino.width())):
                self.state[si][sj] = tetromino[ti][tj]

    def _get_tetromino_drop_row(self, tetromino, column):
        """
		Given a tetromino and a column, return the row that the tetromino
		would end up in if it were dropped in that column.
		Assumes the leftmost column of the tetromino will be aligned with the
		specified column.
		"""
        assert isinstance(tetromino, Tetromino)
        assert column >= 0
        assert column + tetromino.width() <= Field.WIDTH
        last_fit = -1
        for row in range(tetromino.height(), Field.HEIGHT):
            if self._test_tetromino(tetromino, row, column):
                last_fit = row
            else:
                return last_fit
        return last_fit

    def _line_clear(self):
        """
		Checks and removes all filled lines.
		"""
        self.state = list(filter(lambda row: row.count(" ") != 0, self.state))
        c = 0
        while len(self.state) < Field.HEIGHT:
            c += 1
            self.state.insert(0, [" " for col in range(Field.WIDTH)])
        return c

    def copy(self):
        """
		Returns a shallow copy of the field.
		"""
        return Field([row[:] for row in self.state])

    def drop(self, tetromino, column):
        """
		Drops a tetromino in the specified column.
		The leftmost column of the tetromino will be aligned with the specified
		column.
		Returns the row it was dropped in for computations.
		"""
        assert isinstance(tetromino, Tetromino)
        assert column >= 0
        assert column + tetromino.width() <= Field.WIDTH

        row = self._get_tetromino_drop_row(tetromino, column)
        assert row != -1
        self._place_tetromino(tetromino, row, column)
        clears = self._line_clear()
        returns = [row, clears]

        return returns

    def drop_null(self, tetromino, row, column):
        self._place_null_tetromino(tetromino, row, column)

    def add_garbage(self):
        board_array = np.array(self.state)

        garbage_array = ["0" for _ in range(10)]
        gap = random.randint(0, self.WIDTH - 1)
        garbage_array[gap] = " "

        final_board_array = np.vstack([board_array, garbage_array])
        final_board_array = np.delete(final_board_array, (0), axis=0)

        self.state = final_board_array.tolist()

        return True

    def update_garbage(self, garbage):
        board_array = np.array(self.state)

        # first we want to make sure the height of the board stays consistent...
        # garbage[::-1] contains rows of garbage that need to be added to the end of the field.
        # so essentially we want to get the stack field (rows without garbage) then append (vstack) the garbage[::-1]
        # then we must delete rows at the top of the board so the height is correct

        row_mask = (board_array == "x").any(axis=1)  # we get a mask
        stack_array = board_array[row_mask, :]  # this is the stack field with pieces
        stack_h = len(stack_array)  # this is the stack height

        for garbage_row in garbage[::-1]:
            stack_array = np.vstack([stack_array, garbage_row])

            # print("garbage", len(garbage))
            # print("stack height", len(stack_array))
            # print("height - len(garbage) + len(stack_array)", self.HEIGHT - len(stack_array)) ##we can just add empty rows on top of this to field height

        extra_rows_to_add = self.HEIGHT - len(stack_array)
        null = [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "]

        for i in range(extra_rows_to_add):
            stack_array = np.vstack([null, stack_array])

        self.state = stack_array.tolist()
        return True

    def field_array(self):
        return np.array(self.state)

    def heuristics(self):

        heuristics = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        # first lets convert to an array
        board_array = np.array(self.state)

        """
		true_gaps initialization
		"""
        gaps = np.argwhere(board_array == " ")
        true_gaps = []
        for i in gaps:
            if (i[0] - 1) > 0 and board_array[i[0] - 1, i[1]] != " ":
                true_gaps.append(i)

        """
		stack_gaps
		"""
        stack_board_array = board_array[np.all(board_array != "0", axis=1)]

        stack_gaps = np.argwhere(stack_board_array == " ")
        true_stack_gaps = []
        for i in stack_gaps:
            if (i[0] - 1) > 0 and stack_board_array[i[0] - 1, i[1]] != " ":
                true_stack_gaps.append(i)

        """
		stack_hegiht, bumpiness, max_bump, sum_bumps_above_2
		"""
        y = []
        x = []
        heights = []
        garbage_heights = []
        for i in range(Field.WIDTH):
            try:
                j = np.where(board_array[:, i] != " ")[0][0]
                x.append([i, j])
            except:
                x.append([i, Field.HEIGHT])
            try:
                garbage_j = np.where(board_array[:, i] == "0")[0][0]
                y.append([i, garbage_j])
            except:
                y.append([i, Field.HEIGHT])

        for coord in x:
            heights.append(self.HEIGHT - coord[1])
        for coord in y:
            garbage_heights.append(self.HEIGHT - coord[1])

        stack_height = max(heights) - max(garbage_heights)
        field_height = max(heights)
        abs_height_differences = np.absolute(np.ediff1d(heights))
        bumpiness = sum(abs_height_differences)
        sum_bumps_above_two = sum([x for x in abs_height_differences if x > 2])

        """
		tall_holes, blocks over gaps 1, 2
		"""
        blocks_above_gaps = []
        tall_hole_heights = []
        for i in true_gaps:
            # print(i)
            fc = board_array[:, i[1]]
            # print("full column", fc)
            sliced = fc[: i[0]]
            blocks_above_gap = np.count_nonzero(sliced != " ")
            blocks_above_gaps.append(blocks_above_gap)

            height = 0
            for h in range(self.HEIGHT - i[0]):
                if board_array[i[0] + h, i[1]] == " ":
                    height += 1
                else:
                    break
            if height > 1:
                tall_hole_heights.append(height)

        if len(blocks_above_gaps) > 1:
            blocks_over_gap2 = blocks_above_gaps[1]
        else:
            blocks_over_gap2 = 0

        if len(blocks_above_gaps) > 0:
            blocks_over_gap1 = blocks_above_gaps[0]
        else:
            blocks_over_gap1 = 0

        """
		row_trans_above_gap1
		"""
        if len(true_gaps) > 0:
            row_above_gap1 = board_array[true_gaps[0][0] - 1, :]
            new_row = ["x"] + row_above_gap1.tolist() + ["x"]

            # print(row_above_gap1)
            transitions_indexes = []
            for y in range(len(new_row) - 1):
                transitions_indexes.append(y - 1) if xor(
                    new_row[y] != " ", new_row[y + 1] != " "
                ) else None
                # print("transitions_indexes = ", transitions_indexes)

            row_trans_above_gap1 = len(transitions_indexes)
        else:
            row_trans_above_gap1 = 0

        heuristics[0] = len(true_gaps)
        heuristics[1] = bumpiness
        heuristics[2] = blocks_over_gap1
        heuristics[3] = blocks_over_gap2
        heuristics[4] = sum(tall_hole_heights)
        heuristics[5] = field_height
        heuristics[6] = len(true_stack_gaps)
        heuristics[7] = stack_height
        heuristics[8] = sum_bumps_above_two
        heuristics[9] = row_trans_above_gap1

        return heuristics

    def tall_holes(self):
        """
		NEW tall_holes
		"""
        board_array = np.array(self.state)
        gaps = np.argwhere(board_array == " ")

        true_gaps = []
        for i in gaps:
            if (i[0] - 1) > 0:
                if board_array[i[0] - 1, i[1]] != " ":
                    true_gaps.append(i)

        tall_hole_heights = []
        for i in true_gaps:
            # print(i)
            height = 0
            for h in range(self.HEIGHT - i[0]):
                if board_array[i[0] + h, i[1]] == " ":
                    height += 1
                else:
                    break
            if height > 1:
                tall_hole_heights.append(height)

        return sum(tall_hole_heights)
        # if board_array[]

    def count_gaps(self):
        """
		Check each column one by one to make sure there are no gaps in the
		column.
		"""

        # first lets convert to an array
        board_array = np.array(self.state)

        gaps = np.argwhere(board_array == " ")
        true_gaps = []

        for i in gaps:
            if (i[0] - 1) > 0:
                if board_array[i[0] - 1, i[1]] != " ":
                    true_gaps.append(i)

        return len(true_gaps)

    def bumpiness(self):
        """
		Returns sum of the list of differences between adjacent heights
		"""

        # first lets convert to an array
        board_array = np.array(self.state)

        x = []
        for i in range(Field.WIDTH):
            try:
                j = np.where(board_array[:, i] != " ")[0][0]
                x.append([i, j])
            except:
                x.append([i, self.HEIGHT])
        heights = []
        for coord in x:
            heights.append(self.HEIGHT - coord[1])

        abs_height_differences = np.absolute(np.ediff1d(heights))
        bumpiness = sum(abs_height_differences)

        return bumpiness

    def stack_gaps(self):
        # first lets convert to an array
        board_array = np.array(self.state)
        stack_board_array = board_array[np.all(board_array != "0", axis=1)]

        stack_gaps = np.argwhere(stack_board_array == " ")
        true_stack_gaps = []

        for i in stack_gaps:
            if (i[0] - 1) > 0:
                if stack_board_array[i[0] - 1, i[1]] != " ":
                    true_stack_gaps.append(i)

        return len(true_stack_gaps)

    def stack_height(self):
        # first lets convert to an array
        board_array = np.array(self.state)
        board_array = board_array[np.all(board_array != "0", axis=1)]

        x = []
        for i in range(Field.WIDTH):
            try:
                j = np.where(board_array[:, i] != " ")[0][0]
                x.append([i, j])
            except:
                x.append([i, np.size(board_array, 0)])
        heights = []
        for coord in x:
            heights.append(np.size(board_array, 0) - coord[1])

        max_stack_height = np.max(heights)

        return max_stack_height

    def average_stack_height(self):
        # first lets convert to an array
        board_array = np.array(self.state)
        board_array = board_array[np.all(board_array != "0", axis=1)]

        x = []
        for i in range(Field.WIDTH):
            try:
                j = np.where(board_array[:, i] != " ")[0][0]
                x.append([i, j])
            except:
                x.append([i, np.size(board_array, 0)])
        heights = []
        for coord in x:
            heights.append(np.size(board_array, 0) - coord[1])
        average_stack_height = np.average(heights)

        return average_stack_height

    def height(self):
        """
		Returns the height on the field of the highest placed tetromino on the
		field.
		"""
        # first lets convert to an array
        board_array = np.array(self.state)

        x = []
        for i in range(Field.WIDTH):
            try:
                j = np.where(board_array[:, i] != " ")[0][0]
                x.append([i, j])
            except:
                x.append([i, self.HEIGHT])
        heights = []
        for coord in x:
            heights.append(self.HEIGHT - coord[1])

        max_height = np.max(heights)

        return max_height

    def average_height(self):
        """
		Returns the average height on the field of the highest placed tetromino on the
		field.
		"""

        # first lets convert to an array
        board_array = np.array(self.state)

        x = []
        for i in range(Field.WIDTH):
            try:
                j = np.where(board_array[:, i] != " ")[0][0]
                x.append([i, j])
            except:
                x.append([i, self.HEIGHT])
        heights = []
        for coord in x:
            heights.append(self.HEIGHT - coord[1])

        average_height = np.average(heights)

        return average_height

    def row_trans_above_gap1(self):
        # first lets convert to an array
        board_array = np.array(self.state)

        gaps = np.argwhere(board_array == " ")

        true_gaps = []
        for i in gaps:
            if (i[0] - 1) > 0:
                if board_array[i[0] - 1, i[1]] != " ":
                    true_gaps.append(i)

        if len(true_gaps) > 0:
            row_above_gap1 = board_array[true_gaps[0][0] - 1, :]
            new_row = ["x"] + row_above_gap1.tolist() + ["x"]

            # print(row_above_gap1)

            transitions_indexes = []
            for y in range(len(new_row) - 1):
                transitions_indexes.append(y - 1) if xor(
                    new_row[y] != " ", new_row[y + 1] != " "
                ) else None

                # print("transitions_indexes = ", transitions_indexes)

            return len(transitions_indexes)
        else:
            return 0

    def parity(self):

        # first lets convert to an array
        board_array = np.array(self.state)

        # x will hold positions (i,j) all the top most occupied squares
        x = []
        for i in range(Field.WIDTH):
            try:
                j = np.where(board_array[:, i] != " ")[0][0]
                x.append([i, j])
            except:
                pass

                # row odd column even -> white square
                # row even column odd -> white square
                # row odd column odd -> black square
                # row even column even -> black square

        black_squares = 0
        white_squares = 0
        for occupied_square in x:
            # print(occupied_square)
            i = occupied_square[0]
            j = occupied_square[1]

            if i % 2 == 0:  # i is even
                if j % 2 == 0:  # j is even
                    black_squares += 1
                else:  # j is odd
                    white_squares += 1
            else:  # i is odd
                if j % 2 == 0:  # j is even
                    white_squares += 1
                else:  # j is odd:
                    black_squares += 1

                    # print("black sq", black_squares)
                    # print("white sq", white_squares)

        parity = abs(black_squares - white_squares)
        return parity

    def total_blocks_above_gap1(self):
        # first lets convert to an array
        board_array = np.array(self.state)

        gaps = np.argwhere(board_array == " ")
        every_gaps = []

        for i in gaps:
            for h in range(0, i[0]):
                if board_array[h, i[1]] != " ":
                    every_gaps.append(i)
                    break

        x = []
        for i in range(Field.WIDTH):
            try:
                j = np.where(board_array[:, i] != " ")[0][0]
                x.append([i, j])
            except:
                x.append([i, self.HEIGHT])
        heights_rows = []
        if len(every_gaps) > 0:
            for coord in x:
                heights_rows.append(every_gaps[0][0] - coord[1])

                # print(every_gaps[0])
                # print(heights_rows)
                # print(sum(abs(np.array(heights_rows))))

        return sum(abs(np.array(heights_rows)))

    def blocks_over_gap1(self):
        """
		Returns the row and column of the highest most gap in the matrix
		GOAL: find the index (column) of each "hole"
		"""

        # first lets convert to an array
        board_array = np.array(self.state)

        gaps = np.argwhere(board_array == " ")

        true_gaps = []
        for i in gaps:
            if (i[0] - 1) > 0:
                if board_array[i[0] - 1, i[1]] != " ":
                    true_gaps.append(i)

        blocks_above_gaps = []
        for i in true_gaps:
            # print(i)
            fc = board_array[:, i[1]]
            # print("full column", fc)
            sliced = fc[: i[0]]
            blocks_above_gap = np.count_nonzero(sliced != " ")
            blocks_above_gaps.append(blocks_above_gap)

        if len(blocks_above_gaps) > 0:
            # print("blocks_above_gap1", blocks_above_gaps[0])
            return blocks_above_gaps[0]
        else:
            return 0

    def blocks_over_gap2(self):
        """
		Returns the row and column of the highest most gap in the matrix
		GOAL: find the index (column) of each "hole"
		"""

        # first lets convert to an array
        board_array = np.array(self.state)

        gaps = np.argwhere(board_array == " ")
        true_gaps = []
        for i in gaps:
            if (i[0] - 1) > 0:
                if board_array[i[0] - 1, i[1]] != " ":
                    true_gaps.append(i)

        blocks_above_gaps = []
        for i in true_gaps:
            # print(i)
            fc = board_array[:, i[1]]
            # print("full column", fc)
            sliced = fc[: i[0]]
            blocks_above_gap = np.count_nonzero(sliced != " ")
            blocks_above_gaps.append(blocks_above_gap)

        if len(blocks_above_gaps) > 1:
            # print("blocks_above_gap2", blocks_above_gaps[1])
            return blocks_above_gaps[1]
        else:
            return 0
