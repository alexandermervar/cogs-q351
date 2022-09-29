#!/usr/bin/python3


from grade.tests import Criterion, CriterionTester
from . import data
from .compete import compete, RandomPlayer
from .checker import check_player, check_board
from .instructor import RefBoard

import time
import math


class Qualifier(Criterion):
    summary = 'Which player class was used?'
    points = 0
    neverRedact = True
    ERROR = 1
    UNIMPLEMENTED = 2
    def generateText(self):
        if self.problem_code == self.ERROR:
            return self.playername + ' produces an error:\n\n'+self.representError(self.error)
        elif self.problem_code == self.UNIMPLEMENTED:
            return self.playername + ' is not yet implemented.'
        return f'Testing {self.playername}...'


class DepthGood(Criterion):
    TIMEOUT = 1
    def generateText(self):
        if self.problem_code == self.TIMEOUT:
            return 'The above score reflects the fact that your AI timed out and could not complete all 100 boards.'
        return f'Your AI got a score of {self.score*100:.1f}% on the 100 board test suite.'

# give full credit to a 60%
class Depth1Good(DepthGood):
    summary = 'At depth 1, picks moves scoring at least 60% of the best moves.'
    points = 2
    neverRedact = True

# give full credit to a 70%
class Depth3Good(DepthGood):
    summary = 'At depth 3, picks moves scoring at least 70% of the best moves.'
    points = 3
    neverRedact = True

# give full credit to an 80%
class Depth5Good(DepthGood):
    summary = 'At depth 5, picks moves scoring at least 80% of the best moves.'
    points = 5
    neverRedact = True

class Matchup(Criterion):
    def generateHTML(self):
        html = '''<style type="text/css">\n.match-intro {font-size: 15px; }\n.match-checkbox {vertical-align: top; margin-left: 6px; }\n.match-container { display: none; margin-top: 10px; overflow-x: scroll }\n:checked + .match-container { display: block; }\n.match { width: max-content; }\n.match-board-cell { padding-top: 8px; padding-bottom: 8px; padding-right: 10px}\n.match-board-cell p { margin: 0; text-align: center; }</style>\n'''
        html += '''<style type="text/css">\n.mancala { border-collapse: collapse; }\n.mancala tr td {\nheight:25px;\nwidth:25px;\nborder:1px solid gray;\ntext-align:center;\n}\n</style>\n'''
        traces_game1, traces_game2 = self.traces
        turns_game1, turns_game2 = self.turns
        times_game1, times_game2 = self.times

        html += f'<span class="match-intro">Starting with board {self.trace}, you won {self.wins} out of a possible 2 games.</span><input type="checkbox" class="match-checkbox">\n'
        html += '<div class="match-container">\n<table class="match">\n<tr>\n'
        for trace, turn, time in zip(traces_game1, turns_game1, times_game1):
            html += '<td class="match-board-cell">\n'
            board = RefBoard(trace)
            if board.board_history and board.board_history[-1][-1] == 1:
                html += f'<p>{turn} ({time*1000:.0f}ms)</p>\n'
                html += board.getHTML()
                html += '<p>&nbsp;</p>\n'
            else:
                html += '<p>&nbsp;</p>\n'
                html += board.getHTML()
                html += f'<p>{turn} ({time*1000:.0f}ms)</p>\n'
            html += '</td>\n'
        html += '</tr>\n<tr>\n'
        for trace, turn, time in zip(traces_game2, turns_game2, times_game2):
            html += '<td class="match-board-cell">\n'
            board = RefBoard(trace)
            if board.board_history and board.board_history[-1][-1] == 1:
                html += f'<p>{turn} ({time*1000:.0f}ms)</p>\n'
                html += board.getHTML()
                html += '<p>&nbsp;</p>\n'
            else:
                html += '<p>&nbsp;</p>\n'
                html += board.getHTML()
                html += f'<p>{turn} ({time*1000:.0f}ms)</p>\n'
            html += '</td>\n'
        html += '</tr>\n</table>\n</div>\n'
        return html

class Random(Matchup):
    summary = 'Beats a Random AI as both player 1 and player 2 starting from a blank board.'
    points = 5
    neverRedact = True

class Instructor(Matchup):
    summary = 'Beats the instructor AI more than 50% of the time on midgame boards.'
    points = 10
    neverRedact = True

