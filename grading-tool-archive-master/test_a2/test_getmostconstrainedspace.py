#!/usr/bin/python3

import random
import cgi

from grade import tests
from . import data
from .checker import checked_board

class NoneWhenAllSolved(tests.Criterion):
    summary = 'Returns None when the board has been fully solved.'
    points = 2
    ERROR = 1
    def generateText(self):
        board = self.case.represent()
        if self.problem_code == self.ERROR:
            err = self.details['error']
            error_text = self.representError(err)
            return f'Produces an uncaught exception on already solved board {board}.\n\n'+error_text
        else:
            student_result = self.details['student_result']
            return f'Does not return None on already solved board {board} (returns {repr(student_result)}).'

class EvaluatesUnsolvedSpaces(tests.Criterion):
    summary = 'Runs the evaluation function on unsolved spaces.'
    points = 2
    OTHER_SPACE = 1
    MISSES_BEST = 2
    NONE_UNSOLVED = 3
    INDETERMINATE = 4
    def generateText(self):
        if self.problem_code == self.INDETERMINATE:
            return 'You don\'t seem to be using the evaluateSpace function, so we can\'t give you partial credit for this criterion.\nIf your code passes the correctness test, you will also receive this credit.'
        board = self.case.represent()
        if self.problem_code == self.OTHER_SPACE:
            space = self.details['space']
            return f'The evaluateSpace function is called on {space}, even though it is not one of the unsolved spaces, on board {board}.'
        elif self.problem_code == self.MISSES_BEST:
            correct_results = self.details['correct_results']
            return f'The evaluateSpace function is not called on any of the most constrained unsolved spaces {correct_results} on board {board}.'
        elif self.problem_code == self.NONE_UNSOLVED:
            return f'The evaluateSpace function is not called on any of the unsolved spaces on board {board}.'
        else:
            return tests.Criterion.generateText(self)


class Optimizes(tests.Criterion):
    summary = 'Either minimizes or maximizes with respect to the evaluation function.'
    points = 5
    NEITHER = 1
    BOTH = 2
    INDETERMINATE = 3
    def generateText(self):
        if self.problem_code == self.INDETERMINATE:
            return 'You don\'t seem to be using the evaluateSpace function, so we can\'t give you partial credit for this criterion.\nIf your code passes the correctness test, you will also receive this credit.'
        board = self.case.represent()
        maxes, mins, student_result = self.details['maxes'], self.details['mins'], self.details['student_result']
        if self.problem_code == self.NEITHER:
            return f'Returns {student_result} on board {board}, which is neither one of the spaces {maxes} with the highest scores nor one of the spaces {mins} with the lowest scores.'
        elif self.problem_code == self.BOTH:
            previous = self.details['previous']
            if previous == 'min':
                return f'Minimized on previous boards, but returns one of the spaces {maxes} with the highest scores on board {board}.'
            elif previous == 'max':
                return f'Maximized on previous boards, but returns one of the spaces {mins} with the lowest scores on board {board}.'
        return tests.Criterion.generateText(self)

class IsStable(tests.Criterion):
    summary = 'Always returns the same value given the same board.'
    points = 1
    def generateText(self):
        board = self.case.represent()
        first_result, second_result = self.details['first_result'], self.details['second_result']
        return f'Returns both {first_result} and {second_result} on board {board}.'

class IsCorrect(tests.Criterion):
    summary = 'Returns one of the most constrained spaces for every unsolved board.'
    points = 10
    def generateText(self):
        board = self.case.represent()
        student_result, correct_results = self.details['student_result'], self.details['correct_results']
        return f'Returns {student_result} on board {board}. Any of the following would be correct results: {correct_results}'

