#!/usr/bin/python3

import random

from grade import tests
from . import data
from .checker import checked_board

class AssignsSpace(tests.Criterion):
    summary = 'Assigns space to value in the board.'
    points = 3
    NOT_IN_BOARD = 1
    WRONG_VALUE = 2
    def generateText(self):
        if self.problem_code == self.NOT_IN_BOARD:
            space, value = self.details['space'], self.details['value']
            board = self.case.represent()
            return 'Leaves space %s empty after makeMove(%s, %s) is called on board %s.' \
                % (str(space), str(space), str(value), board)
        elif self.problem_code == self.WRONG_VALUE:
            space, value, student_value = self.details['space'], self.details['value'], self.details['student_value']
            board = self.case.represent()
            return 'Places value %s in space %s after makeMove(%s, %s) is called on board %s.' \
                % (str(student_value), str(space), str(space), str(value), board)
        else:
            return tests.Criterion.generateText(self)

class ReservesValue(tests.Criterion):
    summary = 'Records that value has already occurred in the row, column, and box of space.'
    points = 5
    MISSED_ROW = 1
    MISSED_COL = 2
    MISSED_BOX = 3
    def generateText(self):
        if self.problem_code == self.MISSED_ROW:
            space, value, student_vals = self.details['space'], self.details['value'], self.details['student_vals']
            board = self.case.represent()
            return 'Does not add %s to the set %s of values in %s\'s row when makeMove(%s, %s) is called on board %s.' \
                % (str(value), str(student_vals), str(space), str(space), str(value), board)
        elif self.problem_code == self.MISSED_COL:
            space, value, student_vals = self.details['space'], self.details['value'], self.details['student_vals']
            board = self.case.represent()
            return 'Does not add %s to the set %s of values in %s\'s column when makeMove(%s, %s) is called on board %s.' \
                % (str(value), str(student_vals), str(space), str(space), str(value), board)
        elif self.problem_code == self.MISSED_BOX:
            space, value, student_vals = self.details['space'], self.details['value'], self.details['student_vals']
            board = self.case.represent()
            return 'Does not add %s to the set %s of values in %s\'s box when makeMove(%s, %s) is called on board %s.' \
                % (str(value), str(student_vals), str(space), str(space), str(value), board)
        else:
            return tests.Criterion.generateText(self)

class RemovesFromUnsolved(tests.Criterion):
    summary = 'Removes space from the set of unsolved spaces.'
    points = 2
    def generateText(self):
        space, value = self.details['space'], self.details['value']
        board = self.case.represent()
        return 'Does not remove space %s from unsolved after makeMove(%s, %s) is called on board %s.' \
            % (str(space), str(space), str(value), str(board))

class PlaceValueTester(tests.CriterionTester):
    function_name = 'makeMove'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a2'], [AssignsSpace, ReservesValue, RemovesFromUnsolved])
    def run(self, compilation_test=False):
        Board = checked_board(self, self.a2.Board)

        if compilation_test:
            test_cases = data.test_cases[:2]
        else:
            test_cases = data.test_cases
        for case in test_cases:
            board = Board(case.filename)
            if not board.unsolvedSpaces: continue
            picks = list(board.unsolvedSpaces)
            del board

            random.shuffle(picks)
            picks = picks[:5]

            for space in picks:
                board = Board(case.filename)
                if not case.allValidMoves[space]: continue
                value = list(case.allValidMoves[space])[0]
                board.makeMove(space, value)
                if not space in board.board:
                    self.fail_criterion(AssignsSpace, case, problem_code=AssignsSpace.NOT_IN_BOARD, space=space, value=value)
                elif board.board[space] != value:
                    self.fail_criterion(AssignsSpace, case, problem_code=AssignsSpace.WRONG_VALUE, space=space, value=value, student_value=board.board[space])
                r, c = space
                b = board.spaceToBox(r, c)
                if not value in board.valsInRows[r]:
                    self.fail_criterion(ReservesValue, case, problem_code=ReservesValue.MISSED_ROW, space=space, value=value, student_vals=board.valsInRows[r])
                if not value in board.valsInCols[c]:
                    self.fail_criterion(ReservesValue, case, problem_code=ReservesValue.MISSED_COL, space=space, value=value, student_vals=board.valsInCols[c])
                if not value in board.valsInBoxes[b]:
                    self.fail_criterion(ReservesValue, case, problem_code=ReservesValue.MISSED_BOX, space=space, value=value, student_vals=board.valsInBoxes[b])
                if space in board.unsolvedSpaces:
                    self.fail_criterion(RemovesFromUnsolved, case, space=space, value=value)

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/Downloads')

    s = PlaceValueTester()
    s.test()
    print(s.generateText())
