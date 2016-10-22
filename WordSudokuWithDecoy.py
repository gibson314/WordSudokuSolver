'''
Word Sudoku with decoy words
Author: Litian Ma
'''

import copy
import time


class Placement:
    def __init__(self, direction, coordinate, word):
        self.direction = direction
        self.coordinate = coordinate
        self.word = word
        self.word_len = len(word)


# AFTER CHECK. assign command into sudoku, and return a new sudoku
def place_word(sudoku_matrix, placement):
    already_exist = 1
    if placement.direction == 'V':
        for n in range(placement.word_len):
            if sudoku_matrix[placement.coordinate[0] + n][placement.coordinate[1]] != placement.word[n]:
                sudoku_matrix[placement.coordinate[0] + n][placement.coordinate[1]] = placement.word[n]
                already_exist = 0
    elif placement.direction == 'H':
        for n in range(placement.word_len):
            if sudoku_matrix[placement.coordinate[0]][placement.coordinate[1] + n] != placement.word[n]:
                sudoku_matrix[placement.coordinate[0]][placement.coordinate[1] + n] = placement.word[n]
                already_exist = 0
    # do not select this word
    elif placement.direction == 'N':
        pass
    return sudoku_matrix, already_exist


def is_complete(sudoku_matrix):
    for row in sudoku_matrix:
        if '_' in row:
            return False
    return True


class WordSudokuSlover:
    direction = ['V', 'H']

    def __init__(self, gridfile, wordbank):
        self.sudoku_matrix = []
        self.wordbank = []
        self.trackingpath = []
        self.nodenum = 0
        with open(gridfile, 'rt') as grid:
            for line in grid:
                self.sudoku_matrix.append(list(line.strip('\n')))

        with open(wordbank, 'rt') as bank:
            for line in bank:
                self.wordbank.append(line.strip('\n').upper())

    def checkContraint(self, sudoku_matrix, placement):
        y = placement.coordinate[0]
        x = placement.coordinate[1]
        if placement.direction == 'V' and y + placement.word_len <= 9:
            for i in range(placement.word_len):
                if placement.word[i] == sudoku_matrix[y + i][x]:
                    continue
                elif sudoku_matrix[y + i][x] != '_' \
                    or placement.word[i] in sudoku_matrix[y + i] \
                    or placement.word[i] in [sudoku_matrix[j][x] for j in range(9)] \
                    or placement.word[i] in [sudoku_matrix[j][k]
                                             for j in range((y+i)//3*3, (y+i)//3*3+3)
                                             for k in range(x//3*3, x//3*3+3)]:
                    return False
            return True
        elif placement.direction == 'H' and x + placement.word_len <= 9:
            for i in range(placement.word_len):
                if placement.word[i] == sudoku_matrix[y][x + i]:
                    continue
                elif sudoku_matrix[y][x + i] != '_' \
                    or placement.word[i] in sudoku_matrix[y] \
                    or placement.word[i] in [sudoku_matrix[j][x + i] for j in range(9)] \
                    or placement.word[i] in [sudoku_matrix[j][k]
                                             for j in range(y//3*3, y//3*3+3)
                                             for k in range((x+i)//3*3, (x+i)//3*3+3)]:
                    return False
            return True
        else:
            return False

    def recursive_search(self, assignment, wordbank):
        if is_complete(assignment):
            return assignment
        if len(wordbank) == 0:
            return False
        word = self.selectWord(assignment, wordbank)

        for placement in self.domainValues(word, assignment):
            new_assignment = copy.deepcopy(assignment)
            new_wordbank = copy.deepcopy(wordbank)
            new_wordbank.remove(word)
            new_assignment, already_exist = place_word(new_assignment, placement)
            if already_exist == 0:
                self.trackingpath.append(placement)
            else:
                placement.direction = 'A'
                self.trackingpath.append(placement)
            self.nodenum += 1
            result = self.recursive_search(new_assignment, new_wordbank)
            if result:
                return result
            self.trackingpath.remove(placement)
        return False

    def selectWord(self, assignment, wordbank):
        dictionary = {}
        for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            dictionary[ch] = 0
        for i in assignment:
            for j in i:
                if j != '_':
                    dictionary[j] += 1
        # maxlen = 0
        maxweight = 0
        returnword = ''
        for word in wordbank:
            weight = 0
            for ch in word:
                weight += dictionary[ch]
            if len(word) > len(returnword) or (len(word) == len(returnword) and weight > maxweight):
                returnword = word
                maxweight = weight
        return returnword

    def domainValues(self, word, assignment):
        placements = []
        for i in range(10 - len(word)):
            # if some character already exist in the matrix
            direction = 'V'
            for j in range(9):
                placement = Placement(direction, (i, j), word)
                if self.checkContraint(assignment, placement):
                    placements.append(placement)
            direction = 'H'
            for j in range(9):
                placement = Placement(direction, (j, i), word)
                if self.checkContraint(assignment, placement):
                    placements.append(placement)

        placements.sort(key=lambda p: self.count_char_exist(p, assignment), reverse=True)
        direction = 'N'
        placement = Placement(direction, (0, 0), word)
        placements.append(placement)
        a = [(p.direction, p.coordinate, p.word) for p in placements]
        return placements

    # given placement find maximum number of existing character in the assign
    def count_char_exist(self, placement, assignment):
        count = 0
        y = placement.coordinate[0]
        x = placement.coordinate[1]
        origin_string = ""
        if placement.direction == 'V':
            origin_string = [assignment[y + i][x] for i in range(placement.word_len)]
        elif placement.direction == 'H':
            origin_string = [assignment[y][x + i] for i in range(placement.word_len)]
        for i in range(placement.word_len):
            if origin_string[i] != placement.word[i] and origin_string[i] != '_':
                return 0
            if origin_string[i] == placement.word[i]:
                count += 1
        return count

    def solve(self, solution, sequence):
        t0 = time.clock()
        res = self.recursive_search(self.sudoku_matrix, self.wordbank)
        print(time.clock() - t0, "sec")
        print(self.nodenum, "nodes")
        if res == 0:
            print("No Solutions for given Word Sudoku!")
        else:
            print("Successful!")
            with open(solution, 'wt') as file:
                for row in res:
                    print(''.join(row), file=file)
            with open(sequence, 'wt') as file:
                for placement in self.trackingpath:
                    if placement.direction != 'N' and placement.direction != 'A':
                        print(placement.direction + "," +
                              str(placement.coordinate[0]) + "," +
                              str(placement.coordinate[1]) + ": " +
                              placement.word, file=file)


def main():
    sudoku = WordSudokuSlover("grid3.txt", "bank3.txt")
    sudoku.solve("solution3", "sequence3")

if __name__ == '__main__':
    main()

