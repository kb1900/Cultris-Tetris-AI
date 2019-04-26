import os
import sys

import pyautogui
import autopy
import time
from pynput import keyboard
import pickle
import numpy as np
import keyboard as kb
import tkinter

from c2ai.base.tetromino import Tetromino
from c2ai.base.field import Field
from c2ai.base.optimizer import Optimizer
from c2ai.cell_classifier import Classifier
from c2ai.matrix import matrix_updater
from c2ai import build_absolute_path
from c2ai.base import settings

best_drop_times = []
move_execution_times = []
garbage_update_times = []
game_over_check_times = []
game_over = False
break_program = False


def init_label():
    label = tkinter.Label(root, text="", font=("Times", "30"), fg="red")
    label.master.overrideredirect(True)
    label.master.geometry("+750+650")
    label.master.lift()
    label.master.wm_attributes("-topmost", True)
    label.master.wm_attributes("-transparent", 1)
    label.pack()

    return label


root = tkinter.Tk()
combo_label = init_label()
timer_label = init_label()
piece_count_label = init_label()
next_tetromino_label = init_label()
mode_label = init_label()
active_combo_label = init_label()


def update_labels():
    combo_label["text"] = "Combo: " + str(combo_counter)
    timer_label["text"] = "Time: " + str("{0:.2f}".format(combo_time))
    piece_count_label["text"] = "Piece #" + str(count)
    next_tetromino_label["text"] = "Next: " + str(next_tetromino_name)
    mode_label["text"] = "Mode: : " + str(settings.mode)
    active_combo_label["text"] = "Combo Active: " + str(settings.combo)
    root.update()


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
        os.system("open /Applications/cultris4.app")
        return True
    elif key == keyboard.Key.up:
        print("UP pressed, resuming operations!")
        field = Field()
        keys = None
        break_program = False
        count = -1
        os.system("open /Applications/cultris4.app")
        return True


def login():
    target = Classifier.template_match(build_absolute_path("Images/Play_online.png"))
    pyautogui.moveTo(target)
    pyautogui.doubleClick(target)
    time.sleep(0.5)

    target = Classifier.template_match(build_absolute_path("Images/Play_as_guest.png"))
    pyautogui.moveTo(target)
    pyautogui.doubleClick(target)

    # target = template_match(build_absolute_path('Name.png'))
    pyautogui.moveTo(x=target[0] + 600, y=target[1] + 50)
    pyautogui.dragTo(target[0] + 50, target[1] + 50, 0.5, button="left")
    pyautogui.typewrite("kb of python")

    target = Classifier.template_match(build_absolute_path("Images/Play.png"))
    pyautogui.moveTo(target)
    pyautogui.doubleClick(target)
    time.sleep(2)

    target = Classifier.template_match(build_absolute_path("Images/No.png"))
    pyautogui.moveTo(target)
    pyautogui.doubleClick(target)

    time.sleep(1)
    target = Classifier.template_match(build_absolute_path("Images/lobby.png"))
    pyautogui.moveTo(target)
    pyautogui.doubleClick(target)


def leave_room():
    pyautogui.press("escape")
    time.sleep(0.3)
    target = Classifier.template_match(build_absolute_path("Images/yes.png"))
    pyautogui.moveTo(target)
    pyautogui.doubleClick(target)


def leave_challenge():
    pyautogui.press("escape")
    time.sleep(0.3)
    target = Classifier.template_match(build_absolute_path("Images/yes.png"))
    if target == False:
        target = Classifier.template_match(
            build_absolute_path("Images/back_to_menu.png")
        )
        game_over = False
    pyautogui.moveTo(target)
    pyautogui.doubleClick(target)


def find_lobby_chat():

    if Classifier.template_match(build_absolute_path("Images/online3.png")) != False:
        print("we are on the lobby chat page!")
    elif is_on_homescreen() != False:
        login()
    elif is_on_homescreen() == False:
        print("homescreen not found. checking if we are logged in")
        if is_in_room() == True:
            leave_room()
            time.sleep(2)
        if is_loggedin() == True:
            print("we are logged in")
            if (
                Classifier.template_match(build_absolute_path("Images/online3.png"))
                != False
            ):
                print("we are on the lobby chat page!")
            else:
                target = Classifier.template_match(
                    build_absolute_path("Images/lobby.png")
                )
                pyautogui.moveTo(target)
                pyautogui.doubleClick(target)
        else:
            print("we are logged in but not on the lobby chat page")
            target = template_match(build_absolute_path("Images/Back.png"))
            pyautogui.moveTo(target)
            pyautogui.doubleClick(target)
            time.sleep(2)
            login()
    else:
        print("error finding lobby")
    time.sleep(2)
    if Classifier.template_match(build_absolute_path("Images/online3.png")) != False:
        print("we are on the lobby chat page!")


