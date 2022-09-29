#!/usr/bin/python3

from grade.tests import Criterion, CriterionTester
from . import data
from .checker import check_player, check_board

import math
import numbers

class ConsidersValidMoves(Criterion):
    summary = '(Not base case) Calls board.getAllValidMoves() exactly once, possibly specifying an order on the pits.'
    points = 1
    INVALID_ORDER = 1
    CALLED_TWICE = 2
    NEVER_CALLED = 3
    CALLED_ON_BASE_CASE = 4

    def generateText(self):
        text = f'On {self.case.represent()}:\n'

        if self.problem_code == self.INVALID_ORDER:
            text += f"board.getAllValidMoves(order={self.order!r}) is called. order must be a permutation of [0,1,2,3,4,5]."
        if self.problem_code == self.CALLED_TWICE:
            text += f"board.getAllValidMoves is called more than one time."
        if self.problem_code == self.NEVER_CALLED:
            text += f"board.getAllValidMoves is never called."
        if self.problem_code == self.CALLED_ON_BASE_CASE:
            text += f"board.getAllValidMoves is called even though the case is a base case (end state or depth = 0)."

        return text

class MakeUndoMoves(Criterion):
    summary = '(Not base case) Calls board.makeMove(pit) and board.undoMove(pit) exactly once for each valid pit.'
    points = 2
    INVALID_MOVE = 1 # move not in _validMovesReturned
    CALLED_TWICE = 2
    MISSED_MOVE = 3  # based on _validMovesActual
    CALLED_ON_BASE_CASE = 4
    MISSED_UNDO = 5 # doesn't undo move even though move was made...

    def generateText(self):
        text = f'On {self.case.represent()}:\n'

        if self.problem_code == self.INVALID_MOVE:
            text += f"board.makeMove(move={self.pit!r}) is called, even though {self.pit!r} is not one of the valid moves returned by getAllValidMoves ({self.valid!r})."
        if self.problem_code == self.CALLED_TWICE:
            text += f"board.makeMove(move={self.pit!r}) is called more than one time."
        if self.problem_code == self.MISSED_MOVE:
            text += f"board.makeMove is not called on the moves {self.missed!r}, which are valid moves for the board."
        if self.problem_code == self.CALLED_ON_BASE_CASE:
            text += f"board.makeMove is called even though the case is a base case (end state or depth = 0)."
        if self.problem_code == self.MISSED_UNDO:
            text += f"board.undoMove() is not called between trying move {self.pit!r} and trying additional move {self.pit2!r}."

        return text

class ScoresMoves(Criterion):
    summary = '(Not base case) Recursively calls minimax on board after trying each move, with depth - 1, to score each valid move.'
    points = 3
    INVALID_MOVE = 1 # based on _childTracesMade
    CALLED_TWICE = 2
    MISSED_CHILD = 3 # based on _movesMade
    NO_MOVES  = 4 # if _movesMade is empty but _validMovesActual isn't.
    INCORRECT_DEPTH = 5 # expected=self._expectedDepth, attempted=depth)
    CALLED_ON_BASE_CASE = 6
    CALLED_ON_NON_BOARD = 7

    def generateText(self):
        text = f'On {self.case.represent()}:\n'

        if self.problem_code == self.INVALID_MOVE:
            text += f"self.minimax is called on board with trace {self.trace!r}, even though no such move was made."
        if self.problem_code == self.CALLED_TWICE:
            text += f"self.minimax is called more than one time on with trace {self.trace!r}."
        if self.problem_code == self.MISSED_CHILD:
            text += f"self.minimax is not called after trying moves resulting in traces {self.missed!r}."
        if self.problem_code == self.NO_MOVES:
            text += f"No credit is available because board.makeMove was never called."
        if self.problem_code == self.INCORRECT_DEPTH:
            text += f"A depth of {self.attempted!r} is passed to self.minimax -- {self.expected!r} expected."
        if self.problem_code == self.CALLED_ON_BASE_CASE:
            text += f"self.minimax is called even though the case is a base case (end state or depth = 0)."
        if self.problem_code == self.CALLED_ON_NON_BOARD:
            text += f"self.minimax is called on non-board object {self.called_on!r}"

        return text

