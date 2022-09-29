#!/usr/bin/python3

import random
import heapq

from grade import tests

from . import data
from .checker import check_a3

### Shared criteria

# If multiple items are popped, fail everything.
# The tests are based on the popped item if exactly one item is popped,
# and the first item of the fringe if none are popped.

class SingleIteration(tests.Criterion):
    summary = 'Only performs a single search iteration.'
    neverRedact = True
    points = 0

    def generateText(self):
        return 'Pops more than one item from the fringe. (All criteria failed.)'

class StopIfEmpty(tests.Criterion):
    summary = 'If the fringe is empty, returns STOP.'
    points = 1

    WRONG_RETVAL = 1
    ERROR = 2
    def generateText(self):
        if self.problem_code == self.ERROR:
            return 'Search function produces an error when called on an empty fringe:\n\n'+self.representError(self.error)
        elif self.problem_code == self.WRONG_RETVAL:
            return f'Search function returns {self.returned!r} when called on an empty fringe: STOP ({self.stopcode!r}) expected.'
        else:
            return tests.Criterion.generateText(self)

class SeeksGoal(tests.Criterion):
    summary = 'Immediately returns the current state if its board is the goal board.'
    points = 2

    EXPANDS_ANYWAY = 1
    WRONG_RETVAL = 2
    def generateText(self):
        if self.problem_code == self.EXPANDS_ANYWAY:
            return f'Search function expands {self.expanded} after encountering the goal state {self.current_state!r}.'
        elif self.problem_code == self.WRONG_RETVAL:
            return f'Search function returns {self.returned!r} when considering the goal state: current state ({self.current_state!r}) expected.'
        else:
            return tests.Criterion.generateText(self)

class ExpandsFringe(tests.Criterion):
    summary = 'Otherwise, expands the fringe appropriately and returns CONTINUE.'
    points = 2

    DOESNT_EXPAND = 1
    WRONG_EXPANSION = 2
    MULTIPLE_TIMES = 3
    WRONG_RETVAL = 4
    WRONG_F_FUNCTION = 5
    def generateText(self):
        if self.problem_code == self.DOESNT_EXPAND:
            return f'Search function doesn\'t expand the fringe when considering the eligible current state {self.current_state!r}.'
        if self.problem_code == self.WRONG_EXPANSION:
            return f'Search function calls {self.attempted} ({self.correct} expected).'
        if self.problem_code == self.MULTIPLE_TIMES:
            return f'Search function expands state {self.current_state!r} multiple times.'
        if self.problem_code == self.WRONG_RETVAL:
            return f'Search function returns {self.returned!r} after expanding the fringe: CONTINUE ({self.contcode!r}) expected.'
        if self.problem_code == self.WRONG_F_FUNCTION:
            return f'Search function expands {self.current_state!r} with the particular f-function {self.attempted!r} instead of the one passed to informed_search.'
        return tests.Criterion.generateText(self)

### BFS criteria

class ConsidersFirstState(tests.Criterion):
    summary = 'Pops the first element out of the fringe: the current state.'
    points = 3

    DOESNT_POP = 1
    POPS_WRONG_ITEM = 2
    TAKES_BAIT = 3 # if it checks if a different element is the goal state
    EXPANSION_MISMATCH = 4 # if it expands with a different state
    def generateText(self):
        if self.problem_code == self.DOESNT_POP:
            return f'Search function does not remove any state from the fringe to consider.'
        if self.problem_code == self.POPS_WRONG_ITEM:
            return f'Search function inappropriately pops {self.popped!r} from fringe {self.fringe!r}.'
        if self.problem_code == self.TAKES_BAIT:
            return f'Search function returns goal {self.returned!r}, which differs from {self.current_state!r}, the state under consideration.'
        if self.problem_code == self.EXPANSION_MISMATCH:
            return f'Search function expands {self.expanded!r} in place of or in addition to the current state {self.current_state!r}.'
        return tests.Criterion.generateText(self)

