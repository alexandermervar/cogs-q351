from grade import tests
from . import data


class CycleCorrectness(tests.Criterion):
    summary = 'Cycles appropriately until stability is achieved (depends on update_node)'
    points = 20

    WRONG_ANSWER = 1

    def generateText(self):
        intro = f'After {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ANSWER:
            return intro + f'your nodes are {self.student_value!r}. ({self.expected_value!r} expected.)'
        return tests.Criterion.generateText(self)


class UpdateNodeTester(tests.CriterionTester):
    function_name = 'cycle_until_stable'

    def __init__(self):
        tests.CriterionTester.__init__(self, ['hopfieldnetwork'], [CycleCorrectness], timeout=2)

    def load_modules(self):
        tests.CriterionTester.load_modules(self)

    def run(self, compilation_test=False):
        if compilation_test: upper = 3
        else: upper = len(data.cycle_stable_cases)

        for self.case in data.cycle_stable_cases[:upper]:
            hn = self.hopfieldnetwork.HopfieldNetwork(start_nodes=self.case.start.copy(), target_stable=self.case.target)
            #hn.update_node = update_node
            hn.cycle_until_stable()
            student_value = hn.nodes

            if student_value != self.case.result:
                self.fail_criterion(CycleCorrectness, self.case, problem_code=CycleCorrectness.WRONG_ANSWER, student_value=student_value, expected_value=self.case.result)

if __name__ == '__main__':
    import sys

    sys.path.append('/Users/rowlavel/Documents/Programming/Python/admin/assignments/a6/reference-solutions')

    s = UpdateNodeTester()
    s.test()
    print(s.generateText())