class ReturnsMinimax(Criterion):
    summary = '(Not base case) Returns the maximum or minimum-scored move and its score, based on board.turn.'
    points = 5
    INVALID_MOVE = 1   # something not in the actual valid moves of the board (self.move, self.valid)
    WRONG_STRATEGY = 2 # minimizing for max, or vice versa
    NO_STRATEGY = 3    # neither appears to be minimizing nor maximizing
    WRONG_SCORE = 4    # not the score that corresponds with move
    RETURNS_UNCONSIDERED_CHILD = 5    # returns a child move that did not have minimax called on it
    INVALID_FORMAT = 6

    def generateText(self):
        text = f'On {self.case.represent()}:\n'

        if self.problem_code == self.INVALID_MOVE:
            text += f"The returned move ({self.move!r}) is not one of the valid moves {self.valid!r} of the board."
        if self.problem_code == self.WRONG_STRATEGY:
            # student_move=student_move, mins=mins, maxes=maxes, turn=board.turn
            text += f"Uses the wrong minimization/maximization strategy: returns {self.student_move!r} when board.turn={self.turn} -- the minimum-scored moves are {self.mins!r} and the maximum-scored moves are {self.maxes!r}."
        if self.problem_code == self.NO_STRATEGY:
            text += f"Fails to properly apply either minimization or maximization strategy: returns {self.student_move!r} when board.turn={self.turn} -- the minimum-scored moves are {self.mins!r} and the maximum-scored moves are {self.maxes!r}."
        if self.problem_code == self.WRONG_SCORE:
            # move=student_move, student_score=self.interpretScore(student_score), actual_score
            text += f"Returns the wrong score for {self.move!r}: {self.student_score}. The correct score is {self.actual_score}."
        if self.problem_code == self.RETURNS_UNCONSIDERED_CHILD:
            text += f"The returned move ({self.move!r}) is not one of the moves scored by recursively calling minimax."
        if self.problem_code == self.INVALID_FORMAT:
            text += f"minimax returns {self.output!r}, which is not in the proper (move, score) tuple format."

        return text

class ScoresMovesAB(Criterion):
    summary = '(Not base case) Recursively calls alphaBeta after trying each move, with depth - 1, to score each valid move.'
    points = 1
    INVALID_MOVE = 1 # based on _childTracesMade
    CALLED_TWICE = 2
    MISSED_CHILD = 3 # based on _movesMade
    NO_MOVES  = 4 # if _movesMade is empty but _validMovesActual isn't.
    INCORRECT_DEPTH = 5
    CALLED_ON_BASE_CASE = 6
    CALLED_ON_NON_BOARD = 7

    def generateText(self):
        text = f'On {self.case.represent()}:\n'

        if self.problem_code == self.INVALID_MOVE:
            text += f"self.alphaBeta is called on a board with trace {self.trace!r}, even though no such move was made."
        if self.problem_code == self.CALLED_TWICE:
            text += f"self.alphaBeta is called more than one time with trace {self.trace!r}."
        if self.problem_code == self.MISSED_CHILD:
            text += f"self.alphaBeta is not called after making moves with traces {self.missed!r}."
        if self.problem_code == self.NO_MOVES:
            text += f"No credit is available because board.makeMove was never called and no moves were attempted."
        if self.problem_code == self.INCORRECT_DEPTH:
            text += f"A depth of {self.attempted!r} is passed to self.alphaBeta -- {self.expected!r} expected."
        if self.problem_code == self.CALLED_ON_BASE_CASE:
            text += f"self.alphaBeta is called even though the case is a base case (end state or depth = 0)."
        if self.problem_code == self.CALLED_ON_NON_BOARD:
            text += f"self.alphaBeta is called on non-board object {self.called_on!r}"

        return text

class ReturnsMinimaxAB(Criterion):
    summary = '(Not base case) Returns the first encountered maximum or minimum-scored move and its score, based on board.turn.'
    points = 2
    INVALID_MOVE = 1   # something not in the valid moves
    WRONG_STRATEGY = 2 # minimizing for max, or vice versa
    NO_STRATEGY = 3    # neither appears to be minimizing nor maximizing
    WRONG_SCORE = 4    # not the score that corresponds with move
    RETURNS_UNCONSIDERED_CHILD = 5    # returns a child move that did not have minimax called on it
    INVALID_FORMAT = 6
    NOT_FIRST_ENCOUNTERED = 7

    def generateText(self):
        text = f'On {self.case.represent()}:\n'

        if self.problem_code == self.INVALID_MOVE:
            text += f"The returned move ({self.move!r}) is not one of the valid moves {self.valid!r} of the board."
        if self.problem_code == self.WRONG_STRATEGY:
            # student_move=student_move, mins=mins, maxes=maxes, turn=board.turn
            text += f"Uses the wrong minimization/maximization strategy: returns {self.student_move!r} when board.turn={self.turn} -- the minimum-scored moves are {self.mins!r} and the maximum-scored moves are {self.maxes!r}."
        if self.problem_code == self.NO_STRATEGY:
            text += f"Fails to properly apply either minimization or maximization strategy: returns {self.student_move!r} when board.turn={self.turn} -- the minimum-scored moves are {self.mins!r} and the maximum-scored moves are {self.maxes!r}."
        if self.problem_code == self.WRONG_SCORE:
            # move=student_move, student_score=self.interpretScore(student_score), actual_score
            text += f"Returns the wrong score for {self.move!r}: {self.student_score}. The correct score is {self.actual_score}."
        if self.problem_code == self.RETURNS_UNCONSIDERED_CHILD:
            text += f"The returned move ({self.move!r}) is not one of the moves scored by recursively calling alphaBeta."
        if self.problem_code == self.INVALID_FORMAT:
            text += f"alphaBeta returns {self.output!r}, which is not in the proper (move, score) tuple format."
        if self.problem_code == self.NOT_FIRST_ENCOUNTERED:
            if self.turn == 0:
                text += f"Returns {self.student_move!r}, which is not the first maximum-scored move encountered (maximum scored moves: {self.maxes!r})."
            if self.turn == 1:
                text += f"Returns {self.student_move!r}, which is not the first minimum-scored move encountered (minimum scored moves: {self.mins!r})."

        return text

