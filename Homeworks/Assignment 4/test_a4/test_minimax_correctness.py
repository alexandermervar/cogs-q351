#!/usr/bin/python3

from grade import tests
from . import data
from .checker import check_player, check_board
from .instructor import RefBoard
import math
import time

# extra bad style
def quickTraceToTable(trace):
    return RefBoard(trace).getHTML()

class NodesCorrect(tests.Criterion):
    summary = 'The arrangement of nodes is correct.'
    points = 3
    MISSING_NODE = 1
    EXTRA_NODE = 2
    WRONG_PARENT = 3
class ScoresCorrect(tests.Criterion):
    summary = 'Scores for each node are correct.'
    points = 7
    MISSING_SCORE = 1
    WRONG_SCORE = 2
class ABCorrect(tests.Criterion):
    summary = 'Alpha/beta values passed to each node are correct.'
    points = 5
    MISSING = 1
    WRONG = 2

class Tree(tests.Criterion):
    summary = 'Minimax trees should match.'
    points = 0
    neverRedact = True
    TIMEOUT = 1
    # Very nice tree style! Credit Ilya Pestov - https://codepen.io/Pestov/pen/BLpgm
    def generateHTML(self):
        if self.problem_code == self.TIMEOUT:
            return '<h6><strong>Your score for this problem reflects the fact that you timed out.</strong></h6>'

        html = '''<style type="text/css">\n.tree-container { margin-top: 10px; overflow-x: scroll }\n.tree { width: max-content; margin-top: -18px; }\n.tree * {margin: 0; padding: 0;}\n.tree ul { padding-top: 10px; position: relative; }\n.tree li { float: left; text-align: center; list-style-type: none; position: relative; padding: 10px 2px 0 2px; }\n.tree li::before, .tree li::after{ content: ''; position: absolute; top: 0; right: 50%; border-top: 1px solid #ccc; width: 50%; height: 10px; }\n.tree li::after{ right: auto; left: 50%; border-left: 1px solid #ccc; }\n.tree li:only-child::after, .tree li:only-child::before { left: 50%; width: 0; border-radius: 0; }\n.tree > ul > li::after, .tree > ul > li::before {display: none;}\n.tree > ul > li{ padding-top: 0;}\n.tree li:first-child::before, .tree li:last-child::after{ border: 0 none; }\n.tree li:last-child::before{ border-right: 1px solid #ccc; border-radius: 0 5px 0 0; }\n.tree li:first-child::after{ border-radius: 5px 0 0 0; }\n.tree ul ul::before{ content: ''; position: absolute; top: 0; left: 50%; border-left: 1px solid #ccc; width: 0; height: 10px; }\n.tree li a{ border: 1px solid #ccc; padding: 2px 4px; color: #333; font-family: arial, verdana, tahoma; font-size: 10px; display: inline-block; border-radius: 5px; }\n.tree li .problem { background-color: yellow; }\n</style>\n'''
        html += f'<h6>On {self.case.represent()}...</h6>\n'

        html += quickTraceToTable(self.case.trace)

        for tree, scores, description in [(self.student_tree, self.student_scores, 'Student code produces tree:'),
                                        (self.expected_tree, self.expected_scores, 'Expected tree:')]:
            html += '<div class="tree-container">\n<p>'+description+'</p>\n<div class="tree">\n<ul>\n'

            for trace in tree:
                if trace == 'OPEN':
                    html += '<ul>\n'
                elif trace == 'CLOSE':
                    html += '</ul>\n</li>\n'
                else:
                    if trace == self.case.trace:
                        display_trace = '(root)'
                    elif trace[0] == '*':
                        display_trace = trace[1:]
                    else:
                        display_trace = 'Move: '+trace[-1]
                    if trace in scores:
                        score = scores[trace]
                        if score == -2**32:
                            score = '<code>P2_WIN</code>'
                        if score == 2**32:
                            score = '<code>P1_WIN</code>'
                    else:
                        score = 'no score'
                    if trace in self.highlight:
                        anchor_class = ' class="problem"'
                    else:
                        anchor_class = ''
                    html += f'<li>\n<a{anchor_class}>{display_trace}<br>{score}</a>\n'
            html += '</ul>\n</div>\n</div>\n'

        return html.replace('<ul>\n</ul>', '')

