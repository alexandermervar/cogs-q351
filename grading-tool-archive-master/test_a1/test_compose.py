#!/usr/bin/python3

import types
import random

from grade import tests

# Possible criteria:
# - Check that the return type of student's compose is types.FunctionType
# - Proper ordering of composition (i.e. fo(fi(x)), not fi(fo(x))
# - compose(fo, fi)(value) gives proper result (see pseudo-code below)

class ReturnsLambda(tests.Criterion):
    summary = 'Returns a lambda function.'
    points = 5
    NAMED_FUNCTION = 1
    RANDOM_OBJECT = 2
    def generateText(self):
        if self.problem_code == self.NAMED_FUNCTION:
            return f'Returns a function defined with name {self.name!r} instead of a lambda function.'
        elif self.problem_code == self.RANDOM_OBJECT:
            return f'compose returns {type(self.object)} -- function expected.'

class AppliesEachFunction(tests.Criterion):
    summary = 'The returned function invokes both f_outer and f_inner.'
    points = 3
    MISSING_OUTER = 1
    MISSING_INNER = 2
    MISSING_BOTH = 3
    CALLS_INNER = 4
    CALLS_OUTER = 5
    WRONG_ARGUMENT = 6
    def generateText(self):
        if self.problem_code == self.CALLS_INNER:
            return f'compose calls f_inner during its own execution -- should instead return a lambda function that calls it.'
        elif self.problem_code == self.CALLS_OUTER:
            return f'compose calls f_outer during its own execution -- should instead return a lambda function that calls it.'
        elif self.problem_code == self.WRONG_ARGUMENT:
            return f'{self.function} called on {self.argument!r} rather than the argument supplied to the lambda function.'
        elif self.problem_code == self.MISSING_OUTER:
            return 'Never applies f_outer to the output of f_inner.'
        elif self.problem_code == self.MISSING_INNER:
            return 'Applies f_outer directly to the input instead of first applying f_inner.'
        elif self.problem_code == self.MISSING_BOTH:
            return 'Neither applies f_inner nor f_outer to the input.'
        else:
            return tests.Criterion.generateText(self)

class CorrectOrder(tests.Criterion):
    summary = 'The returned function applies f_inner before f_outer.'
    points = 4
    MISSING_FUNCTION = 1
    FLIPPED = 2
    def generateText(self):
        if self.problem_code == self.MISSING_FUNCTION:
            return 'Does not apply both f_outer and f_inner to the input.'
        elif self.problem_code == self.FLIPPED:
            return 'Applies f_outer to the input before f_inner.'
        else:
            return tests.Criterion.generateText(self)

class Correctness(tests.Criterion):
    summary = 'When the returned function is applied to any input, it returns the result of composing f_outer with f_inner.'
    points = 3
    neverRedact = True
    ERROR = 1
    def generateText(self):
        if self.problem_code == self.ERROR:
            error_text = self.representError(self.error)
            return f'When the function returned by compose({self.f_text}) is applied to {self.input!r},\nan uncaught exception is produced:\n'+error_text
        return f'When the function returned by compose({self.f_text}) is applied to {self.input!r},\n{self.value!r} is returned -- {self.expected!r} expected.'