class BaseReturnsEndScore(Criterion):
    points = 2
    summary = '(End state) Returns a null move and the appropriate score constant for board\'s terminal state.'
    MISSES_DRAW = 1
    MISSES_P1_WIN = 2
    MISSES_P2_WIN = 3
    VALID_MOVE = 4
    INVALID_FORMAT = 5

    def generateText(self):
        text = f'On {self.case.represent()}:\n'

        if self.problem_code == self.INVALID_FORMAT:
            text += f"At an end state, returns {self.output!r}, which is not in the proper (move, score) tuple format."
        if self.problem_code == self.VALID_MOVE:
            text += f"The returned move ({self.student_move!r}) is a valid move rather than a meaningless move (such as -1 or None)."
        if self.problem_code == self.MISSES_DRAW:
            text += f"Returns {self.student_score} on an end-game tie, rather than self.TIE_SCORE."
        if self.problem_code == self.MISSES_P1_WIN:
            text += f"Returns {self.student_score} on a player 1 victory, rather than self.P1_WIN_SCORE."
        if self.problem_code == self.MISSES_P2_WIN:
            text += f"Returns {self.student_score} on a player 2 victory, rather than self.P2_WIN_SCORE."

        return text

class BaseReturnsHeuristic(Criterion):
    points = 2
    summary = '(Non-end state + Depth = 0) Returns a null move and the heuristic value for board.'
    INCORRECT_SCORE = 1
    CALLS_HEURISTIC_ON_NON_BOARD = 2
    CALLS_HEURISTIC_ON_WRONG_BOARD = 3
    VALID_MOVE = 4
    INVALID_FORMAT = 5

    def generateText(self):
        text = f'On {self.case.represent()}:\n'

        if self.problem_code == self.INVALID_FORMAT:
            text += f"At an end state, returns {self.output!r}, which is not in the proper (move, score) tuple format."
        if self.problem_code == self.VALID_MOVE:
            text += f"The returned move ({self.student_move!r}) is a valid move rather than a meaningless move (such as -1 or None)."
        if self.problem_code == self.INCORRECT_SCORE:
            text += f"Returns the wrong score: {self.student_score}. The heuristic score for the provided board is {self.heuristic_value}."
        if self.problem_code == self.CALLS_HEURISTIC_ON_NON_BOARD:
            text += f"self.heuristic is called on non-board object {self.called_on!r}"
        if self.problem_code == self.CALLS_HEURISTIC_ON_WRONG_BOARD:
            text += f"self.heuristic is called on board with trace {self.trace!r}, instead of the board provided"

        return text

# Alpha/Beta Criteria
class AlphaBetaPassdown(Criterion):
    points = 5
    summary = 'Updates alpha or beta value (as appropriate) and passes values down to recursive calls.'

    FAILURE = 1
    NEVER_RECURS = 2

    def generateText(self):
        if self.problem_code == self.NEVER_RECURS:
            text = f"Your code never recursively calls self.alphaBeta, so you are not eligible for these points."
        if self.problem_code == self.FAILURE:
            text = f'On {self.case.represent()}:\n'
            if hasattr(self.child, 'trace'):
                trace = self.child.trace
            else:
                trace = '<no trace>'
            text += f"Your code recursively calls self.alphaBeta on child board with trace {trace} with (alpha, beta) = {self.student_ab!r}, at a time when the correct (alpha, beta) are {self.expected_ab!r}."

        return text

