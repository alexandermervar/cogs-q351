#!/usr/bin/python3

#import sys
#sys.path.append("/Users/yohlo/Dev/IU/b351/grading-tool-lib")

from .test_entropy import EntropyTester
from .test_info_gain import InfoGainTester
from .test_classify import ClassifyTester
from .test_euclidean_distance import DistanceTester
from .test_pick_label import PickLabelTester
from .test_knn_classify import KNNClassifyTester

testSuite = [EntropyTester, InfoGainTester, ClassifyTester, DistanceTester, PickLabelTester, KNNClassifyTester]
title = 'A5: Decision Trees and KNN'

if __name__ == '__main__':
    from grade import generate_html

    print(generate_html.defaultGrade('/Users/gjlahman/Documents/GitHub/B351/a5_solution', testSuite, title, None))

#    print(output)
#    print(score)