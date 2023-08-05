import sys
sys.path.append("..")
from timeit import timeit
from gamesolver.Games.TTT import TTT
from gamesolver.Solvers import Solver
from gamesolver.GameManager import GameManager

SIZE = 3
WINBY = 3
NAME = r'TTT' + str(SIZE) + r'by' + str(SIZE) + r'win' + str(WINBY) + r'AndRemotenessOptimized.csv'  

game = TTT(size=SIZE, winBy=WINBY)
solver = Solver.Solver(game=game, name=NAME, read=True)
solver.solve(game)
solver.writeMemory(name=NAME)
GameManager(game, solver).play()
