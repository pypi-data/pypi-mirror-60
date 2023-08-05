from abc import ABC, abstractmethod

class Game(ABC):

    # Returns the beginning state of a Game
    @abstractmethod
    def getBase(self):
        pass

    # Returns a string that is the current player's turn
    @abstractmethod
    def getTurn(self):
        pass

    # Get the placeholders for the first player and second player
    @abstractmethod
    def getFirstPlayer(self):
        pass

    @abstractmethod
    def getSecondPlayer(self):
        pass

    # Returns a list of "moves"
    @abstractmethod
    def generateMoves(self):
        pass

    # Returns a new Game object with move executed
    @abstractmethod
    def doMove(self, move):
        pass

    # Returns a primitive value from class Value
    @abstractmethod
    def primitive(self):
        pass

    # Return the primitive state (for web solver)
    def primitiveState(self):
        return "Undefined"

    # Returns a string of the board state for player's use
    @abstractmethod
    def toString(self):
        pass

    # Returns an identifier of the state to be stored in memory
    @abstractmethod
    def serialize(self):
        pass

    # Returns a move based on the input, must print prompt based on number of times
    # to ask for the number of inputs
    @abstractmethod
    def moveFromInput(self, prompt):
        pass
