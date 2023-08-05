from gamesolver.util import *

class GameManager:

    def __init__(self, game, solver=None):
        self.base = game
        self.game = game
        self.solver = solver
        if solver:
            self.solver.solve(self.game)

    # Starts the GameManager
    def play(self):
        self.game = self.base
        while self.game.primitive() == GameValue.UNDECIDED:
            self.printInfo()
            self.printTurn()
        self.printInfo()
        print("Game Over")

    # Prints the game info
    def printInfo(self):
        print("Primitive:     ", self.game.primitive())
        if self.solver:
            print("Solver:        ", self.solver.solve(self.game))
            print("Wins: ", self.solver.numValues(GameValue.WIN), 
            "Loses: ", self.solver.numValues(GameValue.LOSE), 
            "Ties: ", self.solver.numValues(GameValue.TIE))
            print("Remoteness: ", self.solver.getRemoteness(self.game.serialize()))
        print("Primitive state: ", self.game.primitiveState())
        print(self.game.getTurn(), "'s turn")
        print(self.game.toString())
        print("Possible Moves:", self.game.generateMoves())

    # Prompts for input and moves
    def printTurn(self):
        if self.game.getTurn() == self.game.getFirstPlayer() or not self.solver:
            print("Enter Piece: ")
            move = self.game.moveFromInput(input())
            if move not in self.game.generateMoves():
                print("Not a valid move, try again")
            else:
                self.game = self.game.doMove(move)
        else:
            self.game = self.game.doMove(self.solver.generateMove(self.game))
        print("----------------------------")
