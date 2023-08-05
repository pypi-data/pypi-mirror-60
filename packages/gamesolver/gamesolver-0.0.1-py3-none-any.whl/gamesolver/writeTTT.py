import sys
sys.path.append("..")
from timeit import timeit
from logic.Games.TTT import TTT
from logic.Solvers import Solver
from logic.GameManager import GameManager

SIZE = 4
WINBY = 3
NAME = r'TTT' + str(SIZE) + r'by' + str(SIZE) + r'win' + str(WINBY) + r'AndRemotenessOptimized.csv'  

game = TTT(size=SIZE, winBy=3)
solver = Solver.Solver(game=game, name=NAME, read=False)
solver.solve(game)
solver.writeMemory(name=NAME)
GameManager(game, None).play()
