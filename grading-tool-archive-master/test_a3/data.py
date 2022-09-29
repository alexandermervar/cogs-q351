#!/usr/bin/python3

import random

from grade import tests

class Case(tests.Case):
    def __init__(self, board, distance, manhattan, alt_goal, alt_distance, alt_manhattan):
        self.board = board
        self.distance = distance
        self.manhattan = manhattan
        self.alt_goal = alt_goal
        self.alt_distance = alt_distance
        self.alt_manhattan = alt_manhattan
    def represent(self):
        return f'{self.board} ({self.distance} moves from goal)'
    def __repr__(self):
        return f'Case(board={self.board}, distance={self.distance}, manhattan={self.manhattan}, alt_goal={self.alt_goal}, alt_distance={self.alt_distance}, alt_manhattan={self.alt_manhattan})'

def generateBoard8(n_shifts):
    board = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    zero_row = 2
    zero_col = 2
    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    had = []
    for _ in range(n_shifts):
        random.shuffle(dirs)
        for shift_row, shift_col in dirs:
            new_row = zero_row + shift_row
            new_col = zero_col + shift_col
            if new_row < 0 or new_row > 2: continue
            if new_col < 0 or new_col > 2: continue

            board[zero_row][zero_col] = board[new_row][new_col]
            board[new_row][new_col] = 0

            zero_row = new_row
            zero_col = new_col

            break

    return board

def generateBoard15(n_shifts):
    board = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
    zero_row = 3
    zero_col = 3
    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    had = []
    for _ in range(n_shifts):
        random.shuffle(dirs)
        for shift_row, shift_col in dirs:
            new_row = zero_row + shift_row
            new_col = zero_col + shift_col
            if new_row < 0 or new_row > 3: continue
            if new_col < 0 or new_col > 3: continue

            board[zero_row][zero_col] = board[new_row][new_col]
            board[new_row][new_col] = 0

            zero_row = new_row
            zero_col = new_col

            break

    return board

def boardToCase(board, alt_goal, a3):
    board_obj = a3.Board.Board(board)
    if len(board) == 3:
        goal_board = a3.Board.Board([[1, 2, 3],
                                      [4, 5, 6],
                                      [7, 8, 0]])
    else:
        goal_board = a3.Board.Board([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]])
    alt_goal_board = a3.Board.Board(alt_goal)

    distance = a3.a_star_solver(board_obj, goal_board, a3.manhattan_distance).depth

    manhattan = a3.manhattan_distance(board_obj, goal_board)

    alt_distance = a3.a_star_solver(board_obj, alt_goal_board, a3.manhattan_distance).depth
    alt_manhattan = a3.manhattan_distance(board_obj, alt_goal_board)

    return Case(board, distance, manhattan, alt_goal, alt_distance, alt_manhattan)

if __name__ == '__main__':
    import sys
    # sys.path.append('/home/aleite/b351/admin/assignments/a3')
    sys.path.append('C:/Users/jacob/Desktop/admin/assignments/a3')

    import a3_solutions

    cases = []

    start_boards_8 = [
        [[1, 2, 3], [4, 5, 6], [7, 8, 0]],
        [[1, 2, 3], [0, 5, 6], [4, 7, 8]],
        [[1, 3, 6], [5, 2, 0], [4, 7, 8]],
        [[6, 2, 4], [3, 1, 7], [5, 0, 8]],
        [[3, 6, 8], [0, 4, 1], [2, 7, 5]],
        [[1, 2, 3], [4, 5, 6], [0, 7, 8]],
        [[5, 3, 1], [2, 0, 4], [6, 7, 8]],
        [[1, 0, 3], [5, 2, 6], [4, 7, 8]],
        [[0, 6, 2], [3, 1, 4], [5, 8, 7]],
        [[6, 2, 4], [5, 0, 3], [1, 8, 7]],
        [[3, 6, 2], [5, 1, 4], [8, 0, 7]],
        [[0, 3, 6], [1, 4, 2], [5, 8, 7]],
        [[2, 1, 4], [6, 5, 7], [0, 3, 8]],
        [[7, 3, 2], [0, 6, 4], [5, 1, 8]],
        [[2, 4, 0], [6, 3, 7], [5, 1, 8]],
        [[4, 3, 8], [2, 6, 1], [0, 7, 5]],
        [[4, 3, 6], [1, 8, 5], [2, 7, 0]],
        [[3, 1, 6], [2, 8, 0], [7, 4, 5]]
    ]

    start_boards_15 = [
        [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]],
        [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 0, 15]],
        [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 0], [13, 14, 15, 12]],
        [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 0, 14, 15]],
        [[1, 2, 3, 4], [5, 6, 7, 0], [9, 10, 11, 8], [13, 14, 15, 12]],
        [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]],
        [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 0, 12], [13, 14, 11, 15]],
        [[1, 2, 3, 4], [5, 6, 7, 8], [9, 0, 10, 12], [13, 14, 11, 15]],
        [[1, 0, 3, 4], [5, 2, 7, 8], [9, 6, 10, 12], [13, 14, 11, 15]],
        [[0, 1, 3, 4], [5, 2, 7, 8], [9, 6, 10, 12], [13, 14, 11, 15]],
        [[1, 2, 7, 3], [10, 6, 8, 4], [14, 11, 13, 15], [5, 9, 0, 12]],
        [[1, 2, 3, 4], [5, 6, 8, 7], [11, 0, 10, 15], [9, 14, 13, 12]],
        [[1, 2, 3, 4], [5, 6, 7, 8], [9, 11, 13, 12], [0, 10, 14, 15]],
        [[5, 11, 1, 4], [3, 8, 7, 0], [2, 15, 9, 12], [13, 10, 14, 6]],
        [[5, 1, 0, 7], [12, 15, 4, 10], [9, 14, 8, 3], [13, 6, 2, 11]],
        [[1, 2, 8, 3], [5, 6, 15, 12], [9, 0, 11, 10], [13, 7, 14, 4]],
        [[1, 2, 3, 12], [5, 6, 4, 0], [9, 10, 8, 15], [13, 14, 11, 7]],
        [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]],
        [[1, 2, 3, 4], [5, 6, 15, 0], [9, 10, 12, 7], [13, 14, 11, 8]],
        [[1, 2, 3, 4], [14, 11, 0, 5], [9, 12, 10, 8], [15, 7, 13, 6]],
        [[1, 0, 6, 2], [11, 3, 10, 7], [5, 13, 9, 15], [14, 4, 12, 8]],
        [[1, 2, 3, 4], [5, 6, 7, 8], [0, 15, 10, 12], [14, 9, 13, 11]]
    ]

    # for board in []:#start_boards_8:
    #     alt_goal = random.choice(start_boards_8[1:6])
    #     cases.append(boardToCase(board, alt_goal, a3_solutions))
    #
    # for n_shifts in range(20,160):
    #     board = generateBoard8(n_shifts)
    #     alt_goal = random.choice(start_boards_8[1:6])
    #     cases.append(boardToCase(board, alt_goal, a3_solutions))

    for board in start_boards_15:#[];
        alt_goal = random.choice(start_boards_15[1:6])
        cases.append(boardToCase(board, alt_goal, a3_solutions))

    # for n_shifts in range(20,160):
    #     board = generateBoard15(n_shifts)
    #     alt_goal = random.choice(start_boards_15[1:6])
    #     cases.append(boardToCase(board, alt_goal, a3_solutions))

    print('[')
    for case in cases:
        print(f' {case!r},')
    print(']')
else:
    import os
    a3_path = os.path.dirname(__file__)
    cases = eval(open(a3_path+'/test_cases.txt').read())
