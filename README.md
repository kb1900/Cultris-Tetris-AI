# Cultris-Tetris-AI
[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

This repo contains a preliminary attempt at creating a tetris AI to play the block-based puzzle game, Cultris 2 (available at http://gewaltig.net/cultris2.aspx). It uses a combination of internal game heuristics,particle swarm optimization and genetic algorithms to generate weight based and neural network based models to iterate through possible moves and play those that yield the best gamestates. Currently the AI has been well-trained to downstack and survive as long as possible in all online and offline modes.


# To do:
  - Remove dependencies requrired for interfacing with Cultris
  - Make interfacing with Cultris cross-platform
  - Create evaluation functions/additional heuristics to train upstacking + comboing
  - Continue refactoring heuristic generation
  - Explore novel training methods and better NN structures


### Installation

Create a virtualenv (recommended) and install the dependencies

```sh
$ cd cultris-tetris-ai
$ python3 -m venv . # recommended
$ source bin/activate
$ pip3 install -e . # setup.py contains a list of currently required dependencies
```

To run a test game:
```sh
$ python3 c2ai deap.pso.downstack 
# runs a simulated game in console using the weights in /deap/pso/downstack/tetris.py
```

Running the bot on Cultris 2 currently requires a specific environment (mac os, template matching, resolution and window sizing etc.) that is not transferable between PCs. This is on the to do list, however instructions are below for Mac OS on a 15 inch MBP:
```sh
# Set C2 dimensions to 1552 x 996. Use default piece orientations and colors.
# Controls: 
# C for Harddrop, Q for CCW rotation, W for Cw rotation, TAB for 180 rotation
# Arrow keys for L/R/Downwards Movement
$ cd c2ai
$ python3 main.py -x 
```

### Videos

Early videos of the AI's progress can be found below and will be updated infrequently. The AI is far more efficient now with the introduction of new heuristics, more training iterations, and bugfixes.

| Date | Link |
| ------ | ------ |
| October 8 | https://youtu.be/16yfSYFDXKQ |
| October 2 | https://youtu.be/0DMhihKoAgo |
| August 11 | https://youtu.be/VLiaSU1tr74 |
| August 10 | https://youtu.be/Jz3FvLdF1VU |


