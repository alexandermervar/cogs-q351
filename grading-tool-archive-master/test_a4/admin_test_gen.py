#!/usr/bin/python3

# for everything, make sure to have equal numbers of min / max test cases!
# include several winning boards

# heuristic test cases:
# (inputs)
# trace

# competency test cases:
# (inputs)
# trace
# rating // rating[move] = score (fully computed)

# how I made the competency test cases:
# - compiled mancala_solver.c
# - used generateTrace to make a valid trace at a relatively long length.
# - if mancala_solver 80 <trace> returns, then the tree below the trace is relatively small.
# - used mancala_solver 80 <trace><next_move> for each next_move to get each move's validity and score.
# - ideal play is the value <trace> is assigned.
# - for each valid next move, add <next_move>: -|value(<trace>) - value(<trace><next_move>)| to the ratings dictionary.
# profit! :)

# how I made the vs test cases:
# - tried to find a good mix of obvious wins for one player and balanced boards
# - aim to have ones with relatively

# minimax logic test cases:
# (inputs)
# trace
# /////////////////////////
# generate multiple depths
# generate multiple alpha / beta values to call with (make sure alpha < beta at the beginning)
#    have some where you're minimizing, and values > beta, but that's not a problem
#    have some where you're minimizing, and values < alpha, and that's a problem
#    have some where you're maximizing, and values > beta, and that's a problem
#    have some where you're maximizing, and values < alpha, but that's not a problem
#    for some involving cutoff, make sure that more than one thing will cause cutoff so that it won't matter if it's sorted last

# minimax correctness test cases:
# (inputs)
# trace
# depth
# (outputs)
# movesTree (nested lists of traces, where each list's first item is the parent)
# scores[trace] (the correct score of each valid trace)

# alpha-beta correctness test cases:
# (inputs)
# trace
# depth
# (outputs)
# movesTree (nested lists of traces, where each list's first item is the parent)
# scores[trace] (the correct score of each valid trace)
# call_ab[trace] (the (alpha, beta) pair trace was called with)

import random
import math
from instructor import RefBoard, KylePlayer, RandomPlayer

def generateTrace(length):
    while True:
        board = RefBoard()

        while len(board.trace) < length:
            options = list(board.getAllValidMoves())
            board.makeMove(random.choice(options))
            if board.game_over:
                break
        else:
            return board.trace

def generateFullTrace():
    board = RefBoard()

    while not board.game_over:
        options = list(board.getAllValidMoves())
        board.makeMove(random.choice(options))

    return board.trace

class SamplePlayer:
    def __init__(self, depth):
        self.depth = depth

        self.trace = None

        self.move = None
        self.movesTree = []
        self.scores = {}

        self.pruned = set()
        self.call_ab = {}

    P1_WIN_SCORE = 2**32
    P2_WIN_SCORE = -2**32
    TIE_SCORE = 0

    def heuristic(self, board):
        return board.p1_pot - board.p2_pot
    def minimax(self, board, depth):
        self.movesTree.append(board.trace)
        self.movesTree.append("OPEN")

        if board.winner == -1:
            move, score = None, self.TIE_SCORE
        elif board.winner == 0:
            move, score = None, self.P1_WIN_SCORE
        elif board.winner == 1:
            move, score = None, self.P2_WIN_SCORE
        elif depth == 0:
            move, score = None, self.heuristic(board)
        else:
            generator = ((board.makeMove(move), self.minimax(board, depth-1)[1], move, board.undoMove())[1:3] for move in board.getAllValidMoves())
            if board.turn == 0:
                score, move = max(generator)
            else:
                score, move = min(generator)

        self.scores[board.trace] = score
        self.movesTree.append("CLOSE")

        return move, score
    def findMove(self, trace):
        self.trace = trace
        board = RefBoard(trace=trace)
        self.minimax(board, self.depth)
    def alphaBeta(self, board, depth, alpha, beta):
        self.call_ab[board.trace] = (alpha, beta)
        self.movesTree.append(board.trace)
        self.movesTree.append("OPEN")

        if board.winner == -1:
            move, score = None, self.TIE_SCORE
        elif board.winner == 0:
            move, score = None, self.P1_WIN_SCORE
        elif board.winner == 1:
            move, score = None, self.P2_WIN_SCORE
        elif depth == 0:
            move, score = None, self.heuristic(board)
        else:
            bestMove = None
            bestScore = None
            for move in board.getAllValidMoves():
                board.makeMove(move)
                score = self.alphaBeta(board, depth-1, alpha, beta)[1]
                board.undoMove()
                if score is None: continue
                if board.turn == 0 and (bestScore is None or score > bestScore):
                    bestMove = move
                    bestScore = score
                    alpha = max(alpha, score)
                if board.turn == 1 and (bestScore is None or score < bestScore):
                    bestMove = move
                    bestScore = score
                    beta = min(beta, score)
                if beta <= alpha:
                    self.pruned.add(board.trace)
                    break
            move, score = bestMove, bestScore

        self.scores[board.trace] = score
        self.movesTree.append("CLOSE")

        return move, score
    def findMoveAB(self, trace):
        self.trace = trace
        board = RefBoard(trace=trace)
        self.alphaBeta(board, self.depth, -math.inf, math.inf)


# minimax correctness test cases:
# (inputs)
# trace
# depth
# isEnd[trace]
# heuristic[trace] (the heuristic value for every valid trace) [assign 0 outside of this range]
# (outputs)
# movesTree (nested lists of traces, where each list's first item is the parent)
# scores[trace] (the correct score of each valid trace)

if __name__ == '__main__':
    traces = []
    for i in range(80):
        fullgametrace = generateFullTrace()
        if i % 5: fullgametrace = fullgametrace[:-(i%5)]
        traces.append(fullgametrace)
    for i in range(40):
        earlygametrace = generateTrace(10+i%6)
        traces.append(earlygametrace)
    for i in range(60):
        lategametrace = generateTrace(45)
        traces.append(lategametrace)


    ab = False
    # random.shuffle(traces)
    print('[')
    for i, trace in enumerate(traces):
        if ab == 'logic':
            print(f' LogicCase(trace={trace!r}),\n')
            continue
        if i < 3:
            depth = 2
        elif i < 25:
            if ab:
                depth = i % 5 + 3
            else:
                depth = i % 3 + 3
        else:
            if ab:
                depth = i % 4 + 3
            else:
                depth = i % 2 + 3
        player = SamplePlayer(depth)
        if ab:
            player.findMoveAB(trace)
            print(f' ABCorrectnessCase(trace={player.trace!r}, depth={player.depth!r}, movesTree={player.movesTree!r}, call_ab={player.call_ab!r}, pruned={player.pruned!r}, scores={player.scores!r}),')
        else:
            player.findMove(trace)
            print(f' MinimaxCorrectnessCase(trace={player.trace!r}, depth={player.depth!r}, movesTree={player.movesTree!r}, scores={player.scores!r}),')
    print(']')
