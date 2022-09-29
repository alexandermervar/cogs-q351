#!/usr/bin/python3

import random

from grade import tests

class AddsOwnValue(tests.Criterion):
    summary = 'Adds the node\'s value to the sum.'
    points = 3
    MISSES_EMPTY = 1
    MISSES_PARENT = 2
    def generateText(self):
        if self.problem_code == self.MISSES_EMPTY:
            return f'Returns {self.value} for Node({self.expected}, []) -- {self.expected} expected.'
        elif self.problem_code == self.MISSES_PARENT:
            return f'Adds {self.value} to subnodes\' totals for node with value {self.expected} -- {self.expected} expected.'
        else:
            return tests.Criterion.generateText(self)

class ChecksChildren(tests.Criterion):
    summary = 'Recursively gets the totals for each of the node\'s subnodes.'
    points = 5
    SELF_RECURSION = 1
    MISSED_CHILDREN = 2
    INVALID_RECURSION = 3
    def generateText(self):
        if self.problem_code == self.SELF_RECURSION:
            return f'Calls recSumNodes on the node itself instead of its subnodes, for {self.node}.'
        elif self.problem_code == self.MISSED_CHILDREN:
            return f'Fails to call recSumNodes on subnodes {self.missed}, for {self.node}.'
        elif self.problem_code == self.INVALID_RECURSION:
            return f'Calls recSumNodes on {self.argument} -- Node expected.'
        else:
            return tests.Criterion.generateText(self)

class SumsChildren(tests.Criterion):
    summary = 'Sums up the subnodes\' totals with the node\'s value.'
    points = 7
    MISSING_OWN_VALUE = 1
    MISSING_CHILDREN = 2
    def generateText(self):
        if self.problem_code == self.MISSING_OWN_VALUE:
            return 'Make sure you are including the node\'s own value in your function.'
        if self.problem_code == self.MISSING_CHILDREN:
            return 'Make sure you are including the subnodes\' totals in your function.'
        return f'Returns {self.value!r} for {self.node!r} -- {self.expected!r} expected.'

class SumNodesRecTester(tests.CriterionTester):
    function_name = 'recSumNodes'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a1'], [AddsOwnValue, ChecksChildren, SumsChildren])
    def run(self, compilation_test=False):
        def getAngry(node): raise RuntimeError('Cannot use iterSumNodes for this problem.')
        self.a1.iterSumNodes = getAngry
        self.a1.sumNodes = getAngry

        student_sumNodesRec = self.a1.recSumNodes

        class Node:
            def __init__(self, value, subnodes):
                self._value = value
                self._subnodes = subnodes
                self.orig_subnodes = subnodes.copy()
            @property
            def value(node):
                return node._value
            @property
            def children(node):
                self.set_plagiarism_flag() # real self here!
                return node.subnodes
            @property
            def subnodes(node):
                return node._subnodes
            def __repr__(self):
                return f'Node({self._value}, {self.orig_subnodes})'

        def ref_total(n):
            return n._value + sum(ref_total(m) for m in n._subnodes)

        def diagnostic_sumNodesRec(n):
            if not n.__class__ == Node:
                self.fail_criterion(ChecksChildren, problem_code=ChecksChildren.INVALID_RECURSION, argument=n)
                return 0
            got = ref_total(n)
            self.recent_calls[n] = got
            return got

        def zero_sumNodesRec(n):
            if not n.__class__ == Node:
                self.fail_criterion(ChecksChildren, problem_code=ChecksChildren.INVALID_RECURSION, argument=n)
                return 0
            return 0

        # Check AddsOwnValue
        self.a1.recSumNodes = zero_sumNodesRec
        children = [Node(3, [Node(1, [])]), Node(2, [])]

        top = 6 if compilation_test else 15
        for i in range(4,top):
            # check for empty node
            self.recent_calls = {}
            value = student_sumNodesRec(Node(i, []))
            if value != i:
                self.fail_criterion(AddsOwnValue, problem_code=AddsOwnValue.MISSES_EMPTY, value=value, expected=i)

            # check for parent node

            self.recent_calls = {}
            value = student_sumNodesRec(Node(i, children))
            if value != i:
                self.fail_criterion(AddsOwnValue, problem_code=AddsOwnValue.MISSES_PARENT, value=value, expected=i)

        self.a1.recSumNodes = diagnostic_sumNodesRec

        # Check recursion trees

        def generateTreeRec(node, certain=True):
            chance = random.random()
            if chance > .95: nchildren = 3
            elif chance > .9: nchildren = 2
            elif chance > .7: nchildren = 1
            else: nchildren = 0
            for _ in range(nchildren):
                child = Node(random.randint(-5,10), [])
                generateTreeRec(child)
                node._subnodes.append(child)
            node.orig_subnodes = node._subnodes.copy()

        num_checks = 5 if compilation_test else 50
        for i in range(num_checks):
            node = Node(random.randint(-5,10), [])
            while not node._subnodes:
                generateTreeRec(node)

            expected = ref_total(node)

            self.recent_calls = {}
            value = student_sumNodesRec(node)
            if node in self.recent_calls.keys():
                self.fail_criterion(ChecksChildren, problem_code=ChecksChildren.SELF_RECURSION, node=node)
            missed = set(node._subnodes) - self.recent_calls.keys()
            if missed:
                self.fail_criterion(ChecksChildren, problem_code=ChecksChildren.MISSED_CHILDREN, node=node, missed=missed)

            if value != expected:
                self.fail_criterion(SumsChildren, node=node, value=value, expected=expected)
                if expected - node.value == node.value: pass
                elif value == expected - node.value:
                    self.fail_criterion(SumsChildren, problem_code=SumsChildren.MISSING_OWN_VALUE)
                elif value == node.value:
                    self.fail_criterion(SumsChildren, problem_code=SumsChildren.MISSING_CHILDREN)

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/b351/admin/sp19/Class Materials/assignments/a1/code')

    s = SumNodesRecTester()
    s.test()
    print(s.generateText())
