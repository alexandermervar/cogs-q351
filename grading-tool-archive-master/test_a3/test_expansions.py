#!/usr/bin/python3

import random
import heapq

from grade import tests

from . import data
from .checker import check_a3

### Shared criteria

class MakesChildren(tests.Criterion):
    summary = 'Tries to make child boards for each possible move.'
    points = 2

    MISSING = 1
    NEVER = 2
    def generateText(self):
        if self.problem_code == self.MISSING:
            return f'Does not attempt to make moves {self.missing} on board {self.case.represent()}.'
        if self.problem_code == self.NEVER:
            return f'Does not attempt to make any moves on any board.'
        return tests.Criterion.generateText(self)

class IgnoresBadMoves(tests.Criterion):
    summary = 'Ignores moves that did not successfully produce a child.'
    points = 1
    def generateText(self):
        return f'Attempts to create a State for the None value returned from an invalid move on board {self.case.represent()}.'

class ChildStates(tests.Criterion):
    summary = 'Initializes child states with the appropriate board and depth.'
    points = 5

    NO_STATE = -1
    WRONG_DEPTH = 1
    WRONG_PARENT_STATE = 2
    MULTIPLE_STATES = 3
    def generateText(self):
        if self.problem_code == self.NO_STATE:
            return f'Does not attempt to initialize a State for child {self.board!r} on board {self.case.represent()}.'
        if self.problem_code == self.WRONG_DEPTH:
            return f'Initializes child state with depth {self.depth!r} on board {self.case.represent()} ({self.ref_depth!r} expected).'
        if self.problem_code == self.WRONG_PARENT_STATE:
            return f'Initializes child state with parent {self.parent_state!r} on board {self.case.represent()} ({self.ref_parent_state!r} expected).'
        if self.problem_code == self.MULTIPLE_STATES:
            return f'Initializes multiple states ({self.states!r}) for child {self.board!r} on board {self.case.represent()}.'
        return tests.Criterion.generateText(self)

### fringeExpansion criteria

class Appends(tests.Criterion):
    summary = 'Adds each child state to the end of the fringe.'
    points = 2

    MISSING = 1
    NOT_AT_END = 2
    OVER_ADDED = 3
    NO_STATE = -1
    def generateText(self):
        if self.problem_code == self.NO_STATE:
            return f'Does not attempt to initialize a State for child {self.board!r} on board {self.case.represent()}.'
        if self.problem_code == self.MISSING:
            return f'Never adds initialized child {self.state!r} to the fringe on board {self.case.represent()}.'
        if self.problem_code == self.NOT_AT_END:
            return f'Adds initialized child {self.state!r} to the middle of the fringe on board {self.case.represent()}.'
        if self.problem_code == self.OVER_ADDED:
            return f'Adds initialized child {self.state!r} to the fringe {self.count} times on board {self.case.represent()}.'
        return tests.Criterion.generateText(self)

### informedExpansion criteria

class FValue(tests.Criterion):
    summary = 'Initializes child states with the appropriate f-value given the state\'s board and depth.'
    points = 4

    NOT_CALLED = 1
    WRONG_ARGUMENTS = 2 # unused
    WRONG_DEPTH = 3
    SAVED_WRONG = 4
    NO_STATE = -1
    def generateText(self):
        if self.problem_code == self.NO_STATE:
            return f'Does not attempt to initialize a State for child {self.board!r} on board {self.case.represent()}.'
        if self.problem_code == self.NOT_CALLED:
            return f'Does not call the f_function on child State with {self.board!r} and depth {self.depth!r}, saving f-value {self.fvalue!r} ({self.ref!r} expected), on board {self.case.represent()}.'
        if self.problem_code == self.WRONG_DEPTH:
            return f'Calls the f_function on {self.board!r} with depth {self.call_depth!r}, even though the child State has depth {self.depth!r}, resulting in f-value {self.fvalue!r} ({self.ref!r} expected), on board {self.case.represent()}.'
        if self.problem_code == self.SAVED_WRONG:
            return f'Calls the f_function properly on {self.board!r} with depth {self.depth!r} but saves f-value {self.fvalue!r} ({self.ref!r} expected), on board {self.case.represent()}.'
        return tests.Criterion.generateText(self)