class GetMostConstrainedSpaceTester(tests.CriterionTester):
    function_name = 'getMostConstrainedUnsolvedSpace'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a2'], [NoneWhenAllSolved, EvaluatesUnsolvedSpaces, Optimizes, IsStable, IsCorrect])
    def makeTestBoard(self):
        StudentBoard = checked_board(self, self.a2.Board)
        class TestBoard(StudentBoard):
            def __init__(self, filename):
                self._evaluationResults = {}
                StudentBoard.__init__(self, filename)
            def evaluateSpace(self, space):
                result = StudentBoard.evaluateSpace(self, space)
                self._evaluationResults[space] = result
                return result
        return TestBoard

    def run(self, compilation_test=False):
        Board = self.makeTestBoard()
        uses_evaluation = False
        optimization_behavior = None
        ever_incorrect = False

        if compilation_test:
            test_cases = data.test_cases[:2]
        else:
            test_cases = data.test_cases
        for case in test_cases:
            board = Board(case.filename)

            try:
                student_result = board.getMostConstrainedUnsolvedSpace()
            except Exception as err:
                if not board.unsolvedSpaces:
                    self.fail_criterion(NoneWhenAllSolved, case, problem_code=NoneWhenAllSolved.ERROR, error=err)
                    continue
                else:
                    raise err

            if board._evaluationResults:
                uses_evaluation = True

            if not board.unsolvedSpaces:
                if not student_result is None:
                    self.fail_criterion(NoneWhenAllSolved, case, student_result=student_result)
            elif not student_result in case.mostConstrainedSpaces:
                self.fail_criterion(IsCorrect, case, student_result=student_result, correct_results=case.mostConstrainedSpaces)
                if uses_evaluation:
                    evaluated_spaces = board._evaluationResults.keys()
                    if not set(case.mostConstrainedSpaces).intersection(evaluated_spaces):
                        self.fail_criterion(EvaluatesUnsolvedSpaces, case, problem_code=EvaluatesUnsolvedSpaces.MISSES_BEST, correct_results=case.mostConstrainedSpaces)
                    if not set(board.unsolvedSpaces).intersection(evaluated_spaces):
                        self.fail_criterion(EvaluatesUnsolvedSpaces, case, problem_code=EvaluatesUnsolvedSpaces.NONE_UNSOLVED)
                ever_incorrect = True

                if uses_evaluation: # only grade this if they get something wrong!
                    for space in board._evaluationResults:
                        if not space in board.unsolvedSpaces:
                            self.fail_criterion(EvaluatesUnsolvedSpaces, case, problem_code=EvaluatesUnsolvedSpaces.OTHER_SPACE, space=space)
                    maxes = {space for space in board._evaluationResults
                        if board._evaluationResults[space] == max(board._evaluationResults.values())}
                    mins = {space for space in board._evaluationResults
                        if board._evaluationResults[space] == min(board._evaluationResults.values())}
                    if not maxes == mins:
                        if student_result in maxes:
                            if optimization_behavior == 'min':
                                self.fail_criterion(Optimizes, case, problem_code=Optimizes.BOTH, student_result=student_result, previous='min', maxes=maxes, mins=mins)
                            optimization_behavior = 'max'
                        elif student_result in mins:
                            if optimization_behavior == 'max':
                                self.fail_criterion(Optimizes, case, problem_code=Optimizes.BOTH, student_result=student_result, previous='max', maxes=maxes, mins=mins)
                            optimization_behavior = 'min'
                        else:
                            self.fail_criterion(Optimizes, case, problem_code=Optimizes.NEITHER, student_result=student_result, maxes=maxes, mins=mins)

            for _ in range(5):
                new_result = board.getMostConstrainedUnsolvedSpace()
                if not new_result == student_result:
                    self.fail_criterion(IsStable, case, first_result=student_result, second_result=new_result)
        if ever_incorrect and not uses_evaluation:
            self.fail_criterion(EvaluatesUnsolvedSpaces, problem_code=EvaluatesUnsolvedSpaces.INDETERMINATE)
            self.fail_criterion(Optimizes, problem_code=Optimizes.INDETERMINATE)

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/Downloads')

    s = GetMostConstrainedSpaceTester()
    s.test()
    print(s.generateText())
