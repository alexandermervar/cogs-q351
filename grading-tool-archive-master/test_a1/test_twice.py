#!/usr/bin/python3

import random
import types

from grade import tests

class Iterates(tests.Criterion):
    summary = 'Uses a for loop over the iterable.'
    points = 3
    RETURNS_INPUT = 1
    def generateText(self):
        if self.problem_code == self.RETURNS_INPUT:
            return 'Your function simply returns the input provided to it.'
        return 'Your function does not use a for loop over the iterable.'

class UsesYield(tests.Criterion):
    summary = 'Uses the yield statement at least once in this for loop.'
    points = 7
    RETURNS_LIST = 1
    YIELDS_AFTER = 2
    RETURNS_INPUT = 3
    def generateText(self):
        if self.problem_code == self.RETURNS_LIST:
            return f'Your function returns {self.value} instead of using the yield statement.'
        elif self.problem_code == self.YIELDS_AFTER:
            return 'Your function does not begin to yield results until after it iterates over the iterable.'
        elif self.problem_code == self.RETURNS_INPUT:
            return 'Your function simply returns the input provided to it.'
        else:
            return tests.Criterion.generateText(self)

class Correctness(tests.Criterion):
    summary = 'Yields each element of the list exactly twice.'
    points = 5
    def generateText(self):
        return f'The generator returned for {self.input} evaluates to {self.value} -- {self.expected} expected.'

class TwiceTester(tests.CriterionTester):
    function_name = 'yieldTwice'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a1'], [Iterates, UsesYield, Correctness])
    def run(self, compilation_test=False):
        student_twice = self.a1.yieldTwice

        def diag_generator(length):
            self.iteration_started = True
            for _ in range(length):
                value = random.randint(-20,20)
                self.seen.append(value)
                self.expected.append(value)
                self.expected.append(value)
                yield value
            self.iteration_over = True

        if compilation_test:
            upper = 5
        else:
            upper = 50
        for length in range(3,upper):
            gen = diag_generator(length)

            self.iteration_started = False
            self.iteration_over = False
            self.expected = []
            self.seen = []

            student_gen = student_twice(gen)
            if student_gen is gen:
                self.fail_criterion(Iterates, problem_code=Iterates.RETURNS_INPUT)
                self.fail_criterion(UsesYield, problem_code=UsesYield.RETURNS_INPUT)

            if not hasattr(student_gen, '__iter__'):
                raise ValueError("Student function does not return an iterable.")

            if type(student_gen) != types.GeneratorType:
                self.fail_criterion(UsesYield, problem_code=UsesYield.RETURNS_LIST, value=student_gen)
            got = []
            for i in student_gen:
                if got == [] and self.iteration_over and type(student_gen) == types.GeneratorType:
                    self.fail_criterion(UsesYield, problem_code=UsesYield.YIELDS_AFTER)
                got.append(i)
            if not self.iteration_started:
                self.fail_criterion(Iterates)

            list(gen)
            if got != self.expected:
                self.fail_criterion(Correctness, input=self.seen, value=got, expected=self.expected)

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/b351/admin/sp19/Class Materials/assignments/a1/code')

    s = TwiceTester()
    s.test()
    print(s.generateText())
