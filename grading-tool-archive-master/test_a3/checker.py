#!/usr/bin/python3

import inspect

def State__hash__(self):
    # this is necessary because we added an __eq__ method.
    # note that this means that you might have two State
    # instances that are "equal" but are counted as separate
    # keys in a dictionary
    return object.__hash__(self)

def check_a3(tester, a3):
    a3.State.State.__hash__ = State__hash__
    if '(denoted as 0)' in a3.Board.Board.__doc__:
        tester.set_plagiarism_flag()
    if 'depth' in inspect.signature(a3.ucs_f_function).parameters:
        pass
        #enable this whenever we change "depth" to "current_depth"
        #tester.set_plagiarism_flag()
    if hasattr(a3, 'ucs_f_value_function') and not hasattr(a3, 'ucs_f_function'):
        tester.set_plagiarism_flag()
        a3.ucs_f_function = a3.ucs_f_value_function
    else:
        def ucs_f_value_function(board, depth):
            tester.set_plagiarism_flag()
            return a3.ucs_f_function(board, depth)
        a3.ucs_f_value_function = ucs_f_value_function

    if hasattr(a3, 'a_star_f_value_function_factory') and not hasattr(a3, 'a_star_f_function_factory'):
        tester.set_plagiarism_flag()
        a3.a_star_f_function_factory = a3.a_star_f_value_function_factory
    else:
        def a_star_f_value_function_factory(heuristic, goal_board):
            tester.set_plagiarism_flag()
            return a3.a_star_f_function_factory(heuristic, goal_board)
        a3.a_star_f_value_function_factory = a_star_f_value_function_factory

    if hasattr(a3, 'my_new_heuristic') and not hasattr(a3, 'my_heuristic'):
        tester.set_plagiarism_flag()
        a3.my_heuristic = a3.my_new_heuristic
    else:
        def my_new_heuristic(current_board, goal_board):
            tester.set_plagiarism_flag()
            return a3.my_heuristic(current_board, goal_board)
        a3.my_new_heuristic = my_new_heuristic