class IgnoresDeep(tests.Criterion):
    summary = 'Ignores states with depth above max_depth and returns CONTINUE.'
    points = 2

    TAKES_BAIT = 1
    EXPANDS_ILLEGALLY = 2
    WRONG_RETVAL = 3
    def generateText(self):
        if self.problem_code == self.TAKES_BAIT:
            return f'Search function returns the goal state {self.current_state!r} even though its depth is greater than the maximum depth {self.max_depth!r}.'
        if self.problem_code == self.EXPANDS_ILLEGALLY:
            return f'Search function expands {self.expanded!r} even though the current state {self.current_state!r} has depth greater than the maximum depth {self.max_depth!r}.'
        if self.problem_code == self.WRONG_RETVAL:
            return f'Search function returns {self.returned!r} after determining that the current state is too deep: CONTINUE ({self.contcode!r}) expected.'
        return tests.Criterion.generateText(self)

### informed criteria

class HeapPops(tests.Criterion):
    summary = 'Uses heappop to get the highest-priority element from the fringe: the current state.'
    points = 1

    DOESNT_POP = 1
    NOT_HEAPPOP = 2
    TAKES_BAIT = 3 # if it checks if a different element is the goal state
    EXPANSION_MISMATCH = 4 # if it expands with a different state
    def generateText(self):
        if self.problem_code == self.DOESNT_POP:
            return f'Search function does not remove any state from the fringe to consider.'
        if self.problem_code == self.NOT_HEAPPOP:
            return f'Search function does not use the heapq.heappop function to pop the top-priority element from the fringe.'
        if self.problem_code == self.TAKES_BAIT:
            return f'Search function returns goal {self.returned!r}, which differs from {self.current_state!r}, the state under consideration.'
        if self.problem_code == self.EXPANSION_MISMATCH:
            return f'Search function expands {self.expanded!r} in place of or in addition to the current state {self.current_state!r}.'
        return tests.Criterion.generateText(self)

class IgnoresExplored(tests.Criterion):
    summary = 'Ignores states whose boards have already been seen (unless they have a lower f-value than before) and returns CONTINUE.'
    points = 2

    IGNORES_BETTER = 1
    RECORDS_ILLEGALLY = 2
    TAKES_BAIT = 3
    EXPANDS_ILLEGALLY = 4
    WRONG_RETVAL = 5
    def generateText(self):
        if self.problem_code == self.IGNORES_BETTER:
            return f'Search function fails to consider {self.current_state!r} even though the only time it had been seen before was with worse f-value {self.seen_fvalue!r}.'
        if self.problem_code == self.TAKES_BAIT:
            return f'Search function returns the goal state {self.current_state!r} even though a path to the same board with f-value {self.seen_fvalue!r} has already been explored.'
        if self.problem_code == self.EXPANDS_ILLEGALLY:
            return f'Search function expands {self.expanded!r} even though a path with f-value {self.seen_fvalue!r} to the same board as the current state {self.current_state!r} has already been explored.'
        if self.problem_code == self.RECORDS_ILLEGALLY:
            return f'Search function records {self.current_state.fvalue!r} as the best encountered f-value for board {self.current_state.board!r} even though a path to it with f-value {self.seen_fvalue!r} has already been explored.'
        if self.problem_code == self.WRONG_RETVAL:
            return f'Search function returns {self.returned!r} after determining that the current state is  not worth consideration: CONTINUE ({self.contcode!r}) expected.'
        return tests.Criterion.generateText(self)

