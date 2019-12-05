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
from c2ai.base.keyboardpress import Keyboard

best_drop_times = []
move_execution_times = []
garbage_update_times = []
game_over_check_times = []
game_over = False
break_program = False
wins = 0
losses = 0


def init_label():
    label = tkinter.Label(root, text="", font=("Times", "20"), fg="red")
    label.master.overrideredirect(True)
    label.master.geometry("+750+650")
    label.master.lift()
    label.master.wm_attributes("-topmost", True)
    # label.master.wm_attributes("-transparent", 1)
    label.master.config(bg="gray24")
    label.config(bg="gray24")
    label.pack()

    return label


root = tkinter.Tk()
combo_label = init_label()
timer_label = init_label()
piece_count_label = init_label()
next_tetromino_label = init_label()
rotation_column_label = init_label()
mode_label = init_label()
active_combo_label = init_label()
Win_Loss_label = init_label()


def update_labels():
    combo_label["text"] = "Combo: " + str(combo_counter)
    timer_label["text"] = "Time: " + str("{0:.2f}".format(combo_time))
    piece_count_label["text"] = "Piece #" + str(count)
    next_tetromino_label["text"] = "Next: " + str(next_tetromino.type)
    try:
        rotation_column_label["text"] = (
            "Rotation: "
            + str(rotation)
            + " Column: "
            + str(column)
            + "\n Score: "
            + str(round(best_drop[5], 2))
        )
    except:
        pass
    mode_label["text"] = "Mode: " + str(settings.mode)
    active_combo_label["text"] = (
        "Combo Active: " + str(settings.combo) + "\n Max BPM: " + str(max_bpm)
    )
    Win_Loss_label["text"] = "Wins:" + str(wins) + " Losses:" + str(losses)

    root.update()


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
    pyautogui.typewrite("kb_baby_bot")

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

    return [combo_time, combo_counter]


