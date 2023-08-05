from abc import ABC, abstractmethod
from . Game import Game

class TierGame(Game):

    @abstractmethod
    def getNumTiers(self):
        pass

    @abstractmethod
    def getCurTier(self):
        pass