class ComposeTester(tests.CriterionTester):
    function_name = 'compose'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a1'], [ReturnsLambda, AppliesEachFunction, CorrectOrder, Correctness])
    def run(self, compilation_test=False):
        student_compose = self.a1.compose

        if compilation_test:
            upper = 1
        else:
            upper = 5
        fo_fi_number_to_number = [
                (lambda y: y+3, lambda x: 2*x),
                (lambda y: int(y)+1, lambda x: x ** .5)
                ][:upper]
        fo_fi_number_to_number_text = [
                "lambda y: y+3, lambda x: 2*x",
                "lambda y: int(y)+1, lambda x: x ** .5"
                ][:upper]
        fo_fi_string_to_string = [
                (lambda y: 'The android said: '+y, lambda x: x.upper()),
                (lambda x: 'length of ' + x + ' is ' + str(len(x)), lambda y: y + '!'*4),
                (lambda y: y.replace('Professor', 'Doctor'), lambda x: x.replace('Saúl', 'The Great Professor'))
                ][:upper]
        fo_fi_string_to_string_text = [
                "lambda y: 'The android said: '+y, lambda x: x.upper()",
                "lambda x: 'length of ' + x + ' is ' + str(len(x)), lambda y: y + '!'*4",
                "lambda y: y.replace('Professor', 'Doctor'), lambda x: x.replace('Saúl', 'The Great Professor')"
                ][:upper]
        numbers = [42, 420, 101, 55, 9000, 355][:upper]
        strings = ["Saúl Blanco welcomes you to B351",
                    "We are glad you are here!",
                    "Thank you for participating in our game",
                    "Why doesn't Saúl take a seat over there?"][:upper]
        random.shuffle(strings)

        def diag_first(i):
            if self.called and self.called[0] == -1:
                self.fail_criterion(AppliesEachFunction, problem_code=AppliesEachFunction.CALLS_INNER)
            self.called.append('first')
            if type(i) != int:
                self.fail_criterion(AppliesEachFunction, problem_code=AppliesEachFunction.WRONG_ARGUMENT, function='f_inner', argument=i)
                return 1
            return i+1
        def diag_second(i):
            if self.called and self.called[0] == -1:
                self.fail_criterion(AppliesEachFunction, problem_code=AppliesEachFunction.CALLS_OUTER)
            self.called.append('second')
            if type(i) != int:
                self.fail_criterion(AppliesEachFunction, problem_code=AppliesEachFunction.WRONG_ARGUMENT, function='f_outer', argument=i)
                return 1
            return i+1

        self.called = [-1]
        diag_composition = student_compose(diag_second, diag_first)
        if not type(diag_composition) == types.FunctionType:
            self.fail_criterion(ReturnsLambda, problem_code=ReturnsLambda.RANDOM_OBJECT, object=diag_composition)
            self.fail_all_criteria()
            return
        if not diag_composition.__name__ == '<lambda>':
            self.fail_criterion(ReturnsLambda, problem_code=ReturnsLambda.NAMED_FUNCTION, name=diag_composition.__name__)
        self.called = []
        diag_composition(0)
        missing = {'first', 'second'} - set(self.called)
        if missing == {'first', 'second'}:
            self.fail_criterion(AppliesEachFunction, problem_code=AppliesEachFunction.MISSING_BOTH)
        elif 'first' in missing:
            self.fail_criterion(AppliesEachFunction, problem_code=AppliesEachFunction.MISSING_INNER)
        elif 'second' in missing:
            self.fail_criterion(AppliesEachFunction, problem_code=AppliesEachFunction.MISSING_OUTER)

        if missing:
            self.fail_criterion(CorrectOrder, problem_code=CorrectOrder.MISSING_FUNCTION)
        elif self.called != ['first', 'second']:
            self.fail_criterion(CorrectOrder, problem_code=CorrectOrder.FLIPPED)

        def ref_compose(fo, fi):
            return lambda user_input: fo(fi(user_input))

        for fo_fi, f_text in zip(fo_fi_string_to_string, fo_fi_string_to_string_text):
            student_composition = student_compose(*fo_fi)
            ref_composition = ref_compose(*fo_fi)
            if not type(student_composition) == types.FunctionType:
                self.fail_criterion(ReturnsLambda, problem_code=ReturnsLambda.RANDOM_OBJECT, object=student_composition)
                self.fail_all_criteria()
            for string in strings:
                try:
                    value = student_composition(string)
                except Exception as err:
                    self.fail_criterion(Correctness, problem_code=Correctness.ERROR, error=err, f_text=f_text, input=string)
                else:
                    expected = ref_composition(string)
                    if value != expected:
                        self.fail_criterion(Correctness, f_text=f_text, input=string, value=value, expected=expected)

        for fo_fi, f_text in zip(fo_fi_number_to_number, fo_fi_number_to_number_text):
            student_composition = student_compose(*fo_fi)
            ref_composition = ref_compose(*fo_fi)
            if not type(student_composition) == types.FunctionType:
                self.fail_criterion(ReturnsLambda, problem_code=ReturnsLambda.RANDOM_OBJECT, object=student_composition)
                self.fail_all_criteria()
            for number in numbers:
                try:
                    value = student_composition(number)
                except Exception as err:
                    self.fail_criterion(Correctness, problem_code=Correctness.ERROR, error=err, f_text=f_text, input=number)
                else:
                    expected = ref_composition(number)
                    if value != expected:
                        self.fail_criterion(Correctness, f_text=f_text, input=number, value=value, expected=expected)

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/b351/admin/sp19/Class Materials/assignments/a1/code')

    s = ComposeTester()
    s.test()
    print(s.generateText())