class RecordsFValue(tests.Criterion):
    summary = 'Records the current state\'s board in the explored dictionary, along with its f-value.'
    points = 2

    NOT_RECORDED = 1
    WRONG_FVALUE = 2
    MESSED_UP_DICT = 3 # check if the old explored dictionary is a subset of the new one
    def generateText(self):
        if self.problem_code == self.NOT_RECORDED:
            if self.old_value is None:
                return f'Search function does not record any f-value for the board of new state {self.current_state!r}.'
            return f'Search function leaves old f-value {self.old_value!r} in explored for the board of state under consideration {self.current_state!r}.'
        if self.problem_code == self.WRONG_FVALUE:
            return f'Search function records incorrect f-value {self.recorded_value!r} in explored for the board of state under consideration {self.current_state!r}.'
        if self.problem_code == self.MESSED_UP_DICT:
            return f'When informed_search is called with fringe {self.fringe!r} and explored dictionary {self.explored!r}, sets best encountered f-values for boards other than the current state\'s board: leaves explored dictionary {self.student_explored!r}.'
        return tests.Criterion.generateText(self)


class BFSTester(tests.CriterionTester):
    function_name = "breadth_first_search"
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a3'], [SingleIteration, StopIfEmpty, ConsidersFirstState, IgnoresDeep, SeeksGoal, ExpandsFringe])

    def run(self, compilation_test=False):
        if compilation_test:
            n_tests = 10
        else:
            n_tests = 50
        # overrides
        self.expanded = set()

        def expand_fringe(current_state, fringe):
            if current_state in self.expanded:
                self.fail_criterion(ExpandsFringe, problem_code=ExpandsFringe.MULTIPLE_TIMES, current_state=current_state)
            self.expanded.add(current_state)
        def informed_expansion(current_state, fringe, f_function):
            if current_state in self.expanded:
                self.fail_criterion(ExpandsFringe, problem_code=ExpandsFringe.MULTIPLE_TIMES, current_state=current_state)
            self.expanded.add(current_state)
            self.fail_criterion(ExpandsFringe, problem_code=ExpandsFringe.WRONG_EXPANSION, attempted="informed_expansion", correct="expand_fringe")

        self.a3.expand_fringe = expand_fringe
        self.a3.informed_expansion = informed_expansion

        # boards to use!

        goal_board = self.a3.Board.Board([[1, 2, 3], [4, 5, 6], [7, 8, 0]])

        boards = [self.a3.Board.Board(case.board) for case in data.cases]

        # generate a few fringes
        fringes = []
        for i in range(n_tests):
            fringe = []
            # including some winning fringes
            if i < 5:
                goal_state = self.a3.State.State(goal_board, None, random.randint(0,3))
                fringe.append(goal_state)
            # and one or two at too high of a depth
            elif i < 8:
                goal_state = self.a3.State.State(goal_board, None, random.randint(50, 100))
                fringe.append(goal_state)
            # and just a few other guys
            for _ in range(random.randint(3, 8)):
                this_board = random.choice(boards)
                while len(this_board.matrix) == 4:
                    this_board = random.choice(boards)
                state = self.a3.State.State(this_board, None, random.randint(0,15))
                fringe.append(state)
            fringes.append(fringe)

        ## we're good to go!
        # checks StopIfEmpty
        try:
            retval = self.a3.breadth_first_search([], 3, goal_board)
        except NotImplementedError:
            raise
        except Exception as err:
            self.fail_criterion(StopIfEmpty, problem_code=StopIfEmpty.ERROR, error=err)
        else:
            if retval != self.a3.STOP:
                self.fail_criterion(StopIfEmpty, problem_code=StopIfEmpty.WRONG_RETVAL, returned=retval, stopcode=self.a3.STOP)

        for fringe in fringes:
            max_depth = random.randint(4, 8)
            self.expanded = set()
            student_fringe = fringe.copy()
            retval = self.a3.breadth_first_search(student_fringe, max_depth, goal_board)

            popped = set(fringe) - set(student_fringe)
            if len(popped) > 1:
                self.fail_criterion(SingleIteration)
                self.fail_all_criteria()
                return
            elif len(popped) == 0:
                self.fail_criterion(ConsidersFirstState, problem_code=ConsidersFirstState.DOESNT_POP)
                current_state = fringe[0]
            else:
                current_state = popped.pop()
                if current_state is not fringe[0]:
                    self.fail_criterion(ConsidersFirstState, problem_code=ConsidersFirstState.POPS_WRONG_ITEM,
                        popped=current_state, fringe=fringe)

            # check that nothing extra was expanded
            wrong_expansions = self.expanded.copy()
            wrong_expansions.discard(current_state)
            if wrong_expansions:
                self.fail_criterion(ConsidersFirstState, problem_code=ConsidersFirstState.EXPANSION_MISMATCH,
                    current_state=current_state, expanded=self.expanded)
            # checks if we took the bait for something other than the current_state.
            if isinstance(retval, self.a3.State.State) and retval.board == goal_board and retval is not current_state:
                self.fail_criterion(ConsidersFirstState, problem_code=ConsidersFirstState.TAKES_BAIT,
                    current_state=current_state, returned=retval)

            # check if we're too deep
            if current_state.depth > max_depth:
                if self.expanded:
                    self.fail_criterion(IgnoresDeep, problem_code=IgnoresDeep.EXPANDS_ILLEGALLY,
                        current_state=current_state, max_depth=max_depth, expanded=self.expanded)
                if retval is current_state and current_state.board == goal_board:
                    self.fail_criterion(IgnoresDeep, problem_code=IgnoresDeep.TAKES_BAIT,
                        current_state=current_state, max_depth=max_depth)
                elif retval != self.a3.CONTINUE:
                    self.fail_criterion(IgnoresDeep, problem_code=IgnoresDeep.WRONG_RETVAL, returned=retval, contcode=self.a3.CONTINUE)
            # checks desired behaviors if we found the goal
            elif current_state.board == goal_board:
                if self.expanded:
                    self.fail_criterion(SeeksGoal, problem_code=SeeksGoal.EXPANDS_ANYWAY,
                        current_state=current_state, expanded=self.expanded)
                if retval != current_state:
                    self.fail_criterion(SeeksGoal, problem_code=SeeksGoal.WRONG_RETVAL,
                        returned=retval, current_state=current_state)
            # we should have expanded.
            else:
                if not self.expanded:
                    self.fail_criterion(ExpandsFringe, problem_code=ExpandsFringe.DOESNT_EXPAND,
                        current_state=current_state)
                if retval != self.a3.CONTINUE:
                    self.fail_criterion(ExpandsFringe, problem_code=ExpandsFringe.WRONG_RETVAL, returned=retval, contcode=self.a3.CONTINUE)

