max_bpm = 260 # The bpm will be variable but never peak above this due to time tracking and delays in main.py
move_depth = 16 # The top moves from the current piece that will be used first to check second piece. Minimum value 1, maximum value 34.
max_nodes = float("inf") # The maximum number of nodes (boards) that will be scored in total. Minimum value 1, maximum value 35 * 35

mode = "downstack"

modes = True
train = False #ensures that 'n' passed to get_score is used in the evaluation
combo = False

## debug will save a screenshot of the field with overlayed red dots of the grid
## and print the newfield in console. this is to tackle issues with garbage_updating mistakes 
# when the grid overlays a "edge" causing failed garbage detection
# debug code @ in matrix.py ln 171
# this has been resolved in siwtching to the newest cultris patch which removes the background gradient and glow
debug = False
i = 1

downstack_model = [
    17.266573527809562,
    2.777217126349192,
    6.760730777087559,
    0.7876033208193283,
    12.351036669926016,
    1.5,
    17.853166241417732,
    8.531717290316418,
    1.5111635889673647,
    4.507103638484812,
]

upstack_model = [
    17.32625049964644,
    5.0923969528239796,
    3.608690368432538,
    0.4412110937336604,
    8.073529933900081,
    5.015291328665075,
    6.32286927779888,
    1.17234015916849,
    1.0680254883798543,
    6.190027155117337,
]


test_model = [
    17.32625049964644,
    2.0923969528239796,
    3.608690368432538,
    0.4412110937336604,
    8.073529933900081,
    5.015291328665075,
    6.32286927779888,
    1.17234015916849,
    1.0680254883798543,
    6.190027155117337,
]