def game_over_sequence(game_over):
    global losses
    global wins

    if sys.argv[1] == "-maserati" or sys.argv[1] == "-cheese":
        time.sleep(0.5)
        print("Leaving challenge and restarting")
        leave_challenge()
        time.sleep(0.5)
        game_over = 0
        count = -2
    elif sys.argv[1] == "-multi":
        os.system("open /Applications/cultris4.app")
        if game_over == 1:
            print("Game Over Detected")
            losses += 1
            update_labels()
            kb.write("=")
        elif game_over == 2:
            print("Winner Detected")
            wins += 1
            update_labels()
            kb.write("=")
        if (losses + wins) % 5 == 0:
            kb.write("Questions or Concerns - pm my creator on discord")
            pyautogui.press("enter")
            kb.write(str(wins) + " Wins " + str(losses) + " Losses")
            pyautogui.press("enter")
            kb.write("=")
        else:
            kb.write("=")

        while True:
            i = matrix_updater.check_start_round()
            if i != 0:
                time.sleep(i - 0.5)
                break


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

                    else:
                        os.system("open /Applications/cultris4.app")
                        pass
                    count = -1

                while count == -1 and break_program == False:

                    ############# ORIENTING FIELD MATRIX ################

                    next_piece = Classifier.template_match("Images/nextpiece4.png")
                    # print('NEXT PIECE:,', next_piece)
                    if next_piece == False:
                        print("ERROR finding nextpiece4 template match. hardcoding")
                        next_piece = (689.0, 199.0)
                        # pyautogui.moveTo(next_piece[0], (next_piece[1] + 110))

                    target = Classifier.template_match(
                        build_absolute_path("Images/kb_baby_bot4.png")
                    )
                    # print("TAGRGET", target)
                    if target == False:
                        print("ERROR finding kb_baby_bot4 template match. hardcoding")
                        target = (351.5, 184.5)

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
                            print("detected ghost as:", current_tetromino.type)
                        except:
                            print("did not detect ghost")
                            count = -1
                    print("Game Starting!")
                    count += 1

                    ############# MAIN PLAYING LOOP STARTS HERE ################

                while count > 0 and break_program == False:

                    # Mode handling (upstack, downstack, combo modifier)
                    if settings.mode == "upstack":
                        if (
                            field.height() > 12
                            or field.count_gaps() > 2
                            or field.max_bump() > 6
                        ):
                            # print(
                            #     "MODE SWITCH TO DOWNSTACK",
                            #     # field.height(),
                            #     # field.count_gaps(),
                            # )
                            settings.mode = "downstack"
                    if settings.mode == "downstack":
                        if combo_counter > 5 or combo_counter + combo_time > 8.5:
                            if field.height() < 15:
                                settings.combo = True
                                max_bpm = settings.max_bpm_peak
                                # print("COMBO ACTIVE")
                        else:
                            settings.combo = False
                            max_bpm = settings.max_bpm
                        if (
                            field.height() < 2
                            and field.count_gaps() < 3
                            and combo_counter < 3
                        ):
                            # print(
                            #     "MODE SWITCH TO UPSTACK",
                            #     # field.height(),
                            #     # field.count_gaps(),
                            # )
                            settings.mode = "upstack"
                            settings.combo = False

                    # Next piece updating
                    next_rgb = Classifier.get_next_rgb(next_piece)
                    next_tetromino = Classifier.TETROMINO[next_rgb]()
                    update_labels()

                    t0 = time.time()
                    start_time = time.time()

                    # We replace the following with 1) conversion of field to a type sent to the go microservice
                    # Then send it to go and recieve the chosen move

                    q = Optimizer.go_best_move(
                        field=field,
                        tetromino=current_tetromino,
                        next_tetromino=next_tetromino,
                        combo_time=combo_time,
                        combo_counter=combo_counter,
                    )
                    # # Best move retrieval
                    # try:
                    #     best_drop = Optimizer.best_move(
                    #         field=field,
                    #         tetromino=current_tetromino,
                    #         next_tetromino=next_tetromino,
                    #         combo_time=combo_time,
                    #         combo_counter=combo_counter,
                    #     )
                    # except IndexError:
                    #     print("Game Over, ran out of moves")
                    #     game_over = 1
                    best_drop_times.append(time.time() - t0)

                    t0 = time.time()
                    # rotation = best_drop[1]
                    # column = best_drop[2]

                    # current_tetromino.rotate(rotation)

                    # try:
                    #     returns = field.drop(current_tetromino, column)
                    # except AssertionError:
                    #     print("Game Over, ran out of moves")
                    #     game_over = 1

                    # # Execute moves
                    # keys = Optimizer.get_keystrokes(
                    #     rotation,
                    #     column,
                    #     {
                    #         "rotate_right": "w",
                    #         "rotate_180": "tab",
                    #         "rotate_left": "q",
                    #         "move_left": "left",
                    #         "move_right": "right",
                    #         "drop": "c",
                    #     },
                    #     tetromino_name=current_tetromino.type,
                    # )
                    key_map = {
                        "rotateRight": "w",
                        "rotate180": "tab",
                        "rotateLeft": "q",
                        "moveLeft": "left",
                        "moveRight": "right",
                        "moveDown": "down",
                        "drop": "c",
                    }

                    moveList = q[0]
                    soft = q[1]

                    clears = q[2]
                    keylist = []

                    keyboard = Keyboard()
                    if soft:
                        # print("SOFT DROP:", moveList)
                        predown = []
                        postdown = []
                        for count, i in enumerate(moveList):
                            if i == "moveDown":
                                predown = moveList[:count]
                                moveList = moveList[count:]
                                break
                        for count, i in enumerate(moveList):
                            if i != "moveDown":
                                postdown = moveList[count:]
                                moveList = moveList[:count]
                                break
                        # print("downs", moveList)
                        # print("len(moveList)", len(moveList))
                        # print("predown", predown)
                        # print("postdown", postdown)

                        predownkeylist = []
                        for i in predown:
                            predownkeylist.append(key_map[i])
                        kb.write(predownkeylist, delay=0.00)

                        down_delay = len(moveList)/50
                        if current_tetromino.type == "I":
                            down_delay += 0.1
                        kb.press(key_map["moveDown"])
                        time.sleep(down_delay)
                        kb.release(key_map["moveDown"])

                        postdownkeylist = []
                        for i in postdown:
                            postdownkeylist.append(key_map[i])
                        kb.write(postdownkeylist, delay=0.01)

                    else:
                        for i in moveList:
                            # print(key_map[i])
                            keylist.append(key_map[i])
                            # keyboard.KeyDown(key_map[i])
                            # keyboard.KeyUp(key_map[i])
                            # time.sleep(0.030)

                        kb.write(keylist, delay=0.00)
                    move_execution_times.append(time.time() - t0)

                    t0 = time.time()
                    if count % 1 == 0:
                        newfield = matrix_updater.update_garbage(field)
                        field = newfield
                    garbage_update_times.append(time.time() - t0)

                    ct = timer(
                        combo_time=combo_time,
                        clears=clears,
                        combo_counter=combo_counter,
                    )

                    combo_time = ct[0]
                    combo_counter = ct[1]
                    # print(field)
                    # print("piece_count", count)
                    # print("next_tetromino", next_tetromino.type)
                    # print("combo_counter", combo_counter)

                    current_tetromino = next_tetromino

                    if count > 0:
                        count += 1

                    # Check Round End
                    if count % 10 == 0:
                        if sys.argv[1] != "-maserati":
                            game_over = matrix_updater.check_end_round()
                            if game_over == True:
                                time.sleep(0.5)
                                game_over = matrix_updater.check_end_round()
                        else:
                            game_over = matrix_updater.check_end_round()

                    if game_over != 0:
                        game_over_sequence(game_over)
                        game_over = 0
                        count = -1

                    # Update combo information
                    combo_time = combo_time - (time.time() - start_time)

                    if combo_time < 0:
                        combo_time = 0
                        if combo_counter != 0:
                            combos.append(combo_counter)
                        combo_counter = 0
                    # print("combo_time", combo_time)
                    # print("")

                    # Throttle speed if move would be faster than max speed
                    move_time = time.time() - start_time
                    min_time_per_piece = 1 / (max_bpm / 60)
                    if move_time < min_time_per_piece:
                        time.sleep(min_time_per_piece - move_time)

        listener.join()
