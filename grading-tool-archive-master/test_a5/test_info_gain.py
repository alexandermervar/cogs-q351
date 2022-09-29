#!/usr/bin/python3

from grade import tests
from . import data
from .checker import check_a5

import math
import builtins

class GetsTotal(tests.Criterion):
    summary = 'Gets the total number of data points.'
    # can satisfy by:
    #  get len of parent_classifications
    #  add the len of a child_classifications to something else
    #  add the val_freq of a child to something else
    points = 2.5

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '

        return intro + 'you don\'t appear to be calling len on parent_classifications or adding up the number of data points for each possible value.'

class GetsChildEntropies(tests.Criterion):
    summary = 'Gets the classification entropy of the points under each possible value.'
    # can satisfy by:
    #  calling entropy on every member (value) of classifications_by_val
    points = 5

    MISSING_CLASSES = 1

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.MISSING_CLASSES:
            return intro + f'you aren\'t getting the entropy for values {self.missed!r}.'

class GetsChildProbabilities(tests.Criterion):
    summary = 'Finds the probability of each possible value occurring.'
    # can satisfy by:
    #  dividing a val_freq of a child by a number equal to the number of points
    #  dividing the len of a classifications_by_val by a number equal to the number of points
    points = 5

    MISSING_CLASSES = 1
    WRONG_DIVISORS = 2

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.MISSING_CLASSES:
            return intro + f'you don\'t divide the frequencies for values {self.missed!r} by the total number of data points.'
        if self.problem_code == self.WRONG_DIVISORS:
            return intro + f'you divide a value\'s frequency by {self.divisors!r}, rather than the total number of data points {self.total!r}.'

        return tests.Criterion.generateText(self)

class GetsParentEntropy(tests.Criterion):
    summary = 'Gets the classification entropy of the points under the parent node.'
    # can satisfy by:
    #  calling entropy on parent_classifications
    points = 2.5

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '

        return intro + 'you don\'t appear to be calling entropy on parent_classifications.'

class Correctness(tests.Criterion):
    summary = 'Returns the information gain using the formula given in lecture, utilizing the classes\' probabilities.'
    # expectations:
    #   multiplies each qualifier as child entropy by each qualifier as child probability
    #   adds each child contribution to a total (or rsubs each child contribution)
    #   adds (or calls lsub) the parent entropy to a child contribution or a weighted child entropy
    points = 5

    INCORRECT = 1     # returned, expected
    MISSING_WEIGHTS = 2  # missed
    WRONG_WEIGHTS = 3 # label, multiplicand
    MISSING_TOTAL = 4   # missed
    MISSING_PARENT = 5 # --

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.MISSING_WEIGHTS:
            return intro + f'you don\'t multiply the child entropies for values {self.missed!r} by their probabilities.'
        if self.problem_code == self.WRONG_WEIGHTS:
            return intro + f'you multiply the child entropies for value {self.value!r} by {self.multiplicands!r}, which is not its probability of occurring.'
        if self.problem_code == self.MISSING_TOTAL:
            return intro + f'you don\'t add the terms for values {self.missed!r} to the weighted average.'
        if self.problem_code == self.MISSING_PARENT:
            return intro + f'you don\'t involve the parent entropy in your calculation.'

        if self.problem_code == self.INCORRECT:
            return intro + f'you return {self.returned!r}. ({self.expected!r} expected.)'

        return tests.Criterion.generateText(self)

