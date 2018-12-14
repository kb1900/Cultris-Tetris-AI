from c2ai.base.field import Field
from c2ai.base.tetromino import Tetromino
import cv2
import pyautogui
import os
import autopy


class Classifier:
    @staticmethod
    def template_match(template):

        os.system("screencapture screengrab.png")
        img = cv2.imread("screengrab.png", 0)
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
    def get_occupied_roundstart(field, COLUMN, ROW3):
        print("GETTING occupied")

        for key_c in COLUMN:
            col_cord = COLUMN[key_c]
            for key_r in ROW3:
                row_cord = ROW3[key_r]
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
        (241, 36, 254): Tetromino.L_Tetromino,
        (19, 188, 193): Tetromino.S_Tetromino,
        (170, 188, 58): Tetromino.O_Tetromino,
        (3, 188, 16): Tetromino.I_Tetromino,
        (60, 68, 254): Tetromino.J_Tetromino,
        (180, 27, 32): Tetromino.T_Tetromino,
        (180, 188, 193): Tetromino.Z_Tetromino,
    }
    TETROMINO_NAME = {
        (241, 36, 254): "L",
        (19, 188, 193): "S",
        (170, 188, 58): "O",
        (3, 188, 16): "I",
        (60, 68, 254): "J",
        (180, 27, 32): "T",
        (180, 188, 193): "Z",
    }

    TETROMINO_FADED = {
        (42, 8, 48): Tetromino.L_Tetromino,
        (4, 46, 48): Tetromino.S_Tetromino,
        (40, 46, 14): Tetromino.O_Tetromino,
        (1, 46, 7): Tetromino.I_Tetromino,
        (8, 12, 48): Tetromino.J_Tetromino,
        (42, 8, 10): Tetromino.T_Tetromino,
        (42, 46, 48): Tetromino.Z_Tetromino,
    }
    TETROMINO_FADED_NAME = {
        (42, 8, 48): "L",
        (4, 46, 48): "S",
        (40, 46, 14): "O",
        (1, 46, 7): "I",
        (8, 12, 48): "J",
        (42, 8, 10): "T",
        (42, 46, 48): "Z",
    }

    TETROMINO_FADED_CHEESE = {
        (42, 6, 45): Tetromino.L_Tetromino,
        (4, 44, 45): Tetromino.S_Tetromino,
        (40, 44, 11): Tetromino.O_Tetromino,
        (1, 44, 4): Tetromino.I_Tetromino,
        (8, 10, 45): Tetromino.J_Tetromino,
        (42, 6, 7): Tetromino.T_Tetromino,
        (42, 44, 45): Tetromino.Z_Tetromino,
    }
    TETROMINO_FADED_NAME_CHEESE = {
        (42, 6, 45): "L",
        (4, 44, 45): "S",
        (40, 44, 11): "O",
        (1, 44, 4): "I",
        (8, 10, 45): "J",
        (42, 6, 7): "T",
        (42, 44, 45): "Z",
    }

    # target = template_match('Images/kb_baby_bot.png')
    # next_piece = template_match('Images/nextpiece.png')

    # next_rgb = get_next_rgb()
    # next_tetromino = TETROMINO[next_rgb]()
    # tetromino_name = TETROMINO_NAME[next_rgb]
    # print(tetromino_name)

    # target = pyautogui.moveTo(COLUMN[3],ROW[19])
    # rgb = autopy.screen.get_color(COLUMN[3],ROW[19])
    # print('target', target)
    # print('rgb', rgb)
