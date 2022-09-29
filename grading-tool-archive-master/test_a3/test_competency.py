#!/usr/bin/python3

import random
import heapq
import multiprocessing

from grade import tests

from . import data
from .checker import check_a3

### Shared criteria

#     calls manhattan distance
#     reimplements manhattan distance
#     is zero

class Solves(tests.Criterion):
    NONE_VALUE = 1
    WRONG_TYPE = 2 # not a State
    WRONG_BOARD = 3 # not the goal
    WRONG_DEPTH = 4
    ERROR = 5
    TIMEOUT = 6

    neverRedact = True
    points = 4

    def generateText(self):
        if self.problem_code == self.NONE_VALUE:
            return f'Returns None on {self.case.represent()}: State object expected.'
        if self.problem_code == self.WRONG_TYPE:
            return f'Returns {self.value} on {self.case.represent()}: State object expected.'
        if self.problem_code == self.WRONG_BOARD:
            return f'Returns State with board {self.board} on {self.case.represent()}: goal board expected.'
        if self.problem_code == self.WRONG_DEPTH:
            return f'Returns State with incorrect depth {self.student_depth} on {self.case.represent()}.'
        if self.problem_code == self.ERROR:
            return f'Produces an uncaught exception on {self.case.represent()}.\n\n'+self.error_text
        if self.problem_code == self.TIMEOUT:
            return f'Times out on {self.case.represent()}.'
        return tests.Criterion.generateText(self)

class RecognizesGoal(Solves):
    summary = 'Recognizes the goal state when passed to a solver function.'

class Under5(Solves):
    summary = 'Finds the optimal path for boards that are less than 5 moves away from the goal.'

class Under10(Solves):
    summary = 'Finds the optimal path for boards that are less than 10 moves away from the goal.'

class Under20(Solves):
    summary = 'Finds the optimal path for boards that are less than 20 moves away from the goal.'

class Under30(Solves):
    summary = 'Finds the optimal path for boards that are less than 30 moves away from the goal.'

class Under15Big(Solves):
    summary = 'Finds the optimal path for boards (including BIG boards) that are less than 15 moves away from the goal. Wow!'
    points = 5

class Under30Big(Solves):
    summary = 'Finds the optimal path for boards (including BIG boards) that are less than 30 moves away from the goal. Wow!'
    points = 5

def do_board(board_matrix, goal_board_matrix):
    import a3
    board = a3.Board.Board(board_matrix)
    goal_board = a3.Board.Board(goal_board_matrix)
    try:
        if a3.my_heuristic(goal_board, goal_board) is None:
            raise ValueError
        f_function = a3.a_star_f_function_factory(a3.my_heuristic, goal_board)
        if f_function(goal_board, 10) is None:
            raise ValueError
    except Exception:
        f_function = a3.ucs_f_function

    def informed_solver(start_board, goal_board, f_function):
        """
            Looping function which calls informed_search until it finds a solution
            (a State object) or until STOP has been returned.
            If the goal is reached, this function should return the Goal State,
            which includes a path to the goal. Otherwise, returns None.
        """
        fringe = [a3.State.State(start_board, None, 0, f_function(start_board, 0))]
        explored = {}
        found = a3.CONTINUE
        while found == a3.CONTINUE:
            try:
                found = a3.informed_search(fringe, goal_board, f_function, explored)
            except NotImplementedError:
                found = a3.breadth_first_search(fringe, 32, goal_board)
        if isinstance(found, a3.State.State):
            return found
        return None

    returned = informed_solver(board, goal_board, f_function)
    if returned == None:
        return returned
    if isinstance(returned, a3.State.State):
        return (returned.board.matrix, returned.depth)

    return repr(returned)

### Shared Tester

class CompetencyTester(tests.CriterionTester):
    function_name = "Competency"
    compilation_test_timeout = 3
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a3'], [RecognizesGoal, Under5, Under10, Under20, Under30, Under15Big, Under30Big], timeout=100)

    def fail_depth(self, d, board_size, *args, **kwargs):
        if d <= 15:
            self.fail_criterion(Under15Big, *args, **kwargs)
        if d <= 30:
            self.fail_criterion(Under30Big, *args, **kwargs)
        if board_size > 3:
            return
        if d <= 0:
            self.fail_criterion(RecognizesGoal, *args, **kwargs)
        if d <= 5:
            self.fail_criterion(Under5, *args, **kwargs)
        if d <= 10:
            self.fail_criterion(Under10, *args, **kwargs)
        if d <= 20:
            self.fail_criterion(Under20, *args, **kwargs)
        if d <= 30:
            self.fail_criterion(Under30, *args, **kwargs)

    def run(self, compilation_test=False):
        check_a3(self, self.a3)
        if compilation_test:
            cases = data.cases[:4]
        else:
            cases = data.cases[:100]
            cases.extend(data.cases[719:731])
        for case in cases:
            p = multiprocessing.Pool(1)
            board_size = len(case.board)
            goal_board = [[(row*board_size + col + 1) % board_size**2 for col in range(board_size)] for row in range(board_size)]
            result_obj = p.apply_async(do_board, args=(case.board, goal_board))
            try:
                result = result_obj.get(.5)
            except NotImplementedError:
                raise
            except (TimeoutError, multiprocessing.TimeoutError):
                self.fail_depth(case.distance, board_size, case=case, problem_code=Solves.TIMEOUT)
            except Exception as err:
                self.fail_depth(case.distance, board_size, case=case, problem_code=Solves.ERROR, error_text=eval(err.__cause__.tb).strip())
            else:
                if result is None:
                    self.fail_depth(case.distance, board_size, case=case, problem_code=Solves.NONE_VALUE)
                elif type(result) is str:
                    self.fail_depth(case.distance, board_size, case=case, problem_code=Solves.WRONG_TYPE, value=result)
                else:
                    ret_board, ret_depth = result
                    if ret_board != goal_board:
                        self.fail_depth(case.distance, board_size, case=case, problem_code=Solves.WRONG_BOARD, board=ret_board)
                    if ret_depth != case.distance:
                        self.fail_depth(case.distance, board_size, case=case, problem_code=Solves.WRONG_DEPTH, student_depth=ret_depth)
            finally:
                p.terminate()
