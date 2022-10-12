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

class ChecksResolved(Criterion):
    summary = 'Checks self.resolved for a heuristic value for the board\'s state and returns it without recalculation if found.'
    points = 5

    WRONG_VALUE = 1
    RECALCULATES = 2

    def generateText(self):
        text = f'On {self.case.represent()}:\n'

        if self.problem_code == self.WRONG_VALUE:
            text += f"After calling self.heuristic on a second board with the same state, the wrong value is returned. You return {self.second_val}, while the correct value is {self.original_val}. {self.stored_val} is the value stored in self.resolved."
        if self.problem_code == self.RECALCULATES:
            text += f"While calling self.heuristic on a second board with the same state, you still call BasePlayer.heuristic. {self.stored_val} is the value stored in self.resolved."

        return text

class CallsBasePlayer(Criterion):
    summary = 'Otherwise, calls BasePlayer.heuristic to calculate a heuristic value for this state. (Does not calculate it in this function.)'
    points = 3

    NO_CALL = 1
    WRONG_CALL = 2

    def generateText(self):
        text = f'On {self.case.represent()}:\n'

        if self.problem_code == self.NO_CALL:
            text += f"When calling self.heuristic for the first time, you do not make a call to BasePlayer.heuristic."
        elif self.problem_code == self.WRONG_CALL:
            text += f"When calling self.heuristic for the first time, you call BasePlayer.heuristic on boards with traces {self.calls}. You should only call it on the provided board."

        return text

class StoresValue(Criterion):
    summary = 'Stores calculated values in self.resolved, under the board\'s state.'
    points = 2

    NO_CHANGE = 1
    WRONG_KEY = 2
    WRONG_VALUE = 3


    def generateText(self):
        text = f'On {self.case.represent()}:\n'

        if self.problem_code == self.NO_CHANGE:
            text += f"There was no change in self.resolved."
        elif self.problem_code == self.WRONG_KEY:
            text += f"The wrong key was used to store the board in self.resolved.\nResolved: {self.resolved} -- Expected key: {self.correct_key}."
        elif self.problem_code == self.WRONG_VALUE:
            text += f"The wrong value was stored in self.resolved.\nStores {self.stored_val} -- expected {self.actual_val}."

        return text


class PlayerDPTester(CriterionTester):
    function_name = 'PlayerDP'
    def __init__(self):
        CriterionTester.__init__(self, ['board', 'player'], [ChecksResolved, CallsBasePlayer, StoresValue], timeout=8)

    def run(self, compilation_test=False):
        PlayerDP = self.player.PlayerDP

        def new_heuristic(player, board):
            self.base_heuristic_calls.append(board.trace)
            return board.p1_pot - board.p2_pot

        self.player.BasePlayer.heuristic = new_heuristic


        self.base_heuristic_calls = []

        player = PlayerDP(0)
        if not hasattr(player, 'resolved'):
            raise AttributeError('PlayerDP instance has no attribute resolved -- check your initializer.')

        if compilation_test:
            cases = data.logic_cases[0:5]
        else:
            cases = data.logic_cases
        for case in cases:
            board = self.board.Board(trace=case.trace)

            player.resolved = {}

            self.base_heuristic_calls = []
            heuristic_val = player.heuristic(board)

            if not self.base_heuristic_calls:
                self.fail_criterion(CallsBasePlayer, case=case, problem_code=CallsBasePlayer.NO_CALL)
            elif not self.base_heuristic_calls == [board.trace]:
                self.fail_criterion(CallsBasePlayer, case=case, problem_code=CallsBasePlayer.WRONG_CALL, calls=self.base_heuristic_calls)

            if not player.resolved:
                self.fail_criterion(StoresValue, case=case, problem_code=StoresValue.NO_CHANGE)
            elif not board.state in player.resolved:
                self.fail_criterion(StoresValue, case=case, problem_code=StoresValue.WRONG_KEY, resolved=player.resolved, correct_key=board.state)
            elif player.resolved[board.state] != heuristic_val:
                self.fail_criterion(StoresValue, case=case, problem_code=StoresValue.WRONG_VALUE, actual_val=heuristic_val, stored_val=player.resolved[board.state])

            self.base_heuristic_calls = []

            board2 = self.board.Board(trace=case.trace)
            heuristic_val_2 = player.heuristic(board2)

            if self.base_heuristic_calls:
                self.fail_criterion(ChecksResolved, case=case, problem_code=ChecksResolved.RECALCULATES, stored_val=player.resolved.get(board.state, None))
            if heuristic_val_2 != heuristic_val:
                self.fail_criterion(ChecksResolved, case=case, problem_code=ChecksResolved.WRONG_VALUE,
                    original_val=heuristic_val, stored_val=player.resolved.get(board.state, None), second_val=heuristic_val_2)
