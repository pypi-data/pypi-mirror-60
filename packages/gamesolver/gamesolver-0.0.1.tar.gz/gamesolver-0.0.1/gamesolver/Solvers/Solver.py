from .. util import *
import csv
import math
import os
import random

from multiprocessing import Process, Value, Array, Manager, current_process

# This solver code is my own written creation (Anthony Ling). You can find the source code 
# at https://github.com/Ant1ng2/Gamesolver

# util module not included

class Solver():

    def __init__(self, game=None, name='', read=False, mp=False):
        self.memory = {}
        self.remoteness = {}
        self.base = game
        if mp: self.solve = self.solveTraverseMP
        if not mp: self.solve = self.solveTraverse
        path = os.path.join(os.getcwd() + r'/', name)
        if path and read:
            try:
                with open(path, 'r') as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        self.memory[row[0]] = row[1]
                        self.remoteness[row[0]] = int(row[2])
            except:
                print("Automatically solving manually as path not found: " + path)

    def resetMemory(self):
        self.memory.clear()

    def writeMemory(self, name=r'untitled.csv'):        
        path = os.path.join(os.getcwd() + r'/', name)
        with open(path, 'w') as f:
            f.write("%s,%s,%s\n"%("key", "value", "remoteness"))
            for key in self.memory.keys():
                f.write("%s,%s,%s\n"%(key, self.memory[key], self.getRemoteness(key)))

    def numValues(self, value):
        return len([i for i in self.memory.values() if i == value])

    def getRemoteness(self, key=None, game=None):
        if game: key = game.serialize()
        return self.remoteness[key]

    # this one will traverse all subtree
    def solveTraverse(self, game):
        winFlag = False
        tieFlag = False
        serialized = game.serialize()
        # if len(self.memory) % 1000 == 0: print(len(self.memory))

        if serialized in self.memory:
            return self.memory[serialized]
        primitive = game.primitive()

        if primitive != GameValue.UNDECIDED:
            self.memory[serialized] = primitive
            self.remoteness[serialized] = 0
            return primitive

        min_remote = -1
        for move in game.generateMoves():
            newTicTacToe = game.doMove(move)
            value = self.solveTraverse(newTicTacToe)
            remote = self.remoteness[newTicTacToe.serialize()] + 1
            if min_remote == -1: min_remote = remote
            if value == GameValue.LOSE:
                if tieFlag and not winFlag: min_remote = remote
                min_remote = min(min_remote, remote)
                winFlag = True
            if value == GameValue.TIE:
                if not winFlag: 
                    min_remote = max(min_remote, remote)
                    tieFlag = True
            # You are losing and want to maximize
            if value == GameValue.WIN and not (winFlag or tieFlag): min_remote = max(min_remote, remote)
        if not winFlag: # There does not exist a losing child
            if tieFlag: # There exists a tie
                self.memory[serialized] = GameValue.TIE
            else: # There is no tie
                self.memory[serialized] = GameValue.LOSE
        else:
            self.memory[serialized] = GameValue.WIN
        self.remoteness[serialized] = min_remote
        return self.memory[serialized]

    def solveTraverseMP(self, game):
        self.memory = Manager().dict()
        self.remoteness = Manager().dict()
        serialized = game.serialize()
        primitive = game.primitive()

        if primitive != GameValue.UNDECIDED:
            self.memory[serialized] = primitive
            self.remoteness[serialized] = 0
            return primitive

        def worker(move):
            #print(current_process().name, "start")
            newTicTacToe = game.doMove(move)
            self.solveTraverse(newTicTacToe)
            #print(current_process().name, "end")

        processes = []

        for move in game.generateMoves():
            p = Process(target=worker, args=(move,))
            processes.append(p)
            p.start()
        for p in processes:
            p.join()
            
        return self.solveTraverse(game)

    def generateMove(self, game):
        moveList = game.generateMoves()
        if not moveList: return
        random.shuffle(moveList)
        tieMove, tieRemoteness = None, -1
        lossMove, lossRemoteness = moveList[0], -1
        for move in moveList:
            newGame = game.doMove(move)
            value = self.solve(newGame)
            remoteness = self.getRemoteness(game=newGame)
            # The AI could pick a winning position that doesn't directly end the game.
            # TODO: Pick a move to end the game
            if value == GameValue.LOSE:
                return move
            if value == GameValue.TIE and remoteness > tieRemoteness:
                tieMove, tieRemoteness = move, remoteness
            if value == GameValue.WIN and remoteness > lossRemoteness:
                lossMove, lossRemoteness = move, remoteness
        return tieMove if tieMove else lossMove
