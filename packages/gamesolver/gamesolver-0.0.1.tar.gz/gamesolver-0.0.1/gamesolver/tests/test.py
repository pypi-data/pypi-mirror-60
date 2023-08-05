import pytest

from ..Games.TTT import TTT
from ..Solvers import Solver, TierSolver 
from .. import util

def test_solvers():
    game = TTT()
    solver = Solver.Solver(game)
    tier = TierSolver.TierSolver(game)
    assert solver.solve(game) == util.GameValue.TIE
    assert tier.solve(game) == util.GameValue.TIE
    assert all(item in solver.memory.items() for item in tier.memory.items())

def test_TTT():
    game = TTT()
    assert game.primitive() == util.GameValue.UNDECIDED
    while game.generateMoves():
        assert game.primitive() == util.GameValue.UNDECIDED
        game = game.doMove(game.generateMoves()[0])
    assert game.primitive() != util.GameValue.UNDECIDED