class AlphaBetaCutoff(Criterion):
    points = 3
    summary = 'If a cutoff occurs (alpha >= beta), does not make any further recursive calls.'

    FAILURE = 1
    NEVER_RECURS = 2

    def generateText(self):
        if self.problem_code == self.NEVER_RECURS:
            text = f"Your code never recursively calls self.alphaBeta, so you are not eligible for these points."
        if self.problem_code == self.FAILURE:
            text = f'On {self.case.represent()}:\n'
            if hasattr(self.child, 'trace'):
                trace = self.child.trace
            else:
                trace = '<no trace>'
            text += f"Your code recursively calls self.alphaBeta on child board with trace {trace} even though the current (alpha, beta) values should be {self.ab!r}, a cutoff condition."

        return text

class AlphaBetaReturn(Criterion):
    points = 2
    summary = 'If a cutoff occurs, returns the value that caused the cutoff and a null move.'

    NOT_A_NUMBER = 1
    NOT_ALPHA = 2
    NOT_BETA = 3
    INVALID_FORMAT = 4
    VALID_MOVE = 5

    def generateText(self):
        text = f'On {self.case.represent()}:\n'

        if self.problem_code == self.INVALID_FORMAT:
            text += f"At an end state, returns {self.output!r}, which is not in the proper (move, score) tuple format."
        if self.problem_code == self.VALID_MOVE:
            text += f"The returned move ({self.student_move!r}) is a valid move rather than a meaningless move (such as -1 or None)."
        if self.problem_code == self.NOT_A_NUMBER:
            text += f"The score returned by alphaBeta after a cutoff [should have] occurred was not a number ({self.returned!r})."
        if self.problem_code == self.NOT_ALPHA:
            text += f"When alphaBeta is called with a starting beta value of {self.beta!r} and max encounters a move with score {self.alpha!r}, it returns {self.returned!r} instead of that score, which caused the cutoff."
        if self.problem_code == self.NOT_BETA:
            text += f"When alphaBeta is called with a starting alpha value of {self.alpha!r} and min encounters a move with score {self.beta!r}, it returns {self.returned!r} instead of that score, which caused the cutoff."

        return text

