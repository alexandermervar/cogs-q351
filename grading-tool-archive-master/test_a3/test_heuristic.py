#!/usr/bin/python3

import random
import heapq
import numbers

from grade import tests

from . import data
from .checker import check_a3

### Shared criteria

#     calls manhattan distance
#     reimplements manhattan distance
#     is zero

class ValidHeuristic(tests.Criterion):
    summary = 'Returns numerical values; does not call Manhattan distance; does not reimplement Manhattan distance; is not a constant.'
    points = 0
    neverRedact = True

    NON_NUMERICAL = 1
    CALLS_MANHATTAN = 2
    IS_MANHATTAN = 3
    IS_ZERO = 4
    IS_CONSTANT = 5
    def generateText(self):
        if self.problem_code == self.NON_NUMERICAL:
            return f'my_heuristic({self.board!r}, {self.goal!r}) returns a non-numerical value {self.value!r}.'
        if self.problem_code == self.CALLS_MANHATTAN:
            return f'my_heuristic unexpectedly calls the Manhattan distance function.'
        if self.problem_code == self.IS_MANHATTAN:
            return f'my_heuristic always returns the same estimate as the Manhattan distance heuristic.'
        if self.problem_code == self.IS_ZERO:
            return f'my_heuristic always returns 0.'
        if self.problem_code == self.IS_CONSTANT:
            return f'my_heuristic always returns the constant value {self.value!r}.'
        return tests.Criterion.generateText(self)

class AboveZero(tests.Criterion):
    summary = 'Never returns a value below zero.'
    points = 1
    def generateText(self):
        return f'my_heuristic({self.board!r}, {self.goal!r}) returns {self.value!r}.'

class Admissible(tests.Criterion):
    summary = 'Is admissible (never overestimates distance to goal) with respect to the standard goal board.'
    points = 2
    def generateText(self):
        return f'my_heuristic({self.board!r}, {self.goal!r}) returns an estimate of {self.value!r}. The actual distance to the goal is {self.distance!r}.'

class AlwaysAdmissible(tests.Criterion):
    summary = 'Is admissible given other potential goal boards.'
    points = 2
    def generateText(self):
        return f'my_heuristic({self.board!r}, {self.goal!r}) returns an estimate of {self.value!r}. The actual distance to the goal is {self.distance!r}.'

class Improvement(tests.Criterion):
    summary = 'Returns a value that is closer to the actual distance than (greater than) the Manhattan distance, on average.'
    points = 10
    neverRedact = True

    AVERAGE_IMPROVEMENT = 1
    INADMISSIBLE = 2
    def generateText(self):
        if self.problem_code == self.INADMISSIBLE:
            return f'Your heuristic is not eligible for points on this criterion because it is inadmissible.'
        if self.problem_code == self.AVERAGE_IMPROVEMENT:
            if self.improvement > 0:
                return f'Over our test suite of boards within 30 steps of the goal, your heuristic\'s estimates are {self.improvement:.2f} steps closer to the actual distance on average.'
            else:
                return f'Over our test suite of boards within 30 steps of the goal, your heuristic\'s estimates are {-self.improvement:.2f} lower than Manhattan distance\'s on average.'
        return tests.Criterion.generateText(self)

### Shared Tester

class HeuristicTester(tests.CriterionTester):
    function_name = "my_heuristic"
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a3'], [ValidHeuristic, AboveZero, Admissible, AlwaysAdmissible, Improvement])
    def score_improvement(self, average_improvement):
        # -11: 0/10
        # -2: 5/10
        #  0: 8/10
        #  2: 10/10
        #  5: 15/10
        if average_improvement < -2.5:
            top = -2.5
            bottom = -11
            top_score = 5
            bottom_score = 0
        elif average_improvement < 0:
            top = 0
            bottom = -2.5
            top_score = 8
            bottom_score = 5
        elif average_improvement < 2:
            top = 2
            bottom = 0
            top_score = 10
            bottom_score = 8
        else:
            top = 5 # actual maximum ~= 5.5
            bottom = 2
            top_score = 15
            bottom_score = 10
        score = ((average_improvement - bottom) / (top-bottom)) * (top_score-bottom_score) + bottom_score
        return round(score)
    def run(self, compilation_test=False):
        check_a3(self, self.a3)
        if compilation_test:
            cases = data.cases[:3]
        else:
            cases = data.cases
        def they_done_goofed(current_board, goal_board):
            self.fail_criterion(ValidHeuristic, problem_code=ValidHeuristic.CALLS_MANHATTAN)
            self.fail_all_criteria()
            return 0
        self.a3.manhattan_distance = they_done_goofed

        ever_nonzero = False
        ever_notmanhattan = False
        values = set()

        main_goal = self.a3.Board.Board([[1, 2, 3], [4, 5, 6], [7, 8, 0]])

        net_difference = 0
        n_cases = 0

        for case in cases:
            if len(case.board) == 4:
                main_goal = self.a3.Board.Board([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]])
            else:
                main_goal = self.a3.Board.Board([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
            # members: board, distance, manhattan, alt_goal, alt_distance, alt_manhattan
            board = self.a3.Board.Board(case.board)
            alt_goal = self.a3.Board.Board(case.alt_goal)
            for (goal, distance, manhattan) in [(main_goal, case.distance, case.manhattan), (alt_goal, case.alt_distance, case.alt_manhattan)]:
                if goal is alt_goal: continue
                h = self.a3.my_heuristic(board, goal)

                if not isinstance(h, numbers.Number):
                    ever_nonzero = True
                    ever_notmanhattan = True
                    self.fail_criterion(ValidHeuristic, problem_code=ValidHeuristic.NON_NUMERICAL, board=board, goal=goal, value=h)
                    self.fail_all_criteria()
                    continue

                values.add(h)

                if h < 0:
                    self.fail_criterion(AboveZero, board=board, goal=goal, value=h)
                if h > distance:
                    if goal is main_goal:
                        self.fail_criterion(Admissible, board=board, goal=goal, value=h, distance=distance)
                        self.fail_criterion(Improvement, problem_code=Improvement.INADMISSIBLE)
                    else:
                        self.fail_criterion(AlwaysAdmissible, board=board, goal=goal, value=h, distance=distance)

                if h != 0:
                    ever_nonzero = True
                if h != manhattan:
                    ever_notmanhattan = True

                net_difference += h
                net_difference -= manhattan
                n_cases += 1

        if not ever_nonzero:
            self.fail_criterion(ValidHeuristic, problem_code=ValidHeuristic.IS_ZERO)
            self.fail_all_criteria()
        if not ever_notmanhattan:
            self.fail_criterion(ValidHeuristic, problem_code=ValidHeuristic.IS_MANHATTAN)
            self.fail_all_criteria()
        if len(values) == 1:
            self.fail_criterion(ValidHeuristic, problem_code=ValidHeuristic.IS_CONSTANT, value=values.pop())
            self.fail_all_criteria()

        if Improvement in self.criteria_passed: # don't give them points if inadmissible
            average_improvement = net_difference / n_cases
            self.fail_criterion(Improvement, problem_code=Improvement.AVERAGE_IMPROVEMENT, improvement=average_improvement) # this gives them the feedback whether they passed or not
            self.set_score(Improvement, self.score_improvement(average_improvement))

            if average_improvement > 0:
                self.pass_criterion(Improvement)
