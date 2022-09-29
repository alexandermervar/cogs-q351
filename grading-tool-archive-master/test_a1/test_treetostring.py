#!/usr/bin/python3

import random

from grade import tests

class ConsiderByGeneration(tests.Criterion):
    summary = 'Considers every node by generation -- first the root, then its subnodes, then their subnodes...'
    points = 2
    MISSING_NODE = 1
    WRONG_ORDER = 2
    def generateText(self):
        if self.problem_code == self.MISSING_NODE:
            return f'While processing {self.task}, does not consider the value of {self.missed}.'
        if self.problem_code == self.WRONG_ORDER:
            return f'While processing {self.task}, considers {self.done} (generation {self.done_generation}) before the higher {self.abandoned}  (generation {self.abandoned_generation}).'

class Correctness(tests.Criterion):
    summary = 'Produces the desired output.'
    points = 8
    neverRedact = True
    def generateText(self):
        return f'For {self.task}, returns:\n{self.value}\n\nExpected:\n{self.expected}'

class TreeToStringTester(tests.CriterionTester):
    function_name = 'treeToString'
    isBonus = True
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a1'], [ConsiderByGeneration, Correctness])
    def run(self, compilation_test=False):
        student_treeToString = self.a1.treeToString

        class Node:
            def __init__(self, value, subnodes):
                self._value = value
                self._subnodes = subnodes
                self.orig_subnodes = subnodes.copy()
            @property
            def value(node):
                if (self.generation[node] - 1) in self.unconsidered and self.unconsidered[self.generation[node] - 1]:
                    example = set(self.unconsidered[self.generation[node] - 1]).pop()
                    self.fail_criterion(ConsiderByGeneration, problem_code=ConsiderByGeneration.WRONG_ORDER,
                        task=self.current_task, done=node, done_generation=self.generation[node],
                        abandoned=example, abandoned_generation=self.generation[example])
                self.unconsidered[self.generation[node]].discard(node)
                self.considered.add(node)
                return node._value
            @property
            def subnodes(node):
                self.considered.add(node)
                for child in node._subnodes:
                    if child in self.generation: continue
                    self.generation[child] = self.generation[node] + 1
                    if not self.generation[node] + 1 in self.unconsidered:
                        self.unconsidered[self.generation[node] + 1] = set()
                    self.unconsidered[self.generation[node] + 1].add(child)
                return node._subnodes
            @property
            def children(node):
                self.set_plagiarism_flag() # real self here!
                return node.subnodes
            def __repr__(self):
                return f'Node({self._value}, {self.orig_subnodes})'

        def ref_treeToString(node):
            generations = [[node]]
            while generations[-1]:
                generations.append([])
                for n in generations[-2]:
                    generations[-1] += n._subnodes
            generations = generations[:-1] # the last one is empty
            s = ''
            for gen in generations:
                for n in gen:
                    self.to_consider.add(n)
                    s += str(n._value)
                s += '\n'
            return s

        def generateTreeRec(node):
            chance = random.random()
            if chance > .95: nchildren = 3
            elif chance > .9: nchildren = 2
            elif chance > .7: nchildren = 1
            else: nchildren = 0
            for _ in range(nchildren):
                child = Node(random.randint(1,9), [])
                generateTreeRec(child)
                node._subnodes.append(child)
            node.orig_subnodes = node._subnodes.copy()

        def standardize(treestring): # this only works because every node's value is 1 character
            if type(treestring) != str: return treestring
            return '\n'.join(str(sorted(line)) for line in treestring.strip().split('\n'))

        if compilation_test:
            upper = 2
        else:
            upper = 50
        for i in range(upper):
            node = Node(random.randint(1,9), [])
            while not node._subnodes:
                generateTreeRec(node)

            self.current_task = node
            self.to_consider = set()
            self.considered = set()
            self.generation = {node: 0}
            self.unconsidered = {0: {node}}

            expected = ref_treeToString(node)
            value = student_treeToString(node)

            if self.to_consider - self.considered:
                self.fail_criterion(ConsiderByGeneration, problem_code=ConsiderByGeneration.MISSING_NODE, task=node, missed=(self.to_consider - self.considered).pop())
            if standardize(value) != standardize(expected):
                self.fail_criterion(Correctness, important=(i < 4), task=node, value=value, expected=expected)

if __name__ == '__main__':
    import sys

    sys.path.append('/home/aleite/b351/admin/sp19/Class Materials/assignments/a1/code')

    s = TreeToStringTester()
    s.test()
    print(s.generateText())
