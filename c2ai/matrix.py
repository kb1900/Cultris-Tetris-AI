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
    while True:
        t = time.time()
        field = matrix_updater.update_garbage(field)
        print(field)
        print("fps: {0}".format(1 / (time.time() - t)))
