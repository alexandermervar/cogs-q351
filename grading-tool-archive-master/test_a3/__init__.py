#!/usr/bin/python3

from .test_expansions import FringeExpansionTester, InformedExpansionTester
from .test_f_functions import UCSFFunctionTester, AStarFFunctionFactoryTester
from .test_searches import BFSTester, InformedSearchTester
from .test_heuristic import HeuristicTester
from .test_competency import CompetencyTester

testSuite = [FringeExpansionTester, BFSTester, UCSFFunctionTester,
    AStarFFunctionFactoryTester, HeuristicTester, InformedExpansionTester, InformedSearchTester, CompetencyTester]
title = 'A3: A* Search'

if __name__ == '__main__':
    import sys
    from grade import generate_html
    sys.path.append('/Users/mervar/Library/CloudStorage/OneDrive-IndianaUniversity/cogs-q351/grading-tool-archive-master/distribution/a3') #Yang: your directory of the State.py and Board.py
    root_folder = '/Users/mervar/Library/CloudStorage/OneDrive-IndianaUniversity/cogs-q351/grading-tool-archive-master/submissions/a3.py' #Yang: your directory of the a3.py file, which is the homework file you want to upload.
    folders = [root_folder] 

    import os
    
    for i in sorted(os.listdir(root_folder)):
        folder = os.path.join(root_folder, i)
        if os.path.isdir(folder): folders.append(folder)
    generate_html.batchGrade(folders, testSuite, title)
    
    

	'''
    if len(sys.argv) == 1:
        print("Need a student directory!")

    student_dir = sys.argv[1]
    print(generate_html.safeGrade(student_dir, testSuite, title))
	'''