def timer(combo_time=0, clears=0, combo_counter=0):
    combo_time = combo_time  # current timer
    clears = clears  # lines cleared (returns[1])

    # additional time per Line clear is Base(counter) + NumberOfClearedLines * Bonus(counter)

    if clears > 0 and combo_time >= 0:
        combo_counter += 1

    if combo_time >= 0:
        if clears == 0:  # punish for not clearing
            combo_time = combo_time - 0.42
            if combo_counter > 1:
                if combo_counter < 5:
                    combo_time = combo_time - (combo_counter - 1) * 0.015
                else:
                    combo_time = combo_time - (combo_counter - 1) * 0.03
        else:
            if combo_counter == 1:
                combo_time = combo_time + 2.4 + clears * 1.2
            elif combo_counter == 2:
                combo_time = combo_time + 1.1 + clears * 0.6
            elif combo_counter == 3:
                combo_time = combo_time + 0.4 + clears * 0.3
            elif combo_counter == 4:
                combo_time = combo_time + 0.05 + clears * 0.15
            elif combo_counter == 5:
                combo_time = combo_time + 0 + clears * 0.075
            elif combo_counter == 6:
                combo_time = combo_time + 0 + clears * 0.0375
            elif combo_counter == 7:
                combo_time = combo_time + 0 + clears * 0.01875 - 0.2
            elif combo_counter == 8:
                combo_time = combo_time + 0 + clears * 0.009375 - 0.3
            elif combo_counter == 9:
                combo_time = combo_time + 0 + clears * 0.0046875 - 0.4
            elif combo_counter == 10:
                combo_time = combo_time + 0 + clears * 0 - 0.6
            elif combo_counter == 11:
                combo_time = combo_time + 0 + clears * 0 - 0.8
            elif combo_counter > 11:
                combo_time = combo_time + 0 + clears * 0 - 1
            # elif combo_counter > 9:
            #     # combo_time = combo_time + (-0.775 * combo_counter + 2.925) + clears * 1.2/(2^(combo_counter-1))
            #     # a + b*x + c*x^2 + d*x^3
            #     combo_time = (
            #         combo_time
            #         + (
            #             4.55
            #             - 2.6583 * (combo_counter)
            #             + 0.55 * (combo_counter ^ 2)
            #             - 0.042 * (combo_counter ^ 3)
            #         )
            #         + clears * 1.2 / (2 ^ (combo_counter - 1))
            #     )
            # y0 + a/x
            # combo_time = combo_time - 0.61 + 3.0677/combo_counter + clears * 1.2/(2^(combo_counter-1))

    return [combo_time, combo_counter]


############# LAUNCHING GAME ################

# if c2_open() == False:
#   print('Starting up Cultris')
#   os.system("open /Applications/cultris4.app")
#   time.sleep(5)
#   pyautogui.press('enter')
#   time.sleep(.5)

# elif c2_open() == True:
#   print('C2 is open, navigating to login page')
#   os.system("open /Applications/cultris4.app")
#   time.sleep(.5)
# else:
#   print('error on launching cultris4')


# find_lobby_chat()


# target = template_match(build_absolute_path('Challenges.png'))
# pyautogui.moveTo(target)
# pyautogui.doubleClick(target)
# time.sleep(2)


# print('Press Enter to start a game!!')
# input()
count = -2
field = Field()
cell_height = 41.75
cell_width = 41.75


