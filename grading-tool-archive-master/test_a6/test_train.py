from grade import tests
from . import data


class Correctness(tests.Criterion):
    summary = 'Returns the correct weights after training the Perceptron.'
    points = 10

    WRONG_ANSWER = 1

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ANSWER:
            return intro + f'you return {self.student_value!r}. ({self.expected_value!r} expected.)'

        return tests.Criterion.generateText(self)

class CorrectTrainLogic(tests.Criterion):
    summary = 'Correct code structure for training.'
    points = 5

    BAD_CALL = 2

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.BAD_CALL:
            return intro + f'you return {self.student_value!r}. ({self.expected_value!r} expected.)'

        return tests.Criterion.generateText(self)

class TrainTester(tests.CriterionTester):
    function_name = 'train'

    def __init__(self):
        tests.CriterionTester.__init__(self, ['perceptron'], [Correctness, CorrectTrainLogic], timeout=2)

    def load_modules(self):
        tests.CriterionTester.load_modules(self)

    def run(self, compilation_test=False):
        if compilation_test: upper = 3
        else: upper = len(data.train_cases)

        class Diagnostic_Classifier(self.perceptron.Perceptron):
            def train_sample(student, input, target):
                # feed the point through the perceptron
                output = student.dot(input, student.weights)
                # update the weights if necessary
                if target == 1 and output < 0:
                    student.weights = student.add(student.weights, input)
                    return True
                if target == 0 and output >= 0:
                    student.weights = student.sub(student.weights, input)
                    return True
                return False

        for self.case in data.train_cases[:upper]:
            student_classifier = Diagnostic_Classifier([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 1, 1, 1])
            student_classifier.weights = self.case.start_weight
            pcn = self.perceptron.Perceptron([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 1, 1, 1])
            pcn.weights = self.case.start_weight
            student_value_diag = student_classifier.train()
            student_value = pcn.train()
            if student_value != self.case.weights:
                self.fail_criterion(Correctness, self.case, problem_code=Correctness.WRONG_ANSWER, input=(), student_value=student_value, expected_value=self.case.weights)
            if student_value_diag != self.case.weights:
                self.fail_criterion(CorrectTrainLogic, self.case, problem_code=CorrectTrainLogic.BAD_CALL, input=(), student_value=student_value_diag, expected_value=self.case.weights)


if __name__ == '__main__':
    import sys

    sys.path.append('/Users/rowlavel/Documents/Programming/Python/admin/assignments/a6/reference-solutions')

    s = TrainTester()
    s.test()
    print(s.generateText())