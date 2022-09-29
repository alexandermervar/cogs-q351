#!/usr/bin/python3

import random
import types

from grade import tests

class AppliesToEach(tests.Criterion):
    summary = 'Applies the function exactly once to each element of the iterable.'
    points = 5
    def generateText(self):
        return f'yieldAllValid({self.expected}, toHex) applies toHex to {self.applied} -- {self.expected} expected.'

class CatchesValueError(tests.Criterion):
    summary = 'Catches any ValueErrors that result from applying the function.'
    points = 5
    MISSES_VALUE_ERROR = 1
    DOES_NOT_APPLY = 2
    def generateText(self):
        if self.problem_code == self.MISSES_VALUE_ERROR:
            return f'yieldAllValid({self.input}, toHex) produces an uncaught ValueError.'
        elif self.problem_code == self.DOES_NOT_APPLY:
            return f'yieldAllValid({self.input}, toHex) does not apply toHex to each member of {self.input}.'
        else:
            return tests.Criterion.generateText(self)

class Specificity(tests.Criterion):
    summary = 'Does NOT catch any other errors.'
    points = 5
    DOES_NOT_APPLY = 1
    def generateText(self):
        if self.problem_code == self.DOES_NOT_APPLY:
            return f'yieldAllValid({self.input}, toHex) does not apply toHex to each member of {self.input}.'
        return f'yieldAllValid({self.input}, toHex) suppresses a RuntimeError.'

class Correctness(tests.Criterion):
    summary = 'Yields the result of applying the function to each valid input.'
    points = 5
    MISSES_VALUE_ERROR = 1
    def generateText(self):
        if self.problem_code == self.MISSES_VALUE_ERROR:
            return f'yieldAllValid({self.input}, toHex) produces an uncaught ValueError.'
        return f'The generator returned for {self.input} evaluates to {self.value} -- {self.expected} expected.'

class ValidTester(tests.CriterionTester):
    function_name = 'yieldAllValid'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a1'], [AppliesToEach, CatchesValueError, Specificity, Correctness])
    def run(self, compilation_test=False):
        student_valid = self.a1.yieldAllValid

        def toHex(value, minbytes=0, maxbytes=-1):
            if value == 'freebsd':
                raise RuntimeError('FreeBSD is not supported.')
            if type(value) != int:
                raise ValueError('Integer expected.')
            hexValues = '0123456789abcdef'
            hexString = ''
            while (value or minbytes > 0) and maxbytes != 0:
                hexString = hexValues[value % 16] + hexString
                value //= 16
                minbytes -= .5
                maxbytes -= .5
            return hexString

        def diag_toHex(val):
            self.applied.append(val)
            return toHex(val)

        def ref_valid(iterable, function):
            for value in iterable:
                try: yield function(value)
                except ValueError: pass

        def evaluate(gen):
            if not hasattr(gen, '__iter__'):
                return None
            else:
                return list(gen)

        if compilation_test:
            upper = 3
        else:
            upper = 12

        for length in range(2,upper):
            l = [random.randint(1,32) for _ in range(length)]
            self.applied = []
            try:
                evaluate(student_valid(l, diag_toHex))
            except Exception:
                pass
            if self.applied != l:
                self.fail_criterion(AppliesToEach, expected=list(l), applied=self.applied)

            for i in range(2): l.insert(random.randint(0,length), random.choice(['blue','hello','test','Saúl']))

            self.applied = []
            expected = list(ref_valid(l, toHex))
            try:
                got = evaluate(student_valid(l, diag_toHex))
            except ValueError:
                self.fail_criterion(CatchesValueError, problem_code=CatchesValueError.MISSES_VALUE_ERROR, input=l)
                self.fail_criterion(Correctness, problem_code=Correctness.MISSES_VALUE_ERROR, input=l)
            else:
                if set(self.applied) < set(l):
                    self.fail_criterion(AppliesToEach, expected=list(l), applied=self.applied)
                    self.fail_criterion(CatchesValueError, problem_code=CatchesValueError.DOES_NOT_APPLY, input=l)
                if expected != got:
                    self.fail_criterion(Correctness, input=l, value=got, expected=expected)

            self.applied = []
            l = [random.randint(1,32) for _ in range(length)]
            l.insert(0, 'freebsd')
            try:
                got = evaluate(student_valid(l, diag_toHex))
            except RuntimeError: pass
            else:
                if set(self.applied) >= set(l):
                    self.fail_criterion(Specificity, input=l)
                else:
                    self.fail_criterion(Specificity, problem_code=Specificity.DOES_NOT_APPLY, input=l)

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/b351/admin/sp19/Class Materials/assignments/a1/code')

    s = ValidTester()
    s.test()
    print(s.generateText())