class InfoGainTester(tests.CriterionTester):
    function_name = 'calc_information_gain'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a5'], [GetsTotal, GetsChildProbabilities, GetsChildEntropies, GetsParentEntropy, Correctness])
    def load_modules(self):
        tests.CriterionTester.load_modules(self)

    def prep_tests(self):
        if hasattr(builtins, 'oldlen'):
            builtins.len = builtins.oldlen
        builtins.oldlen = builtins.len
        def new_len(collection):
            if isinstance(collection, ValueLabels):
                return ValueCount(builtins.oldlen(collection), collection.value)
            if collection == self.case.parent_classifications:
                self.got_total = True
            return builtins.oldlen(collection)
        builtins.len = new_len

        def entropy(classifications):
            assert isinstance(classifications, list)
            set(classifications) # check nothing unhashable found its way in
            length = builtins.oldlen(classifications)
            entropy = -sum(   prob * math.log2(prob)   for prob in  (classifications.count(item)/length for item in set(classifications))    )
            if isinstance(classifications, ValueLabels):
                self.got_child_entropies.add(classifications.value)
                return EntropyTerm(entropy, classifications.value)
            if classifications == self.case.parent_classifications:
                self.got_parent_entropy = True
                return EntropyTerm(entropy, "PARENT")
            return entropy
        self.a5.calc_entropy = entropy

        class EntropyTerm(float):
            def __new__(cls, val, value):
                me = float.__new__(cls, val)
                me.value = value
                return me
            def __mul__(me, o):
                product = float.__mul__(me, o)
                if product is NotImplemented: return NotImplemented
                if isinstance(o, ValueProbability) and o.value == me.value:
                    self.weights_multed.add(me.value)
                else:
                    if not me.value in self.wrong_weights: self.wrong_weights[me.value] = set()
                    self.wrong_weights[me.value].add(o)
                return me.__class__(product, me.value)
            def __rmul__(me, o):
                return me.__mul__(o)
            def __neg__(me):
                return me.__class__(float.__neg__(me), me.value)
            def __add__(me, o):
                added = float.__add__(me, o)
                if added is NotImplemented: return NotImplemented
                if isinstance(o, EntropyTerm) and o.value is not None:
                    self.contribs_totaled.add(o.value)
                if me.value is not None:
                    self.contribs_totaled.add(me.value)
                return me.__class__(added, None)
            def __radd__(me, o):
                return me.__add__(o)
            def __sub__(me, o):
                return me.__add__(-o)
            def __rsub__(me, o):
                return me.__neg__().__radd__(o)

        class ValueLabels(list):
            def __init__(me, val, value):
                list.__init__(me, val)
                me.value = value
        self.ValueLabels = ValueLabels
        class ValueCount(int):
            def __new__(cls, val, value):
                me = int.__new__(cls, val)
                me.value = value
                return me
            def __add__(me, o):
                added = int.__add__(me, o)
                if added is NotImplemented: return NotImplemented
                if isinstance(o, ValueCount):
                    self.got_total = True
                return ValueCount(added, None)
            def __radd__(me, o):
                return me.__add__(o)
            def __truediv__(me, o):
                quotient = int.__truediv__(me, o)
                if quotient is NotImplemented: return NotImplemented
                if o == oldlen(self.case.parent_classifications):
                    self.counts_divided.add(me.value)
                else:
                    self.count_divisors.add(o)
                return ValueProbability(quotient, me.value)
        self.ValueCount = ValueCount
        class ValueProbability(float):
            def __new__(cls, val, value):
                me = float.__new__(cls, val)
                me.value = value
                return me
            def __neg__(me):
                return me.__class__(float.__neg__(me), me.value)
            def __mul__(me, o):
                return o.__rmul__(me)

    def teardown_tests(self):
        if hasattr(builtins, 'oldlen'):
            builtins.len = builtins.oldlen
            del builtins.oldlen

    def run(self, compilation_test=False):
        check_a5(self, self.a5)
        self.prep_tests()

        for self.case in data.info_gain_cases:
            self.expected_values = set(self.case.val_freqs.keys())

            self.got_total = False
            self.got_parent_entropy = False
            self.got_child_entropies = set()
            self.counts_divided = set()
            self.count_divisors = set()
            self.weights_multed = set()
            self.wrong_weights = {}
            self.contribs_totaled = set()

            classifications_by_val = {val: self.ValueLabels(labels, val) for val, labels in self.case.classifications_by_val.items()}
            val_freqs = {val: self.ValueCount(freq, val) for val, freq in self.case.val_freqs.items()}
            student_result = self.a5.calc_information_gain(self.case.parent_classifications, classifications_by_val, val_freqs)
            if not math.isclose(student_result, self.case.info_gain, rel_tol=1e-4, abs_tol=1e-7):
                # all the other criteria debugging / partial credit; it's okay if they use a different mechanism

                if not self.got_total:
                    self.fail_criterion(GetsTotal, self.case)
                # (Python 3.8) "if missing_probs := self.counts_returned - self.counts_divided:"
                missing_probs = self.expected_values - self.counts_divided
                if missing_probs:
                    self.fail_criterion(GetsChildProbabilities, self.case, problem_code=GetsChildProbabilities.MISSING_CLASSES, missed=missing_probs)
                if self.count_divisors:
                    self.fail_criterion(GetsChildProbabilities, self.case, problem_code=GetsChildProbabilities.WRONG_DIVISORS, divisors=self.count_divisors, total=oldlen(self.case.parent_classifications))

                missing_ents = self.expected_values - self.got_child_entropies
                if missing_ents:
                    self.fail_criterion(GetsChildEntropies, self.case, problem_code=GetsChildEntropies.MISSING_CLASSES, missed=missing_ents)

                if not self.got_parent_entropy:
                    self.fail_criterion(GetsParentEntropy, self.case)
                
                missing_mults = self.expected_values - self.weights_multed
                if missing_mults:
                    self.fail_criterion(Correctness, self.case, problem_code=Correctness.MISSING_WEIGHTS, missed=missing_mults)
                
                for value, weights in self.wrong_weights.items():
                    self.fail_criterion(Correctness, self.case, problem_code=Correctness.WRONG_WEIGHTS, value=value, multiplicands=weights)

                missing_totals = self.expected_values - self.contribs_totaled
                if missing_totals:
                    self.fail_criterion(Correctness, self.case, problem_code=Correctness.MISSING_TOTAL, missed=missing_totals)

                if not "PARENT" in self.contribs_totaled:
                    self.fail_criterion(Correctness, self.case, problem_code=Correctness.MISSING_PARENT)

                self.fail_criterion(Correctness, self.case, problem_code=Correctness.INCORRECT, returned=student_result, expected=self.case.info_gain)

        self.teardown_tests()