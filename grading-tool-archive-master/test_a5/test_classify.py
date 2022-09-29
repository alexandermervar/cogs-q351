#!/usr/bin/python3

from grade import tests
from . import data
from .checker import check_a5

import math
import builtins

class ReturnsBaseCase(tests.Criterion):
    summary = 'If the node has a classification, returns that classification.'
    points = 2

    def generateText(self):
        intro = f'When {self.case.represent()} is called on {self.point!r}, '

        return intro + f'you return {self.returned!r} -- {self.label!r} expected.'

class GetsValue(tests.Criterion):
    summary = 'Otherwise, gets the value of the node\'s attribute at the point.'
    points = 2

    MISSING = 1
    WRONG_SUB = 2
    POPPED_VALUE = 3

    def generateText(self):
        intro = f'When {self.case.represent()} is called on {self.point!r}, '
        if self.problem_code == self.MISSING:
            return intro + f'you aren\'t taking {self.point!r}[{self.attribute!r}].'
        if self.problem_code == self.WRONG_SUB:
            return intro + f'you find {self.point!r}[{self.got!r}] -- you should be finding {self.point!r}[{self.attribute!r}].'
        if self.problem_code == self.POPPED_VALUE:
            return intro + f'you delete keys {self.popped!r} from the point provided.'
        return tests.Criterion.generateText(self)

class GetsChildNode(tests.Criterion):
    summary = 'If this value maps to one of the node\'s child nodes, gets the child node corresponding to the value.'
    points = 4

    MISSING = 1
    WRONG_SUB = 2
    POPPED_CHILD = 3

    def generateText(self):
        intro = f'When {self.case.represent()} is called on {self.point!r}, '
        if self.problem_code == self.MISSING:
            return intro + f'you aren\'t taking self.children[{self.value!r}].'
        if self.problem_code == self.WRONG_SUB:
            return intro + f'you find self.children[{self.got!r}] -- you should be finding self.children[{self.value!r}].'
        if self.problem_code == self.POPPED_CHILD:
            return intro + f'you delete keys {self.popped!r} from self.children.'
        return tests.Criterion.generateText(self)

class GetsOtherNode(GetsChildNode):
    summary = 'Otherwise, gets the child node corresponding to OTHER.'
    points = 4

class RecursiveCall(tests.Criterion):
    summary = 'Recursively calls the child node\'s classify_point method on the provided point argument, returning the result.'
    points = 4

    MISSING = 1
    WRONG_CHILD = 2
    WRONG_ARG = 3
    NO_RETURN = 4

    def generateText(self):
        intro = f'When {self.case.represent()} is called on {self.point!r}, '
        if self.problem_code == self.MISSING:
            return intro + f'you aren\'t calling the child node\'s classify_point method.'
        if self.problem_code == self.WRONG_CHILD:
            return intro + f'you\'re calling self.children[{self.key!r}].classify_point, instead of using the child node you found in the previous step.'
        if self.problem_code == self.WRONG_ARG:
            return intro + f'you\'re calling classify_point on {self.argument!r}, instead of the provided data point.'
        if self.problem_code == self.NO_RETURN:
            return intro + f'you returned {self.returned!r} instead of the value returned by the recursive call to classify_point.'
        return tests.Criterion.generateText(self)

class Correctness(tests.Criterion):
    summary = 'Correctly applies the decision tree under the node to classify the point provided. (Correctness.)'
    points = 4

    def generateText(self):
        return f'When {self.case.represent()} is called on {self.point!r}, you return {self.returned!r} -- {self.label!r} expected.'

class DiagnosticDict(dict):
    def __init__(self, val):
        dict.__init__(self, val)
        self.got = set()
        self.popped = set()
    def __getitem__(self, key):
        self.got.add(key)
        return dict.__getitem__(self, key)
    def __delitem__(self, key):
        self.popped.add(key)
        return dict.__delitem__(self, key)
    def get(self, key, default=None):
        self.got.add(key)
        return dict.get(self, key, default)
    def pop(self, key, default='unprovided string'):
        self.got.add(key)
        self.popped.add(key)
        if default != 'unprovided string':
            return dict.pop(self, key, default)
        else:
            return dict.pop(self, key)

