#!/usr/bin/python3

import random

from grade import tests

class NoRecursion(tests.Criterion):
    summary = 'Does NOT use recursion.'
    points = 0
    neverRedact = True
    RECURSION = 9
    def generateText(self):
        return 'Your code uses recursion.'

class SumsValues(tests.Criterion):
    summary = 'For each node that is considered, adds its value to the total.'
    points = 3
    MISSES_EMPTY = 1
    NEVER_ACCESSED_VALUE = 2
    RECURSION = 9
    def generateText(self):
        if self.problem_code == self.RECURSION:
            return 'Your code uses recursion.'
        elif self.problem_code == self.MISSES_EMPTY:
            return f'Does not add root value to total for empty node Node({self.expected}, []) -- returns {self.value} instead.'
        elif self.problem_code == self.NEVER_ACCESSED_VALUE:
            return f'Never accesses the value attribute of considered node {self.node}.'
        else:
            return tests.Criterion.generateText(self)

class ConsidersChildren(tests.Criterion):
    summary = 'For each node that is considered, also considers its subnodes.'
    points = 7
    DOUBLE_CONSIDER = 1
    MISSED_CHILDREN = 2
    NEVER_ACCESSED_CHILDREN = 3
    NEVER_ACCESSED_CHILDREN_ROOT = 4
    RECURSION = 9
    def generateText(self):
        if self.problem_code == self.RECURSION:
            return 'Your code uses recursion.'
        elif self.problem_code == self.DOUBLE_CONSIDER:
            return f'Considers node {self.node} more than once.'
        elif self.problem_code == self.MISSED_CHILDREN:
            return f'Does not consider all the subnodes of considered node {self.node}.'
        elif self.problem_code == self.NEVER_ACCESSED_CHILDREN:
            return f'Never accesses the subnodes attribute of considered node {self.node}.'
        elif self.problem_code == self.NEVER_ACCESSED_CHILDREN_ROOT:
            return f'Never accesses the subnodes attribute of root node {self.node}.'
        else:
            return tests.Criterion.generateText(self)

class Correctness(tests.Criterion):
    summary = 'Returns the correct total sum of all nodes\' values.'
    points = 10
    RECURSION = 9
    def generateText(self):
        if self.problem_code == self.RECURSION:
            return 'Your code uses recursion.'
        return f'Returns {self.value} for {self.node} -- {self.expected} expected.'

class SumNodesNoRecTester(tests.CriterionTester):
    function_name = 'iterSumNodes'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a1'], [NoRecursion, SumsValues, ConsidersChildren, Correctness])
    def run(self, compilation_test=False):
        try: 
            student_sumNodesNoRec = self.a1.sumNodesNoRec
            self.set_plagiarism_flag()
        except:
            try: student_sumNodesNoRec = self.a1.iterSumNodes
            except AttributeError: student_sumNodesNoRec = self.a1.sumNodes

        def failEverything(node):
            self.fail_criterion(NoRecursion, problem_code=NoRecursion.RECURSION)
            self.fail_criterion(SumsValues, problem_code=SumsValues.RECURSION)
            self.fail_criterion(ConsidersChildren, problem_code=ConsidersChildren.RECURSION)
            self.fail_criterion(Correctness, problem_code=Correctness.RECURSION)
            return 0

        self.a1.iterSumNodes = failEverything
        self.a1.recSumNodes = failEverything

        class Node:
            def __init__(self, value, subnodes):
                self._value = value
                self._subnodes = subnodes
                self.orig_subnodes = subnodes.copy()
            @property
            def value(node):
                self.considered.add(node)
                if node in self.value_accessed:
                    self.fail_criterion(ConsidersChildren, problem_code=ConsidersChildren.DOUBLE_CONSIDER, node=node)
                self.value_accessed.add(node)
                return node._value
            @property
            def children(node):
                self.set_plagiarism_flag() # real self here!
                return node.subnodes
            @property
            def subnodes(node):
                self.considered.add(node)
                self.subnodes_accessed.add(node)
                return node._subnodes
            def __repr__(self):
                return f'Node({self._value}, {self.orig_subnodes})'

        self.a1.Node = Node

        def ref_total(n):
            return n._value + sum(ref_total(m) for m in n._subnodes)

        # Check blank nodes
        top = 7 if compilation_test else 15
        for i in range(5,top):
            n = Node(i, [])
            self.considered = set()
            self.value_accessed = set()
            self.subnodes_accessed = set()

            value = student_sumNodesNoRec(n)
            if value != i:
                self.fail_criterion(SumsValues, problem_code=SumsValues.MISSES_EMPTY, value=value, expected=i)

        # Check trees

        def generateTreeRec(node):
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

            self.considered = set()
            self.value_accessed = set()
            self.subnodes_accessed = set()

            expected = ref_total(node)
            value = student_sumNodesNoRec(node)
            if not node in self.considered and not node in self.subnodes_accessed:
                self.fail_criterion(ConsidersChildren, problem_code=ConsidersChildren.NEVER_ACCESSED_CHILDREN_ROOT, node=node)
            if self.considered - self.value_accessed:
                missed = (self.considered - self.value_accessed).pop()
                self.fail_criterion(SumsValues, problem_code=SumsValues.NEVER_ACCESSED_VALUE, node=missed)
            if self.considered - self.subnodes_accessed:
                missed = (self.considered - self.subnodes_accessed).pop()
                self.fail_criterion(ConsidersChildren, problem_code=ConsidersChildren.NEVER_ACCESSED_CHILDREN, node=missed)
            for i in self.considered:
                if set(i._subnodes) - self.considered:
                    self.fail_criterion(ConsidersChildren, problem_code=ConsidersChildren.MISSED_CHILDREN, node=i)
                    break

            if value != expected:
                self.fail_criterion(Correctness, node=node, value=value, expected=expected)

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/b351/admin/sp19/Class Materials/assignments/a1/code')

    s = SumNodesNoRecTester()
    s.test()
    print(s.generateText())
