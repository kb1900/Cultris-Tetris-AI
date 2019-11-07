class Tetromino:

    TYPES = ["I", "O", "T", "S", "Z", "J", "L", "x"]

    def __init__(self, state, type=""):
        # assert that there are rows
        assert len(state) > 0
        assert type in Tetromino.TYPES
        # assert rows and columns form a rectangle
        assert len({len(row) for row in state}) == 1
        self.state = state
        self.type = type

    @staticmethod
    def I_Tetromino():
        return Tetromino([["x", "x", "x", "x"]], "I")

    @staticmethod
    def O_Tetromino():
        return Tetromino([["x", "x"], ["x", "x"]], "O")

    @staticmethod
    def T_Tetromino():
        return Tetromino([[" ", "x", " "], ["x", "x", "x"]], "T")

    @staticmethod
    def S_Tetromino():
        return Tetromino([[" ", "x", "x"], ["x", "x", " "]], "S")

    @staticmethod
    def Z_Tetromino():
        return Tetromino([["x", "x", " "], [" ", "x", "x"]], "Z")

    @staticmethod
    def J_Tetromino():
        return Tetromino([["x", " ", " "], ["x", "x", "x"]], "J")

    @staticmethod
    def L_Tetromino():
        return Tetromino([[" ", " ", "x"], ["x", "x", "x"]], "L")

    @staticmethod
    def null_Tetromino():
        return Tetromino([["x"]], "x")

    @staticmethod
    def create(letter):
        if not letter:
            letter = "O"
        assert letter.upper() in Tetromino.TYPES
        return getattr(Tetromino, "{}_Tetromino".format(letter.upper()))()

    def __str__(self):
        return "\n".join("".join(x) for x in self.state)

    def __getitem__(self, key):
        return self.state[key]

    def copy(self):
        return Tetromino([row[:] for row in self.state], self.type)

    def width(self):
        return len(self.state[0])

    def height(self):
        return len(self.state)

    def rotate(self, change):
        while change < 0:
            change += 4
        change = change % 4
        assert 0 <= change <= 3
        if not change:
            return
        elif change == 1:
            self.rotate_right()
        elif change == 2:
            self.flip()
        else:
            self.rotate_left()

    def rotate_right(self):
        self.state = list(zip(*reversed(self.state)))

    def rotate_left(self):
        self.state = list(zip(*self.state))[::-1]

    def flip(self):
        self.state = [row[::-1] for row in reversed(self.state)]


if __name__ == "__main__":
    t = Tetromino.L_Tetromino()  # L tetromino
    print(t)

    raw_piece = [[" ", " ", "x"], ["x", "x", "x"]]
    print(raw_piece)  # the "raw" tetromino

    print(
        "\n".join("".join(x) for x in raw_piece)
    )  # the string tetromnino is just converting the list of lists (raw) to a real piece by 1) joining each list by a new line 2) each sublist becomes a string

    flipped_raw_piece = list(
        reversed(raw_piece)
    )  # this flips the two substings of the raw piece
    print(flipped_raw_piece)
    print("\n".join("".join(x) for x in flipped_raw_piece))

    flipped_zipped_raw_piece = list(
        zip(*reversed(raw_piece))
    )  # zip returns iterator of tuples where the first item in each passed iterator is paired together, then the second item in each passed iterator are paired together etc.
    # the star just turns the argument into positional arguments
    # so zip(['x', 'x', 'x'], [' ', ' ', 'x']) becomes ('x', ' '), ('x', ' '), ('x', 'x')
    print(flipped_zipped_raw_piece)
    # then again we just join each list (tuple) by new line and each sublist (tuple) becomes a string
    print("\n".join("".join(x) for x in flipped_zipped_raw_piece))

    # print()
    # t.rotate_right()
    # print(t)
    # print()
    # t.rotate_right()
    # print(t)
    # print()
    # t.rotate_left()
    # print(t)
    # print(t.height())
    # print(t.width())
    # t.flip()
    # print(t)
