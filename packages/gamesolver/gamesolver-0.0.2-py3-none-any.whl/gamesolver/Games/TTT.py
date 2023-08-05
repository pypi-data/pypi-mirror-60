from copy import copy, deepcopy

from gamesolver.Games.TierGame import TierGame
from gamesolver.util import GameValue

FIRST = "X"
SECOND = "O"
NONE = "_"

class TTT(TierGame):

    def __init__(self, size=3, winBy=None, turn=FIRST, code=None):
        self.turn = turn
        self.size = size
        self.numPieces = 0
        self.board = [[NONE for _ in range(size)] for _ in range(size)]
        if code: 
            self.size = int(len(code) ** 0.5)
            assert self.size % 1 == 0
            numFIRST = code.count(FIRST)
            numSECOND = code.count(SECOND)
            diff = abs(numSECOND - numFIRST)
            assert diff == 0 or diff == 1
            self.turn = FIRST if numFIRST <= numSECOND else SECOND
            self.numPieces = numFIRST + numSECOND
            self.board = [[code[i + self.size * j] for i in range(self.size)] for j in range(self.size)]
        self.winBy = winBy if winBy else self.size    
    
    def getBase(self):
        return TTT(size=self.size, turn=self.getFirstPlayer())

    def getTurn(self):
        return self.turn

    def getFirstPlayer(self):
        return FIRST

    def getSecondPlayer(self):
        return SECOND

    def generateMoves(self):
        if self.primitive() != GameValue.UNDECIDED: return []
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == NONE:
                    moves += [(row, col)]
        return moves

    def doMove(self, move):
        assert move[0] is not None and move[1] is not None
        switch = { FIRST : SECOND, SECOND : FIRST }
        board = deepcopy(self.board)
        board[move[0]][move[1]] = self.turn
        game = TTT(turn=switch[self.turn])
        game.size = self.size
        game.winBy = self.winBy
        game.board = board
        game.numPieces = self.numPieces + 1
        return game

    def primitiveState(self):
        def end(indices):
            start, length = 0, 0
            same = NONE
            for i, index in enumerate(indices):
                length+=1
                entry = self.board[index[0]][index[1]]
                if entry == NONE: same, start, length = NONE, i, 0
                if entry != same: same, start, length = entry, i, 1
                if length >= self.winBy: return indices[start:start+length]
            return []

        indices = set()
        # Horizontals
        for row_num in range(len(self.board)):
            row = [(row_num, j) for j in range(len(self.board))]
            if end(row) : indices.update(end(row))
        
        # Verticals
        for col_num in range(len(self.board[0])):
            col = [(i, col_num) for i in range(len(self.board))]
            if end(col): indices.update(end(col))

        # Diagonals
        def clamp(value): return value < self.size and value >= 0
        for i in range(-self.size + 1, self.size):
            diag1 = [(i + j, j) for j in range(self.size) if clamp(i + j)]
            diag2 = [(j, self.size - 1 + i - j) for j in range(self.size) if clamp(self.size - 1 + i - j)]
            if end(diag1): indices.update(end(diag1))
            if end(diag2): indices.update(end(diag2))
        return list(indices)

    def primitive(self):
        if self.primitiveState(): return GameValue.LOSE
        if self.numPieces == self.size ** 2: return GameValue.TIE
        return GameValue.UNDECIDED

    def toString(self):
        string = ""
        for row in self.board:
            string += "".join(row) + "\n"
        return string

    def serialize(self):
        switch = { 
            FIRST : { FIRST : FIRST, SECOND : SECOND, NONE : NONE }, 
            SECOND : { SECOND : FIRST, FIRST : SECOND, NONE : NONE }
            #,SECOND : { FIRST : SECOND, SECOND : FIRST, NONE : NONE } 
        }
        flatten_list = [switch[self.turn][entry] for row in self.reduction() for entry in row]
        return "".join(flatten_list)

    # Returns lowest equivalent state
    def reduction(self):
        def value(board):
            values = { NONE : "0", FIRST : "1", SECOND : "2" }
            flatten_list = [values[entry] for row in board for entry in row]
            return int("".join(flatten_list))
        def rotate(board):
            return [list(row) for row in zip(*board[::-1])]
        def flip(board):
            return board[::-1]
        board, lowest_value, lowest_board = self.board, int("2" * len(self.board) * len(self.board[0])), self.board
        for _ in range(2):
            for _ in range(4):
                board_value = value(board)
                if board_value <= lowest_value: lowest_board, lowest_value = board, board_value
                board = rotate(board)
            board = flip(board)                        
        return lowest_board

    def moveFromInput(self, input):
        return tuple(int(x.strip()) for x in input.split(','))

    def getNumTiers(self):
        return self.size ** 2 + 1

    def getCurTier(self):
        return self.numPieces
