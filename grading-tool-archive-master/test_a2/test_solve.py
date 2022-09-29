#!/usr/bin/python3

from grade import tests
from . import data
from .checker import checked_board

def quickBtoS(board, n=9):
    return ''.join(str(board[(r,c)]) if (r,c) in board else '_'
                    for r in range(n) for c in range(n)) # for the record, this is REALLY bad style. - Abe
def quickBtoTable(board, n=9):
    style = '''<style type="text/css">\n.sudoku { border-collapse: collapse; }\n.sudoku tr td {\nheight:30px;\nwidth:30px;\nborder:1px solid gray;\ntext-align:center;\n}\n.sudoku tr td:first-child { border-left:solid black; }\n.sudoku tr td:nth-child(3n) { border-right:solid black; }\n.sudoku tr:first-child { border-top:solid black; }\n.sudoku tr:nth-child(3n) td { border-bottom:solid black; }\n</style>\n'''
    return style+'<table class="sudoku">\n<tr>' + '</tr>\n<tr>'.join('<td>' + '</td><td>'.join(repr(board[(r,c)]) if (r,c) in board else '' for c in range(n)) + '</td>' for r in range(n)) + '</tr>\n</table>' # also bad style

class RightSpace(tests.Criterion):
    summary = 'Attempts to make moves in a single space, the most constrained unsolved space.'
    INCORRECT = 1 # must be a correct space
    MULTIPLE = 2  # must be a single space
    NO_ATTEMPT = 3  # never attempts to make moves
    points = 5
    def generateText(self):
        if self.problem_code == self.INCORRECT:
            attempted, detected = self.details['attempted'], self.details['detected']
            board = self.case.represent()
            return 'Attempts to make a move in a space %s other than the most constrained space %s on board %s.' \
                % (str(attempted), str(detected), board)
        elif self.problem_code == self.MULTIPLE:
            attempted_spaces = self.details['attempted_spaces']
            board = self.case.represent()
            return 'Attempts to make moves in multiple spaces (%s) on board %s.' \
                % (str(attempted_spaces), board)
        elif self.problem_code == self.NO_ATTEMPT:
            return 'Does not attempt to make moves in any space on any board.'
        else:
            return tests.Criterion.generateText(self)

class TriesValues(tests.Criterion):
    summary = 'Does not attempt any invalid values, and attempts each valid value exactly once (until a solution is found).'
    INVALID_MOVE = 1 # tries to make an invalid move for a square
    REPEATED_MOVE = 2 # makes a move twice
    UNNECESSARY_MOVE = 3 # makes a move after a solution is found
    MISSED_VALUE = 4 # returns false without checking every move
    NO_ATTEMPT = 5  # never attempts to make moves
    points = 5
    def generateText(self):
        if self.problem_code == self.INVALID_MOVE:
            space, attempted_value = self.details['space'], self.details['attempted_value']
            board = self.case.represent()
            return 'Attempts to assign invalid value %s to space %s on board %s.' \
                % (str(attempted_value), str(space), board)
        elif self.problem_code == self.REPEATED_MOVE:
            space, attempted_value = self.details['space'], self.details['attempted_value']
            board = self.case.represent()
            return 'Tries assigning value %s to space %s more than once on board %s.' \
                % (str(attempted_value), str(space), board)
        elif self.problem_code == self.UNNECESSARY_MOVE:
            space, attempted_value = self.details['space'], self.details['attempted_value']
            board = self.case.represent()
            return 'Tries assigning value %s to space %s after a solution is found on board %s.' \
                % (str(attempted_value), str(space), board)
        elif self.problem_code == self.MISSED_VALUE:
            space, possible, attempted = self.details['space'], self.details['possible_values'], self.details['attempted_values']
            board = self.case.represent()
            return 'Reports that board %s is unsolvable without attempting every possible value (%s) for most constrained space %s. (Attemped values: %s.)' \
                % (board, str(possible), str(space), str(attempted))
        elif self.problem_code == self.NO_ATTEMPT:
            return 'Does not attempt to assign values to any space on any board.'
        else:
            return tests.Criterion.generateText(self)

