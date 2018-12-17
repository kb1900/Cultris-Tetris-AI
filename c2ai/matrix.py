import time
import mss
from c2ai.base.field import Field
from c2ai.base.tetromino import Tetromino
from PIL import Image, ImageDraw
from pylab import *


class matrix_updater:
    def is_occupied(pixels):
        if pixels[0] < 50 and pixels[1] < 50 and pixels[2] < 50:
            return False
        else:
            return True

    def is_garbage(pixels):
        garbage = (85, 89, 91)
        if max(map(lambda a, b: abs(a - b), pixels, garbage)) < 5:
            return True
        else:
            return False

    def is_ghost(px):
        ghosts = [
            (42, 8, 48),
            (4, 46, 48),
            (40, 46, 14),
            (1, 46, 7),
            (8, 12, 48),
            (42, 8, 10),
            (42, 46, 48),
        ]
        for ghost_rgb in ghosts:
            if max(map(lambda a, b: abs(a - b), px, ghost_rgb)) < 5:
                return True
        return False

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
        # plot(x,y,'r*')
        # show()
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

        x = [166, 347, 466]
        y = [600, 600, 600]
        if (
            pixels[x[0], y[0]] == (255, 255, 255)
            and pixels[x[1], y[1]] == (255, 255, 255)
            and pixels[x[2], y[2]] == (255, 255, 255)
        ):
            print("Game Over detected")
            return True

        x = [105, 180, 252]  # The W in winner ## Need to edit this one
        y = [700, 700, 700]
        if (
            pixels[x[0], y[0]] == (255, 255, 255)
            and pixels[x[1], y[1]] == (255, 255, 255)
            and pixels[x[2], y[2]] == (255, 255, 255)
        ):
            print("Winner detected")
            return True

    def update_garbage(field):
        # the goal here is to get the bottom row
        # then check to see if it has garbage (Gray color)
        # then create a 1x10 array with ['0','0','0','0','0','0','0','0','0','0']
        # then identify where the gap is and garbage_array[gap] = ' '
        # then append this to the bottom of the field

        box = {"top": 234, "left": 106, "width": 420, "height": 756}
        width, height = box["width"] * 2, box["height"] * 2
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

        if len(garbage) > 1:
            newfield.update_garbage(garbage)
            # print(newfield)

        if [
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
        ] in newfield.field_array().tolist():
            print("full row bad error")
            return field
        return newfield

    def update_field(field):
        box = {"top": 234, "left": 106, "width": 420, "height": 756}
        width, height = box["width"] * 2, box["height"] * 2
        # print(width, height)

        cell_widthx = width / 10
        cell_widthy = height / 18

        column_cords = []
        row_cords = []
        for i in range(10):
            column_cords.append((cell_widthx / 2) + cell_widthx * i)

        for j in range(18):
            row_cords.append((cell_widthy / 2) + cell_widthy * j)
            newfield = Field()

        with mss.mss() as sct:
            sct_img = sct.grab(box)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        pixels = img.load()
        # im_array = array(img)
        # imshow(im_array)
        # plot the points with red star-markers
        for i in range(len(column_cords)):
            for j in range(len(row_cords) - 1, 0, -1):
                # if matrix_updater.is_occupied(pixels[column_cords[i],row_cords[j]]) and matrix_updater.is_ghost(pixels[column_cords[i],row_cords[j]]) == False:
                if (
                    matrix_updater.is_occupied(pixels[column_cords[i], row_cords[j]])
                    == True
                    and matrix_updater.is_garbage(pixels[column_cords[i], row_cords[j]])
                    == False
                ):
                    newfield.drop_null(Tetromino.null_Tetromino(), j + 2, i)

                    # for i in field.field_array():
                    # 	print(i)

                    # print(newfield)

        newfield_array = newfield.field_array()

        if [
            "x",
            "x",
            "x",
            "x",
            "x",
            "x",
            "x",
            "x",
            "x",
            "x",
        ] in newfield_array.tolist():
            print("BAD FIELD UPDATE full row")
            # print(field)
            # print(newfield)
            return field

        else:
            # print('old')
            # print(field)
            # print('new')
            # print(newfield)
            return newfield


if __name__ == "__main__":
    field = Field()
    # while True:
    #     t = time.time()
    #     field = matrix_updater.update_garbage(field)
    #     print(field)
    #     print("fps: {0}".format(1 / (time.time() - t)))

    matrix_updater.check_start_round()
