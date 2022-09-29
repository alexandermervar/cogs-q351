#!/usr/bin/python3

from grade import tests
from . import data
from .checker import check_a5

import math
import builtins
from itertools import permutations

class Correctness(tests.Criterion):
    summary = 'Returns one of the most frequent labels.'
    points = 8

    WRONG_ANSWER = 1
    RETURNED_NONE = 2

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ANSWER:
            return intro + f'you return {self.student_value!r} which is not in {self.expected_value!r}.)'
        elif self.problem_code == self.RETURNED_NONE:
            return intro + f'you return None, output must be one of {self.input!r}.)'

        return tests.Criterion.generateText(self)

class Consistency(tests.Criterion):
    summary = 'Always returns the same value given the same top_k_labels list.'
    points = 2

    WRONG_ANSWER = 1

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ANSWER:
            return intro + f'you return {self.student_value!r}. ({self.expected_value!r} expected.)'

        return tests.Criterion.generateText(self)

class PickLabelTester(tests.CriterionTester):
    function_name = 'get_top_label'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a5'], [Correctness, Consistency], timeout=2)
    def load_modules(self):
        tests.CriterionTester.load_modules(self)

    def run(self, compilation_test=False):
        check_a5(self, self.a5)
        if compilation_test: upper = 3
        else: upper = len(data.pick_label_cases)

        for self.case in data.pick_label_cases[:upper]:
            previous_run = {}
            student_value = self.a5.KNN_Classifier(3).get_top_label(self.case.labels)
            if student_value not in self.case.valid:
                self.fail_criterion(Correctness, self.case, problem_code=Correctness.WRONG_ANSWER, input=self.case.labels, student_value=student_value, expected_value=self.case.valid)
            previous_run[self.case] = student_value
        
        for self.case in data.pick_label_cases:
            student_value = self.a5.KNN_Classifier(3).get_top_label(self.case.labels)
            if self.case in previous_run and student_value != previous_run[self.case]:
                self.fail_criterion(Consistency, self.case, problem_code=Correctness.WRONG_ANSWER, input=self.case.labels, student_value=student_value, expected_value=previous_run[self.case])