class MinimaxTester(CriterionTester):
    function_name = 'minimax (logic)'
    def __init__(self):
        CriterionTester.__init__(self, ['board', 'player'], [BaseReturnsEndScore, BaseReturnsHeuristic, ConsidersValidMoves, MakeUndoMoves, ScoresMoves, ReturnsMinimax], timeout=2)
    def makeTestPlayer(self, StudentPlayer):
        StudentBoard = self.board.Board
        class TestBoard(StudentBoard):
            def __init__(self, parent, case):
                self._parent = parent
                self._case = case
                self._init = True
                StudentBoard.__init__(self, trace=case.trace)

                self._init = False
                self._validMovesActual = set(StudentBoard.getAllValidMoves(self))
                self._validMovesReturned = []
                self._movesMade = set()
                self._childTracesMade = set()
                self._getAllValidMovesCalled = False
                self._isBaseCase = False # set by minimax_test
            def getAllValidMoves(self, preorder=range(6)):
                if not self._init:
                    pits = list(preorder)
                    if sorted(pits) != sorted(range(6)):
                        self._parent.fail_criterion(ConsidersValidMoves, self._case, ConsidersValidMoves.INVALID_ORDER, order=pits)
                    if self._getAllValidMovesCalled:
                        self._parent.fail_criterion(ConsidersValidMoves, self._case, ConsidersValidMoves.CALLED_TWICE)
                    self._getAllValidMovesCalled = True
                    if self._isBaseCase:
                        self._parent.fail_criterion(ConsidersValidMoves, self._case, ConsidersValidMoves.CALLED_ON_BASE_CASE)
                    self._validMovesReturned = list(StudentBoard.getAllValidMoves(self, preorder))
                    return self._validMovesReturned
                return StudentBoard.getAllValidMoves(self, preorder)
            def makeMove(self, move):
                if not self._init:
                    if not move in self._validMovesReturned:
                        self._parent.fail_criterion(MakeUndoMoves, self._case, MakeUndoMoves.INVALID_MOVE, pit=move, valid=self._validMovesReturned)
                    if move in self._movesMade:
                         self._parent.fail_criterion(MakeUndoMoves, self._case, MakeUndoMoves.CALLED_TWICE, pit=move)
                    if self._isBaseCase:
                         self._parent.fail_criterion(MakeUndoMoves, self._case, MakeUndoMoves.CALLED_ON_BASE_CASE, pit=move)
                    self._movesMade.add(move)
                    if self.trace != self._case.trace:
                        lastPit = self._trace[-1]
                        self._parent.fail_criterion(MakeUndoMoves, self._case, MakeUndoMoves.MISSED_UNDO, pit=lastPit, pit2=move)

                StudentBoard.makeMove(self, move)
                if not self._init:
                    self._childTracesMade.add(self.trace)

        class TestPlayer(StudentPlayer):
            def __init__(self, parent, case):
                StudentPlayer.__init__(self, 3)

                self._parent = parent
                self._case = case
                self._childScores = {}
                self._expectedDepth = None # set by minimax_test
                self.board = None     # set by minimax_test

                # Variables used for alpha/beta
                self._alpha = None
                self._beta = None
                self._isMax = None
                self._testing_order = False
            P1_WIN_SCORE = 2**32 + 2*10**80 # above all states
            P2_WIN_SCORE = 2**32 + -2 # below everything
            TIE_SCORE = 2**32 + -1 # below all states
            NON_BOARD_HEURISTIC = 2**32 + 10**80 - 1
            NON_BOARD_SCORE = 2**32 + 10**80 - 2
            def interpretScore(self, score):
                if not isinstance(score, numbers.Number):
                    return repr(score)
                if score == self.P1_WIN_SCORE:
                    return str(score)+" (P1_WIN_SCORE)"
                if score == self.P2_WIN_SCORE:
                    return str(score)+" (P2_WIN_SCORE)"
                if score == self.TIE_SCORE:
                    return str(score)+" (TIE_SCORE)"
                if score == self.NON_BOARD_HEURISTIC:
                    return str(score)+" (heuristic value for non-board object)"
                if score == self.NON_BOARD_SCORE:
                    return str(score)+" (minimax score for non-board object)"
                if score < self.P2_WIN_SCORE or score > self.P1_WIN_SCORE:
                    return str(score)
                if 2**32 <= score and score < 2**32 + 10**80:
                    return str(score)+" (heuristic value for board with trace "+str(score-2**32)+")"
                if 2**32 + 10**80 <= score and score < 2**32 + 2 * 10**80:
                    return str(score)+" (minimax value for board with trace "+str(score-2**32-10**80)+")"
                return str(score)
            def heuristic(self, board):
                if not isinstance(board, StudentBoard):
                    self._parent.fail_criterion(BaseReturnsHeuristic, self._case, BaseReturnsHeuristic.CALLS_HEURISTIC_ON_NON_BOARD,
                        called_on=board)
                    return self.NON_BOARD_HEURISTIC
                elif board.trace != self._case.trace:
                    if hasattr(board, 'trace'):
                        self._parent.fail_criterion(BaseReturnsHeuristic, self._case, BaseReturnsHeuristic.CALLS_HEURISTIC_ON_WRONG_BOARD,
                            trace=board.trace)
                    else:
                        self._parent.fail_criterion(BaseReturnsHeuristic, self._case, BaseReturnsHeuristic.CALLS_HEURISTIC_ON_WRONG_BOARD,
                            trace=None)
                        return self.NON_BOARD_HEURISTIC
                return 2**32 + int(board.trace)
            def minimax(self, board, depth):
                if not isinstance(board, StudentBoard):
                    self._parent.fail_criterion(ScoresMoves, self._case, ScoresMoves.CALLED_ON_NON_BOARD,
                        called_on=board)
                    self._parent.fail_criterion(ScoresMovesAB, self._case, ScoresMovesAB.CALLED_ON_NON_BOARD,
                        called_on=board)
                    return None, self.NON_BOARD_SCORE
                if not board.trace in self._board._childTracesMade:
                    self._parent.fail_criterion(ScoresMoves, self._case, ScoresMoves.INVALID_MOVE, trace=board.trace)
                    self._parent.fail_criterion(ScoresMovesAB, self._case, ScoresMovesAB.INVALID_MOVE, trace=board.trace)
                if self._expectedDepth == -1:
                    self._parent.fail_criterion(ScoresMoves, self._case, ScoresMoves.CALLED_ON_BASE_CASE)
                    self._parent.fail_criterion(ScoresMovesAB, self._case, ScoresMovesAB.CALLED_ON_BASE_CASE)
                if board.trace in self._childScores:
                    self._parent.fail_criterion(ScoresMoves, self._case, ScoresMoves.CALLED_TWICE, trace=board.trace)
                    self._parent.fail_criterion(ScoresMovesAB, self._case, ScoresMovesAB.CALLED_TWICE, trace=board.trace)
                if not depth == self._expectedDepth:
                    self._parent.fail_criterion(ScoresMoves, self._case, ScoresMoves.INCORRECT_DEPTH, expected=self._expectedDepth, attempted=depth)
                    self._parent.fail_criterion(ScoresMovesAB, self._case, ScoresMovesAB.INCORRECT_DEPTH, expected=self._expectedDepth, attempted=depth)
                if self._testing_order:
                    self._childScores[board.trace] = 2**32 + 10**80 + int(self._board.trace) + int(board.trace[-1])//3 # we want some of the children to have the same value
                else:
                    self._childScores[board.trace] = 2**32 + 10**80 + int(board.trace) # generates appropriate child score here
                return None, self._childScores[board.trace]
            def alphaBeta(self, board, depth, alpha, beta):
                self._parent.everABRecurs = True
                if self._alpha >= self._beta: # crossed alpha and beta, should have had a cutoff by here
                    self._parent.fail_criterion(AlphaBetaCutoff, case=self._case, problem_code=AlphaBetaCutoff.FAILURE, child=board, ab=(self.interpretScore(self._alpha), self.interpretScore(self._beta)))
                if alpha != self._alpha or beta != self._beta: # they have the wrong values
                    self._parent.fail_criterion(AlphaBetaPassdown, case=self._case, problem_code=AlphaBetaPassdown.FAILURE, child=board, student_ab=(self.interpretScore(alpha), self.interpretScore(beta)), expected_ab=(self.interpretScore(self._alpha), self.interpretScore(self._beta)))
                move, score = self.minimax(board, depth)
                if self._isMax is True and score > self._alpha:
                    self._alpha = score
                if self._isMax is False and score < self._beta:
                    self._beta = score
                return move, score
            def minimax_test(self, depth, ab=None):
                board = TestBoard(self._parent, self._case)
                backup_board = TestBoard(self._parent, self._case)
                self._board = board
                self._childScores = {}
                self._expectedDepth = depth - 1
                if board.game_over or depth == 0:
                    board._isBaseCase = True
                else:
                    board._isBaseCase = False

                if board.turn == 0:
                    self._isMax = True
                else:
                    self._isMax = False
                if ab is None:
                    self._alpha = None
                    self._beta = None
                    self._isMax = None
                    output = StudentPlayer.minimax(self, board, depth)
                else:
                    self._alpha, self._beta = ab
                    output = StudentPlayer.alphaBeta(self, board, depth, self._alpha, self._beta)

                try:
                    student_move, student_score = output
                    valid = True
                except ValueError:
                    valid = False
                except TypeError:
                    valid = False

                if not board._isBaseCase:
                    if not board._getAllValidMovesCalled:
                        self._parent.fail_criterion(ConsidersValidMoves, self._case, ConsidersValidMoves.NEVER_CALLED)
                    missed_children = board._validMovesActual - board._movesMade
                    if missed_children and not (ab and self._alpha >= self._beta):
                        self._parent.fail_criterion(MakeUndoMoves, self._case, MakeUndoMoves.MISSED_MOVE, missed=missed_children)
                    unscored_children = board._childTracesMade - self._childScores.keys()
                    if unscored_children:
                        self._parent.fail_criterion(ScoresMoves, self._case, ScoresMoves.MISSED_CHILD, missed=unscored_children)
                        self._parent.fail_criterion(ScoresMovesAB, self._case, ScoresMovesAB.MISSED_CHILD, missed=unscored_children)
                    elif len(board._movesMade) == 0 and len(board._validMovesActual) > 0:
                        self._parent.fail_criterion(ScoresMoves, self._case, ScoresMoves.NO_MOVES)
                        self._parent.fail_criterion(ScoresMovesAB, self._case, ScoresMovesAB.NO_MOVES)

                    if not valid:
                        if ab is not None and self._alpha >= self._beta:
                            self._parent.fail_criterion(AlphaBetaReturn, self._case, AlphaBetaReturn.INVALID_FORMAT, output=output)
                        else:
                            self._parent.fail_criterion(ReturnsMinimax, self._case, ReturnsMinimax.INVALID_FORMAT, output=output)
                            self._parent.fail_criterion(ReturnsMinimaxAB, self._case, ReturnsMinimaxAB.INVALID_FORMAT, output=output)
                    elif ab is not None and self._alpha >= self._beta: # cutoff situation, want the value that caused the cutoff
                        if type(student_move) == int and student_move >= 0 and student_move < 6:
                            self._parent.fail_criterion(AlphaBetaReturn, self._case, AlphaBetaReturn.VALID_MOVE,
                                student_move=student_move)
                        if not isinstance(student_score, numbers.Number):
                            self._parent.fail_criterion(AlphaBetaReturn, self._case, AlphaBetaReturn.NOT_A_NUMBER, alpha=self._alpha, beta=self._beta, returned=student_score)
                        elif self._isMax and student_score != self._alpha:
                            self._parent.fail_criterion(AlphaBetaReturn, self._case, AlphaBetaReturn.NOT_ALPHA, alpha=self._alpha, beta=self._beta, returned=student_score)
                        elif (not self._isMax) and student_score != self._beta:
                            self._parent.fail_criterion(AlphaBetaReturn, self._case, AlphaBetaReturn.NOT_BETA, alpha=self._alpha, beta=self._beta, returned=student_score)
                    elif not student_move in board._validMovesActual:
                        self._parent.fail_criterion(ReturnsMinimax, self._case, ReturnsMinimax.INVALID_MOVE,
                            move=student_move, valid=board._validMovesActual)
                        self._parent.fail_criterion(ReturnsMinimaxAB, self._case, ReturnsMinimaxAB.INVALID_MOVE,
                            move=student_move, valid=board._validMovesActual)
                    else:
                        child_trace = board.trace + str(student_move)
                        if not child_trace in self._childScores.keys():
                            self._parent.fail_criterion(ReturnsMinimax, self._case, ReturnsMinimax.RETURNS_UNCONSIDERED_CHILD,
                                move=student_move)
                            self._parent.fail_criterion(ReturnsMinimaxAB, self._case, ReturnsMinimaxAB.RETURNS_UNCONSIDERED_CHILD,
                                move=student_move)
                        elif student_score != self._childScores[child_trace]:
                            self._parent.fail_criterion(ReturnsMinimax, self._case, ReturnsMinimax.WRONG_SCORE,
                                move=student_move, student_score=self.interpretScore(student_score), actual_score=self.interpretScore(self._childScores[child_trace]))
                            self._parent.fail_criterion(ReturnsMinimaxAB, self._case, ReturnsMinimaxAB.WRONG_SCORE,
                                move=student_move, student_score=self.interpretScore(student_score), actual_score=self.interpretScore(self._childScores[child_trace]))
                        moves_by_trace = {}
                        for move in board._validMovesActual:
                            moves_by_trace[board.trace + str(move)] = move
                        try:
                            mins = [moves_by_trace[trace] for trace in self._childScores.keys()
                                if trace in moves_by_trace and self._childScores[trace] == min(self._childScores.values())]
                            maxes = [moves_by_trace[trace] for trace in self._childScores.keys()
                                if trace in moves_by_trace and self._childScores[trace] == max(self._childScores.values())]
                        except (TypeError, ValueError): # invalid trace or empty list
                            mins = []
                            maxes = []
                        if student_move in mins:
                            if backup_board.turn == 0 and not student_move in maxes: # should be maximizing
                                self._parent.fail_criterion(ReturnsMinimax, self._case, ReturnsMinimax.WRONG_STRATEGY,
                                    student_move=student_move, mins=mins, maxes=maxes, turn=backup_board.turn)
                                self._parent.fail_criterion(ReturnsMinimaxAB, self._case, ReturnsMinimaxAB.WRONG_STRATEGY,
                                    student_move=student_move, mins=mins, maxes=maxes, turn=backup_board.turn)
                            if backup_board.turn == 1 and student_move != mins[0]: # this check relies on a Python 3.6+ feature -- _childScores.keys() order stable
                                self._parent.fail_criterion(ReturnsMinimaxAB, self._case, ReturnsMinimaxAB.NOT_FIRST_ENCOUNTERED,
                                    student_move=student_move, mins=mins, maxes=maxes, turn=backup_board.turn)
                        elif student_move in maxes:
                            if backup_board.turn == 1 and not student_move in mins: # should be minimizing
                                self._parent.fail_criterion(ReturnsMinimax, self._case, ReturnsMinimax.WRONG_STRATEGY,
                                    student_move=student_move, mins=mins, maxes=maxes, turn=backup_board.turn)
                                self._parent.fail_criterion(ReturnsMinimaxAB, self._case, ReturnsMinimaxAB.WRONG_STRATEGY,
                                    student_move=student_move, mins=mins, maxes=maxes, turn=backup_board.turn)
                            if backup_board.turn == 0 and student_move != maxes[0]: # this check relies on a Python 3.6+ feature
                                self._parent.fail_criterion(ReturnsMinimaxAB, self._case, ReturnsMinimaxAB.NOT_FIRST_ENCOUNTERED,
                                    student_move=student_move, mins=mins, maxes=maxes, turn=backup_board.turn)
                        else:
                            self._parent.fail_criterion(ReturnsMinimax, self._case, ReturnsMinimax.NO_STRATEGY,
                                student_move=student_move, mins=mins, maxes=maxes, turn=backup_board.turn)
                            self._parent.fail_criterion(ReturnsMinimaxAB, self._case, ReturnsMinimaxAB.NO_STRATEGY,
                                student_move=student_move, mins=mins, maxes=maxes, turn=backup_board.turn)
                elif board._isBaseCase:
                    if backup_board.game_over:
                        if not valid:
                            self._parent.fail_criterion(BaseReturnsEndScore, self._case, BaseReturnsEndScore.INVALID_FORMAT, output=output)
                        else:
                            if type(student_move) == int and student_move >= 0 and student_move < 6:
                                self._parent.fail_criterion(BaseReturnsEndScore, self._case, BaseReturnsEndScore.VALID_MOVE,
                                    student_move=student_move)
                            terminal_type = backup_board.winner
                            if terminal_type == -1 and student_score != self.TIE_SCORE:
                                self._parent.fail_criterion(BaseReturnsEndScore, self._case, BaseReturnsEndScore.MISSES_DRAW,
                                    student_score=self.interpretScore(student_score))
                            if terminal_type == 0 and student_score != self.P1_WIN_SCORE:
                                self._parent.fail_criterion(BaseReturnsEndScore, self._case, BaseReturnsEndScore.MISSES_P1_WIN,
                                    student_score=self.interpretScore(student_score))
                            if terminal_type == 1 and student_score != self.P2_WIN_SCORE:
                                self._parent.fail_criterion(BaseReturnsEndScore, self._case, BaseReturnsEndScore.MISSES_P2_WIN,
                                    student_score=self.interpretScore(student_score))
                    elif depth == 0:
                        if not valid:
                            self._parent.fail_criterion(BaseReturnsHeuristic, self._case, BaseReturnsHeuristic.INVALID_FORMAT, output=output)
                        else:
                            if type(student_move) == int and student_move >= 0 and student_move < 6:
                                self._parent.fail_criterion(BaseReturnsHeuristic, self._case, BaseReturnsHeuristic.VALID_MOVE,
                                    student_move=student_move)
                            if student_score != self.heuristic(backup_board):
                                self._parent.fail_criterion(BaseReturnsHeuristic, self._case, BaseReturnsHeuristic.INCORRECT_SCORE,
                                    student_score=self.interpretScore(student_score), heuristic_value=self.interpretScore(self.heuristic(backup_board)))
        return TestPlayer

    def run(self, compilation_test=False):
        check_player(self, self.player)
        check_board(self, self.board)
        TestPlayer = self.makeTestPlayer(self.player.PlayerMM)

        if compilation_test:
            cases = data.logic_cases[:2]
        else:
            cases = data.logic_cases
        for case in cases:
            player = TestPlayer(self, case)
            player.minimax_test(7)
            player.minimax_test(0)