class AlphaBetaTree(tests.Criterion):
    summary = 'Alpha/beta trees should match.'
    points = 0
    neverRedact = True
    TIMEOUT = 1
    # Very nice tree style! Credit Ilya Pestov - https://codepen.io/Pestov/pen/BLpgm
    def generateHTML(self):
        if self.problem_code == self.TIMEOUT:
            return '<h6><strong>Your score for this problem reflects the fact that you timed out.</strong></h6>'
        html = '''<style type="text/css">\n.abtree-container { margin-top: 10px; overflow-x: scroll }\n.abtree { width: max-content; margin-top: -18px; }\n.abtree * {margin: 0; padding: 0;}\n.abtree ul { padding-top: 10px; position: relative; }\n.abtree li { float: left; text-align: center; list-style-type: none; position: relative; padding: 10px 2px 0 2px; }\n.abtree li::before, .abtree li::after{ content: ''; position: absolute; top: 0; right: 50%; border-top: 1px solid #ccc; width: 50%; height: 40px; }\n.abtree li::after{ right: auto; left: 50%; border-left: 1px solid #ccc; }\n.abtree li:only-child::after, .abtree li:only-child::before { left: 50%; width: 0; border-radius: 0; }\n.abtree > ul > li::after, .abtree > ul > li::before {display: none;}\n.abtree > ul > li{ padding-top: 0;}\n.abtree li:first-child::before, .abtree li:last-child::after{ border: 0 none; }\n.abtree li:last-child::before{ border-right: 1px solid #ccc; border-radius: 0 5px 0 0; }\n.abtree li:first-child::after{ border-radius: 5px 0 0 0; }\n.abtree ul ul::before{ content: ''; position: absolute; top: 0; left: 50%; border-left: 1px solid #ccc; width: 0; height: 10px; }\n.abtree li span { position: relative; height: 30px; display: block; left: 50%; font-size: 10px; line-height: 12px; color: #333; text-align: left; margin-left: -10px; }\n.abtree li span.problem { color: red !important; }\n.abtree li a { border: 1px solid #ccc; padding: 2px 4px; color: #333; font-family: arial, verdana, tahoma; font-size: 10px; display: inline-block; border-radius: 5px; }\n.abtree li a.problem { background-color: yellow; }\n</style>\n'''
        html += f'<h6>On {self.case.represent()}...</h6>\n'

        html += quickTraceToTable(self.case.trace)

        for tree, scores, ab, description in [(self.student_tree, self.student_scores, self.student_ab, 'Student code produces tree:'),
                                        (self.expected_tree, self.expected_scores, self.expected_ab, 'Expected tree:')]:
            html += '<div class="abtree-container">\n<p>'+description+'</p>\n<div class="abtree">\n<ul>\n'

            for trace in tree:
                if trace == 'OPEN':
                    html += '<ul>\n'
                elif trace == 'CLOSE':
                    html += '</ul>\n</li>\n'
                else:
                    if trace == self.case.trace:
                        display_trace = '(root)'
                    else:
                        display_trace = 'Move: '+trace[-1]
                    if trace in scores:
                        score = scores[trace]
                        if score == -2**32:
                            score = '<code>P2_WIN</code>'
                        if score == 2**32:
                            score = '<code>P1_WIN</code>'
                        if score is None:
                            score = '<code>None</code>'
                    else:
                        score = 'no score'
                    if trace in ab:
                        alpha, beta = ab[trace]
                    else:
                        alpha, beta = None, None
                    if trace in self.highlight:
                        anchor_class = ' class="problem"'
                    else:
                        anchor_class = ''
                    if trace in self.highlight_ab:
                        ab_class = ' class="problem"'
                    else:
                        ab_class = ''
                    html += '<li>\n'
                    if trace != self.case.trace:
                        html += f'<span{ab_class}>'
                        for name, var in (('&alpha;: ', alpha), ('<br>&beta;: ', beta)):
                            if var == -2**32:
                                var = 'P2'
                            if var == 2**32:
                                var = 'P1'
                            if var == math.inf:
                                var = '&infin;'
                            if var == -math.inf:
                                var = '-&infin;'
                            html += f'{name}{var}'
                        html += '</span>\n'
                    html += f'<a{anchor_class}>{display_trace}<br>{score}</a>\n'
            html += '</ul>\n</div>\n</div>\n'

        return html.replace('<ul>\n</ul>', '')