class InformedSearchTester(tests.CriterionTester):
    function_name = "informed_search"
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a3'], [SingleIteration, StopIfEmpty, HeapPops, IgnoresExplored, RecordsFValue, SeeksGoal, ExpandsFringe])
    def f_function(self, board, depth, safe=False):
        if type(depth) != int or not isinstance(board, self.a3.Board.Board):
            return hash(str(board) + str(depth)) # way to check what is gotten back

        heuristic = 0
        if len(board.matrix) == 4:
            goal_matrix = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
        else:
            goal_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        for i in range(len(board.matrix)):
            for j in range((len(board.matrix))):
                if goal_matrix[i][j] == 0:
                    continue
                c_i, c_j = board.find_element(goal_matrix[i][j])
                heuristic += abs(i - c_i) + abs(j - c_j)

        return heuristic + depth
    def run(self, compilation_test=False):
        check_a3(self, self.a3)
        if compilation_test:
            n_tests = 10
        else:
            n_tests = 150
        # overrides
        self.expanded = set()

        def expand_fringe(current_state, fringe):
            if current_state in self.expanded:
                self.fail_criterion(ExpandsFringe, problem_code=ExpandsFringe.MULTIPLE_TIMES, current_state=current_state)
            self.expanded.add(current_state)
            self.fail_criterion(ExpandsFringe, problem_code=ExpandsFringe.WRONG_EXPANSION, attempted="expand_fringe", correct="informed_expansion")
        def informed_expansion(current_state, fringe, f_function):
            if not f_function == self.f_function:
                self.fail_criterion(ExpandsFringe, problem_code=ExpandsFringe.WRONG_F_FUNCTION, current_state=current_state, attempted=f_function)
            if current_state in self.expanded:
                self.fail_criterion(ExpandsFringe, problem_code=ExpandsFringe.MULTIPLE_TIMES, current_state=current_state)
            self.expanded.add(current_state)

        self.a3.expand_fringe = expand_fringe
        self.a3.informed_expansion = informed_expansion

        # because this is a global function, I'm overriding it for as short of a period as possible.
        self.heappopped = False

        heapq._heappop = heapq.heappop
        def new_heappop(heap):
            self.heappopped = True
            return heapq._heappop(heap)
        heapq.heappop = new_heappop

        try:
            # boards to use!
            goal_board = self.a3.Board.Board([[1, 2, 3], [4, 5, 6], [7, 8, 0]])

            boards = [self.a3.Board.Board(case.board) for case in data.cases]

            # generate a few fringes
            fringes = []
            for i in range(n_tests):
                fringe = []
                # including some winning fringes
                if i < n_tests//10:
                    goal_state = self.a3.State.State(goal_board, None, random.randint(0,3))
                    goal_state.fvalue = self.f_function(goal_state.board, goal_state.depth)
                    fringe.append(goal_state)
                # and one or two at a very high depth
                elif i < n_tests//5:
                    goal_state = self.a3.State.State(goal_board, None, random.randint(100, 200))
                    goal_state.fvalue = self.f_function(goal_state.board, goal_state.depth)
                    fringe.append(goal_state)
                # and just a few other guys
                for _ in range(random.randint(4, 9)):
                    state = self.a3.State.State(random.choice(boards), None, random.randint(0,15))
                    state.fvalue = self.f_function(state.board, state.depth)
                    fringe.append(state)

                heapq.heapify(fringe)
                fringes.append(fringe)

            ## we're good to go!
            # checks StopIfEmpty
            try:
                retval = self.a3.informed_search([], goal_board, self.f_function, set())
            except NotImplementedError:
                raise
            except Exception as err:
                self.fail_criterion(StopIfEmpty, problem_code=StopIfEmpty.ERROR, error=err)
            else:
                if retval != self.a3.STOP:
                    self.fail_criterion(StopIfEmpty, problem_code=StopIfEmpty.WRONG_RETVAL, returned=retval, stopcode=self.a3.STOP)

            for fringe in fringes:
                explored = {}
                for state in fringe:
                    if state.board in explored and state.fvalue >= explored[state.board]:
                        continue
                    if random.random() > .5: continue
                    explored[state.board] = state.fvalue + random.randint(-1, 1)

                student_fringe = fringe.copy()
                student_explored = explored.copy()

                self.expanded = set()
                self.heappopped = False

                retval = self.a3.informed_search(student_fringe, goal_board, self.f_function, student_explored)

                # find the current state
                popped = set(fringe) - set(student_fringe)
                if len(popped) > 1:
                    self.fail_criterion(SingleIteration)
                    self.fail_all_criteria()
                    return
                elif len(popped) == 0:
                    self.fail_criterion(HeapPops, problem_code=HeapPops.DOESNT_POP)
                    current_state = fringe[0]
                else:
                    current_state = popped.pop()
                    if not self.heappopped:
                        self.fail_criterion(HeapPops, problem_code=HeapPops.NOT_HEAPPOP)

                # make sure they didn't corrupt explored.
                for board, fvalue in explored.items():
                    if board == current_state.board: continue
                    if board not in student_explored or student_explored[board] != fvalue:
                        self.fail_criterion(RecordsFValue, problem_code=RecordsFValue.MESSED_UP_DICT,
                            fringe=fringe, explored=explored, student_explored=student_explored)

                # check that nothing extra was expanded
                wrong_expansions = self.expanded.copy()
                wrong_expansions.discard(current_state)
                if wrong_expansions:
                    self.fail_criterion(HeapPops, problem_code=HeapPops.EXPANSION_MISMATCH,
                        current_state=current_state, expanded=self.expanded)
                # checks if we took the bait for something other than the current_state.
                if isinstance(retval, self.a3.State.State) and retval.board == goal_board and retval is not current_state:
                    self.fail_criterion(HeapPops, problem_code=HeapPops.TAKES_BAIT,
                        current_state=current_state, returned=retval)

                if current_state.board in explored:
                    seen_fvalue = explored[current_state.board]
                else:
                    seen_fvalue = None

                # make sure they didn't ignore something that was good
                if seen_fvalue is not None and current_state.fvalue < seen_fvalue \
                        and not self.expanded and student_explored[current_state.board] == seen_fvalue \
                        and retval is not current_state:
                    self.fail_criterion(IgnoresExplored, problem_code=IgnoresExplored.IGNORES_BETTER,
                        current_state=current_state, seen_fvalue=seen_fvalue)
                    # if it is the case that they did absolutely nothing because they thought it was already explored,
                    # go ahead and skip to the next one.
                    continue

                # check if we're redundant
                if seen_fvalue is not None and current_state.fvalue >= seen_fvalue:
                    if self.expanded:
                        self.fail_criterion(IgnoresExplored, problem_code=IgnoresExplored.EXPANDS_ILLEGALLY,
                            current_state=current_state, seen_fvalue=seen_fvalue, expanded=self.expanded)
                    if student_explored[current_state.board] > seen_fvalue:
                        self.fail_criterion(IgnoresExplored, problem_code=IgnoresExplored.RECORDS_ILLEGALLY,
                            current_state=current_state, seen_fvalue=seen_fvalue, recorded=student_explored[current_state.board])
                    if retval is current_state and current_state.board == goal_board:
                        self.fail_criterion(IgnoresExplored, problem_code=IgnoresExplored.TAKES_BAIT,
                            current_state=current_state, seen_fvalue=seen_fvalue)
                    elif retval != self.a3.CONTINUE:
                        self.fail_criterion(IgnoresExplored, problem_code=IgnoresExplored.WRONG_RETVAL, returned=retval, contcode=self.a3.CONTINUE)
                    # they shouldn't have recorded, expanded, or checked if it was the goal.
                    # and we just checked all of those. so continue
                    continue

                # check that they properly recorded their value...
                if not current_state.board in student_explored or \
                        (student_explored[current_state.board] == seen_fvalue):
                    self.fail_criterion(RecordsFValue, problem_code=RecordsFValue.NOT_RECORDED,
                        current_state=current_state, old_value=seen_fvalue)
                elif student_explored[current_state.board] != current_state.fvalue:
                    self.fail_criterion(RecordsFValue, problem_code=RecordsFValue.WRONG_FVALUE,
                        current_state=current_state, recorded_value=student_explored[current_state.board])

                # checks desired behaviors if we found the goal
                if current_state.board == goal_board:
                    if self.expanded:
                        self.fail_criterion(SeeksGoal, problem_code=SeeksGoal.EXPANDS_ANYWAY,
                            current_state=current_state, expanded=self.expanded)
                    if retval != current_state:
                        self.fail_criterion(SeeksGoal, problem_code=SeeksGoal.WRONG_RETVAL,
                            returned=retval, current_state=current_state)
                # we should have expanded.
                else:
                    if not self.expanded:
                        self.fail_criterion(ExpandsFringe, problem_code=ExpandsFringe.DOESNT_EXPAND,
                            current_state=current_state)
                    if retval != self.a3.CONTINUE:
                        self.fail_criterion(ExpandsFringe, problem_code=ExpandsFringe.WRONG_RETVAL, returned=retval, contcode=self.a3.CONTINUE)
        finally:
            heapq.heappop = heapq._heappop
