import random
import math

class RefBoard:
    def __init__(self, trace=None):
        #           p2_pits[5] [4] [3] [2] [1] [0]
        # p2_pot                                    p1_pot
        #           p1_pits[0] [1] [2] [3] [4] [5]
        self.board_history = []
        self.board = [4,4,4,4,4,4,0,4,4,4,4,4,4,0,0]
        self._trace = []
        self.game_over = False
        if not (trace is None):
            for c in trace:
                self.makeMove(int(c))

    @property
    def p1_pits(self):
        return self.board[0:6]

    @property
    def p1_pot(self):
        return self.board[6]

    @property
    def p2_pits(self):
        return self.board[7:13]

    @property
    def p2_pot(self):
        return self.board[13]

    @property
    def turn(self):
        return self.board[14]

    @turn.setter
    def turn(self, value):
        self.board[14] = value

    @property
    def winner(self):
        if not self.game_over:
            return None
        if self.p1_pot > self.p2_pot:
            return 0
        if self.p2_pot > self.p1_pot:
            return 1
        return -1

    def isValidMove(self, pit):
        if self.game_over:
            return False
        if pit < 0 or pit > 5:
            return False
        if self.turn == 0:
            return self.board[pit] > 0
        return self.board[7+pit] > 0

    def makeMove(self, move):
        # add move to stack
        self._trace.append(move)
        # create new board in stack
        self.board_history.append(self.board[:])

        player = self.turn
        pit = player*7 + move

        # remove stones from corresponding pit
        stones = self.board[pit]
        self.board[pit] = 0

        while stones > 0:
            # skip opponent's pot, otherwise move 1 forward
            if (pit == 5 and player == 1) or (pit == 12 and player == 0):
                pit += 2
            else:
                pit += 1
            # loop around
            pit %= 14
            # add stone to next pit
            self.board[pit] += 1
            stones -= 1
        # switch turns, unless the player's last stone landed in their pot
        if pit != 6 and pit != 13:
            self.turn = 1 - self.turn

            # do the crazy capturing thing
            side = pit // 7
            across_pit = 12 - pit
            if side == player and self.board[pit] == 1 and self.board[across_pit] != 0:
                player_pot = 7*player+6
                self.board[player_pot] += 1 + self.board[across_pit]
                self.board[pit] = 0
                self.board[across_pit] = 0

        # check whether the game is over, and award the bonus if so
        p1_total = sum(self.board[0:6])
        p2_total = sum(self.board[7:13])
        if p1_total == 0 or p2_total == 0 :
            self.board[6] += p1_total
            self.board[13] += p2_total
            self.board[0:6] = [0, 0, 0, 0, 0, 0]
            self.board[7:13] = [0, 0, 0, 0, 0, 0]
            self.game_over = True

    def undoMove(self):
        ''' Undoes the most recent move, returning the board to the previous state.
            Does not require the move to be specificially passed to the function. '''
        self.board = self.board_history.pop()
        self._trace.pop()
        self.game_over = False

    def getAllValidMoves(self, preorder=None):
        if preorder is None:
            preorder = range(6)
        if self.turn == 0:
            for i in preorder:
                if self.board[i] > 0:
                    yield i
        else:
            for i in preorder:
                if self.board[7+i] > 0:
                    yield i

    def print(self):
        print("   " + str(self.p2_pits[5]) + " " + str(self.p2_pits[4]) + " " + str(self.p2_pits[3]) +
         " " + str(self.p2_pits[2]) + " " + str(self.p2_pits[1]) + " " + str(self.p2_pits[0]))
        print("" + str(self.p2_pot) + "\t\t  " + str(self.p1_pot))
        print("   " + str(self.p1_pits[0]) + " " + str(self.p1_pits[1]) + " " + str(self.p1_pits[2]) +
         " " + str(self.p1_pits[3]) + " " + str(self.p1_pits[4]) + " " + str(self.p1_pits[5]))

    def printSpaced(self):
        #A spaced out printing method so that opt actually shows correctly
        print("   " + str(self.p2_pits[5]) + "   " + str(self.p2_pits[4]) + "   " + str(self.p2_pits[3]) +
         "   " + str(self.p2_pits[2]) + "   " + str(self.p2_pits[1]) + "   " + str(self.p2_pits[0]))
        print("" + str(self.p2_pot) + "\t\t\t  " + str(self.p1_pot))
        print("   " + str(self.p1_pits[0]) + "   " + str(self.p1_pits[1]) + "   " + str(self.p1_pits[2]) +
         "   " + str(self.p1_pits[3]) + "   " + str(self.p1_pits[4]) + "   " + str(self.p1_pits[5]))

    def getHTML(self):
        return f'<table class="mancala">\n<tr><td rowspan="2">{self.p2_pot}</td>' + ''.join(f'<td>{i}</td>' for i in reversed(self.p2_pits)) + f'<td rowspan="2">{self.p1_pot}</td></tr>\n<tr>' + \
            ''.join(f'<td>{i}</td>' for i in self.p1_pits) + '</tr></table>\n'

    @property
    def trace(self):
        return ''.join(str(move) for move in self._trace)

    @property
    def state(self):
        return hash(tuple(self.board))

