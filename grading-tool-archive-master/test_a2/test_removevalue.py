#!/usr/bin/python3

import random

from grade import tests
from . import data
from .checker import checked_board

class ClearsSpace(tests.Criterion):
    summary = 'Deletes space from the board.'
    points = 3
    SAME_VALUE = 1
    ZERO_VALUE = 2
    WRONG_VALUE = 3
    def generateText(self):
        if self.problem_code == self.SAME_VALUE:
            space, value, student_value = self.details['space'], self.details['value'], self.details['student_value']
            board = self.case.represent()
            return 'Does not change value %s in space %s after undoMove(%s, %s) is called on board %s.' \
                % (str(student_value), str(space), str(space), str(value), board)
        elif self.problem_code == self.ZERO_VALUE:
            space, value, student_value = self.details['space'], self.details['value'], self.details['student_value']
            board = self.case.represent()
            return 'Leaves value %s in space %s after undoMove(%s, %s) is called on board %s.' \
                % (str(student_value), str(space), str(space), str(value), board)
        elif self.problem_code == self.WRONG_VALUE:
            space, value, student_value = self.details['space'], self.details['value'], self.details['student_value']
            board = self.case.represent()
            return 'Places value %s in space %s after undoMove(%s, %s) is called on board %s.' \
                % (str(student_value), str(space), str(space), str(value), board)
        else:
            return tests.Criterion.generateText(self)

class FreesValue(tests.Criterion):
    summary = 'Records that value no longer appears in the row, column, and box of space.'
    points = 5
    MISSED_ROW = 1
    MISSED_COL = 2
    MISSED_BOX = 3
    def generateText(self):
        if self.problem_code == self.MISSED_ROW:
            space, value, student_vals = self.details['space'], self.details['value'], self.details['student_vals']
            board = self.case.represent()
            return 'Does not remove %s from the set %s of values in %s\'s row when undoMove(%s, %s) is called on board %s.' \
                % (str(value), str(student_vals), str(space), str(space), str(value), board)
        elif self.problem_code == self.MISSED_COL:
            space, value, student_vals = self.details['space'], self.details['value'], self.details['student_vals']
            board = self.case.represent()
            return 'Does not remove %s from the set %s of values in %s\'s column when undoMove(%s, %s) is called on board %s.' \
                % (str(value), str(student_vals), str(space), str(space), str(value), board)
        elif self.problem_code == self.MISSED_BOX:
            space, value, student_vals = self.details['space'], self.details['value'], self.details['student_vals']
            board = self.case.represent()
            return 'Does not remove %s from the set %s of values in %s\'s box when undoMove(%s, %s) is called on board %s.' \
                % (str(value), str(student_vals), str(space), str(space), str(value), board)
        else:
            return tests.Criterion.generateText(self)

class AddsToUnsolved(tests.Criterion):
    summary = 'Adds space to the set of unsolved spaces.'
    points = 2
    def generateText(self):
        space, value = self.details['space'], self.details['value']
        board = self.case.represent()
        return 'Does not add space %s to unsolved after undoMove(%s, %s) is called on board %s.' \
            % (str(space), str(space), str(value), str(board))

class RemoveValueTester(tests.CriterionTester):
    function_name = 'undoMove'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a2'], [ClearsSpace, FreesValue, AddsToUnsolved])
    def run(self, compilation_test=False):
        Board = checked_board(self, self.a2.Board)

        if compilation_test:
            test_cases = data.test_cases[:2]
        else:
            test_cases = data.test_cases
        for case in test_cases:
            board = Board(case.filename)
            picks = list(board.board.keys())
            del board

            random.shuffle(picks)
            picks = picks[:5]

            for space in picks:
                board = Board(case.filename)
                value = board.board[space]
                board.undoMove(space, value)
                if space in board.board:
                    if board.board[space] == value:
                        self.fail_criterion(ClearsSpace, case, problem_code=ClearsSpace.SAME_VALUE, space=space, value=value, student_value=board.board[space])
                    elif not board.board[space]:
                        self.fail_criterion(ClearsSpace, case, problem_code=ClearsSpace.ZERO_VALUE, space=space, value=value, student_value=board.board[space])
                    else:
                        self.fail_criterion(ClearsSpace, case, problem_code=ClearsSpace.WRONG_VALUE, space=space, value=value, student_value=board.board[space])
                r, c = space
                b = board.spaceToBox(r, c)
                if value in board.valsInRows[r]:
                    self.fail_criterion(FreesValue, case, problem_code=FreesValue.MISSED_ROW, space=space, value=value, student_vals=board.valsInRows[r])
                if value in board.valsInCols[c]:
                    self.fail_criterion(FreesValue, case, problem_code=FreesValue.MISSED_COL, space=space, value=value, student_vals=board.valsInCols[c])
                if value in board.valsInBoxes[b]:
                    self.fail_criterion(FreesValue, case, problem_code=FreesValue.MISSED_BOX, space=space, value=value, student_vals=board.valsInBoxes[b])
                if not space in board.unsolvedSpaces:
                    self.fail_criterion(AddsToUnsolved, case, space=space, value=value)

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/Downloads')

    s = RemoveValueTester()
    s.test()
    print(s.generateText())
