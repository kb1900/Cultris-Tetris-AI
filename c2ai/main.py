import os
import sys

import pyautogui
import autopy
import time
from pynput import keyboard
import pickle
import numpy as np
import keyboard as kb


from c2ai.base.tetromino import Tetromino
from c2ai.base.field import Field
from c2ai.base.optimizer import Optimizer
from c2ai.cell_classifier import Classifier
from c2ai.matrix import matrix_updater
from c2ai import build_absolute_path
from c2ai.base import settings

best_drop_times = []
move_execution_times = []
update_field_times = []
game_over_check_times = []
game_over = False
min_time_per_piece = 1 / (settings.max_bpm / 60)
break_program = False

# with open ('current_generation_dump', 'rb') as dump_file:
#           dump = pickle.load(dump_file)
#           current_generation = dump[0]
#           n = current_generation[0]
#           #score = Tetris.run_game(n,render=True)
#           # print('loaded previous netowrk')
#           # print(score)
#           # print(n.wih)
#           # print(n.who)


def on_press(key):
    global break_program
    global count
    global keys
    global field
    if key == keyboard.Key.shift_r:
        print("SHIFT_R pressed: Press UP to continue")
        break_program = True
        os.system("open /Applications/cultris2.app")
        return True
    elif key == keyboard.Key.up:
        print("UP pressed, resuming operations!")
        field = Field()
        keys = None
        break_program = False
        count = -1
        os.system("open /Applications/cultris2.app")
        return True


def leave_challenge():
    pyautogui.press("escape")
    time.sleep(0.3)
    target = Classifier.template_match(build_absolute_path("Images/yes.png"))
    if target == False:
        target = Classifier.template_match(
            build_absolute_path("Images/back_to_menu.png")
        )
    pyautogui.moveTo(target)
    pyautogui.doubleClick(target)


count = -2
field = Field()

while True:
    with keyboard.Listener(on_press=on_press) as listener:
        while break_program == False:
            while count > -5:
                while count == -2 and break_program == False:

                    ############# STARTING GAME MODE ################
                    if sys.argv[1] == "-maserati":
                        os.system("open /Applications/cultris2.app")
                        print("maserati mode selected")
                        maserati = Classifier.template_match(
                            build_absolute_path("Images/maserati.png")
                        )
                        if maserati == False:
                            maserati = Classifier.template_match(
                                build_absolute_path("Images/maserati2.png")
                            )
                        if maserati == False:
                            print("ERROR finding maserati template match")
                            count = -100
                            break
                        pyautogui.moveTo(maserati)
                        pyautogui.doubleClick(maserati)
                        time.sleep(0.25)

                        No = Classifier.template_match(
                            build_absolute_path("Images/No.png")
                        )
                        pyautogui.moveTo(No)
                        pyautogui.doubleClick(No)
                        time.sleep(2)  # 3,2,1 countdown

                    else:
                        os.system("open /Applications/cultris2.app")
                        pass
                        count = -1
                    count = -1

                    ############# ORIENTING FIELD MATRIX ################
                while count == -1 and break_program == False:
                    target = Classifier.template_match(
                        build_absolute_path("Images/kb_baby_bot.png")
                    )

                    while target == False:
                        print(
                            "ERROR finding kb_baby_bot template match. ATTEMPTING AGAIN"
                        )
                        target = Classifier.template_match(
                            build_absolute_path("Images/kb_baby_bot.png")
                        )

                    count = 0

                    ############# PLAYING STARTS HERE // INITIALIZATION ################

                while count == 0 and break_program == False:
                    field = Field()
                    if sys.argv[1] != "-cheese" and sys.argv[1] != "-cheesemp":
                        curr_p = matrix_updater.get_first_piece()
                        current_tetromino = curr_p[0]
                        tetromino_name = curr_p[1]
                        print("detected first piece ghost as:", tetromino_name)

                    count += 1

                    ############# MAIN PLAYING LOOP STARTS HERE ################

                while count > 0 and break_program == False:
                    if settings.mode == "upstack":
                        if field.height() > 12 or field.count_gaps() > 3:
                            settings.mode = "downstack"

                    t0 = time.time()
                    if count % 1 == 0:
                        returns = matrix_updater.update_field(field)
                        newfield = returns[0]
                        field = newfield
                        next_tetromino = returns[1]
                        next_tetromino_name = returns[2]
                    update_field_times.append(time.time() - t0)

                    t0 = time.time()
                    start_time = time.time()
                    try:
                        best_drop = Optimizer.best_move(
                            field, current_tetromino, next_tetromino
                        )
                    except IndexError:
                        print("Game Over, ran out of moves")
                        game_over = True
                    best_drop_times.append(time.time() - t0)

                    t0 = time.time()
                    rotation = best_drop[1]
                    column = best_drop[2]

                    current_tetromino.rotate(rotation)
                    try:
                        field.drop(current_tetromino, column)
                    except AssertionError:
                        print("Game Over, topped out")
                        game_over = True

                    keys = Optimizer.get_keystrokes(
                        rotation,
                        column,
                        {
                            "rotate_right": "w",
                            "rotate_180": "tab",
                            "rotate_left": "q",
                            "move_left": "left",
                            "move_right": "right",
                            "drop": "c",
                        },
                        tetromino_name=tetromino_name,
                    )

                    # pyautogui.typewrite(keys)
                    kb.write(
                        keys, delay=0.005
                    )  # 0.111s execution speed av and stable at delay = 0.005s but only needed if lag
                    move_execution_times.append(time.time() - t0)

                    current_tetromino = next_tetromino
                    tetromino_name = next_tetromino_name

                    if count > 0:
                        count += 1

                    if count % 10 == 0:
                        t0 - time.time()
                        game_over = matrix_updater.check_end_round()
                        game_over_check_times.append(time.time() - t0)

                    ## Throttle speed if move would be faster than max speed
                    move_time = time.time() - start_time
                    if move_time < min_time_per_piece:
                        time.sleep(min_time_per_piece - move_time)

                    if game_over == True:
                        print("GAME OVER DETECTED")
                        times = [
                            np.average(best_drop_times),
                            np.average(move_execution_times),
                            np.average(update_field_times),
                            np.average(game_over_check_times),
                        ]
                        print("average time to get best move", times[0])
                        print("average time to get execute move", times[1])
                        print("average time to get update field", times[2])
                        print("average time to get check game over", times[3])
                        print("bpm estimate:", float(60 / (np.sum(times))))

                        if sys.argv[1] == "-maserati" or sys.argv[1] == "-cheese":
                            time.sleep(0.5)
                            print("Leaving challenge and restarting")
                            leave_challenge()
                            time.sleep(0.5)
                            count = -2
                        else:
                            while True:
                                i = matrix_updater.check_start_round()
                                if i != 0:
                                    time.sleep(i + 0.10)
                                    count = -1
                                    game_over = False
                                    break

        listener.join()
