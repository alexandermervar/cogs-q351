from grade import tests
from . import data
import numpy as np


class Correctness(tests.Criterion):
    summary = 'Returns the correct weights after applying the back propagation algorithm.'
    points = 20

    WRONG_ANSWER = 1

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ANSWER:
            return intro + f'you return {self.student_value!r}. ({self.expected_value!r} expected.)'

        return tests.Criterion.generateText(self)


class BackPropTester(tests.CriterionTester):
    function_name = 'back_propagation'

    def __init__(self):
        tests.CriterionTester.__init__(self, ['backpropagation'], [Correctness], timeout=2)

    def load_modules(self):
        tests.CriterionTester.load_modules(self)

    def run(self, compilation_test=False):
        if compilation_test: upper = 3
        else: upper = len(data.backprop_cases)

        mlp = self.backpropagation.MLP(nn_architecture=[
            {"layer_size": 13, "activation": "none"},  # input layer
            {"layer_size": 6, "activation": "sigmoid"},  # hidden layer
            {"layer_size": 3, "activation": "softmax"}  # output layer
        ], seed=9234875)

        for self.case in data.backprop_cases[:upper]:
            student_value = mlp.back_propagation(np.array(self.case.targets), [np.array(activation) for activation in self.case.activations])['W1'].tolist()
            if student_value != self.case.weights:
                self.fail_criterion(Correctness, self.case, problem_code=Correctness.WRONG_ANSWER, input=(self.case.targets, self.case.activations), student_value=student_value, expected_value=self.case.weights)


if __name__ == '__main__':
    import sys

    sys.path.append('/Users/rowlavel/Documents/Programming/Python/admin/assignments/a6/reference-solutions')

    s = BackPropTester()
    s.test()
    print(s.generateText())