class BaseCorrectnessTester(tests.CriterionTester):
    def makeTestPlayer(self, StudentPlayer, useAB):
        StudentBoard = self.board.Board
        StudentBoard._parent = self # fixed
        StudentBoard._case = None # shared between all instances, but changed every time
        # I'm modifying the student board directly here because we can't trust the way they clone it.
        StudentBoard._getAllValidMovesNormal = StudentBoard.getAllValidMoves
        def getAllValidMoves(self, preorder=range(6)):
            return StudentBoard._getAllValidMovesNormal(self, range(6))
        StudentBoard.getAllValidMoves = getAllValidMoves # overriding whatever order they put in

        class TestPlayer(StudentPlayer):
            P1_WIN_SCORE = 2**32  # same as cases were built with
            P2_WIN_SCORE = -2**32 # same as cases were built with
            TIE_SCORE = 0        # same as cases were built with
            def __init__(self, parent, case):
                StudentPlayer.__init__(self, max_depth=case.depth)

                self._parent = parent
                self._case = case
                self._movesTree = [] # a list of traces plus "OPEN" and "CLOSE" commands
                self._scores = {} # by trace
                self._call_ab = {}
            def heuristic(self, board): # same as cases were built with
                if board.__class__ != StudentBoard: # not complaining here because we already do in the logic tests
                    return 0
                return board.p1_pot - board.p2_pot
            def minimax(self, board, depth):
                if not isinstance(board, StudentBoard):
                    trace = f'*{board!r}'
                else:
                    trace = board.trace
                self._movesTree.append(trace)
                self._movesTree.append("OPEN")
                move, score = StudentPlayer.minimax(self, board, depth)
                self._scores[trace] = score
                self._movesTree.append("CLOSE")
                return move, score
            def alphaBeta(self, board, depth, alpha, beta):
                if not isinstance(board, StudentBoard):
                    trace = f'*{board!r}'
                else:
                    trace = board.trace
                self._movesTree.append(trace)
                self._movesTree.append("OPEN")
                self._call_ab[board.trace] = (alpha, beta)
                move, score = StudentPlayer.alphaBeta(self, board, depth, alpha, beta)
                self._scores[trace] = score
                self._movesTree.append("CLOSE")
                return move, score
            def findMove_test(self):
                move = self.findMove(self._case.trace)
                # check children tree:
                #   check that everything that appears in one appears in the other, and that everything has the same parent in each
                relevantTraces = set(self._movesTree).union(self._case.movesTree)
                relevantTraces.discard("OPEN")
                relevantTraces.discard("CLOSE")

                missingTraces = set()
                extraTraces   = set()
                wrongScores   = set()
                missingScores = set()
                wrongParent   = set()
                self._wrongAB = set()

                self._showTree = False # |= this with the uniqueness returned by each fail_criterion call.

                for trace in relevantTraces:
                    if not trace in self._movesTree:
                        missingTraces.add(trace)
                        self._showTree |= self._parent.fail_criterion(NodesCorrect, self._case, NodesCorrect.MISSING_NODE, trace=trace)
                    elif not trace in self._case.movesTree:
                        extraTraces.add(trace)
                        self._showTree |= self._parent.fail_criterion(NodesCorrect, self._case, NodesCorrect.EXTRA_NODE, trace=trace)
                    else:
                        # figure out its parent in the each tree
                        parents = []
                        for tree in (self._movesTree, self._case.movesTree):
                            loc = tree.index(trace)
                            if loc == 0:
                                parents.append(None)
                                continue
                            depth = 1
                            while depth > 0:
                                if tree[loc] == "OPEN": depth -= 1
                                if tree[loc] == "CLOSE": depth += 1
                                loc -= 1
                            parents.append(tree[loc])
                        # check that they're the same
                        if not parents[0] == parents[1]:
                            wrongParent.add(trace)
                            self._showTree |= self._parent.fail_criterion(NodesCorrect, self._case, NodesCorrect.WRONG_PARENT,
                                trace=trace, attempted=parents[0], correct=parents[1])

                for trace in self._case.scores:
                    if not trace in self._scores:
                        missingScores.add(trace)
                        self._showTree |= self._parent.fail_criterion(ScoresCorrect, self._case, ScoresCorrect.MISSING_SCORE, trace=trace)
                    elif not self._scores[trace] == self._case.scores[trace]:
                        if False: # useAB and trace in self._case.pruned: # /* won't help to be lenient here */
                            if self._scores[trace] < self._case.call_ab[trace][0] or self._scores[trace] > self._case.call_ab[trace][1]:
                                continue
                        wrongScores.add(trace)
                        self._showTree |= self._parent.fail_criterion(ScoresCorrect, self._case, ScoresCorrect.WRONG_SCORE,
                            trace=trace, attempted=self._scores[trace], correct=self._case.scores[trace])

                if useAB: # parameter to function
                    for trace in self._case.call_ab:
                        if not trace in self._call_ab:
                            self._showTree |= self._parent.fail_criterion(ABCorrect, self._case, ABCorrect.MISSING, trace=trace)
                        elif self._call_ab[trace] != self._case.call_ab[trace]:
                            self._showTree |= self._parent.fail_criterion(ABCorrect, self._case, ABCorrect.WRONG, trace=trace,
                                attempted=self._call_ab[trace], correct=self._case.call_ab[trace])
                            self._wrongAB.add(trace)

                self._wrongTraces = missingTraces | extraTraces | wrongScores | missingScores | wrongParent
        return TestPlayer