class ClassifyTester(tests.CriterionTester):
    function_name = 'classify_point'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a5'], [ReturnsBaseCase, GetsValue, GetsChildNode, GetsOtherNode, RecursiveCall, Correctness])

    def make_classify(self, value):
        def classify(point):
            self.recursions.append(value)
            self.recursion_args.append(point)
            retval = f"<result of self.children[{value!r}].classify_point({point!r})>"
            self.recursion_returns.append(retval)
            return retval
        return classify

    def run(self, compilation_test=False):
        check_a5(self, self.a5)
        for self.case in data.classify_cases:
            # logic
            tree = eval(self.case.tree_string, self.a5.__dict__)
            for value, child in tree.children.items():
                child.classify_point = self.make_classify(value)
            tree._children = tree.children

            for _point, label in zip(self.case.points, self.case.labels):
                point = DiagnosticDict(_point)
                tree.children = DiagnosticDict(tree._children)
                self.recursions = []
                self.recursion_args = []
                self.recursion_returns = []

                returned = tree.classify_point(point)

                if tree.classification is not None:
                    if returned != tree.classification:
                        self.fail_criterion(ReturnsBaseCase, self.case, point=_point, returned=returned, label=label)
                    continue

                if not point.got:
                    self.fail_criterion(GetsValue, self.case, problem_code=GetsValue.MISSING, point=_point, attribute=tree.attribute)
                elif not tree.attribute in point.got:
                    # ick... want something like this:
                    # attribute = point.got.getitem()
                    for got in point.got: break
                    self.fail_criterion(GetsValue, self.case, problem_code=GetsValue.WRONG_SUB, point=_point, attribute=tree.attribute, got=got)

                if point.popped:
                    self.fail_criterion(GetsValue, self.case, problem_code=GetsValue.POPPED_VALUE, point=_point, popped=point.popped)

                value = _point[tree.attribute]

                if value in tree._children.keys():
                    GetsNode = GetsChildNode
                else:
                    value = self.a5.OTHER
                    GetsNode = GetsOtherNode

                # if present, got is the key for the child they actually got, rather than the one they were meant to get
                got = None
                if not tree.children.got:
                    self.fail_criterion(GetsNode, self.case, problem_code=GetsNode.MISSING, point=_point, value=value)
                elif not value in tree.children.got:
                    # ick... want something like this:
                    # attribute = point.got.getitem()
                    for got in tree.children.got: break
                    self.fail_criterion(GetsNode, self.case, problem_code=GetsNode.WRONG_SUB, point=_point, value=value, got=got)

                if tree.children.popped:
                    self.fail_criterion(GetsNode, self.case, problem_code=GetsNode.POPPED_CHILD, point=_point, popped=tree.children.popped)

                if not self.recursions:
                    self.fail_criterion(RecursiveCall, self.case, problem_code=RecursiveCall.MISSING, point=_point)
                    continue

                if not value in self.recursions and not got in self.recursions:
                    self.fail_criterion(RecursiveCall, self.case, problem_code=RecursiveCall.WRONG_CHILD, point=_point, key=self.recursions[0])
                if not point in self.recursion_args:
                    self.fail_criterion(RecursiveCall, self.case, problem_code=RecursiveCall.WRONG_ARG, point=_point, argument=self.recursion_args[0])
                if not returned in self.recursion_returns:
                    self.fail_criterion(RecursiveCall, self.case, problem_code=RecursiveCall.NO_RETURN, point=_point, returned=returned) # self.recursion_returns[0]

            # correctness
            tree = eval(self.case.tree_string, self.a5.__dict__)

            for point, label in zip(self.case.points, self.case.labels):
                returned = tree.classify_point(dict(point)) # before this was destroying unrelated results
                if returned != label:
                    self.fail_criterion(Correctness, self.case, point=point, returned=returned, label=label)