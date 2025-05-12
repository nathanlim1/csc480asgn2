# CSC480 Assignment 2: Monte Carlo Tree Search Poker Bot
Nathan Lim (nlim10@calpoly.edu)

Dr. Kirk Duran

Implemented in two files:

- Poker.py -> Implementation of the poker simulator as a Python Class, including the game state, player actions, and hand evaluation.
- Bot.py -> Implementation of the Monte Carlo Tree Search Poker Bot and the main function.

To run the simulation, simply run Bot.py in terminal. A game of poker will be simulated between the bot and an opponent that
never folds. The result of the game will be printed to the console, and the program will give you the opportunity to
run another game once the current one ends.

The bot is implemented as the assignment specifies, running simulations for 10 seconds and then determining whether
to stay or fold based on whether or not it won in >=50% of the simulations.

Thank you!