#!/usr/bin/python3

# B351/Q351 Fall 2022
# Do not share these assignments or their solutions outside of this class.

###################################
#                                 #
# Assignment 3: Search Algorithms #
#                                 #
###################################

import State
import Board
import heapq

STOP = -1
CONTINUE = 0

# Possible Moves Enumeration
moveOne = (0, -1)
moveTwo = (0, 1)
moveThree = (-1, 0)
moveFour = (1, 0)


#################################
# Problem 1 - Fringe Expansion
#################################
# Objective:
# 1) Write a function that adds the possible states that we can get to
#    from the current state to the end of the fringe.
#
# Notes:
# (1) This function should not return or yield anything but just update the contents of the fringe
# (2) board_object.slide_blank is error-safe. It will return None if it is impossible to slide the blank

def expand_fringe(current_state, fringe):
    # Takes the possible states that we can get to from the current state and adds them to the end of the fringe
    # This function should not return or yield anything but just update the contents of the fringe
    # board_object.slide_blank is error-safe. It will return None if it is impossible to slide the blank
    # Go through each possible move and create a child state for each one
    for move in [moveOne, moveTwo, moveThree, moveFour]:
        # Create a child state for each possible move
        testCase = current_state.board.slide_blank(move)
        if testCase is not None:
            # If the move is possible, add it to the fringe
            fringe.append(State.State(testCase, current_state, current_state.depth + 1, 0))

########################################
# Problem 2 - BFS (Breadth First Search)
########################################
# Objectives:
# (1) Write a function that implements a single iteration of the BFS algorithm
#     by considering the first state from the fringe.
#     (Returns STOP if the fringe is empty.)
#     See the project documentation for more details.

def breadth_first_search(fringe, max_depth, goal_board):
    # Implement a single iteration of the BFS algorithm by considering the first state from the fringe.
    # Returns STOP if the fringe is empty.
    if len(fringe) == 0:
        return STOP
    # Get the first state from the fringe
    current_state = fringe.pop(0)
    # Check if the current state is the goal state
    if current_state.board == goal_board:
        return current_state
    # Check if the current state is at the maximum depth
    if current_state.depth == max_depth:
        return STOP
    # Expand the fringe
    expand_fringe(current_state, fringe)
    return CONTINUE

def uninformed_solver(start_board, max_depth, goal_board):
    """
        Looping function which calls breadth_first_search until it finds a solution (a State object) or
        until STOP has been returned. Does not consider States below max_depth.
        If the goal is reached, this function should return the Goal State,
        which includes a path to the goal. Otherwise, returns None.
    """
    fringe = [State.State(start_board, None, 0, 0)]
    found = CONTINUE
    while found == CONTINUE:
        found = breadth_first_search(fringe, max_depth, goal_board)
    if isinstance(found, State.State):
        # Found goal!
        return found
    # Max depth reached...
    return None


####################################
# Problem 3 - UCS f-value Function
####################################
# Objectives:
# (1) Write a function that takes a board and depth and returns the f-value
#     (priority) that board should have in a uniform-cost search scenario.

def ucs_f_function(board, current_depth):
    # In a uniform-cost search, the f-value is the depth of the state.
    return current_depth

###########################################
# Problem 4 - A* f-value Function Factory
###########################################
# Objectives:
# (1) Given a heuristic function and a goal board, returns a f-value FUNCTION
#     (like ucs_f_function) that evaluates boards and depths as in the A* algorithm.
#
# Notes:
# (1) It may be helpful to consult your solution for a1.compose here.

def a_star_f_function_factory(heuristic, goal_board):
    # Returns a function that accepts a board and depth and returns the f-value
    # The function returned applies the heuristic to the board provided at run-time
    # and the given goal board
    # The function returned produces the appropriate f-value for an A* search
    def f_function(board, current_depth):
        return current_depth + heuristic(board, goal_board)
    return f_function

# Here is an example heuristic function.
def manhattan_distance(current_board, goal_board):
    total = 0
    goal_matrix = goal_board.matrix
    for goal_r in range(len(goal_board.matrix)):
        for goal_c in range(len(goal_board.matrix[0])):
            val = goal_matrix[goal_r][goal_c]
            if val == 0:
                continue
            current_r, current_c = current_board.find_element(val)
            total += abs(goal_r - current_r) + abs(goal_c - current_c)
    return total

#################################
# Problem 5 - Your Own Heuristic
#################################
# Objectives:
# (1) Write a function that takes current_board and goal_board as arguments and
#     returns an estimate of how many moves it will take to reach the goal board.
#     Your heuristic must be admissible (never overestimate cost to goal), but
#     it does not have to be consistent (never overestimate step costs).
#
# Notes:
# (1) This heuristic should be admissible, but greater than (closer to the real
#     value than) the manhattan distance heuristic on average. That makes it a
#     better heuristic.