class MinimaxCorrectnessTester(BaseCorrectnessTester):
    function_name = 'minimax (correctness)'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['board', 'player'], [NodesCorrect, ScoresCorrect, Tree], timeout=30)

    def run(self, compilation_test=False):
        check_player(self, self.player)
        check_board(self, self.board)
        TestPlayer = self.makeTestPlayer(StudentPlayer=self.player.PlayerMM, useAB=False)

        treesLeft = 3

        start = time.perf_counter()

        if compilation_test:
            cases = data.minimax_correctness_cases[:2]
        else:
            cases = data.minimax_correctness_cases
        for case in cases:
            if time.perf_counter() - start > 15:
                self.fail_criterion(Tree, case=case, problem_code=Tree.TIMEOUT)
                self.fail_all_criteria()
                break
            player = TestPlayer(self, case)
            player.findMove_test()
            if player._wrongTraces and treesLeft > 0 or player._showTree:
                self.fail_criterion(Tree, important=True, case=case, student_tree=player._movesTree, student_scores=player._scores,
                    expected_tree=case.movesTree, expected_scores=case.scores, highlight=player._wrongTraces)
                treesLeft -= 1

class ABCorrectnessTester(BaseCorrectnessTester):
    function_name = 'alphaBeta (correctness)'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['board', 'player'], [NodesCorrect, ScoresCorrect, ABCorrect, AlphaBetaTree], timeout=30)

    def run(self, compilation_test=False):
        check_player(self, self.player)
        check_board(self, self.board)
        TestPlayer = self.makeTestPlayer(StudentPlayer=self.player.PlayerAB, useAB=True)

        treesLeft = 3

        start = time.perf_counter()

        if compilation_test:
            cases = data.ab_correctness_cases[:2]
        else:
            cases = data.ab_correctness_cases[10:30] + data.ab_correctness_cases[75:100]
        for case in cases:
            if case.trace == '312440606323150663113': continue
            if time.perf_counter() - start > 15:
                self.fail_criterion(AlphaBetaTree, case=case, problem_code=AlphaBetaTree.TIMEOUT)
                self.fail_all_criteria()
                break
            player = TestPlayer(self, case)
            player.findMove_test()
            if (player._wrongTraces or player._wrongAB) and treesLeft > 0 or player._showTree:
                self.fail_criterion(AlphaBetaTree, important=True, case=case, student_tree=player._movesTree, student_scores=player._scores, student_ab=player._call_ab,
                    expected_tree=case.movesTree, expected_scores=case.scores, expected_ab=case.call_ab, highlight=player._wrongTraces, highlight_ab=player._wrongAB)
                treesLeft -= 1

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/Downloads/a4/')
    sys.path.append('../shared/')

    s = MinimaxTester()
    s.test()
    print(s.generateText())
