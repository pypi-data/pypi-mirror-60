from copy import copy, deepcopy
import sys
sys.path.append('..')

from Game import *
import Solver
from GameManager import *

# This game is a variation of AllQueens except with 8 queens and three in a row with a 4x4 board.

class ThreeQueens(Game):