def my_heuristic(current_board, goal_board):
    # Returns an estimate of how many moves it will take to reach the goal board
    # Returns the euclidean distance between the current board and the goal board
    total = 0
    goal_matrix = goal_board.matrix
    for goal_r in range(len(goal_board.matrix)):
        for goal_c in range(len(goal_board.matrix[0])):
            val = goal_matrix[goal_r][goal_c]
            if val == 0:
                continue
            current_r, current_c = current_board.find_element(val)
            total += ((goal_r - current_r) ** 2 + (goal_c - current_c) ** 2) ** 0.5
    return total

#################################
# Problem 6 - Informed Expansion
#################################
# Objectives:
# (1) Write a function that expands the fringe using the f-value function
#     provided. Note that States automatically sort by their f-values.
#
# Notes:
# (1) This function should update the contents of the fringe using heap.

# TODO: Check with TA
def informed_expansion(current_state, fringe, f_function):
    # Expands the fringe using the f-value function provided
    # This function should update the contents of the fringe using heapq
    # board_object.slide_blank is error-safe. It will return None if it is impossible to slide the blank
    # Go through each possible move and create a child state for each one
    for move in [moveOne, moveTwo, moveThree, moveFour]:
        # Create a child state for each possible move
        testCase = current_state.board.slide_blank(move)
        if testCase is not None:
            # If the move is possible, add it to the fringe
            # The f-value of the child state is the current depth + the f-value of the board
            heapq.heappush(fringe, State.State(testCase, current_state, current_state.depth + 1, f_function(testCase, current_state.depth + 1)))

#################################
# Problem 7 - Informed Search
#################################
# Objectives:
# (1) Write a function that implements a single iteration of the
#     A*/UCS algorithm by considering the top-priority state from the fringe.
#     (Returns STOP if the fringe is empty.)
#     See the project documentation for more details.

# TODO: Check with TA
def informed_search(fringe, goal_board, f_function, explored):
# 1. If the fringe is empty then stop.
# 2. Otherwise, get the top state from the fringe.
# 3. If the current state’s board has already been seen and the current state’s f-value is not smaller than the previous f-value, then skip this state and continue.
# 4. Add the current state’s board and its f-value to the explored dictionary.
# 5. If the current state is the goal board, return the state.
# 6. Otherwise expand the fringe and continue.

# Explored is a dictionary mapping boards to their lowest encountered f-values
    if len(fringe) == 0:
        return STOP
    current_state = heapq.heappop(fringe)
    if current_state.board in explored:
        if explored[current_state.board] <= current_state.fvalue:
            return CONTINUE
    explored[current_state.board] = current_state.fvalue
    if current_state.board == goal_board:
        return current_state
    informed_expansion(current_state, fringe, f_function)
    return CONTINUE

def informed_solver(start_board, goal_board, f_function):
    """
        Looping function which calls informed_search until it finds a solution
        (a State object) or until STOP has been returned.
        If the goal is reached, this function should return the Goal State,
        which includes a path to the goal. Otherwise, returns None.
    """
    fringe = [State.State(start_board, None, 0, f_function(start_board, 0))]
    explored = {}
    found = CONTINUE
    while found == CONTINUE:
        found = informed_search(fringe, goal_board, f_function, explored)
    if isinstance(found, State.State):
        return found
    return None


def ucs_solver(start_board, goal_board):
    return informed_solver(start_board, goal_board, ucs_f_function)


def a_star_solver(start_board, goal_board, heuristic):
    f_function = a_star_f_function_factory(heuristic, goal_board)
    return informed_solver(start_board, goal_board, f_function)

#################################
# Bonus Problem - IDS (10pts)
#################################
# Implement IDS in any way you choose. You will probably want to write multiple
# helper functions; be sure to document these appropriately.
#
# ids should take a start board and goal board and then perform multiple
# depth-first searches, with the maximum depth increasing from 0 all the way to
# final depth.
#
# If there is a solution within final_depth moves, ids should return the board.


def ids(start_board, goal_board, final_depth):
    raise NotImplementedError
###########################
# Main method for testing #
###########################