class AlphaBetaTester(MinimaxTester):
    function_name = 'alphaBeta (logic)'
    def __init__(self):
        CriterionTester.__init__(self, ['board', 'player'], [BaseReturnsEndScore, BaseReturnsHeuristic, ConsidersValidMoves, MakeUndoMoves, ScoresMovesAB, ReturnsMinimaxAB,
            AlphaBetaPassdown, AlphaBetaCutoff, AlphaBetaReturn], timeout=2)

    def run(self, compilation_test=False):
        check_player(self, self.player)
        check_board(self, self.board)
        self.everABRecurs = False

        TestPlayer = self.makeTestPlayer(self.player.PlayerAB)

        if compilation_test:
            cases = data.logic_cases[:2]
        else:
            cases = data.logic_cases[5:20] + data.logic_cases[40:80]
        for case in cases:
            player = TestPlayer(self, case)
            player.minimax_test(0, (-math.inf, math.inf))
            base = 2**32 + 10**80 + int(case.trace)*10
            strides = [(-math.inf, 0), (0, math.inf), (-math.inf, math.inf), (-10, -4), (-5, 3), (-10, 15), (1, 4), (3, 8), (5, 10), (20, 40), (0, 1)]
            if compilation_test: strides = [strides[0], strides[3], strides[8]]
            ab_args = [(base+alpha_stride, base+beta_stride) for alpha_stride, beta_stride in strides]
            for ab in ab_args:
                player.minimax_test(7, ab)
            player._testing_order = True
            player.minimax_test(5, (2**32 + 10**80 + int(case.trace) - 5, 2**32 + 10**80 + int(case.trace) + 5))

        if not self.everABRecurs:
            self.fail_criterion(AlphaBetaPassdown, problem_code=AlphaBetaPassdown.NEVER_RECURS)
            self.fail_criterion(AlphaBetaCutoff, problem_code=AlphaBetaCutoff.NEVER_RECURS)

if __name__ == '__main__':
    import sys
    sys.path.append('../shared/')

    sys.path.append('/home/aleite/Downloads/a4/')

    s = MinimaxTester()
    s.test()
    print(s.generateText())
