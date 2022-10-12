#!/usr/bin/python3

from .test_baseplayer import BasePlayerTester
from .test_minimax import MinimaxTester, AlphaBetaTester
from .test_minimax_correctness import MinimaxCorrectnessTester, ABCorrectnessTester
from .test_dp import PlayerDPTester
from .test_competency import CompetencyTester, GameplayTester

testSuite = [BasePlayerTester, MinimaxTester, MinimaxCorrectnessTester, AlphaBetaTester, ABCorrectnessTester, PlayerDPTester, CompetencyTester, GameplayTester]
title = 'A4: Minimax'

if __name__ == '__main__':
    import sys
    from grade import generate_html
    #sys.path.append('/home/wang-yang/eclipse-workspace/grading_B351/distribution/a3')
    root_folder = '../HW3'
    folders = [root_folder]

    import os

    for i in sorted(os.listdir(root_folder)):
        folder = os.path.join(root_folder, i)
        if os.path.isdir(folder): folders.append(folder)
    generate_html.batchGrade(folders, testSuite, title)
    
    '''
    from grade import generate_html

    import sys

    if len(sys.argv) == 1:
        print("Need a student directory!")

    student_dir = sys.argv[1]
    print(generate_html.defaultGrade(student_dir, testSuite, title, None)[3])
    #print(generate_html.defaultCompilationTest(student_dir, testSuite, title, None))
    '''