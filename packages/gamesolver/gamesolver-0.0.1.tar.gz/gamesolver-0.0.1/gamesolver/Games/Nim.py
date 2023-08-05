import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from Game import Game
import Solver
from GameManager import *
from util import Value

class Nim(Game):

    def __init__(self, start=10, moves=[1, 2], turn=1):
        self.pile = start
        self.turn = turn
        self.moves = moves

    def getBase(self):
        return Nim(start = self.start, moves = self.moves, turn = self.getFirstPlayer())

    def getTurn(self):
        return self.turn

    def getFirstPlayer(self):
        return 1

    def getSecondPlayer(self):
        return 2

    def generateMoves(self):
        return [x for x in self.moves if x <= self.pile]

    def doMove(self, move):
        if move not in self.generateMoves():
            return self
        game = Nim(
            self.pile - move, 
            self.moves, 
            2 if self.turn == 1 else 1)
        return game
    
    def primitive(self):
        return Value.LOSE if self.pile == 0 else Value.UNDECIDED

    def toString(self):
        return str(self.pile)

    def serialize(self):
        return self.toString()
        
    def moveFromInput(self, prompt):
        print(prompt)
        return int(input())

if __name__ == '__main__':
    game = Nim(10, [1, 2])
    solver = Solver.Solver()
    gameManager = GameManager(game, solver)
    gameManager.play()
