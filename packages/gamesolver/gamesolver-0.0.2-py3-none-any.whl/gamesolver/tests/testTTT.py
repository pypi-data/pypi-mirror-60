from timeit import timeit
from ..Games.TTT import TTT
from ..Solvers import Solver, TierSolver 
from ..GameManager import GameManager

def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

def execute(size=3, tier=True, name='', read=False, mp=False):
    game = TTT(size=size)
    if tier: solver = TierSolver.TierSolver(game, name=name, read=read, mp=mp)
    else: solver = Solver.Solver(game, name=name, read=read, mp=mp)
    gameManager = GameManager(game, solver)
    return gameManager

if __name__ == '__main__':
    """for i in range(10):
        wrapped = wrapper(lambda game, tier : [i.serialize() for i in game.generateTierBoards(game, tier)], TTT(size=3), i) 
        print(timeit(wrapped, number=1))
        print(wrapped())"""
    wrapped = wrapper(execute, size=3)
    print(timeit(wrapped, number=1))
    wrapped = wrapper(execute, tier=False, size=3)
    print(timeit(wrapped, number=1))