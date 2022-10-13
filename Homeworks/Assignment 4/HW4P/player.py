#!/usr/bin/python3

### CSCI-B 351 / COGS-Q 351 Spring 2020
### Framework code copyright 2020 B351/Q351 instruction team.
### Do not copy or redistribute this code without permission
### and do not share your solutions outside of this class.
### Doing so constitutes academic misconduct and copyright infringement.

import math
import random
from board import Board
import copy

class BasePlayer:
    def __init__(self, max_depth):
        self.max_depth = max_depth

    # Assign integer scores to the three terminal states
    # P2_WIN_SCORE < TIE_SCORE < P1_WIN_SCORE
    # Access these with "self.TIE_SCORE", etc.
    P1_WIN_SCORE = 1
    P2_WIN_SCORE = -1
    TIE_SCORE = 0

    # Returns a heuristic for the board position
    # Good positions for 0 pieces should be positive and
    # good positions for 1 pieces should be negative
    # for all boards, P2_WIN_SCORE < heuristic(b) < P1_WIN_SCORE
    
    def heuristic(self, board):
        # returns a value based on the given board between -1 and 1
        # 1 is a win for player 1, -1 is a win for player 2
        # 0 is a tie
        # the closer to 0, the closer to a tie
        # the closer to 1, the closer to a win for player 1
        # the closer to -1, the closer to a win for player 2
        playerOneScore = board.p1_pot
        playerTwoScore = board.p2_pot
        playerOnePits = board.p1_pits
        playerTwoPits = board.p2_pits
        # add the number of stones in each pit to available score
        availableStones = sum(playerOnePits) + sum(playerTwoPits)
        if playerOneScore > playerTwoScore:
            return 1 - (availableStones / 48)
        elif playerTwoScore > playerOneScore:
            return -1 + (availableStones / 48)
        else:
            return 0
        

    def findMove(self, trace):
        raise NotImplementedError


class ManualPlayer(BasePlayer):
    def __init__(self, max_depth=None):
        BasePlayer.__init__(self, max_depth)

    def findMove(self, trace):
        board = Board(trace)
        opts = "  "
        for c in range(6):
            opts += " "+(str(c+1) if board.isValidMove(c) else ' ')+"  "

        while True:
            if(board.turn == 0):
                print("\n")
                board.printSpaced()
                print(opts)
                pit = input("Pick a pit (P1 side): ")
            else:
                print("\n")
                print(" " + opts[::-1])
                board.printSpaced()
                pit = input("Pick a pit (P2 side): ")
            try: pit = int(pit) - 1
            except ValueError: continue
            if board.isValidMove(pit):
                return pit

class RandomPlayer(BasePlayer):
    def __init__(self, max_depth=None):
        BasePlayer.__init__(self, max_depth)
        self.random = random.Random(13487951347859)
    def findMove(self, trace):
        board = Board(trace)
        options = list(board.getAllValidMoves())
        return self.random.choice(options)

class RemotePlayer(BasePlayer):
    def __init__(self, max_depth=None):
        BasePlayer.__init__(self, max_depth)
        self.instructor_url = "http://silo.cs.indiana.edu:30005"
        if self.max_depth > 8:
            print("It refused to go that hard. Sorry.")
            self.max_depth = 8
    def findMove(self, trace):
        import requests
        r = requests.get(f'{self.instructor_url}/getmove/{self.max_depth},{trace}')
        move = int(r.text)
        return move


class PlayerMM(BasePlayer):
    # performs minimax on board with depth.
    # returns the best move and best score as a tuple
    def minimax(self, board, depth):
        # evaluate which players turn it is
        move = -1
        score = -math.inf
        # go through all legal moves and find the best one
        if depth == 0:
            return move, self.heuristic(board)
        else:   
            for m in board.getAllValidMoves():
                # make a copy of the board array
                newBoard = copy.deepcopy(board)
                newBoard.makeMove(m)
                newScore = self.minValue(newBoard, depth - 1)
                if newScore > score:
                    score = newScore
                    move = m
            return move, score

    def minValue(self, board, depth):
        if depth == 0:
            return self.heuristic(board)
        else:
            score = math.inf
            for m in board.getAllValidMoves():
                newBoard = copy.deepcopy(board)
                newBoard.makeMove(m)
                newScore = self.maxValue(newBoard, depth - 1)
                if newScore < score:
                    score = newScore
            return score

    def maxValue(self, board, depth):
        if depth == 0:
            return self.heuristic(board)
        else:
            score = -math.inf
            for m in board.getAllValidMoves():
                newBoard = copy.deepcopy(board)
                newBoard.makeMove(m)
                newScore = self.minValue(newBoard, depth - 1)
                if newScore > score:
                    score = newScore
            return score

    def findMove(self, trace):
        board = Board(trace)
        move, score = self.minimax(board, self.max_depth)
        return move

class PlayerAB(BasePlayer):
    # performs minimax with alpha-beta pruning on board with depth.
    # alpha represents the score of max's current strategy
    # beta  represents the score of min's current strategy
    # in a cutoff situation, return the score that resulted in the cutoff
    # returns the best move and best score as a tuple
    #TODO: Implement this function
    def alphaBeta(self, board, depth, alpha, beta):
        raise NotImplementedError

    def findMove(self, trace):
        board = Board(trace)
        move, score = self.alphaBeta(board, self.max_depth, -math.inf, math.inf)
        return move

class PlayerDP(PlayerAB):
    ''' A version of PlayerAB that implements dynamic programming
        to cache values for its heuristic function, improving performance. '''
    def __init__(self, max_depth):
        PlayerAB.__init__(self, max_depth)
        self.resolved = {}

    # if a saved heuristic value exists in self.resolved for board.state, returns that value
    # otherwise, uses BasePlayer.heuristic to get a heuristic value and saves it under board.state
    #TODO: Implement this function
    def heuristic(self, board):
        raise NotImplementedError


class PlayerBonus(BasePlayer):
    ''' This class is here to give you space to experiment for your ultimate Mancala AI,
        your one and only PlayerBonus. This is only used for the extra credit tournament. '''
    #TODO: Implement this function
    def findMove(self, trace):
        raise NotImplementedError

#######################################################
###########Example Subclass for Testing
#######################################################

# This will inherit your findMove from above, but will override the heuristic function with
# a new one; you can swap out the type of player by changing X in "class TestPlayer(X):"
class TestPlayer(BasePlayer):
    # define your new heuristic here
    def heuristic(self):
        pass


