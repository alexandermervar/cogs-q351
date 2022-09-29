from grade import tests
from . import data


class UpdatesCorrectness(tests.Criterion):
    summary = 'Updates the node when it\'s value should change'
    points = 20

    WRONG_ANSWER = 1

    def generateText(self):
        intro = f'After {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ANSWER:
            return intro + f'your nodes are {self.student_value!r}. ({self.expected_value!r} expected.)'
        return tests.Criterion.generateText(self)

class ReturnsCorrectly(tests.Criterion):
    summary = 'Returns True iff the node has changed'
    points = 10

    UPDATED_INAPPROPRIATELY_TO_NEGATIVE = 1
    UPDATED_INAPPROPRIATELY_TO_POSITIVE = 2

    def generateText(self):
        intro = f'After {self.case.represent()} is called, '
        if self.problem_code == self.UPDATED_INAPPROPRIATELY_TO_NEGATIVE:
            return intro + f'your nodes changed from {self.expected_value} to {self.student_value!r}. Yet your function returned False)'
        if self.problem_code == self.UPDATED_INAPPROPRIATELY_TO_POSITIVE:
            return intro + f'your nodes started as {self.expected_value} and ended as {self.student_value!r}. Yet your function returned True)'
        return tests.Criterion.generateText(self)


class UpdateNodeTester(tests.CriterionTester):
    function_name = 'update_node'

    def __init__(self):
        tests.CriterionTester.__init__(self, ['hopfieldnetwork'], [UpdatesCorrectness, ReturnsCorrectly], timeout=2)

    def load_modules(self):
        tests.CriterionTester.load_modules(self)

    def run(self, compilation_test=False):
        if compilation_test: upper = 3
        else: upper = len(data.update_node_cases)

        for self.case in data.update_node_cases[:upper]:
            hn = self.hopfieldnetwork.HopfieldNetwork(start_nodes=self.case.start.copy(), target_stable=self.case.target)
            student_did_update = hn.update_node(self.case.node)
            student_value = hn.nodes

            if student_value != self.case.result:
                self.fail_criterion(UpdatesCorrectness, self.case, problem_code=UpdatesCorrectness.WRONG_ANSWER, input=self.case.node, student_value=student_value, expected_value=self.case.result)
                
            if student_did_update != (self.case.start[self.case.node] != hn.nodes[self.case.node]):
                if student_did_update:
                    self.fail_criterion(ReturnsCorrectly, self.case, problem_code=ReturnsCorrectly.UPDATED_INAPPROPRIATELY_TO_POSITIVE, input=self.case.node, student_value=student_value, expected_value=self.case.start)
                else:
                    self.fail_criterion(ReturnsCorrectly, self.case, problem_code=ReturnsCorrectly.UPDATED_INAPPROPRIATELY_TO_NEGATIVE, input=self.case.node, student_value=student_value, expected_value=self.case.start)

if __name__ == '__main__':
    import sys

    sys.path.append('/Users/rowlavel/Documents/Programming/Python/admin/assignments/a6/reference-solutions')

    s = UpdateNodeTester()
    s.test()
    print(s.generateText())