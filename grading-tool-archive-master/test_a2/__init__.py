#!/usr/bin/python3

from .test_placevalue import PlaceValueTester
from .test_removevalue import RemoveValueTester
from .test_isvalidmove import IsValidMoveTester
from .test_getmostconstrainedspace import GetMostConstrainedSpaceTester
from .test_solve import SolveTester, CompetencyTester

testSuite = [PlaceValueTester, RemoveValueTester, IsValidMoveTester, GetMostConstrainedSpaceTester, SolveTester, CompetencyTester]
title = 'A2: Sudoku'

if __name__ == '__main__':
    from grade import generate_html

    #root_folder = '/home/aleite/Downloads/Assignment 2_all_submission_files/B351_Assignment 2'
    #folders = []

    #import os

    #for i in sorted(os.listdir(root_folder)):
    #    folder = os.path.join(root_folder, i)
    #    if os.path.isdir(folder): folders.append(folder)
    #generate_html.batchGrade(folders, testSuite, title)

    import sys

    if len(sys.argv) == 1:
        print("Need a student directory!")

    student_dir = sys.argv[1]
    generate_html.safeGrade(student_dir, 'output.html', testSuite, title)
