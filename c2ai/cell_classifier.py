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
