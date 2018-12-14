#!/usr/bin/python

class Tetromino():

    TYPES = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']

    def __init__(self, state):
        # assert that there are rows
        assert len(state) > 0
        # assert rows and columns form a rectangle
        assert len({len(row) for row in state}) == 1
        self.state = state

    @staticmethod
    def I_Tetromino():
        return Tetromino(
            [
                ['x', 'x', 'x', 'x']
            ]
        )

    @staticmethod
    def O_Tetromino():
        return Tetromino(
            [
                ['x', 'x'],
                ['x', 'x']
            ]
        )

    @staticmethod
    def T_Tetromino():
        return Tetromino(
            [
                [' ', 'x', ' '],
                ['x', 'x', 'x']
            ]
        )

    @staticmethod
    def S_Tetromino():
        return Tetromino(
            [
                [' ', 'x', 'x'],
                ['x', 'x', ' ']
            ]
        )

    @staticmethod
    def Z_Tetromino():
        return Tetromino(
            [
                ['x', 'x', ' '],
                [' ', 'x', 'x']
            ]
        )

    @staticmethod
    def J_Tetromino():
        return Tetromino(
            [
                ['x', ' ', ' '],
                ['x', 'x', 'x']
            ]
        )

    @staticmethod
    def L_Tetromino():
        return Tetromino(
            [
                [' ', ' ', 'x'],
                ['x', 'x', 'x']
            ]
        )

    @staticmethod
    def null_Tetromino():
        return Tetromino(
            [
                ['x']
            ]
        )

    @staticmethod
    def create(letter):
        if letter == None:
            letter = 'O'
        assert letter.upper() in Tetromino.TYPES
        return getattr(Tetromino, '{}_Tetromino'.format(letter.upper()))()

    def __str__(self):
        return "\n".join(["".join(x) for x in self.state])

    def __getitem__(self, key):
        return self.state[key]

    def copy(self):
        return Tetromino([row[:] for row in self.state])

    def width(self):
        return len(self.state[0])

    def height(self):
        return len(self.state)

    def rotate(self, change):
        while change < 0:
            change += 4
        change = (change % 4)
        assert 0 <= change and change <= 3
        if change == 0:
            return None
        elif change == 1:
            self.rotate_right()
        elif change == 2:
            self.flip()
        elif change == 3:
            self.rotate_left()
        else:
            raise Exception('This should never happen!')

    def rotate_right(self):
        self.state = list(zip(*self.state[::-1]))
        return self

    def rotate_left(self):
        self.state = list(reversed(list(zip(*self.state))))
        return self

    def flip(self):
        self.state = [row[::-1] for row in self.state[::-1]]
        return self

if __name__ == '__main__':
    t = Tetromino.LTetromino()
    print(t)
    print()
    t.rotate_right()
    print(t)
    print()
    t.rotate_right()
    print(t)
    print()
    t.rotate_left()
    print(t)
    print(t.height())
    print(t.width())
    t.flip()
    print(t)