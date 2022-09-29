#!/usr/bin/python3


from grade.tests import Criterion, CriterionTester
from . import data
from .checker import check_player, check_board

import math
import numbers

#self.P2_WIN_SCORE, self.TIE_SCORE, self.P1_WIN_SCORE all real-valued (1)
#self.P2_WIN_SCORE < self.TIE_SCORE < self.P1_WIN_SCORE (1)
#Heuristic is real-valued on all boards. (1)
#Heuristic always falls between self.P2_WIN_SCORE and self.P1_WIN_SCORE (2)

class RealValuedConstants(Criterion):
    summary = 'self.P2_WIN_SCORE, self.TIE_SCORE, self.P1_WIN_SCORE are all real-valued (and not infinity).'
    points = 1

    P1_NON_NUMBER = 1
    DRAW_NON_NUMBER = 2
    P2_NON_NUMBER = 3

class ConstantsOrder(Criterion):
    summary = 'self.P2_WIN_SCORE < self.TIE_SCORE < self.P1_WIN_SCORE.'
    points = 1

    NOT_REAL = 1
    BAD_ORDER = 2

class RealValuedHeuristic(Criterion):
    summary = 'Heuristic is real-valued on all boards.'
    points = 1

class HeuristicOrder(Criterion):
    summary = 'Heuristic always falls strictly between self.P2_WIN_SCORE and self.P1_WIN_SCORE.'
    points = 2

    WINSCORE_NOT_REAL = 1
    HEURISTIC_NOT_REAL = 2
    BAD_ORDER = 3

class BasePlayerTester(CriterionTester):
    function_name = 'BasePlayer'
    def __init__(self):
        CriterionTester.__init__(self, ['board', 'player'], [RealValuedConstants, ConstantsOrder, RealValuedHeuristic, HeuristicOrder], timeout=8)

    def run(self, compilation_test=False):
        check_player(self, self.player)
        check_board(self, self.board)
        BasePlayer = self.player.BasePlayer

        not_real = False
        if not isinstance(BasePlayer.P1_WIN_SCORE, numbers.Number) or not -math.inf < BasePlayer.P1_WIN_SCORE < math.inf:
            self.fail_criterion(RealValuedConstants, problem_code=RealValuedConstants.P1_NON_NUMBER, value=BasePlayer.P1_WIN_SCORE)
            not_real = True
        if not isinstance(BasePlayer.TIE_SCORE, numbers.Number) or not -math.inf < BasePlayer.P1_WIN_SCORE < math.inf:
            self.fail_criterion(RealValuedConstants, problem_code=RealValuedConstants.DRAW_NON_NUMBER, value=BasePlayer.TIE_SCORE)
            not_real = True
        if not isinstance(BasePlayer.P2_WIN_SCORE, numbers.Number) or not -math.inf < BasePlayer.P1_WIN_SCORE < math.inf:
            self.fail_criterion(RealValuedConstants, problem_code=RealValuedConstants.P2_NON_NUMBER, value=BasePlayer.P2_WIN_SCORE)
            not_real = True

        if not_real:
            self.fail_criterion(ConstantsOrder, problem_code=ConstantsOrder.NOT_REAL)
            self.fail_criterion(HeuristicOrder, problem_code=HeuristicOrder.WINSCORE_NOT_REAL)
        elif not BasePlayer.P1_WIN_SCORE > BasePlayer.TIE_SCORE or not BasePlayer.TIE_SCORE > BasePlayer.P2_WIN_SCORE:
            self.fail_criterion(ConstantsOrder, problem_code=ConstantsOrder.BAD_ORDER,
                P1_WIN_SCORE=BasePlayer.P1_WIN_SCORE, TIE_SCORE=BasePlayer.TIE_SCORE, P2_WIN_SCORE=BasePlayer.P2_WIN_SCORE)


        player = BasePlayer(0)
        if compilation_test:
            cases = data.logic_cases[:5]
        else:
            cases = data.logic_cases
        for case in cases:
            board = self.board.Board(trace=case.trace)

            heuristic_val = player.heuristic(board)

            if not isinstance(heuristic_val, numbers.Number):
                self.fail_criterion(RealValuedHeuristic, case, heuristic_val=heuristic_val)
                self.fail_criterion(HeuristicOrder, problem_code=HeuristicOrder.HEURISTIC_NOT_REAL)
                break

            if not not_real:
                if not BasePlayer.P1_WIN_SCORE > heuristic_val or not heuristic_val > BasePlayer.P2_WIN_SCORE:
                    self.fail_criterion(HeuristicOrder, case, problem_code=HeuristicOrder.BAD_ORDER,
                        P1_WIN_SCORE=BasePlayer.P1_WIN_SCORE, heuristic_val=heuristic_val, P2_WIN_SCORE=BasePlayer.P2_WIN_SCORE)
