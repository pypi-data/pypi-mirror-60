import sys
sys.path.append("..")
from timeit import timeit
from gamesolver.Games.TTT import TTT
from gamesolver.Solvers import Solver
from gamesolver.GameManager import GameManager

def example(size=4, winby=3, name=None):
    if not name: 
        name = r'TTT' + str(size) + r'by' + str(size) + r'win' + str(winby) + r'AndRemotenessOptimized.csv'    
    game = TTT(size=size, winBy=winby)
    solver = Solver(name=name, read=True)
    solver.solve(game)
    solver.writeMemory(name=name)
    GameManager(game, solver).play()
