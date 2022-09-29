#!/usr/bin/python3

from grade import tests
from . import data
from .checker import check_a5

import math
import builtins
from itertools import permutations

class DistanceCall(tests.Criterion):
    summary = 'Calls calc_euclidean_distance on each sample point with the classification point.'
    points = 5

    UNKNOWN_POINT1 = 0 # trigged when point1 isn't a sample point or a classification point
    UNKNOWN_POINT2 = 1 # same but for point 2
    SAME_POINT = 2     # comparing the same point
    BOTH_IN_SAMPLE = 3 # comparing two points in the sample data - not a sample point to the new classification point

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.UNKNOWN_POINT1:
            return intro + f'you call calc_euclidean_distance({self.point1!r}, {self.point2!r}) with point {self.point1!r}, which is neither the classification point nor a sample point.'
        if self.problem_code == self.UNKNOWN_POINT2:
            return intro + f'you call calc_euclidean_distance({self.point1!r}, {self.point2!r}) with point {self.point2!r}, which is neither the classification point nor a sample point.'
        if self.problem_code == self.SAME_POINT:
            return intro + f'you call calc_euclidean_distance({self.point1!r}, {self.point2!r}) which is comparing the same point. If this is a sample point, you should already know it\'s label.'
        if self.problem_code == self.BOTH_IN_SAMPLE:
            return intro + f'you call calc_euclidean_distance({self.point1!r}, {self.point2!r}) which is comparing the distance of two sample points.'

        return tests.Criterion.generateText(self)

class PickLabelCall(tests.Criterion):
    summary = 'Calls get_top_label on closest k labels after sorting by distance.'
    points = 10

    NOT_K_LABELS = 0  # triggered when the argument passed to the func is not of length K
    WRONG_LABELS = 1  # triggered when the argument passed to the func doesn't contain the right labels
    UNKNOWN_LABEL = 2 # triggered when the argument passed to the func has an unknown label
    NOT_CALLED = 3
    MULTIPLE_CALLS = 4

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.NOT_K_LABELS:
            return intro + f'you call get_top_label with {self.top_k_labels!r}, which is of size {len(self.top_k_labels)!r}. Needs to be of size k={self.case.k}.'
        if self.problem_code == self.WRONG_LABELS:
            return intro + f'you call get_top_label with {self.top_k_labels!r}, which does not contain the correct labels. Valid labels include: {list(set(self.case.closest_k))!r}.'
        if self.problem_code == self.UNKNOWN_LABEL:
            return intro + f'you call get_top_label with {self.top_k_labels!r}, which contains an unknown label.'

        if self.problem_code == self.NOT_CALLED:
            return intro + f'you don\'t call get_top_label.'
        if self.problem_code == self.MULTIPLE_CALLS:
            return intro + f'you call get_top_label multiple times. Ensure you\'re calling it only once, and return it\'s exact result.'
        return tests.Criterion.generateText(self)

class PickLabelReturn(tests.Criterion):
    summary = 'Returns the label determined by get_top_label.'
    points = 5

    WRONG_ANSWER = 0

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ANSWER:
            return intro + f'you return {self.student_value!r}, while get_top_label({self.top_k_labels!r}) returns {self.expected_value!r}.'
        return tests.Criterion.generateText(self)

class KNNClassifyTester(tests.CriterionTester):
    function_name = 'KNN classify_point'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a5'], [DistanceCall, PickLabelCall, PickLabelReturn])
    def load_modules(self):
        tests.CriterionTester.load_modules(self)

    def run(self, compilation_test=False):
        check_a5(self, self.a5)

        if compilation_test: upper = 5
        else: upper = len(data.knn_classify_cases)

        class Diagnostic_Classifier(self.a5.KNN_Classifier):
            def euclidean_distance(student, point1, point2):
                self.distance_args.append((point1, point2))
                try: return math.sqrt(sum([(point2[i] - point1[i])**2 for i in range(len(point1))]))
                except: return 0
            def get_top_label(student, top_k_labels):
                student_pick = super().get_top_label(top_k_labels)
                self.pick_label_calls.append((top_k_labels, student_pick))
                return student_pick

        # k, points, labels, test_point, closest_k
        for self.case in data.knn_classify_cases[:upper]:
            student_classifier = Diagnostic_Classifier(self.case.k)
            self.distance_args = []
            self.pick_label_calls = []

            student_label = student_classifier.classify_point(self.case.test_point, self.case.points, self.case.labels)

            for point1, point2 in self.distance_args:
                if point1 == point2: 
                    self.fail_criterion(DistanceCall, self.case, problem_code=DistanceCall.SAME_POINT, point1=point1, point2=point2)
                point1_in_sample = point1 in self.case.points
                point2_in_sample = point2 in self.case.points
                if not point1 == self.case.test_point and not point1_in_sample: 
                    self.fail_criterion(DistanceCall, self.case, problem_code=DistanceCall.P1_UNKNOWN, point1=point1, point2=point2)
                if not point2 == self.case.test_point and not point2_in_sample:
                    self.fail_criterion(DistanceCall, self.case, problem_code=DistanceCall.P2_UNKNOWN, point1=point1, point2=point2)
                if point1_in_sample and point2_in_sample: 
                    self.fail_criterion(DistanceCall, self.case, problem_code=DistanceCall.BOTH_IN_SAMPLE, point1=point1, point2=point2)

            if len(self.pick_label_calls) == 0:
                self.fail_criterion(PickLabelCall, self.case, problem_code=PickLabelCall.NOT_CALLED)
            elif len(self.pick_label_calls) > 1:
                self.fail_criterion(PickLabelCall, self.case, problem_code=PickLabelCall.MULTIPLE_CALLS)
            else:
                top_k_labels, student_pick = self.pick_label_calls[0]
                if not len(top_k_labels) == self.case.k:
                    self.fail_criterion(PickLabelCall, self.case, problem_code=PickLabelCall.NOT_K_LABELS, top_k_labels=top_k_labels)
                for label in top_k_labels:
                    if label not in self.case.closest_k:
                        self.fail_criterion(PickLabelCall, self.case, problem_code=PickLabelCall.WRONG_LABELS, top_k_labels=top_k_labels)
                    if label not in self.case.labels:
                        self.fail_criterion(PickLabelCall, self.case, problem_code=PickLabelCall.UNKNOWN_LABEL, top_k_labels=top_k_labels)

                if not student_label == student_pick:
                    self.fail_criterion(PickLabelReturn, self.case, problem_code=PickLabelReturn.WRONG_ANSWER, top_k_labels=top_k_labels, expected_value=student_pick, student_value=student_label)