class ClearsBadMoves(tests.Criterion):
    summary = 'Clears every move that does not lead to a solution.'
    LEAVES_DIRTY = 1     # leaves the board different on failure
    RETRIES_ON_DIRTY = 2 # tries to make a move without clearing the last one
    CLEARS_EMPTY = 3     # tries to clear an empty square
    CLEARS_WRONG_VALUE = 4 # tries to clear but without the right value
    NO_ATTEMPT = 5  # never attempts to clear moves
    points = 5
    def generateText(self):
        if self.problem_code == self.LEAVES_DIRTY:
            board = self.case.represent()
            if 'space' in self.details:
                space, value = self.details['space'], self.details['value']
                return f'Exits without clearing incorrect move {value} in space {space} on board {board}.'
            else:
                return 'Exits without clearing incorrect moves on board %s.' \
                    % (board)
        elif self.problem_code == self.RETRIES_ON_DIRTY:
            space, current_value, attempted_value = self.details['space'], self.details['current_value'], self.details['attempted_value']
            board = self.case.represent()
            return 'Tries assigning value %s to space %s without clearing previous assignment %s on board %s.' \
                % (str(attempted_value), str(space), str(current_value), board)
        elif self.problem_code == self.CLEARS_EMPTY:
            space, attempted_value = self.details['space'], self.details['attempted_value']
            board = self.case.represent()
            return 'Tries clearing value %s from empty space %s on board %s.' \
                % (str(attempted_value), str(space), board)
        elif self.problem_code == self.CLEARS_WRONG_VALUE:
            space, current_value, attempted_value = self.details['space'], self.details['current_value'], self.details['attempted_value']
            board = self.case.represent()
            return 'Tries clearing value %s from space %s, which is actually assigned to %s, on board %s.' \
                % (str(attempted_value), str(space), str(current_value), board)
        elif self.problem_code == self.NO_ATTEMPT:
            return 'Does not attempt to clear any space on any board.'
        else:
            return tests.Criterion.generateText(self)

class TestsEveryMove(tests.Criterion):
    summary = 'Recursively calls solve exactly once for each move made, in order to test whether it leads to a solution.'
    CLEARS_WITHOUT_TEST = 1 # clears a move without having tested it
    ENDS_WITHOUT_TEST = 2   # exits solve without testing every move made
    SOLVES_WITHOUT_MOVE = 3 # calls solve without having made a move
    MULTIPLE_MOVES_PER_SOLVE = 4 # calls solve after having made multiple moves
    NO_ATTEMPT = 5  # never calls solve
    points = 5
    def generateText(self):
        if self.problem_code == self.CLEARS_WITHOUT_TEST:
            board = self.case.represent()
            if 'space' in self.details:
                space, attempted_value = self.details['space'], self.details['attempted_value']
                return 'Attempts to clear move %s in space %s without having first tested the board state on board %s.' \
                    % (str(attempted_value), str(space), board)
            else:
                return 'Exits without clearing incorrect moves on board %s.' \
                    % (board)
        elif self.problem_code == self.ENDS_WITHOUT_TEST:
            moves = self.details['moves']
            board = self.case.represent()
            return 'Exits the solve procedure without checking whether %s moves lead to a solution, on board %s.' \
                % (str(moves), board)
        elif self.problem_code == self.SOLVES_WITHOUT_MOVE:
            board = self.case.represent()
            return 'Recursively calls solve without having made any moves to test, on board %s.' \
                % (board)
        elif self.problem_code == self.MULTIPLE_MOVES_PER_SOLVE:
            moves = self.details['moves']
            board = self.case.represent()
            return 'Tests the board state after making more than 1 move (%s) on board %s.' \
                % (str(moves), board)
        elif self.problem_code == self.NO_ATTEMPT:
            return 'Does not attempt to test any move on any board.'
        else:
            return tests.Criterion.generateText(self)

