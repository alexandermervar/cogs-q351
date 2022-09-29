#!/usr/bin/python3

import sys

from .test_fib import FibTester
from .test_firstlast import FirstLastTester
from .test_sumnodesrec import SumNodesRecTester
from .test_sumnodesnorec import SumNodesNoRecTester
from .test_compose import ComposeTester
from .test_twice import TwiceTester
from .test_valid import ValidTester
from .test_treetostring import TreeToStringTester

testSuite = [FibTester, FirstLastTester, SumNodesRecTester, SumNodesNoRecTester, ComposeTester, TwiceTester, ValidTester, TreeToStringTester]
title = 'A1: Python Methods'

if __name__ == '__main__':
    from grade import generate_html
    root_folder = '/home/aleite/Downloads/Assignment 1_all_submission_files/B351_Assignment 1'
    folders = []

    import os

    for i in sorted(os.listdir(root_folder)):
        folder = os.path.join(root_folder, i)
        if os.path.isdir(folder): folders.append(folder)
    generate_html.batchGrade(folders, testSuite, title)

#    generate_html.safeGrade('/home/aleite/Downloads/Assignment 1_all_submission_files/B351_Assignment 1/renfrog@iu.edu-2018-08-25T01:09:45.571200+00:00',
#                            'grade.html', testSuite, title, redact=False, include_subjective=True, github_link = 'https://google.com')