class HeapPushes(tests.Criterion):
    summary = 'Adds each child state to the fringe using heappush.'
    points = 3

    MISSING = 1
    NOT_PUSHED = 2
    OVER_PUSHED = 3
    OVER_ADDED = 4
    NO_STATE = -1
    def generateText(self):
        if self.problem_code == self.NO_STATE:
            return f'Does not attempt to initialize a State for child {self.board!r} on board {self.case.represent()}.'
        if self.problem_code == self.MISSING:
            return f'Never adds initialized child State {self.state!r} to the fringe on board {self.case.represent()}.'
        if self.problem_code == self.NOT_PUSHED:
            return f'Adds initialized child {self.state!r} to the fringe, without properly calling heappush, on board {self.case.represent()}.'
        if self.problem_code == self.OVER_PUSHED:
            return f'Pushes initialized child {self.state!r} to the fringe {self.count} times on board {self.case.represent()}.'
        if self.problem_code == self.OVER_ADDED:
            return f'Adds initialized child {self.state!r} to the fringe {self.count} times on board {self.case.represent()}, even though heappush is only called once.'
        return tests.Criterion.generateText(self)

### Shared Tester

class BaseExpansionTester(tests.CriterionTester):
    def addDiagnosticHooks(self):
        self.slide_blank_calls = []
        self.slide_blank_results = []

        old_slide_blank = self.a3.Board.Board.slide_blank
        if hasattr(old_slide_blank, 'old'):
            old_slide_blank = old_slide_blank.old

        def new_slide_blank(board, move):
            self.slide_blank_calls.append(move)
            result = old_slide_blank(board, move)
            self.slide_blank_results.append(result)
            return result

        new_slide_blank.old = old_slide_blank
        self.a3.Board.Board.slide_blank = new_slide_blank

        self.child_states = []

        old_State__init__ = self.a3.State.State.__init__
        if hasattr(old_State__init__, 'old'):
            old_State__init__ = old_State__init__.old

        def new_State__init__(state, *args, ignore=False, **kwargs):
            if not ignore: self.child_states.append(state)
            old_State__init__(state, *args, **kwargs)

        new_State__init__.old = old_State__init__
        self.a3.State.State.__init__ = new_State__init__
    def load_modules(self):
        tests.CriterionTester.load_modules(self)

        self.addDiagnosticHooks()
    def run(self, compilation_test=False):
        check_a3(self, self.a3)
        if compilation_test:
            cases = data.cases[:2]
        else:
            cases = data.cases
        # because this is a global function, I'm overriding it for as short of a period as possible.
        heapq._heappush = heapq.heappush
        def new_heappush(heap, item):
            self.heap_pushed.append(item)
            try:
                heapq._heappush(heap, item)
            except TypeError:
                pass
        heapq.heappush = new_heappush

        try:
            self.ever_slide_blank_calls = set()

            for case in cases:
                board = self.a3.Board.Board(case.board)

                self.state = self.a3.State.State(board, parent_state=None, depth=random.randint(3,15), fvalue=0, ignore=True)

                other_board = self.a3.Board.Board([[1,2,4],[3,5,7],[6,0,8]]) # some poor student called a BFS iteration and these used to be None!
                self.fringe = [self.a3.State.State(other_board, None, 0, fvalue=random.randint(0, 30), ignore=True) for _ in range(3, 10)]
                self.original_fringe_length = len(self.fringe)

                heapq.heapify(self.fringe)

                self.slide_blank_calls = []
                self.slide_blank_results = []
                self.child_states = []
                self.heap_pushed = []

                self.call_function(self.state, self.fringe)

                self.ever_slide_blank_calls.update(self.slide_blank_calls)

                self.do_tests(case)
            if not self.ever_slide_blank_calls:
                self.fail_criterion(MakesChildren, problem_code=MakesChildren.NEVER)
                self.fail_all_criteria()
        finally:
            heapq.heappush = heapq._heappush
    def call_function(self, state, fringe):
        raise NotImplementedError
    def do_tests(self, case):
        # check that it tried sliding the blank each way
        missing = set()
        for move in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if not move in self.slide_blank_calls:
                missing.add(move)
        if missing:
            self.fail_criterion(MakesChildren, case, problem_code=MakesChildren.MISSING, missing=missing)

        for child_board in self.slide_blank_results:
            found_states = []
            for state in self.child_states:
                if state.board == child_board:
                    found_states.append(state)

            if child_board is not None and not found_states:
                for criterion in [ChildStates, Appends, FValue, HeapPushes]:
                    if criterion in self.criteria:
                        self.fail_criterion(criterion, case, problem_code=criterion.NO_STATE, board=child_board)
            elif child_board is None and found_states:
                self.fail_criterion(IgnoresBadMoves, case)
            if len(found_states) > 1:
                self.fail_criterion(ChildStates, case, problem_code=ChildStates.MULTIPLE_STATES, board=child_board, states=found_states)
            if child_board and found_states:
                self.verify_child_state(case, found_states[0])
    def verify_child_state(self, case, child_state):
        ref_depth = self.state.depth + 1
        ref_parent_state = self.state

        if child_state.depth != ref_depth:
            self.fail_criterion(ChildStates, case, problem_code=ChildStates.WRONG_DEPTH, depth=child_state.depth, ref_depth=ref_depth)
        if child_state.parent_state is not ref_parent_state:
            self.fail_criterion(ChildStates, case, problem_code=ChildStates.WRONG_PARENT_STATE, parent_state=child_state.parent_state, ref_parent_state=ref_parent_state)