class CompetencyTester(CriterionTester):
    function_name = 'Competency'
    compilation_test_timeout = 3
    def __init__(self):
        CriterionTester.__init__(self, ['board', 'player'], [Qualifier, Depth1Good, Depth3Good, Depth5Good], timeout=90)

    def run(self, compilation_test=False):
        check_player(self, self.player)
        check_board(self, self.board)
        StudentBoard = self.board.Board
        first_board = StudentBoard()
        try:
            first_player = self.player.PlayerDP(1)
            first_player.findMove('')
            first_player.heuristic(first_board)
        except Exception as err:
            if err.__class__ is NotImplementedError:
                self.fail_criterion(Qualifier, problem_code=Qualifier.UNIMPLEMENTED, important=True, playername="PlayerDP")
            else:
                self.fail_criterion(Qualifier, problem_code=Qualifier.ERROR, important=True, error=err, playername="PlayerDP")
            try:
                first_player = self.player.PlayerAB(1)
                first_player.findMove('')
            except Exception as err:
                if err.__class__ is NotImplementedError:
                    self.fail_criterion(Qualifier, problem_code=Qualifier.UNIMPLEMENTED, important=True, playername="PlayerAB")
                else:
                    err.__suppress_context__ = True
                    self.fail_criterion(Qualifier, problem_code=Qualifier.ERROR, important=True, error=err, playername="PlayerAB")
                StudentPlayer = self.player.PlayerMM
            else:
                StudentPlayer = self.player.PlayerAB
        else:
            StudentPlayer = self.player.PlayerDP

        del first_board
        del first_player

        self.fail_criterion(Qualifier, playername=StudentPlayer.__name__)
        self.pass_criterion(Qualifier)

        player1 = StudentPlayer(1)
        player3 = StudentPlayer(3)
        player5 = StudentPlayer(5)

        total1 = 0
        total3 = 0
        total5 = 0

        timeout1 = False
        if compilation_test:
            timeout3 = 3
            timeout5 = 3
            cases = data.competency_cases[0:3]
        else:
            timeout3 = False
            timeout5 = False
            cases = data.competency_cases
        num_cases = len(cases)

        for i, case in enumerate(cases):
            r = set(case.rating.values())
            span = max(r) - min(r)
            low = min(r)
            if not span: continue

            if timeout1 < 3:
                start = time.perf_counter()
                move = player1.findMove(case.trace)
                try:
                    score = (case.rating[move] - low) / span
                except:
                    score = 0
                end = time.perf_counter()
                if end-start > .5:
                    timeout1 += 1

                total1 += score

            if timeout3 < 3:
                start = time.perf_counter()
                move = player3.findMove(case.trace)
                try:
                    score = (case.rating[move] - low) / span
                except:
                    score = 0
                end = time.perf_counter()
                if end-start > .5:
                    timeout3 += 1

                total3 += score

            if timeout5 < 3:
                start = time.perf_counter()
                move = player5.findMove(case.trace)
                try:
                    score = (case.rating[move] - low) / span
                except:
                    score = 0
                end = time.perf_counter()
                if end-start > .5:
                    timeout5 += 1

                total5 += score

        self.fail_criterion(Depth1Good, score=total1/num_cases)
        self.set_score(Depth1Good, int(2*total1/num_cases/.6))
        if timeout1:
            self.fail_criterion(Depth1Good, problem_code=Depth1Good.TIMEOUT)
        if total1/num_cases >= .6:
            self.pass_criterion(Depth1Good)

        self.fail_criterion(Depth3Good, score=total3/num_cases)
        self.set_score(Depth3Good, int(3*total3/num_cases/.7))
        if timeout3:
            self.fail_criterion(Depth3Good, problem_code=Depth3Good.TIMEOUT)
        if total3/num_cases >= .7:
            self.pass_criterion(Depth3Good)

        self.fail_criterion(Depth5Good, score=total5/num_cases)
        self.set_score(Depth5Good, int(5*total5/num_cases/.8))
        if timeout5:
            self.fail_criterion(Depth5Good, problem_code=Depth5Good.TIMEOUT)
        if total5/num_cases >= .8:
            self.pass_criterion(Depth5Good)

class GameplayTester(CriterionTester):
    function_name = 'Gameplay'
    def __init__(self):
        CriterionTester.__init__(self, ['board', 'player'], [Qualifier, Random, Instructor], timeout=120)

    def run(self, compilation_test=False):
        check_player(self, self.player)
        check_board(self, self.board)
        if compilation_test:
            return
        StudentBoard = self.board.Board
        first_board = StudentBoard()
        try:
            first_player = self.player.PlayerDP(1)
            first_player.findMove('')
            first_player.heuristic(first_board)
        except Exception as err:
            if err.__class__ is NotImplementedError:
                self.fail_criterion(Qualifier, problem_code=Qualifier.UNIMPLEMENTED, important=True, playername="PlayerDP")
            else:
                self.fail_criterion(Qualifier, problem_code=Qualifier.ERROR, important=True, error=err, playername="PlayerDP")
            try:
                first_player = self.player.PlayerAB(1)
                first_player.findMove('')
            except Exception as err:
                if err.__class__ is NotImplementedError:
                    self.fail_criterion(Qualifier, problem_code=Qualifier.UNIMPLEMENTED, important=True, playername="PlayerAB")
                else:
                    err.__suppress_context__ = True
                    self.fail_criterion(Qualifier, problem_code=Qualifier.ERROR, important=True, error=err, playername="PlayerAB")
                StudentPlayer = self.player.PlayerMM
            else:
                StudentPlayer = self.player.PlayerAB
        else:
            StudentPlayer = self.player.PlayerDP

        del first_board
        del first_player

        self.fail_criterion(Qualifier, playername=StudentPlayer.__name__)
        self.pass_criterion(Qualifier)

        traces, turns, times, wins = compete(StudentPlayer, StudentBoard, '', TestPlayer=RandomPlayer)
        self.fail_criterion(Random, important=True, trace='(empty)', traces=traces, turns=turns, times=times, wins=wins)
        if wins == 2:
            self.pass_criterion(Random)

        total_wins = 0
        for case in data.versus_cases:
            traces, turns, times, wins = compete(StudentPlayer, StudentBoard, case.trace)
            self.fail_criterion(Instructor, important=True, trace=case.trace, traces=traces, turns=turns, times=times, wins=wins)
            total_wins += wins
        if total_wins >= 10:
            self.pass_criterion(Instructor)
        self.set_score(Instructor, total_wins)
