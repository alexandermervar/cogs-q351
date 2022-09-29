#!/usr/bin/python3

import random
import heapq
import types
import inspect

from grade import tests

from . import data
from .checker import check_a3


class UCSCorrectness(tests.Criterion):
    summary = 'Returns the appropriate f-value for a Uniform Cost Search.'
    points = 5
    def generateText(self):
        return f'ucs_f_function({self.board!r}, {self.depth!r}) returns {self.returned!r} -- {self.expected!r} expected.'


class AStarReturnsFunction(tests.Criterion):
    summary = 'Returns a function that accepts a board and a depth and returns an f-value.'
    points = 3
    neverRedact = True

    NOT_A_FUNCTION = 1
    WRONG_N_ARGUMENTS = 2
    CALLS_HEURISTIC = 3
    def generateText(self):
        if self.problem_code == self.NOT_A_FUNCTION:
            return f'The f-function factory returns {self.returned!r} -- function expected.'
        if self.problem_code == self.WRONG_N_ARGUMENTS:
            return f'The f-function factory returns a function that takes arguments {self.signature} -- f-functions take arguments (board, depth).'
        if self.problem_code == self.CALLS_HEURISTIC:
            return f'The f-function factory calls the heuristic directly -- only the f-function itself should call the heuristic.'
        return tests.Criterion.generateText(self)

class AStarAppliesHeuristic(tests.Criterion):
    summary = 'The f-function returned applies the given heuristic to the board provided at run-time and the given goal board.'
    points = 5

    DOES_NOT_CALL = 1
    CALLS_WRONG_FUNCTION = 2
    WRONG_ARGUMENTS = 3
    def generateText(self):
        if self.problem_code == self.DOES_NOT_CALL:
            return f'f_function({self.board!r}, {self.depth!r}) does not call any heuristic function.'
        if self.problem_code == self.CALLS_WRONG_FUNCTION:
            return f'f_function({self.board!r}, {self.depth!r}) calls the particular heuristic function {self.function} instead of the heuristic passed to the f-function factory.'
        if self.problem_code == self.WRONG_ARGUMENTS:
            return f'f_function({self.board!r}, {self.depth!r}) passes arguments {self.arguments!r} to the heuristic function -- {self.expected!r} expected.'
        return tests.Criterion.generateText(self)

class AStarCorrectness(tests.Criterion):
    summary = 'The f-function returned produces the appropriate f-value for an A* search.'
    points = 2

    INCORRECT = 1
    DEPTH_MISSING = 2
    HEURISTIC_MISSING = 3
    def generateText(self):
        if self.problem_code == self.INCORRECT:
            return f'f_function({self.board!r}, {self.depth!r}) returns {self.returned!r} -- {self.expected!r} expected.'
        if self.problem_code == self.DEPTH_MISSING:
            return f'f_function({self.board!r}, {self.depth!r}) returns {self.returned!r} -- {self.expected!r} expected. Make sure you\'re including the relevant depth.'
        if self.problem_code == self.HEURISTIC_MISSING:
            return f'f_function({self.board!r}, {self.depth!r}) returns {self.returned!r} -- {self.expected!r} expected. Make sure you\'re including the relevant heuristic value.'
        return tests.Criterion.generateText(self)

### Shared Tester

class UCSFFunctionTester(tests.CriterionTester):
    function_name = "ucs_f_function"
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a3'], [UCSCorrectness])
    def run(self, compilation_test=False):
        check_a3(self, self.a3)
        if compilation_test:
            cases = data.cases[:2]
        else:
            cases = data.cases
        boards = [self.a3.Board.Board(case.board) for case in cases]
        for board in boards:
            depth = random.randint(0, 100)
            fvalue = self.a3.ucs_f_function(board, depth)
            expected = depth
            if fvalue != expected:
                self.fail_criterion(UCSCorrectness, board=board, depth=depth,
                    returned=fvalue, expected=depth)

