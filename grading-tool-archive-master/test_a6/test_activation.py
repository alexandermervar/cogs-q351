from grade import tests
from . import data


class Correctness(tests.Criterion):
    summary = 'Returns the threshold activation of a value.'
    points = 2

    WRONG_ANSWER = 1

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ANSWER:
            return intro + f'you return {self.student_value!r}. ({self.expected_value!r} expected.)'

        return tests.Criterion.generateText(self)


class ActivationTester(tests.CriterionTester):
    function_name = 'activation'

    def __init__(self):
        tests.CriterionTester.__init__(self, ['perceptron'], [Correctness], timeout=2)

    def load_modules(self):
        tests.CriterionTester.load_modules(self)

    def run(self, compilation_test=False):
        if compilation_test: upper = 3
        else: upper = len(data.activation_cases)

        for self.case in data.activation_cases[:upper]:
            student_value = self.perceptron.Perceptron([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 1, 1, 1]).activation(self.case.n)
            if student_value != self.case.activation:
                self.fail_criterion(Correctness, self.case, problem_code=Correctness.WRONG_ANSWER, input=self.case.n, student_value=student_value, expected_value=self.case.activation)


if __name__ == '__main__':
    import sys

    sys.path.append('/Users/rowlavel/Documents/Programming/Python/admin/assignments/a6/reference-solutions')

    s = ActivationTester()
    s.test()
    print(s.generateText())