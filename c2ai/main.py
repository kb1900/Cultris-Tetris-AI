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
garbage_update_times = []
game_over_check_times = []
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


############# LAUNCHING GAME ################

# if c2_open() == False:
#   print('Starting up Cultris')
#   os.system("open /Applications/cultris2.app")
#   time.sleep(5)
#   pyautogui.press('enter')
#   time.sleep(.5)

# elif c2_open() == True:
#   print('C2 is open, navigating to login page')
#   os.system("open /Applications/cultris2.app")
#   time.sleep(.5)
# else:
#   print('error on launching cultris2')


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

                    elif sys.argv[1] == "-cheese":
                        os.system("open /Applications/cultris2.app")
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
                        os.system("open /Applications/cultris2.app")
                        pass
                        count = -1
                    count = -1

                    # time.sleep(.01)

                    ############# ORIENTING FIELD MATRIX ################
                while count == -1 and break_program == False:
                    next_piece = Classifier.template_match("Images/nextpiece.png")
                    ## Define future coordinates relative to this template matched position
                    if next_piece == False:
                        print(
                            "ERROR finding nextpiece template match. ATTEMPTING 2nd TIME"
                        )
                        next_piece = Classifier.template_match("Images/nextpiece.png")
                        ## Define future coordinates relative to this template matched position
                        if next_piece == False:
                            print(
                                "ERROR finding nextpiece template match. ATTEMPTING 3rd TIME"
                            )
                            next_piece = Classifier.template_match(
                                "Images/nextpiece.png"
                            )
                            ## Define future coordinates relative to this template matched position
                            if next_piece == False:
                                print(
                                    "ERROR finding nextpiece template match. Re-setting count to -2"
                                )
                                count = -2
                                break

                    target = Classifier.template_match(
                        build_absolute_path("Images/kb_baby_bot.png")
                    )
                    if target == False:
                        print(
                            "ERROR finding kb_baby_bot template match. ATTEMPTING 2nd TIME"
                        )
                        target = Classifier.template_match(
                            build_absolute_path("Images/kb_baby_bot.png")
                        )
                        if target == False:
                            print(
                                "ERROR finding kb_baby_bot template match. ATTEMPTING 3rd TIME"
                            )
                            target = Classifier.template_match(
                                build_absolute_path("Images/kb_baby_bot.png")
                            )
                            if target == False:
                                print(
                                    "ERROR finding kb_baby_bot template match. Re-setting count to -2"
                                )
                                count = -2
                                break

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
                    if sys.argv[1] != "-cheese" and sys.argv[1] != "-cheesemp":
                        try:
                            current_rgb = Classifier.get_first_piece_rgb(COLUMN, ROW)
                            current_tetromino = Classifier.TETROMINO_FADED[
                                current_rgb
                            ]()
                            tetromino_name = Classifier.TETROMINO_FADED_NAME[
                                current_rgb
                            ]
                            print("detected ghost as:", tetromino_name)
                        except:
                            next_rgb = Classifier.get_next_rgb(next_piece)
                            next_tetromino = Classifier.TETROMINO[next_rgb]()
                            next_tetromino_name = Classifier.TETROMINO_NAME[next_rgb]
                            print("did not detect ghost")
                            print("detected next piece as", next_tetromino_name)

                            pyautogui.typewrite(
                                " "
                            )  # place 1st piece at spawn location
                            Classifier.get_occupied(field, COLUMN, ROW)

                            current_tetromino = next_tetromino
                            tetromino_name = next_tetromino_name
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
                        if field.height() > 15 or field.count_gaps() > 3:
                            settings.mode = "downstack"

                    next_rgb = Classifier.get_next_rgb(next_piece)
                    next_tetromino = Classifier.TETROMINO[next_rgb]()
                    next_tetromino_name = Classifier.TETROMINO_NAME[next_rgb]

                    t0 = time.time()
                    start_time = time.time()
                    try:
                        best_drop = Optimizer.best_move(
                            field, current_tetromino, next_tetromino
                        )
                    except IndexError:
                        print("Game Over, ran out of moves")
                        game_over = 1
                    best_drop_times.append(time.time() - t0)

                    t0 = time.time()
                    rotation = best_drop[1]
                    column = best_drop[2]

                    current_tetromino.rotate(rotation)
                    field.drop(current_tetromino, column)

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
                        # updated_field = matrix_updater.update_field(field)
                        newfield = matrix_updater.update_garbage(field)
                        field = newfield
                    garbage_update_times.append(time.time() - t0)

                    current_tetromino = next_tetromino
                    tetromino_name = next_tetromino_name
                    if count > 0:
                        count += 1

                    t0 - time.time()
                    if autopy.screen.get_color(COLUMN[4], ROW[9]) == (
                        255,
                        255,
                        255,
                    ) and autopy.screen.get_color(COLUMN[4], ROW[13] - 14) == (
                        255,
                        255,
                        255,
                    ):
                        game_over = 1
                    elif autopy.screen.get_color(COLUMN[9] + 56, ROW[8]) == (
                        255,
                        255,
                        255,
                    ):
                        game_over = 1
                    else:
                        game_over = 0
                    game_over_check_times.append(time.time() - t0)

                    ## Throttle speed if move would be faster than max speed
                    move_time = time.time() - start_time
                    if move_time < min_time_per_piece:
                        time.sleep(min_time_per_piece - move_time)

                    if game_over == 1:
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
                        settings.mode = "upstack"
                        if sys.argv[1] == "-maserati" or sys.argv[1] == "-cheese":
                            time.sleep(0.5)
                            print("Leaving challenge and restarting")
                            leave_challenge()
                            time.sleep(0.5)
                            count = -2
                        else:
                            print("press UP to continue @ next round start")
                            break_program = True
                            count = -1
                            break
                            # ### write winner check a la above and improve game over check since it is non-specific!! can be triggered by z

        listener.join()