class AStarFFunctionFactoryTester(tests.CriterionTester):
    function_name = "a_star_f_function_factory"
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a3'], [AStarReturnsFunction, AStarAppliesHeuristic, AStarCorrectness])
    def run(self, compilation_test=False):
        check_a3(self, self.a3)
        if compilation_test:
            cases = data.cases[1:3]
        else:
            cases = data.cases[1:]
        self.heuristic_call = None
        self.heuristic_value = None
        self.called_wrong = None

        def do_heuristic(current_board, goal_board):
            total = 0
            if len(current_board) == 4:
                goal_matrix = self.a3.Board.Board([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]])
            else:
                goal_matrix = goal_board.matrix
            for goal_r in range(len(current_board)):
                for goal_c in range(len(current_board)):
                    val = goal_matrix[goal_r][goal_c]
                    if val == 0:
                        continue
                    current_r, current_c = current_board.find_element(val)
                    total += abs(goal_r - current_r) + abs(goal_c - current_c)
            return total
        def test_heuristic(current_board, goal_board):
            self.heuristic_call = (current_board, goal_board)
            try:
                total = do_heuristic(current_board, goal_board)
            except:
                total = 0
            self.heuristic_value = total
            return total
        def manhattan_distance(current_board, goal_board):
            self.called_wrong = 'manhattan_distance'
            return test_heuristic(current_board, goal_board)
        self.a3.manhattan_distance = manhattan_distance
        def my_heuristic(current_board, goal_board):
            self.called_wrong = 'my_heuristic'
            return test_heuristic(current_board, goal_board)
        self.a3.my_heuristic = my_heuristic

        goal_board = self.a3.Board.Board([[1, 2, 3], [4, 5, 6], [7, 8, 0]])

        f_function = self.a3.a_star_f_function_factory(test_heuristic, goal_board)
        if self.heuristic_call is not None:
            self.fail_criterion(AStarReturnsFunction, problem_code=AStarReturnsFunction.CALLS_HEURISTIC)

        if type(f_function) != types.FunctionType:
            self.fail_criterion(AStarReturnsFunction, problem_code=AStarReturnsFunction.NOT_A_FUNCTION, returned=f_function)
            self.fail_all_criteria()
            return

        sig = inspect.signature(f_function)

        if len(sig.parameters) != 2:
            self.fail_criterion(AStarReturnsFunction, problem_code=AStarReturnsFunction.WRONG_N_ARGUMENTS, signature=sig)
            self.fail_all_criteria()
            return

        boards = [self.a3.Board.Board(case.board) for case in cases[1:]]
        for board in boards:
            depth = random.randint(0, 100)

            self.heuristic_call = None
            self.heuristic_value = None
            self.called_wrong = None

            fvalue = f_function(board, depth)

            if self.heuristic_value is None:
                self.heuristic_value = do_heuristic(board, goal_board)

            if self.called_wrong is not None:
                self.fail_criterion(AStarAppliesHeuristic, problem_code=AStarAppliesHeuristic.CALLS_WRONG_FUNCTION,
                    board=board, depth=depth, function=self.called_wrong)

            if self.heuristic_call is None:
                self.fail_criterion(AStarAppliesHeuristic, problem_code=AStarAppliesHeuristic.DOES_NOT_CALL, board=board, depth=depth)
            elif self.heuristic_call != (board, goal_board):
                self.fail_criterion(AStarAppliesHeuristic, problem_code=AStarAppliesHeuristic.WRONG_ARGUMENTS,
                    board=board, depth=depth, arguments=self.heuristic_call, expected=(board, goal_board))

            expected = depth + self.heuristic_value
            if fvalue != expected:
                if fvalue == depth:
                    self.fail_criterion(AStarCorrectness, problem_code=AStarCorrectness.HEURISTIC_MISSING,
                        board=board, depth=depth, returned=fvalue, expected=expected)
                elif fvalue == self.heuristic_value:
                    self.fail_criterion(AStarCorrectness, problem_code=AStarCorrectness.DEPTH_MISSING,
                        board=board, depth=depth, returned=fvalue, expected=expected)
                else:
                    self.fail_criterion(AStarCorrectness, problem_code=AStarCorrectness.INCORRECT,
                        board=board, depth=depth, returned=fvalue, expected=expected)