class BasedOnOriginal(tests.Criterion):
    summary = 'Never overwrites or clears any of the squares of the original board.'
    points = 2
    OVERWRITES_ORIGINAL = 1
    CLEARS_ORIGINAL = 2
    def generateText(self):
        board = self.case.represent()
        if self.problem_code == OVERWRITES_ORIGINAL:
            space, original_value, attempted_value = self.details['space'], self.details['original_value'], self.details['attempted_value']
            return f'Attempts to make move {attempted_value} in space {space}, which is originally {original_value} in {board}.'
        elif self.problem_code == CLEARS_ORIGINAL:
            space, original_value, attempted_value = self.details['space'], self.details['original_value'], self.details['attempted_value']
            return f'Attempts to remove value {attempted_value} from space {space}, which is originally {original_value} in {board}.'
        return 'Overwrites the original assignments on board %s.' \
            % (board)

class TrueOnSolved(tests.Criterion):
    summary = 'Returns True in the case where the entire board is already solved.'
    points = 2
    ERROR = 1
    def generateText(self):
        board = self.case.represent()
        if self.problem_code == self.ERROR:
            err = self.details['error']
            error_text = self.representError(err)
            return f'Produces an uncaught exception on already solved board {board}:\n\n'+error_text
        else:
            return f'Does not return True on already solved board {board}.'

class TrueOnSolvable(tests.Criterion):
    summary = 'Returns True when a solution is found, indicating that the current state leads to a solution.'
    points = 2
    def generateText(self):
        board = self.case.represent()
        return 'Does not return True on solvable board %s.' \
            % (board)

class FalseOnImpossible(tests.Criterion):
    summary = 'Returns False when no solution exists, because the most constrained cell cannot take any value.'
    points = 2
    def generateText(self):
        board = self.case.represent()
        return 'Does not return False on unsolvable board %s.' \
            % (board)

class LeavesSolved(tests.Criterion):
    summary = 'Does not undo any correct moves or attempt any other moves after a solution is found.'
    UNDOES_RIGHT_MOVES = 1 # undoes one of the moves that led to a solution
    LEAVES_WRONG_MOVE = 2  # makes an invalid move after finding a solution
    NO_ATTEMPT = 3  # did not attempt any moves on a solvable board
    points = 2
    def generateText(self):
        board = self.case.represent()
        if self.problem_code == self.NO_ATTEMPT:
            return 'Did not attempt any moves on solvable board %s.' \
                % (board)
        elif self.problem_code == self.UNDOES_RIGHT_MOVES:
            return 'Undoes correct moves on solvable board %s.' \
                % (board)
        elif self.problem_code == self.LEAVES_WRONG_MOVE:
            return 'Leaves incorrect assignments on solvable board %s.' \
                % (board)
        else:
            return tests.Criterion.generateText(self)


class LeavesOriginal(tests.Criterion):
    summary = 'Leaves the board in its original state if no solution exists.'
    points = 5
    neverRedact = True
    def generateText(self):
        board = self.case.represent()
        original_board = self.details['original_board']
        attempted_board = self.details['attempted_board']
        return 'Does not return the original board for unsolvable board %s.\nOriginal:  %s\nAttempted: %s' \
            % (board, quickBtoS(original_board), quickBtoS(attempted_board))
    def generateHTML(self):
        board = self.case.represent()
        original_board = self.details['original_board']
        attempted_board = self.details['attempted_board']
        return '<p>Does not return the original board for unsolvable board <samp>%s</samp>.</p>\n<span style="display: inline-block; text-align: center; ">\n<p>Original:</p>\n%s\n</span>\n<span style="display: inline-block; text-align: center; ">\n<p>Attempted:</p>\n%s\n</span>\n' \
            % (board, quickBtoTable(original_board), quickBtoTable(attempted_board))

class SolvesCorrectly(tests.Criterion):
    summary = 'After running on a solvable board, the board\'s final state is the same as the solution.'
    points = 15
    neverRedact = True
    def generateText(self):
        board = self.case.represent()
        solved_board = self.details['solved_board']
        attempted_board = self.details['attempted_board']
        return 'Does not return the correct solution for board %s.\nSolution:  %s\nAttempted: %s' \
            % (board, quickBtoS(solved_board), quickBtoS(attempted_board))
    def generateHTML(self):
        board = self.case.represent()
        solved_board = self.details['solved_board']
        attempted_board = self.details['attempted_board']
        return '<p>Does not return the correct solution for board <samp>%s</samp>.</p>\n<span style="display: inline-block; text-align: center; ">\n<p>Solution:</p>\n%s\n</span>\n<span style="display: inline-block; text-align: center; ">\n<p>Attempted:</p>\n%s\n</span>\n' \
            % (board, quickBtoTable(solved_board), quickBtoTable(attempted_board))