class KylePlayer:
    P1_WIN_SCORE = 2000
    P2_WIN_SCORE = -2000
    TIE_SCORE =  0
    def __init__(self, maxDepth = 5):
        self.maxDepth = maxDepth
        self.resolved = {}

    ##################
    #      TODO      #
    ##################
    # performs minimax with alpha-beta pruning on board with depth.
    # alpha represents the score of max's current strategy
    # beta  represents the score of min's current strategy
    # in a cutoff situation, return the score that resulted in the cutoff
    # returns the best move and best score as a tuple
    def alphaBeta(self, board, depth, alpha, beta):
        winner = board.winner
        if (winner is not None):
            if(winner == 0):
                return (None, self.P1_WIN_SCORE)
            if(winner == 1):
                return (None, self.P2_WIN_SCORE)
            if(winner == -1):
                return (None, self.TIE_SCORE)
        if depth == 0:
            return (None, self.heuristic(board))
        if(board.turn == 0):
            bestScore = self.P2_WIN_SCORE - 1
            bestMove = -1
            for move in board.getAllValidMoves():
                board.makeMove(move)
                _, score = self.alphaBeta(board, depth - 1, alpha, beta)
                board.undoMove()
                if(score > bestScore):
                    bestScore = score
                    bestMove = move
                alpha = max(alpha, score)
                if alpha >= beta:
                    return (None, score)
                if(bestScore == self.P1_WIN_SCORE):
                    return (bestMove, bestScore)
            return (bestMove, bestScore)
        else:
            bestScore = self.P1_WIN_SCORE + 1
            bestMove = -1
            for move in board.getAllValidMoves():
                board.makeMove(move)
                _, score = self.alphaBeta(board, depth - 1, alpha, beta)
                board.undoMove()
                if(score < bestScore):
                    bestScore = score
                    bestMove = move

                beta = min(beta, score)
                if alpha >= beta:
                    return (None, score)

                if(bestScore == self.P2_WIN_SCORE):
                    return (bestMove, bestScore)
            return (bestMove, bestScore)

    def findMove(self, trace):
        board = RefBoard(trace)
        move, score = self.alphaBeta(board, self.maxDepth, -math.inf, math.inf)
        return move

    def heuristic(self, board):
        score = (board.p1_pot - board.p2_pot) * 15
        ## game over :( or :) maybe?
        if board.p1_pot > 25 or board.p2_pot > 25:
            return 1999 if board.p1_pot > 25 else -1999
        ## hoarder
        score += sum([(3-i)*board.p1_pits[i-1] for i in range(3)])
        score += sum(board.p1_pits)
        score -= sum([(3-i)*board.p2_pits[i-1] for i in range(3)])
        score -= sum(board.p2_pits)
        for i in range(6):
            ## captures
            pit = i if not board.turn else i + 7
            stones = board.board[pit]
            while stones > 0:
                if (pit == 5 and board.turn) or (pit == 12 and not board.turn):
                    pit += 2
                else: pit += 1
                pit %= 14
                stones -= 1
            new_side = pit // 7
            if board.turn == new_side and not board.board[pit] and board.board[12-pit]:
                score += (board.board[12-pit] + 1) * (1 - board.turn*2)
        return score

class RandomPlayer:
    def __init__(self):
        self.random = random.Random(13487951347859)
    def findMove(self, trace):
        board = RefBoard(trace)
        options = list(board.getAllValidMoves())
        return self.random.choice(options)
