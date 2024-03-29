from grade import tests
from . import data


class Correctness(tests.Criterion):
    summary = 'Returns the Perceptrons prediction based on an input.'
    points = 15

    WRONG_ANSWER = 1

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ANSWER:
            return intro + f'you return {self.student_value!r}. ({self.expected_value!r} expected.)'

        return tests.Criterion.generateText(self)


class TrainSampleTester(tests.CriterionTester):
    function_name = 'train_sample'

    def __init__(self):
        tests.CriterionTester.__init__(self, ['perceptron'], [Correctness], timeout=2)

    def load_modules(self):
        tests.CriterionTester.load_modules(self)

    def run(self, compilation_test=False):
        if compilation_test: upper = 3
        else: upper = len(data.train_sample_cases)

        for self.case in data.train_sample_cases[:upper]:
            pcn = self.perceptron.Perceptron([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 1, 1, 1])
            pcn.weights = self.case.start_weight
            student_value = pcn.train_sample(self.case.input, self.case.target)
            if student_value != self.case.update:
                self.fail_criterion(Correctness, self.case, problem_code=Correctness.WRONG_ANSWER, input=self.case.input, student_value=student_value, expected_value=self.case.update)


if __name__ == '__main__':
    import sys

    sys.path.append('/Users/rowlavel/Documents/Programming/Python/admin/assignments/a6/reference-solutions')

    s = TrainSampleTester()
    s.test()
    print(s.generateText())