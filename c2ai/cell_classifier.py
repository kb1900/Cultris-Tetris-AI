from c2ai.base.field import Field
from c2ai.base.tetromino import Tetromino
import cv2
import pyautogui
import os
import autopy
import mss
import numpy as np
from c2ai import build_absolute_path


class Classifier:
    @staticmethod
    def template_match(template):

        with mss.mss() as sct:
            mon = sct.monitors[-1]
            img = sct.grab(mon)
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        A, B = img.shape[::-1]

        template = cv2.imread(template, 0)
        w, h = template.shape[::-1]

        methods = ["cv2.TM_SQDIFF"]
        for meth in methods:
            method = eval(meth)

            # Apply template Matching
            res = cv2.matchTemplate(img, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
                if min_val > 4041568.0:
                    # print('min_val', min_val)
                    return False

            else:
                top_left = max_loc
                if max_val > 4041568.0:
                    print("ERROR: template not found", max_val)
                    return False

            bottom_right = (top_left[0] + w, top_left[1] + h)

            center = ((top_left[0] + (w / 2)) / 2, (top_left[1] + (h / 2)) / 2)

            if pyautogui.onScreen(center) == True:
                return center
            else:
                print("bad coords error")
                return center

    @staticmethod
    def get_next_rgb(next_piece):
        # pyautogui.moveTo(next_piece[0], (next_piece[1] + 110))
        next_rgb = autopy.screen.get_color(next_piece[0], (next_piece[1] + 110))
        return next_rgb

    @staticmethod
    def get_first_piece_rgb(COLUMN, ROW):
        first_rgb = autopy.screen.get_color(COLUMN[4], (ROW[19]))
        return first_rgb

    @staticmethod
    def get_first_cheese_piece_rgb(COLUMN, ROW):
        first_rgb = autopy.screen.get_color(COLUMN[4], ROW[10])
        return first_rgb

    @staticmethod
    def is_occupied(rgb):
        # x = min_color_diff(rgb, colors)
        if rgb[0] < 50 and rgb[1] < 50 and rgb[2] < 50:
            return False
        else:
            return True

    @staticmethod
    def get_occupied(field, COLUMN, ROW):
        print("GETTING occupied")
        for key_c in COLUMN:
            col_cord = COLUMN[key_c]
            for key_r in ROW:
                row_cord = ROW[key_r]
                rgb = autopy.screen.get_color(col_cord, row_cord)
                if Classifier.is_occupied(rgb) == True:
                    field.drop_null(Tetromino.null_Tetromino(), key_r, key_c)

    @staticmethod
    def remove_2_col(field, COLUMN, ROW):
        print("removing col 8 and 9")
        for key_r in ROW:
            field.drop_null(Tetromino.null_Tetromino(), key_r, 8)
            field.drop_null(Tetromino.null_Tetromino(), key_r, 9)

    @staticmethod
    def remove_1_col(field, COLUMN, ROW):
        print("removing col 8 and 9")
        for key_r in ROW:
            field.drop_null(Tetromino.null_Tetromino(), key_r, 9)

    TETROMINO = {
        (118, 26, 118): Tetromino.L_Tetromino,
        (26, 118, 118): Tetromino.S_Tetromino,
        (113, 118, 41): Tetromino.O_Tetromino,
        (16, 118, 16): Tetromino.I_Tetromino,
        (41, 41, 118): Tetromino.J_Tetromino,
        (118, 26, 26): Tetromino.T_Tetromino,
        (118, 118, 118): Tetromino.Z_Tetromino,
    }

    TETROMINO_FADED = {
        (27, 5, 27): Tetromino.L_Tetromino,
        (5, 27, 27): Tetromino.S_Tetromino,
        (26, 27, 8): Tetromino.O_Tetromino,
        (2, 27, 2): Tetromino.I_Tetromino,
        (8, 8, 27): Tetromino.J_Tetromino,
        (27, 5, 5): Tetromino.T_Tetromino,
        (27, 27, 27): Tetromino.Z_Tetromino,
    }