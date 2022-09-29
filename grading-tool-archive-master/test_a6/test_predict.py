from grade import tests
from . import data


class Correctness(tests.Criterion):
    summary = 'Returns the Perceptrons prediction based on an input.'
    points = 5

    WRONG_ANSWER = 1

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ANSWER:
            return intro + f'you return {self.student_value!r}. ({self.expected_value!r} expected.)'

        return tests.Criterion.generateText(self)


class PredictTester(tests.CriterionTester):
    function_name = 'predict'

    def __init__(self):
        tests.CriterionTester.__init__(self, ['perceptron'], [Correctness], timeout=2)

    def load_modules(self):
        tests.CriterionTester.load_modules(self)

    def run(self, compilation_test=False):
        if compilation_test: upper = 3
        else: upper = len(data.predict_cases)

        for self.case in data.predict_cases[:upper]:
            pcn = self.perceptron.Perceptron([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 1, 1, 1])
            pcn.weights = self.case.weights
            student_value = pcn.predict(self.case.input)
            if student_value != self.case.prediction:
                self.fail_criterion(Correctness, self.case, problem_code=Correctness.WRONG_ANSWER, input=self.case.input, student_value=student_value, expected_value=self.case.prediction)


if __name__ == '__main__':
    import sys

    sys.path.append('/Users/rowlavel/Documents/Programming/Python/admin/assignments/a6/reference-solutions')

    s = PredictTester()
    s.test()
    print(s.generateText())