class SolveTester(tests.CriterionTester):
    function_name = 'solve'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a2'], [RightSpace, TriesValues, TestsEveryMove, ClearsBadMoves, LeavesSolved, BasedOnOriginal, TrueOnSolved, TrueOnSolvable, FalseOnImpossible], timeout=10)
    def makeTestSolver(self):
        StudentBoard = checked_board(self, self.a2.Board)
        class TestBoard(StudentBoard):
            def __init__(self, parent, case):
                self._parent = parent
                self._case = case
                self._movesTried = {}
                self._uncheckedMoves = 0
                self._foundSolution = False
                self._everMakesMove = False
                self._everClearsMove = False
                self._everTestsMove = False
                self._calledMostConstrained = False
                self._isValidCalled = False
                self._outstandingMoves = set()
                StudentBoard.__init__(self, case.filename)
                self._originalAssignments = self.board.copy()
                if self.unsolvedSpaces:
                    self._mostConstrainedSpace = self.getMostConstrainedUnsolvedSpace()
                    self._calledMostConstrained = False
                else:
                    self._mostConstrainedSpace = None
            def getMostConstrainedUnsolvedSpace(self):
                if not self.unsolvedSpaces:
                    space = None
                else:
                    space = max(self.unsolvedSpaces, key=
                        lambda space: len(self.valsInRows[space[0]] | self.valsInCols[space[1]]
                                            | self.valsInBoxes[self.spaceToBox(*space)])
                      )
                if not self._calledMostConstrained:
                    self._calledMostConstrained = True
                    self._mostConstrainedSpace = space
                return space
            def isValidMove(self, space, val):
                self._isValidCalled = True
                if not space in self.unsolvedSpaces: return False
                if val in self.valsInRows[space[0]] | self.valsInCols[space[1]] \
                        | self.valsInBoxes[self.spaceToBox(*space)]:
                    return False
                return True
            def makeMove(self, space, val):
                self._everMakesMove = True
                if self._foundSolution:
                    self._parent.fail_criterion(TriesValues, self._case, TriesValues.UNNECESSARY_MOVE, space=space, attempted_value=val)
                if space != self._mostConstrainedSpace:
                    self._parent.fail_criterion(RightSpace, self._case, RightSpace.INCORRECT, attempted=space, detected=self._mostConstrainedSpace)

                if not space in self._movesTried:
                    self._movesTried[space] = set()

                if len(self._movesTried) > 1:
                    self._parent.fail_criterion(RightSpace, self._case, RightSpace.MULTIPLE, attempted_spaces=self._movesTried.keys())

                if val in self._movesTried[space]:
                    self._parent.fail_criterion(TriesValues, self._case, TriesValues.REPEATED_MOVE, space=space, attempted_value=val)

                self._movesTried[space].add(val)

                if space in self._outstandingMoves and not self._foundSolution:
                    self._parent.fail_criterion(ClearsBadMoves, self._case, ClearsBadMoves.RETRIES_ON_DIRTY, space=space, current_value=self.board[space], attempted_value=val)
                if space in self._originalAssignments:
                    self._parent.fail_criterion(BasedOnOriginal, self._case, BasedOnOriginal.OVERWRITES_ORIGINAL, space=space, original_value=self._originalAssignments[space], attempted_value=val)

                if not space in self._case.allValidMoves or not val in self._case.allValidMoves[space]:
                    self._parent.fail_criterion(TriesValues, self._case, TriesValues.INVALID_MOVE, space=space, attempted_value=val)

                self._uncheckedMoves += 1
                self._outstandingMoves.add(space)

                #StudentBoard.placeValue(self, space, val)
                try:
                    self.board[space] = val
                    self.unsolvedSpaces.discard(space)
                    r, c = space
                    self.valsInRows[r].add(val)
                    self.valsInCols[c].add(val)
                    self.valsInBoxes(self.spaceToBox(r,c)).add(val)
                except: pass
            def undoMove(self, space, val):
                self._everClearsMove = True
                if self._uncheckedMoves > 0:
                    self._parent.fail_criterion(TestsEveryMove, self._case, TestsEveryMove.CLEARS_WITHOUT_TEST, space=space, attempted_value=val)
                if not space in self.board:
                    self._parent.fail_criterion(ClearsBadMoves, self._case, ClearsBadMoves.CLEARS_EMPTY, space=space, attempted_value=val)
                elif self.board[space] != val:
                    self._parent.fail_criterion(ClearsBadMoves, self._case, ClearsBadMoves.CLEARS_WRONG_VALUE, space=space, current_value=self.board[space], attempted_value=val)
                if space in self._originalAssignments:
                    self._parent.fail_criterion(BasedOnOriginal, self._case, BasedOnOriginal.CLEARS_ORIGINAL, space=space, original_value=self._originalAssignments[space], attempted_value=val)

                self._outstandingMoves.discard(space)
                #StudentBoard.removeValue(self, space, val)
                try:
                    if space in self.board: del self.board[space]
                    self.unsolvedSpaces.add(space)
                    r, c = space
                    self.valsInRows[r].discard(val)
                    self.valsInCols[c].discard(val)
                    self.valsInBoxes(self.spaceToBox(r,c)).discard(val)
                except: pass
        StudentSolver = self.a2.Solver
        class TestSolver(StudentSolver):
            def __init__(self, parent, case):
                self._parent = parent
                self._case = case
                self._original_board = StudentBoard(case.filename)
                self._solved_board = StudentBoard(case.solution_filename)
                self._test_board = TestBoard(parent, case)
                StudentSolver.__init__(self)
            def solveBoard(self, board):
                board._everTestsMove = True
                if not self._original_board.board.items() <= board.board.items():
                    self._parent.fail_criterion(BasedOnOriginal, self._case)

                if board._uncheckedMoves < 1: # len(self.board.board) <= len(self._original_board.board)
                    self._parent.fail_criterion(TestsEveryMove, self._case, TestsEveryMove.SOLVES_WITHOUT_MOVE)
                elif board._uncheckedMoves > 1:
                    self._parent.fail_criterion(TestsEveryMove, self._case, TestsEveryMove.MULTIPLE_MOVES_PER_SOLVE, moves=board._uncheckedMoves)
                board._uncheckedMoves -= 1

                # returns True iff the current state leads to a solution
                if board.board.items() <= self._solved_board.board.items():
                    board._foundSolution = True
                    return True
                board._foundSolution = False
                return False
            def test_solve(self):
                try:
                    value = StudentSolver.solveBoard(self, self._test_board)
                except Exception as err:
                    if self._original_board.board == self._solved_board.board:
                        self._parent.fail_criterion(TrueOnSolved, self._case, TrueOnSolved.ERROR, error=err)
                        return
                    else:
                        raise err

                # checks that the original board's assignments aren't chagned
                if not self._original_board.board.items() <= self._test_board.board.items():
                    self._parent.fail_criterion(BasedOnOriginal, self._case)
                # already solved case
                if self._original_board.board == self._solved_board.board:
                    if value != True:
                        self._parent.fail_criterion(TrueOnSolved, self._case)
                # solvable case
                elif self._original_board.board.items() <= self._solved_board.board.items():
                    if value != True:
                        self._parent.fail_criterion(TrueOnSolvable, self._case)
                    if self._test_board.board == self._original_board.board and self._test_board._everMakesMove == False:
                        self._parent.fail_criterion(LeavesSolved, self._case, LeavesSolved.NO_ATTEMPT)
                    elif self._test_board.board == self._original_board.board:
                        self._parent.fail_criterion(LeavesSolved, self._case, LeavesSolved.UNDOES_RIGHT_MOVES)
                    elif not self._test_board.board.items() <= self._solved_board.board.items():
                        self._parent.fail_criterion(LeavesSolved, self._case, LeavesSolved.LEAVES_WRONG_MOVE)
                # unsolvable case
                else:
                    if value != False:
                        self._parent.fail_criterion(FalseOnImpossible, self._case)
                    if self._test_board._outstandingMoves:
                        if self._test_board._mostConstrainedSpace and self._test_board._mostConstrainedSpace in self._test_board._outstandingMoves:
                            self._parent.fail_criterion(ClearsBadMoves, self._case, ClearsBadMoves.LEAVES_DIRTY, space=self._test_board._mostConstrainedSpace, value=self._test_board.board[self._test_board._mostConstrainedSpace])
                        else:
                            self._parent.fail_criterion(ClearsBadMoves, self._case, ClearsBadMoves.LEAVES_DIRTY)
                # check that they looked at each case before saying false
                if value == False:
                    selected_space = self._test_board._mostConstrainedSpace
                    valid = set()
                    if selected_space:
                        if self._test_board._isValidCalled:
                            for val in range(1, self._test_board.n2+1):
                                if self._test_board.isValidMove(selected_space, val):
                                    valid.add(val)
                        else:
                            valid = self._case.allValidMoves[selected_space]
                    if valid:
                        if not selected_space in self._test_board._movesTried:
                            self._test_board._movesTried[selected_space] = set()
                        if self._test_board._movesTried[selected_space] < valid:
                            self._parent.fail_criterion(TriesValues, self._case, TriesValues.MISSED_VALUE, space=selected_space, possible_values=valid, attempted_values=self._test_board._movesTried[selected_space])
                # check that they tested every move
                if self._test_board._uncheckedMoves > 0:
                    self._parent.fail_criterion(TestsEveryMove, self._case, TestsEveryMove.ENDS_WITHOUT_TEST, moves=self._test_board._uncheckedMoves)
        return TestSolver
    def run(self, compilation_test=False):
        TestSolver = self.makeTestSolver()

        ever_makes_move = False
        ever_clears_move = False
        ever_tests_move = False

        if compilation_test:
            test_cases = data.test_cases[:2]
        else:
            test_cases = data.test_cases
        for case in test_cases:
            t = TestSolver(self, case)
            try:
                t.test_solve()
            except Exception as err:
                self.reraise(err, 'An uncaught exception occurred while solving '+case.represent())

            ever_makes_move += t._test_board._everMakesMove
            ever_clears_move += t._test_board._everClearsMove
            ever_tests_move += t._test_board._everTestsMove

        if not ever_makes_move:
            self.fail_criterion(RightSpace, problem_code=RightSpace.NO_ATTEMPT)
            self.fail_criterion(TriesValues, problem_code=TriesValues.NO_ATTEMPT)
        if not ever_clears_move:
            self.fail_criterion(ClearsBadMoves, problem_code=ClearsBadMoves.NO_ATTEMPT)
        if not ever_tests_move:
            self.fail_criterion(TestsEveryMove, problem_code=TestsEveryMove.NO_ATTEMPT)

