#!/usr/bin/python3

from grade import tests
from . import data
from .checker import checked_board

class ChecksInDomain(tests.Criterion):
    summary = 'Returns False when the space is not on the board.'
    points = 2
    ERROR = 1
    def generateText(self):
        board = self.case.represent()
        if self.problem_code == self.ERROR:
            err, space, value = self.details['error'], self.details['space'], self.details['value']
            error_text = self.representError(err)
            return f'Produces an uncaught exception when isValidMove({space}, {value}) is called on {board}.\n\n'+error_text
        else:
            student_result, space, value = self.details['student_result'], self.details['space'], self.details['value']
            return f'Returns {student_result} when isValidMove({space}, {value}) is called on {board}.'

class ChecksEmpty(tests.Criterion):
    summary = 'Returns False when the space is not empty.'
    points = 2
    def generateText(self):
        board = self.case.represent()
        student_result, space, value, current_value = self.details['student_result'], self.details['space'], self.details['value'], self.details['current_value']
        return f'Returns {student_result} when isValidMove({space}, {value}) is called on {board}, even though {space} is currently assigned to {current_value}.'

class ChecksConstraints(tests.Criterion):
    summary = 'Checks that the value has not already occurred in the column, row, and box of space.'
    points = 5
    MISSED_ROW = 1
    MISSED_COL = 2
    MISSED_BOX = 3
    def generateText(self):
        board = self.case.represent()
        student_result, space, value, current_vals = self.details['student_result'], self.details['space'], self.details['value'], self.details['current_vals']
        place = {self.MISSED_ROW: 'row', self.MISSED_COL: 'column', self.MISSED_BOX: 'box'}[self.problem_code]
        return f'Returns {student_result} when isValidMove({space}, {value}) is called on {board}, even though {space} has values {current_vals} in the same {place}.'

class TrueOtherwise(tests.Criterion):
    summary = 'Returns True whenever the assignment is valid.'
    points = 1
    def generateText(self):
        board = self.case.represent()
        student_result, space, value, actual_result = self.details['student_result'], self.details['space'], self.details['value'], self.details['actual_result']
        return f'Returns {student_result} when isValidMove({space}, {value}) is called on {board}. (Correct answer: {actual_result})'

#class IsCorrect(tests.Criterion):
#    summary = 'Returns True whenever the assignment is valid, and False when it is not.'
#    points = 10
#    def generateText(self):
#        board = self.case.represent()
#        student_result, space, value, actual_result = self.details['student_result'], self.details['space'], self.details['value'], self.details['actual_result']
#        return f'Returns {student_result} when isValidMove({space}, {value}) is called on {board}. (Correct answer: {actual_result})'

class IsValidMoveTester(tests.CriterionTester):
    function_name = 'isValidMove'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a2'], [ChecksInDomain, ChecksEmpty, ChecksConstraints, TrueOtherwise])
    def run(self, compilation_test=False):
        Board = checked_board(self, self.a2.Board)

        if compilation_test:
            test_cases = data.test_cases[:2]
        else:
            test_cases = data.test_cases
        for case in test_cases:
            board = Board(case.filename)

            for row in range(-1, board.n2+1):
                for col in range(-1, board.n2+1):
                    space = (row, col)
                    box = board.spaceToBox(row, col)
                    for value in range(1, board.n2+1):
                        try:
                            student_result = board.isValidMove(space, value)
                        except Exception as err:
                            if not space in case.allValidMoves:
                                self.fail_criterion(ChecksInDomain, case, problem_code=ChecksInDomain.ERROR, space=space, value=value, error=err)
                                continue
                            else:
                                raise err
                        actual_result = (space in case.allValidMoves and value in case.allValidMoves[space])
                        if not student_result is actual_result:
                            if actual_result is True:
                                self.fail_criterion(TrueOtherwise, case, space=space, value=value, student_result=student_result, actual_result=actual_result)
                            else:
                                if not space in case.allValidMoves:
                                    self.fail_criterion(ChecksInDomain, case, space=space, value=value, student_result=student_result, actual_result=actual_result)
                                elif space in board.board:
                                    self.fail_criterion(ChecksEmpty, case, space=space, value=value, current_value=board.board[space], student_result=student_result, actual_result=actual_result)
                                elif value in board.valsInRows[row]:
                                    self.fail_criterion(ChecksConstraints, case, problem_code=ChecksConstraints.MISSED_ROW, space=space, value=value, current_vals=board.valsInRows[row], student_result=student_result, actual_result=actual_result)
                                elif value in board.valsInCols[col]:
                                    self.fail_criterion(ChecksConstraints, case, problem_code=ChecksConstraints.MISSED_COL, space=space, value=value, current_vals=board.valsInCols[col], student_result=student_result, actual_result=actual_result)
                                elif value in board.valsInBoxes[box]:
                                    self.fail_criterion(ChecksConstraints, case, problem_code=ChecksConstraints.MISSED_BOX, space=space, value=value, current_vals=board.valsInBoxes[box], student_result=student_result, actual_result=actual_result)

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/Downloads')

    s = IsValidMoveTester()
    s.test()
    print(s.generateText())