def main():
    # 8-Puzzle Tests!
    goal_board = Board.Board([[1, 2, 3],
                              [4, 5, 6],
                              [7, 8, 0]])

    simple_board = Board.Board([[1, 2, 0],
                              [4, 5, 3],
                              [7, 8, 6]])

    hard_board = Board.Board([[3, 2, 4],
                                [1, 5, 0],
                                [7, 8, 6]])

    # Simple test case for expand_fringe
    fringe1 = []
    node1 = State.State(simple_board, None, 0, 0)
    expand_fringe(node1, fringe1)
    assert State.State(simple_board.slide_blank((-1, 0)), node1, 0, 0) not in fringe1, "moveThree should not be in fringe1"
    assert State.State(simple_board.slide_blank((0, -1)), node1, 0, 1) in fringe1, "moveOne should be in fringe1"

    # Simple test case for breadth_first_search
    fringe1 = []
    node1 = State.State(simple_board, None, 0, 0)
    expand_fringe(node1, fringe1)
    assert breadth_first_search(fringe1, 3, goal_board) == CONTINUE
    fringe1[0] = State.State(goal_board, node1, 0, 0)
    assert type(breadth_first_search(fringe1, 3, goal_board)) is State.State

    # Simple test case for ucs_f_function
    node1 = State.State(simple_board, None, 0, 0)
    assert ucs_f_function(node1.board, 0) == 0

    # Simple test case for a_star_f_function
    # -> This checks that the return type is correct
    assert hasattr(a_star_f_function_factory(None, goal_board), '__call__')

    # # This section is for you to create tests for your own heuristic
    # A test for the euclidean distance heuristic
    assert my_heuristic(simple_board, goal_board) <= manhattan_distance(simple_board, goal_board)
    assert my_heuristic(hard_board, goal_board) <= manhattan_distance(hard_board, goal_board)


    # Simple test for Informed Expansion
    node1 = State.State(simple_board, None, 0, 0)
    fringe1 = []
    informed_expansion(node1, fringe1, ucs_f_function)
    assert State.State(simple_board.slide_blank((-1, 0)), node1, 0, 0) not in fringe1
    assert State.State(simple_board.slide_blank((0, -1)), node1, 0, 1) in fringe1

    # Simple test for Informed Search
    fringe1 = []
    explored = {}
    node1 = State.State(simple_board, None, 0, 0)
    expand_fringe(node1, fringe1)
    assert informed_search(fringe1, goal_board, ucs_f_function, explored) == CONTINUE
    fringe1[0] = State.State(goal_board, node1, 0, 0)
    assert type(informed_search(fringe1, goal_board, ucs_f_function, explored)) is State.State

    # # Simple test for IDS
    # node1 = State.State(simple_board, None, 0, 0)
    # assert ids(node1.board, goal_board, 1) is None
    # result = ids(node1.board, goal_board, 2)
    # assert type(result) is Board.Board

    # 15-Puzzle Tests

    goal_board = Board.Board([[1, 2, 3, 4],
                              [5, 6, 7, 8],
                              [9, 10, 11, 12],
                              [13, 14, 15, 0]])

    simple_board = Board.Board([[1, 2, 3, 0],
                                [5, 6, 7, 4],
                                [9, 10, 11, 8],
                                [13, 14, 15, 12]])
    # print(goal_board)
    # print(simple_board)

    fringe1 = []
    node1 = State.State(simple_board, None, 0, 0)
    expand_fringe(node1, fringe1)
    assert State.State(simple_board.slide_blank((-1, 0)), node1, 0, 0) not in fringe1
    assert State.State(simple_board.slide_blank((0, -1)), node1, 0, 1) in fringe1

    # Simple test case for breadth_first_search
    fringe1 = []
    node1 = State.State(simple_board, None, 0, 0)
    expand_fringe(node1, fringe1)
    assert breadth_first_search(fringe1, 3, goal_board) == CONTINUE
    fringe1[0] = State.State(goal_board, node1, 0, 0)
    assert type(breadth_first_search(fringe1, 3, goal_board)) is State.State

    # Simple test case for ucs_f_function
    node1 = State.State(simple_board, None, 0, 0)
    assert ucs_f_function(node1.board, 0) == 0

    # Simple test case for a_star_f_function
    # -> This ONLY checks that the return type is correct
    assert hasattr(a_star_f_function_factory(None, goal_board), '__call__')

    # This section is for you to create tests for your own heuristic
    assert my_heuristic(simple_board, goal_board) <= manhattan_distance(simple_board, goal_board)

    # Simple test for Informed Expansion
    node1 = State.State(simple_board, None, 0, 0)
    fringe1 = []
    informed_expansion(node1, fringe1, ucs_f_function)
    assert State.State(simple_board.slide_blank((-1, 0)), node1, 0, 0) not in fringe1
    assert State.State(simple_board.slide_blank((0, -1)), node1, 0, 1) in fringe1

    # Simple test for Informed Search
    fringe1 = []
    explored = {}
    node1 = State.State(simple_board, None, 0, 0)
    expand_fringe(node1, fringe1)
    assert informed_search(fringe1, goal_board, ucs_f_function, explored) == CONTINUE
    fringe1[0] = State.State(goal_board, node1, 0, 0)
    assert type(informed_search(fringe1, goal_board, ucs_f_function, explored)) is State.State

    # # Simple test for IDS
    # node1 = State.State(simple_board, None, 0, 0)
    # assert ids(node1.board, goal_board, 1) == None
    # result = ids(node1.board, goal_board, 4)
    # assert type(result) is Board.Board


if __name__ == "__main__":
    main()