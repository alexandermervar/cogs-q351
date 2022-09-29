#!/usr/bin/python3

from grade import tests

class DefinesBaseCase(tests.Criterion):
    summary = 'Returns the correct values for base cases.'
    points = 2
    ZERO_WRONG = 1
    ONE_WRONG = 2
    RECURS = 3
    def generateText(self):
        if self.problem_code == self.ZERO_WRONG:
            value = self.details['value']
            return f'Returns {value} for fib(0).'
        elif self.problem_code == self.ONE_WRONG:
            value = self.details['value']
            return f'Returns {value} for fib(1).'
        elif self.problem_code == self.RECURS:
            original_argument, recur_arguments = self.details['original_argument'], self.details['recur_arguments']
            inner = ', '.join(f'fib({arg})' for arg in recur_arguments)
            return f'For fib({original_argument}), recursively calls [{inner}] instead of returning the appropriate base value.'
        else:
            return tests.Criterion.generateText(self)

class CorrectRecursion(tests.Criterion):
    summary = 'Makes the correct recursion calls for input > 1.'
    points = 3
    WRONG_RECURSIONS = 1
    WRONG_ANSWER = 2
    def generateText(self):
        if self.problem_code == self.WRONG_RECURSIONS:
            original_argument, recur_arguments = self.details['original_argument'], self.details['recur_arguments']
            inner = ', '.join(f'fib({arg})' for arg in recur_arguments)
            return f'For fib({original_argument}), recursively calls [{inner}] -- fib({original_argument-1}) and fib({original_argument-2}) are expected.'
        elif self.problem_code == self.WRONG_ANSWER:
            original_argument, student_value, expected_value = self.details['original_argument'], self.details['student_value'], self.details['expected_value']
            return f'For fib({original_argument}), returns {student_value} -- {expected_value} is expected.'
        else:
            return tests.Criterion.generateText(self)

class FibTester(tests.CriterionTester):
    function_name = 'fib'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a1'], [DefinesBaseCase, CorrectRecursion])
    def run(self, compilation_test=False):
        student_fib = self.a1.fib

        memo = {}
        def ref_fib(n):
            if n == 0: return 0
            elif n == 1: return 1
            elif not n in memo: memo[n] = ref_fib(n-1) + ref_fib(n-2)
            return memo[n]

        def diagnostic_fib(n):
            if n < 0:
                got = 0
            else:
                got = ref_fib(n)
            self.recent_calls[n] = got
            return got

        self.a1.fib = diagnostic_fib

        self.recent_calls = {}
        value = student_fib(0)
        if value != 0:
            self.fail_criterion(DefinesBaseCase, problem_code=DefinesBaseCase.ZERO_WRONG, value=value)
        recur_arguments = self.recent_calls.keys()
        if recur_arguments:
            self.fail_criterion(DefinesBaseCase, problem_code=DefinesBaseCase.RECURS, original_argument=0, recur_arguments=recur_arguments)

        self.recent_calls = {}
        value = student_fib(1)
        if value != 1:
            self.fail_criterion(DefinesBaseCase, problem_code=DefinesBaseCase.ONE_WRONG, value=value)
        recur_arguments = self.recent_calls.keys()
        if recur_arguments:
            self.fail_criterion(DefinesBaseCase, problem_code=DefinesBaseCase.RECURS, original_argument=1, recur_arguments=recur_arguments)

        if compilation_test:
            upper = 4
        else:
            upper = 100
        for original_argument in range(2, upper):
            self.recent_calls = {}
            student_value = student_fib(original_argument)
            expected_value = ref_fib(original_argument)
            recur_arguments = self.recent_calls.keys()
            if recur_arguments != {original_argument-1, original_argument-2}:
                self.fail_criterion(CorrectRecursion, problem_code=CorrectRecursion.WRONG_RECURSIONS, original_argument=original_argument, recur_arguments=recur_arguments)
            if student_value != expected_value:
                self.fail_criterion(CorrectRecursion, problem_code=CorrectRecursion.WRONG_ANSWER, original_argument=original_argument, student_value=student_value, expected_value=expected_value)

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/b351/admin/sp19/Class Materials/assignments/a1/code')

    s = FibTester()
    s.test()
    print(s.generateText())
