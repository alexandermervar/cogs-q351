#!/usr/bin/python3

from grade import tests
from . import data
from .checker import check_a5

import math
import builtins
from itertools import permutations

class Correctness(tests.Criterion):
    summary = 'Returns the euclidean distance between the two given points.'
    points = 10

    WRONG_ANSWER = 1

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ANSWER:
            point1, point2 = self.input
            return intro + f'you return {self.student_value!r}. ({self.expected_value!r} expected.)'

        return tests.Criterion.generateText(self)

class DistanceTester(tests.CriterionTester):
    function_name = 'calc_euclidean_distance'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a5'], [Correctness], timeout=2)
    def load_modules(self):
        tests.CriterionTester.load_modules(self)

    def run(self, compilation_test=False):
        check_a5(self, self.a5)
        if compilation_test: upper = 3
        else: upper = len(data.distance_cases)

        for self.case in data.distance_cases[:upper]:
            student_value = self.a5.KNN_Classifier(3).calc_euclidean_distance(self.case.point1, self.case.point2)
            if student_value != self.case.distance:
                self.fail_criterion(Correctness, self.case, problem_code=Correctness.WRONG_ANSWER, input=(self.case.point1, self.case.point2), student_value=student_value, expected_value=self.case.distance)