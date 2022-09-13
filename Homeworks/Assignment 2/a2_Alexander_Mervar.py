#!/usr/bin/python3
# B351/Q351 Fall 2022
# Do not share these assignments or their solutions outside of this class.

import csv
import itertools

class Board():

    ##########################################
    ####   Constructor
    ##########################################
    def __init__(self, filename):

        # initialize all of the variables
        self.n2 = 0
        self.n = 0
        self.spaces = 0
        self.board = None
        self.valsInRows = None
        self.valsInCols = None
        self.valsInBoxes = None
        self.unsolvedSpaces = None

        # load the file and initialize the in-memory board with the data
        self.loadSudoku(filename)


    # loads the sudoku board from the given file
    def loadSudoku(self, filename):

        with open(filename) as csvFile:
            self.n = -1
            reader = csv.reader(csvFile)
            for row in reader:

                # Assign the n value and construct the approriately sized dependent data
                if self.n == -1:
                    self.n = int(len(row) ** (1/2))
                    if not self.n ** 2 == len(row):
                        raise Exception('Each row must have n^2 values! (See row 0)')
                    else:
                        self.n2 = len(row)
                        self.spaces = self.n ** 4
                        self.board = {}
                        self.valsInRows = [set() for _ in range(self.n2)]
                        self.valsInCols = [set() for _ in range(self.n2)]
                        self.valsInBoxes = [set() for _ in range(self.n2)]
                        self.unsolvedSpaces = set(itertools.product(range(self.n2), range(self.n2)))

                # check if each row has the correct number of values
                else:
                    if len(row) != self.n2:
                        raise Exception('Each row must have the same number of values. (See row ' + str(reader.line_num - 1) + ')')

                # add each value to the correct place in the board; record that the row, col, and box contains value
                for index, item in enumerate(row):
                    if not item == '':
                        self.board[(reader.line_num-1, index)] = int(item)
                        self.valsInRows[reader.line_num-1].add(int(item))
                        self.valsInCols[index].add(int(item))
                        self.valsInBoxes[self.spaceToBox(reader.line_num-1, index)].add(int(item))
                        self.unsolvedSpaces.remove((reader.line_num-1, index))


    ##########################################
    ####   Utility Functions
    ##########################################

    # converts a given row and column to its inner box number
    def spaceToBox(self, row, col):
        return self.n * (row // self.n) + col // self.n

    # prints out a command line representation of the board
    def print(self):
        for r in range(self.n2):
            # add row divider
            if r % self.n == 0 and not r == 0:
                if self.n2 > 9:
                    print("  " + "----" * self.n2)
                else:
                    print("  " + "---" * self.n2)

            row = ""

            for c in range(self.n2):

                if (r,c) in self.board:
                    val = self.board[(r,c)]
                else:
                    val = None

                # add column divider
                if c % self.n == 0 and not c == 0:
                    row += " | "
                else:
                    row += "  "

                # add value placeholder
                if self.n2 > 9:
                    if val is None: row += "__"
                    else: row += "%2i" % val
                else:
                    if val is None: row += "_"
                    else: row += str(val)
            print(row)


    ##########################################
    ####   Move Functions - YOUR IMPLEMENTATIONS GO HERE
    ##########################################

    # makes a move, records it in its row, col, and box, and removes the space from unsolvedSpaces
    def makeMove(self, space, value):
        # Takes a tuple of the form (r, c) and a valid assignment.
        # 1. Saves the value in board at the appropriate space
        # 2. Saves the value in the appropriate row, col, and box
        # 3. Removes the space from unsolvedSpaces
        selectedRow = space[0]
        selectedCol = space[1]
        self.board[space] = value
        self.valsInRows[selectedRow].add(value)
        self.valsInCols[selectedCol].add(value)
        self.valsInBoxes[self.spaceToBox(selectedRow, selectedCol)].add(value)
        self.unsolvedSpaces.remove(space)




    # removes the move, its record in its row, col, and box, and adds the space back to unsolvedSpaces
    def undoMove(self, space, value):
        # Takes a tuple of the form (r, c) and a valid assignment.
        # 1. Remove the value from board at the appropriate space
        # 2. Remove the value from the appropriate row, col, and box
        # 3. Add the space back to unsolvedSpaces
        selectedRow = space[0]
        selectedCol = space[1]
        self.board[space] = None
        self.valsInRows[selectedRow].remove(value)
        self.valsInCols[selectedCol].remove(value)
        self.valsInBoxes[self.spaceToBox(selectedRow, selectedCol)].remove(value)
        self.unsolvedSpaces.add(space)

    # returns True if the space is empty and on the board,
    # and assigning value to it if not blocked by any constraints
    def isValidMove(self, space, value):
        # Takes a tuple of the form (r, c) and a valid assignment.
        # 1. Check if the space is empty
        # 2. Check if the space is on the board
        if not (space in self.board):
            return False
        if self.board[space] is not None:
            return False
        # 3. Check if the value is not blocked by any constraints
        if value in self.valsInRows[self.valsInRows[space[0]]]:
            return False
        if value in self.valsInCols[self.valsInCols[space[1]]]:
            return False
        if value in self.valsInBoxes[self.spaceToBox(space[0], space[1])]:
            return False
        return True

    # optional helper function for use by getMostConstrainedUnsolvedSpace
    def evaluateSpace(self, space):
        # returns the number of possible values for the space
        domain = set(range(1, self.n2 + 1))
        domain = set(domain - self.valsInRows[space[0]])
        domain = set(domain - self.valsInCols[0])
        domain = set(domain - self.valsInBoxes[self.spaceToBox(space[0], space[1])])
        return domain

    # gets the unsolved space with the most current constraints
    # returns None if unsolvedSpaces is empty
    def getMostConstrainedUnsolvedSpace(self):
        # 1. Check if unsolvedSpaces is empty
        if len(self.unsolvedSpaces) == 0:
            return None
        # 2. Get the space with the most current constraints
        mostConstrainedSpace = None
        mostConstrainedSpaceConstraints = 0
        for space in self.unsolvedSpaces:
            constraints = self.evaluateSpace(space)
            if len(constraints) > mostConstrainedSpaceConstraints:
                mostConstrainedSpace = space
                mostConstrainedSpaceConstraints = len(constraints)
        return mostConstrainedSpace

class Solver:
    ##########################################
    ####   Constructor
    ##########################################
    def __init__(self):
        pass

    ##########################################
    ####   Solver
    ##########################################

    # recursively selects the most constrained unsolved space and attempts
    # to assign a value to it

    # upon completion, it will leave the board in the solved state (or original
    # state if a solution does not exist)

    # returns True if a solution exists and False if one does not
    def solveBoard(self, board):
        # Takes in a Board object and implements backtracking search with forward checking.
        # Returns a solved board if a solution exists and the original board if a solution does not exist.
        
        # A 9 x 9 board should take about 1 minute to solve.

        # 0. Is the board solved?
        if board.unsolvedSpaces == None:
            return True

        # 1. Get the most constrained unsolved space
        mostConstrainedSpace = board.getMostConstrainedUnsolvedSpace()
        domain = board.evaluateSpace(mostConstrainedSpace)
        for value in domain:
            # 2. Try assigning the value to the space
            board.makeMove(mostConstrainedSpace, value)
            # 3. Is the board solved?
            if self.solveBoard(board):
                return True
            else:
                # 4. If the board is not solved, undo the move
                board.undoMove(mostConstrainedSpace, value)
                return False


if __name__ == "__main__":
    # change this to the input file that you'd like to test
    board = Board('Homeworks/Assignment 2/tests/example.csv')
    s = Solver()
    s.solveBoard(board)
    board.print()