class CompetencyTester(tests.CriterionTester):
    function_name = 'Competency'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a2'], [LeavesOriginal, SolvesCorrectly], timeout=30)
    def run(self, compilation_test=False):
        StudentSolver = self.a2.Solver
        StudentBoard = checked_board(self, self.a2.Board)

        if compilation_test:
            test_cases = data.test_cases[:2]
        else:
            test_cases = data.test_cases
        for case in test_cases:
            original_board = StudentBoard(case.filename)
            solved_board = StudentBoard(case.solution_filename)
            test_board = StudentBoard(case.filename)

            try:
                s = StudentSolver()
                s.solveBoard(test_board)
            except Exception as err:
                self.reraise(err, 'An uncaught exception occurred while solving '+case.represent())
            if original_board.board.items() <= solved_board.board.items():
                if test_board.board != solved_board.board:
                    self.fail_criterion(SolvesCorrectly, case, solved_board=solved_board.board, attempted_board=test_board.board)
            else:
                if test_board.board != original_board.board:
                    self.fail_criterion(LeavesOriginal, case, original_board=original_board.board, attempted_board=test_board.board)

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/Downloads')

    s = SolveTester()
    s.test()
    print(s.generateHTML())

    s = CompetencyTester()
    s.test()
    print(s.generateHTML())
