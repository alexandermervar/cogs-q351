#!/usr/bin/python3

from grade import tests

class Case(tests.Case):
    def __init__(self, filename, solution_filename, mostConstrainedSpaces, allValidMoves):
        self.filename = filename
        self.solution_filename = solution_filename
        self.mostConstrainedSpaces = mostConstrainedSpaces
        self.allValidMoves = allValidMoves
    def represent(self):
        return self.filename

def load_tests(filename, path_stem=None):
    if path_stem:
        filename = os.path.join(path_stem, filename)

    cases = []
    for line in open(filename):
        case = eval(line)
        if path_stem:
            case.filename = os.path.join(path_stem, case.filename)
            case.solution_filename = os.path.join(path_stem, case.solution_filename)
        cases.append(case)
    return cases

if __name__ != '__main__':
    import os
    a2_path = os.path.dirname(__file__)
    tests_file = 'data/test_cases.txt'
    test_cases = load_tests(tests_file, a2_path) # can be modified as you wish

elif __name__ == '__main__': # ONLY USED FOR TEST CASE GENERATION
    import csv
    import itertools

    class Board:
        def __init__(self, filename):
            with open(filename) as csvFile:
                self.n = -1
                reader = csv.reader(csvFile)
                for row in reader:
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
                    else:
                        if len(row) != self.n2:
                            raise Exception('Each row must have the same number of values. (See row ' + str(reader.line_num - 1) + ')')
                    for index, item in enumerate(row):
                        if not item == '':
                            self.board[(reader.line_num-1, index)] = int(item)
                            self.valsInRows[reader.line_num-1].add(int(item))
                            self.valsInCols[index].add(int(item))
                            self.valsInBoxes[self.spaceToBox(reader.line_num-1, index)].add(int(item))
                            self.unsolvedSpaces.remove((reader.line_num-1, index))
        #converts a given row and column to its inner box number
        def spaceToBox(self, row, col):
            return self.n * (row // self.n) + col // self.n
        #returns the number of constraints on a given space (used as helper for the below fx)
        def __valueSpace(self, space):
            r, c = space
            return len(self.valsInRows[r].union(self.valsInCols[c]).union(self.valsInBoxes[self.spaceToBox(r,c)]))
        #gets all spaces with the most current constraints.
        #good for making test cases.
        def getAllConstrainedUnsolvedSpaces(self):
            spaces = sorted(self.unsolvedSpaces, key=self.__valueSpace)
            if not spaces: return spaces

            constrained = [spaces.pop()]
            constraints = self.__valueSpace(constrained[0])
            while spaces:
                space = spaces.pop()
                if self.__valueSpace(space) == constraints:
                    constrained.append(space)
                else:
                    break
            return constrained
        #returns True if the move is not blocked by any constraints
        #and it hasn't already been filled
        #and it exists
        # used as a helper for the below function
        def isValidMove(self,space,val):
            if space in self.board: return False
            r,c = space
            if r >= self.n2 or r < 0: return False
            if c >= self.n2 or c < 0: return False
            return not (val in self.valsInRows[r] or
                        val in self.valsInCols[c] or
                        val in self.valsInBoxes[self.spaceToBox(r,c)])
        #gets all valid moves for all spaces
        #good for making test cases
        def getAllValidMoves(self):
            allValidMoves = {}
            for r in range(self.n2):
                for c in range(self.n2):
                    valid = set()
                    for val in range(1, self.n2+1):
                        if self.isValidMove((r,c), val):
                            valid.add(val)
                    allValidMoves[(r,c)] = valid
            return allValidMoves

    # Here's the good stuff
    print('What file do you want to output test cases to?\nThis file will be automatically located in data/, and is by default called test_cases.txt')
    output_filename = input('Output filename? ')
    if not output_filename.strip(): output_filename = 'test_cases.txt'
    f = open('data/'+output_filename, 'w')

    print('\nWhat board would you like to use for your first test case?\nThis board should be a filename located in both data/tests/ and data/solutions.')
    filename = input('Board filename? ')

    while filename:
        test_fn = 'data/tests/'+filename
        sol_fn = 'data/solutions/'+filename
        board = admin_test_gen.Board(test_fn)
        f.write('Case(%s,%s,%s,%s)\n' % (repr(test_fn), repr(sol_fn), repr(board.getAllConstrainedUnsolvedSpaces()), repr(board.getAllValidMoves())))
        f.flush()

        print('Test case successfully added!\n\nWould you like to add another board? (Blank for no.)')
        filename = input('Board filename? ').strip()
    f.close()