class FringeExpansionTester(BaseExpansionTester):
    function_name = "expand_fringe"
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a3'], [MakesChildren, IgnoresBadMoves, ChildStates, Appends])
    def call_function(self, state, fringe):
        self.a3.expand_fringe(state, fringe)
    def verify_child_state(self, case, child_state):
        BaseExpansionTester.verify_child_state(self, case, child_state)
        if not child_state in self.fringe:
            self.fail_criterion(Appends, case, problem_code=Appends.MISSING, state=child_state)
        elif self.fringe.index(child_state) < self.original_fringe_length:
            self.fail_criterion(Appends, case, problem_code=Appends.NOT_AT_END, state=child_state)
        elif self.fringe.count(child_state) > 1:
            self.fail_criterion(Appends, case, problem_code=Appends.OVER_ADDED, state=child_state, count=self.fringe.count(child_state))

class InformedExpansionTester(BaseExpansionTester):
    function_name = "informed_expansion"
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a3'], [MakesChildren, IgnoresBadMoves, ChildStates, FValue, HeapPushes])
    def f_function(self, board, depth, ignore=False):
        import a3
        if not ignore: self.f_function_calls.append((board, depth))
        if type(depth) != int or not isinstance(board, self.a3.Board.Board):
            return hash(str(board) + str(depth)) # way to check what is gotten back

        heuristic = 0
        if len(board.matrix) == 4:
            goal_matrix = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
        else:
            goal_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        for i in range(len(board.matrix)):
            for j in range(len(board.matrix)):
                if goal_matrix[i][j] == 0:
                    continue
                c_i, c_j = board.find_element(goal_matrix[i][j])
                heuristic += abs(i - c_i) + abs(j - c_j)

        return heuristic + depth
    def call_function(self, state, fringe):
        self.f_function_calls = []
        self.a3.informed_expansion(state, fringe, self.f_function)
    def verify_child_state(self, case, child_state):
        BaseExpansionTester.verify_child_state(self, case, child_state)

        ref_fvalue = self.f_function(child_state.board, child_state.depth, ignore=True)
        if child_state.fvalue != ref_fvalue:
            for (o_board, o_depth) in self.f_function_calls:
                if o_board is child_state.board:
                    # the expectation is that they call it with the same depth
                    # they give the child, even if that depth is wrong.
                    if o_depth == child_state.depth:
                        self.fail_criterion(FValue, case, problem_code=FValue.SAVED_WRONG, fvalue=child_state.fvalue, ref=ref_fvalue, board=child_state.board, depth=child_state.depth)
                    else:
                        self.fail_criterion(FValue, case, problem_code=FValue.WRONG_DEPTH,
                            fvalue=child_state.fvalue, ref=ref_fvalue, board=child_state.board,
                            call_depth=o_depth, depth=child_state.depth)
                    break
            else: # if break was not triggered
                self.fail_criterion(FValue, case, problem_code=FValue.NOT_CALLED, fvalue=child_state.fvalue, ref=ref_fvalue, board=child_state.board, depth=child_state.depth)

        count = self.heap_pushed.count(child_state)
        if not child_state in self.fringe:
            self.fail_criterion(HeapPushes, case, problem_code=HeapPushes.MISSING, state=child_state)
        elif count == 0:
            self.fail_criterion(HeapPushes, case, problem_code=HeapPushes.NOT_PUSHED, state=child_state)
        elif count != 1:
            self.fail_criterion(HeapPushes, case, problem_code=HeapPushes.OVER_PUSHED, state=child_state, count=count)
        elif self.fringe.count(child_state) > 1:
            self.fail_criterion(HeapPushes, case, problem_code=HeapPushes.OVER_ADDED, state=child_state, count=self.fringe.count(child_state))

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/b351/admin/sp19/Class Materials/assignments/a1/code')

    s = ValidTester()
    s.test()
    print(s.generateText())
