import time
import mss
from c2ai.base.field import Field
from c2ai.base.tetromino import Tetromino
from PIL import Image, ImageDraw
from pylab import *


class matrix_updater:
    def is_garbage(pixels):
        garbage = (85, 89, 91)
        if max(map(lambda a, b: abs(a - b), pixels, garbage)) < 5:
            return True
        else:
            return False

    def get_first_piece():
        box = {"top": 234, "left": 106, "width": 420, "height": 756}
        width, height = box["width"] * 2, box["height"] * 2
        cell_widthx = width / 10
        cell_widthy = height / 18
        TETROMINO_FADED = {
            (42, 8, 48): Tetromino.L_Tetromino,
            (4, 46, 48): Tetromino.S_Tetromino,
            (40, 46, 14): Tetromino.O_Tetromino,
            (1, 46, 7): Tetromino.I_Tetromino,
            (8, 12, 48): Tetromino.J_Tetromino,
            (42, 8, 10): Tetromino.T_Tetromino,
            (39, 24, 10): Tetromino.Z_Tetromino,
        }

        TETROMINO_FADED_NAME = {
            (42, 8, 48): "L",
            (4, 46, 48): "S",
            (40, 46, 14): "O",
            (1, 46, 7): "I",
            (8, 12, 48): "J",
            (42, 8, 10): "T",
            (39, 24, 10): "Z",
        }

        column_cords = []
        row_cords = []
        for i in range(10):
            column_cords.append((cell_widthx / 2) + cell_widthx * i)

        for j in range(18):
            row_cords.append((cell_widthy / 2) + cell_widthy * j + 4)

        with mss.mss() as sct:
            sct_img = sct.grab(box)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        pixels = img.load()
        ghost_rgb = pixels[column_cords[4], row_cords[-1]]

        return [TETROMINO_FADED[ghost_rgb](), TETROMINO_FADED_NAME[ghost_rgb]]

        # im_array = array(img)
        # imshow(im_array)
        # plot(column_cords[4],row_cords[-1],'r*')
        # show()

    def check_start_round():
        # the goal here is to detect the 3, 2, 1 countdown of the round starting
        # it will be checked in a loop when a game is not active
        # and return true once it is detected leading to a 3 second sleep and bot resumption

        box = {"top": 234, "left": 106, "width": 420, "height": 756}
        width, height = box["width"] * 2, box["height"] * 2

        with mss.mss() as sct:
            sct_img = sct.grab(box)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        pixels = img.load()

        x = [375, 470, 426]  # 1 location
        y = [860, 860, 700]

        if (
            pixels[x[0], y[0]] == (255, 255, 255)
            and pixels[x[1], y[1]] == (255, 255, 255)
            and pixels[x[2], y[2]] == (255, 255, 255)
        ):
            print("Round Start 1 detected")
            return 1

        x = [375, 470, 471]  # 2 location
        y = [842, 842, 700]
        if (
            pixels[x[0], y[0]] == (255, 255, 255)
            and pixels[x[1], y[1]] == (255, 255, 255)
            and pixels[x[2], y[2]] == (255, 255, 255)
        ):
            print("Round Start 2 detected")
            return 2

        return 0

    def check_end_round():
        # the goal here is to detect the different states of the round ending
        # if the round is over, white text will overlay the field saying "Game Over" or "Winner"
        # we can check a few distinct points (3 should suffice) to verify the gamestate

        box = {"top": 234, "left": 106, "width": 420, "height": 756}
        width, height = box["width"] * 2, box["height"] * 2

        with mss.mss() as sct:
            sct_img = sct.grab(box)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        pixels = img.load()

        x = [166, 374, 523]
        y = [600, 630, 860]
        # im_array = array(img)
        # imshow(im_array)
        # plot(x,y,'r*')
        # show()
        if (
            pixels[x[0], y[0]] == (255, 255, 255)
            and pixels[x[1], y[1]] == (255, 255, 255)
            and pixels[x[2], y[2]] == (255, 255, 255)
        ):
            print("Game Over detected")
            return True

        x = [180, 350, 695]
        y = [700, 810, 758]
        # im_array = array(img)
        # imshow(im_array)
        # plot(x,y,'r*')
        # show()

        if (
            pixels[x[0], y[0]] == (255, 255, 255)
            and pixels[x[1], y[1]] == (255, 255, 255)
            and pixels[x[2], y[2]] == (255, 255, 255)
        ):
            print("Winner detected")
            # im_array = array(img)
            # imshow(im_array)
            # plot(x,y,'r*')
            # show()
            return True

    def update_field(field):
        # the goal here is to get the bottom row
        # then check to see if it has garbage (Gray color)
        # then create a 1x10 array with ['0','0','0','0','0','0','0','0','0','0']
        # then identify where the gap is and garbage_array[gap] = ' '
        # then append this to the bottom of the field

        # we will also return the next_piece for optimization
        TETROMINO = {
            (180, 28, 193): Tetromino.L_Tetromino,
            (19, 189, 193): Tetromino.S_Tetromino,
            (170, 189, 58): Tetromino.O_Tetromino,
            (3, 255, 16): Tetromino.I_Tetromino,
            (45, 54, 193): Tetromino.J_Tetromino,
            (180, 28, 32): Tetromino.T_Tetromino,
            (160, 100, 32): Tetromino.Z_Tetromino,
        }

        TETROMINO_NAME = {
            (180, 28, 193): "L",
            (19, 189, 193): "S",
            (170, 189, 58): "O",
            (3, 255, 16): "I",
            (45, 54, 193): "J",
            (180, 28, 32): "T",
            (160, 100, 32): "Z",
        }

        box = {"top": 234, "left": 106, "width": 620, "height": 756}
        width, height = 420 * 2, box["height"] * 2
        # print(width, height)

        cell_widthx = width / 10
        cell_widthy = height / 18

        column_cords = []
        row_cords = []
        for i in range(10):
            column_cords.append((cell_widthx / 2) + cell_widthx * i)

        for j in range(18):
            row_cords.append((cell_widthy / 2) + cell_widthy * j + 4)
            newfield = Field()

        with mss.mss() as sct:
            sct_img = sct.grab(box)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        pixels = img.load()

        garbage = []
        go = True
        for j in range(len(row_cords) - 1, 0, -1):  # iterate from last row upwards
            garbage_row = [
                " ",
                " ",
                " ",
                " ",
                " ",
                " ",
                " ",
                " ",
                " ",
                " ",
            ]  # initialize a blank row
            for i in range(len(column_cords)):  # iterate through the columns
                if (
                    matrix_updater.is_garbage(pixels[column_cords[i], row_cords[j]])
                    == True
                ):  # check if there is a gray block
                    garbage_row[i] = "0"  # put 0 where there is a gray block
            if garbage_row.count(" ") == 1:
                garbage.append(garbage_row)

        newfield = field.copy()

        if len(garbage) > 0:
            newfield.update_garbage(garbage)
            # print(newfield)

        return [
            newfield,
            TETROMINO[pixels[1093, 208]](),
            TETROMINO_NAME[pixels[1093, 208]],
        ]


if __name__ == "__main__":
    field = Field()
    # while True:
    #     t = time.time()
    #     field = matrix_updater.update_field(field)[0]
    #     print(field)
    #     print("fps: {0}".format(1 / (time.time() - t)))
    matrix_updater.check_end_round()
