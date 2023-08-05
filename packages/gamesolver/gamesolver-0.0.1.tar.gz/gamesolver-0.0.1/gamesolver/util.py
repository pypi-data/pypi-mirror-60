class GameValue:
    WIN = "Win"
    LOSE = "Lose"
    UNDECIDED = "Undecided"
    TIE = "Tie"

def count(self, array):
    lines = array.split()
    count = 0
    for word in lines:
        for character in list(word):
            if character != " ":
                count += 1
    return count