while True:
    with keyboard.Listener(on_press=on_press) as listener:

        while break_program == False:
            while count > -5:
                while count == -2 and break_program == False:
                    ############# STARTING GAME MODE ################
                    if sys.argv[1] == "-maserati":
                        os.system("open /Applications/cultris4.app")
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

                    elif sys.argv[1] == "-cheese":
                        os.system("open /Applications/cultris4.app")
                        print("cheese mode selected")
                        cheese = Classifier.template_match(
                            build_absolute_path("Images/swiss_cheese.png")
                        )
                        if cheese == False:
                            cheese = Classifier.template_match(
                                "Images/swiss_cheese2.png"
                            )

                        if cheese == False:
                            print("ERROR finding cheese template match")
                            count = -100
                            break
                        pyautogui.moveTo(cheese)
                        pyautogui.doubleClick(cheese)
                        time.sleep(0.25)

                        No = Classifier.template_match(
                            build_absolute_path("Images/No.png")
                        )
                        pyautogui.moveTo(No)
                        pyautogui.doubleClick(No)
                        time.sleep(2)  # 3,2,1 countdonw

                    else:
                        # input() #3,2,1 countdown
                        os.system("open /Applications/cultris4.app")
                        pass
                        count = -1
                    count = -1

                    # time.sleep(.01)

                    ############# ORIENTING FIELD MATRIX ################
                while count == -1 and break_program == False:
                    next_piece = Classifier.template_match("Images/nextpiece4.png")
                    # pyautogui.moveTo(next_piece[0], (next_piece[1] + 110))
                    # print('NEXT PIECE:,', next_piece)
                    ## Define future coordinates relative to this template matched position
                    if next_piece == False:
                        print("ERROR finding nextpiece4 template match. hardcoding")
                        # next_piece = (689.0, 199.0)
                        # next_piece = Classifier.template_match("Images/nextpiece4.png")
                        # ## Define future coordinates relative to this template matched position
                        # if next_piece == False:
                        #     print(
                        #         "ERROR finding nextpiece4 template match. ATTEMPTING 3rd TIME"
                        #     )
                        #     next_piece = Classifier.template_match(
                        #         "Images/nextpiece4.png"
                        #     )
                        #     ## Define future coordinates relative to this template matched position
                        #     if next_piece == False:
                        #         print(
                        #             "ERROR finding nextpiece4 template match. Hardcoding location"
                        #         )
                        #         next_piece = (689.0, 199.0)
                        #         print(next_piece)
                        #         break

                    target = Classifier.template_match(
                        build_absolute_path("Images/kb_baby_bot4.png")
                    )
                    print("TAGRGET", target)
                    if target == False:
                        print("ERROR finding kb_baby_bot4 template match. hardcoding")
                        # target = (351.5, 184.5)
                        # target = Classifier.template_match(
                        #     build_absolute_path("Images/kb_baby_bot4.png")
                        # )
                        # if target == False:
                        #     print(
                        #         "ERROR finding kb_baby_bot4 template match. ATTEMPTING 3rd TIME"
                        #     )
                        #     target = Classifier.template_match(
                        #         build_absolute_path("Images/kb_baby_bot4.png")
                        #     )
                        #     if target == False:
                        #         print(
                        #             "ERROR finding kb_baby_bot4 template match. Re-setting count to -2"
                        #         )
                        #         count = -2
                        #         break

                    ROW = {
                        19: (target[1] + 773),
                        18: ((target[1] + 773) - (cell_height) * 1),
                        17: ((target[1] + 773) - (cell_height) * 2),
                        16: ((target[1] + 773) - (cell_height) * 3),
                        15: ((target[1] + 773) - (cell_height) * 4),
                        14: ((target[1] + 773) - (cell_height) * 5),
                        13: ((target[1] + 773) - (cell_height) * 6),
                        12: ((target[1] + 773) - (cell_height) * 7),
                        11: ((target[1] + 773) - (cell_height) * 8),
                        10: ((target[1] + 773) - (cell_height) * 9),
                        9: ((target[1] + 773) - (cell_height) * 10),
                        8: ((target[1] + 773) - (cell_height) * 11),
                        7: ((target[1] + 773) - (cell_height) * 12),
                        6: ((target[1] + 773) - (cell_height) * 13),
                        5: ((target[1] + 773) - (cell_height) * 14),
                        # 4: ((target[1]+773) - (cell_height)*15),
                        # 3: ((target[1]+773) - (cell_height)*16),
                        # 2: ((target[1]+773) - (cell_height)*17),
                    }

                    ROW11 = {
                        19: (target[1] + 773),
                        18: ((target[1] + 773) - (cell_height) * 1),
                        17: ((target[1] + 773) - (cell_height) * 2),
                        16: ((target[1] + 773) - (cell_height) * 3),
                        15: ((target[1] + 773) - (cell_height) * 4),
                        14: ((target[1] + 773) - (cell_height) * 5),
                        13: ((target[1] + 773) - (cell_height) * 6),
                        12: ((target[1] + 773) - (cell_height) * 7),
                        11: ((target[1] + 773) - (cell_height) * 8),
                        10: ((target[1] + 773) - (cell_height) * 9),
                        9: ((target[1] + 773) - (cell_height) * 10),
                    }

                    COLUMN = {
                        9: ((target[0] - 20) + ((cell_width) * 5)),
                        8: ((target[0] - 20) + ((cell_width) * 4)),
                        7: ((target[0] - 20) + ((cell_width) * 3)),
                        6: ((target[0] - 20) + ((cell_width) * 2)),
                        5: ((target[0] - 20) + ((cell_width) * 1)),
                        4: (target[0] - 20),
                        3: ((target[0] - 20) - ((cell_width) * 1)),
                        2: ((target[0] - 20) - ((cell_width) * 2)),
                        1: ((target[0] - 20) - ((cell_width) * 3)),
                        0: ((target[0] - 20) - ((cell_width) * 4)),
                    }

                    count = 0

                    ############# PLAYING STARTS HERE // INITIALIZATION ################

                while count == 0 and break_program == False:
                    field = Field()
                    combo_counter = 0
                    combo_time = 0
                    combos = []

                    if sys.argv[1] != "-cheese" and sys.argv[1] != "-cheesemp":
                        try:
                            current_rgb = Classifier.get_first_piece_rgb(COLUMN, ROW)
                            # pyautogui.moveTo(COLUMN[4], (ROW[19]))
                            print(current_rgb)

                            current_tetromino = Classifier.TETROMINO_FADED[
                                current_rgb
                            ]()
                            tetromino_name = Classifier.TETROMINO_FADED_NAME[
                                current_rgb
                            ]
                            print("detected ghost as:", tetromino_name)
                        except:
                            # next_rgb = Classifier.get_next_rgb(next_piece)
                            # next_tetromino = Classifier.TETROMINO[next_rgb]()
                            # next_tetromino_name = Classifier.TETROMINO_NAME[next_rgb]
                            print("did not detect ghost")
                            input()
                            # print("detected next piece as", next_tetromino_name)

                            # pyautogui.typewrite(
                            #     " "
                            # )  # place 1st piece at spawn location
                            # Classifier.get_occupied(field, COLUMN, ROW)

                            # current_tetromino = next_tetromino
                            # tetromino_name = next_tetromino_name
                    elif sys.argv[1] == "-cheese" or sys.argv[1] == "-cheesemp":
                        try:
                            current_rgb = Classifier.get_first_cheese_piece_rgb(
                                COLUMN, ROW
                            )
                            current_tetromino = Classifier.TETROMINO_FADED_CHEESE[
                                current_rgb
                            ]()
                            tetromino_name = Classifier.TETROMINO_FADED_NAME_CHEESE[
                                current_rgb
                            ]
                            print("detected ghost as:", tetromino_name)

                            Classifier.get_occupied(field, COLUMN, ROW11)

                        except:
                            next_rgb = Classifier.get_next_rgb(next_piece)
                            next_tetromino = Classifier.TETROMINO[next_rgb]()
                            next_tetromino_name = Classifier.TETROMINO_NAME[next_rgb]
                            print("did not detect ghost")
                            print("detected next piece as", next_tetromino_name)

                            pyautogui.typewrite(
                                " "
                            )  # place 1st piece at spawn location
                            Classifier.get_occupied(field, COLUMN, ROW11)

                            current_tetromino = next_tetromino
                            tetromino_name = next_tetromino_name

                    print(field)
                    count += 1

                    ############# MAIN PLAYING LOOP STARTS HERE ################
                    # try:
                while count > 0 and break_program == False:

                    if settings.mode == "upstack":
                        if (
                            field.height() > 12
                            or field.count_gaps() > 2
                            or field.max_bump() > 6
                        ):
                            print(
                                "MODE SWITCH TO DOWNSTACK",
                                # field.height(),
                                # field.count_gaps(),
                            )
                            settings.mode = "downstack"
                    if settings.mode == "downstack":
                        if combo_counter > 5 or combo_counter + combo_time > 8.5:
                            if field.height() < 14:
                                settings.combo = True
                                settings.max_bpm = 280
                                print("COMBO ACTIVE")
                        else:
                            settings.combo = False
                            settings.max_bpm = 280
                        if (
                            field.height() < 2
                            and field.count_gaps() < 3
                            and combo_counter < 3
                        ):
                            print(
                                "MODE SWITCH TO UPSTACK",
                                # field.height(),
                                # field.count_gaps(),
                            )
                            settings.mode = "upstack"
                            settings.combo = False

                    next_rgb = Classifier.get_next_rgb(next_piece)
                    next_tetromino = Classifier.TETROMINO[next_rgb]()
                    next_tetromino_name = Classifier.TETROMINO_NAME[next_rgb]
                    update_labels()

                    t0 = time.time()
                    start_time = time.time()
                    # print('tetromino_name', tetromino_name)
                    try:
                        best_drop = Optimizer.best_move(
                            field=field,
                            tetromino=current_tetromino,
                            next_tetromino=next_tetromino,
                            combo_time=combo_time,
                            combo_counter=combo_counter,
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
                        returns = field.drop(current_tetromino, column)
                    except AssertionError:
                        print("Game Over, ran out of moves")
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
                        keys, delay=0.00
                    )  # 0.111s execution speed av and stable at delay = 0.005s but only needed if lag
                    move_execution_times.append(time.time() - t0)

                    t0 = time.time()
                    if count % 1 == 0:
                        newfield = matrix_updater.update_garbage(field)
                        field = newfield
                    garbage_update_times.append(time.time() - t0)

                    ct = timer(
                        combo_time=combo_time,
                        clears=returns[1],
                        combo_counter=combo_counter,
                    )

                    combo_time = ct[0]
                    combo_counter = ct[1]
                    # print(field)
                    # print("combos", combos)
                    print("piece_count", count)
                    print("next_tetromino", next_tetromino_name)
                    print("combo_counter", combo_counter)

                    current_tetromino = next_tetromino
                    tetromino_name = next_tetromino_name

                    if count > 0:
                        count += 1

                    if count % 10 == 0:
                        if sys.argv[1] != "-maserati":
                            t0 - time.time()
                            game_over = matrix_updater.check_end_round()
                            if game_over == True:
                                time.sleep(0.5)
                                game_over = matrix_updater.check_end_round()
                            game_over_check_times.append(time.time() - t0)
                        else:
                            game_over = matrix_updater.check_end_round()

                    combo_time = combo_time - (time.time() - start_time)

                    if combo_time < 0:
                        combo_time = 0
                        if combo_counter != 0:
                            combos.append(combo_counter)
                        combo_counter = 0
                    print("combo_time", combo_time)
                    print("")

                    ## Throttle speed if move would be faster than max speed
                    move_time = time.time() - start_time
                    min_time_per_piece = 1 / (settings.max_bpm / 60)
                    if move_time < min_time_per_piece:
                        time.sleep(min_time_per_piece - move_time)

                    if game_over == True:
                        print("GAME OVER DETECTED")
                        times = [
                            np.average(best_drop_times),
                            np.average(move_execution_times),
                            np.average(garbage_update_times),
                            np.average(game_over_check_times),
                        ]
                        print("average time to get best move", times[0])
                        print("average time to get execute move", times[1])
                        print("average time to get update garbage", times[2])
                        print("average time to get check game over", times[3])
                        print("bpm estimate:", float(60 / (np.sum(times))))

                        if sys.argv[1] == "-maserati" or sys.argv[1] == "-cheese":
                            time.sleep(0.5)
                            print("Leaving challenge and restarting")
                            leave_challenge()
                            time.sleep(0.5)
                            game_over = False
                            count = -2
                        else:
                            while True:
                                i = matrix_updater.check_start_round()
                                if i != 0:
                                    time.sleep(i - 0.5)
                                    count = -1
                                    game_over = False
                                    break

        listener.join()
