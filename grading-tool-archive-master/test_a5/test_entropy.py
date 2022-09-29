#!/usr/bin/python3

from grade import tests
from . import data
from .checker import check_a5

import math
import builtins

#def represent: 'entropy({classifications!r})'

class CountsClasses(tests.Criterion):
    summary = 'Counts occurrences of each classification (using the unique helper function).'
    points = 5

    WRONG_ARGS = 1
    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ARGS:
            return intro + f'you call unique on the wrong arguments: {self.args!r}. You should only call it on the list of labels supplied in classifications.'

        return intro + 'you don\'t appear to be calling unique on classifications.'

class GetsTotal(tests.Criterion):
    summary = 'Gets the total number of classifications (using the len builtin function).'
    points = 2

    WRONG_ARGS = 1
    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.WRONG_ARGS:
            return intro + f'you call len on the wrong arguments: {self.args!r}. You should call it on the list of labels supplied in classifications.'

        return intro + 'you don\'t appear to be calling len on classifications.'

class GetsProbs(tests.Criterion):
    summary = 'Gets the probability of each classification (using division).'
    points = 5

    MISSING_CLASSES = 1
    WRONG_DIVISORS = 2
    NO_CLASSES = 3

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.NO_CLASSES:
            return intro + 'you never get the counts of each class, so you can\'t get partial credit on this criterion.'
        if self.problem_code == self.MISSING_CLASSES:
            return intro + f'you don\'t divide the counts for labels {self.missed!r} by the total number of classifications.'
        if self.problem_code == self.WRONG_DIVISORS:
            return intro + f'you divide a class\'s count by {self.divisors!r}, rather than the total number of classifications {self.total!r}.'

        return tests.Criterion.generateText(self)

class Correctness(tests.Criterion):
    summary = 'Returns the entropy using the entropy formula given in lecture, utilizing the classes\' probabilities.'
    points = 8

    INCORRECT = 1     # returned, expected
    MISSING_LOGS = 2  # missed
    MISSING_MULTS = 3 # missed
    WRONG_MULTS = 4   # label, multiplicands
    MISSING_TOTAL = 5 # missed

    def generateText(self):
        intro = f'When {self.case.represent()} is called, '
        if self.problem_code == self.MISSING_LOGS:
            return intro + f'you don\'t take the log of the probabilities of labels {self.missed!r}.'
        if self.problem_code == self.MISSING_MULTS:
            return intro + f'you don\'t multiply the log-probabilities of labels {self.missed!r} by their probabilities.'
        if self.problem_code == self.WRONG_MULTS:
            return intro + f'you multiply the log-probability of label {self.label!r} by {self.multiplicands!r}, rather than its probability.'
        if self.problem_code == self.MISSING_TOTAL:
            return intro + f'you don\'t add the terms for classes {self.missed!r} to the entropy sum.'

        if self.problem_code == self.INCORRECT:
            return intro + f'you return {self.returned!r}. ({self.expected!r} expected.)'

        return tests.Criterion.generateText(self)

class EntropyTester(tests.CriterionTester):
    function_name = 'calc_entropy'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a5'], [CountsClasses, GetsTotal, GetsProbs, Correctness])
    def load_modules(self):
        tests.CriterionTester.load_modules(self)

    def prep_tests(self):
        # the following tools assume that
        # the EntropyTester instance has a member "case"
        # (instance of Case) with a member "classifications"
        # they modify members "got_total" (bool), "len_calls" (set),
        # "got_counts" (bool), "unique_calls" (set),
        # "counts_returned" (set), "counts_divided" (set),
        # "count_divisors" (set), "probs_logged" (set),
        # "logs_multiplied" (set), "log_multiplicands" (dict of sets),
        # "products_totaled" (set)

        if hasattr(builtins, 'oldlen'):
            builtins.len = builtins.oldlen
        builtins.oldlen = builtins.len
        def new_len(collection):
            if collection == self.case.classifications:
                self.got_total = True
            else:
                self.len_calls.append(collection)
            return builtins.oldlen(collection)
        builtins.len = new_len

        def unique(iterable):
            if iterable == self.case.classifications:
                self.got_counts = True
            else:
                self.unique_calls.append(iterable)
            items = list(iterable)
            unique_items = list(set(items))
            counts = [LabelCount(items.count(item), item) for item in unique_items]
            self.counts_returned.update(unique_items)
            return unique_items, counts
        self.a5.unique = unique

        class LabelCount(int):
            def __new__(cls, value, label):
                me = int.__new__(cls, value)
                me.label = label
                return me
            def __truediv__(me, o):
                quotient = int.__truediv__(me, o)
                if quotient is NotImplemented: return NotImplemented
                if o == oldlen(self.case.classifications):
                    self.counts_divided.add(me.label)
                else:
                    self.count_divisors.add(o)
                return LabelProbability(quotient, me.label)
        class LabelProbability(float):
            def __new__(cls, value, label):
                me = float.__new__(cls, value)
                me.label = label
                return me
            def __neg__(me):
                return me.__class__(float.__neg__(me), me.label)
            def __truediv__(me, o):
                quotient = float.__truediv__(me, o)
                if quotient is NotImplemented: return NotImplemented
                if o == oldlen(self.case.classifications):
                    self.counts_divided.add(me.label)
                else:
                    self.count_divisors.add(o)
                return me.__class__(quotient, me.label)
            def __mul__(me, o):
                return me.__class__(float.__mul__(me, o), me.label)

        if hasattr(math, 'oldlog'):
            math.log = math.oldlog
        if hasattr(math, 'oldlog10'):
            math.log10 = math.oldlog10
        if hasattr(math, 'oldlog2'):
            math.log2 = math.oldlog2
        math.oldlog = math.log
        math.oldlog10 = math.log10
        math.oldlog2 = math.log2
        def log_wrap(log, n, *args, **kwargs):
            result = log(n, *args, **kwargs)
            if isinstance(n, LabelProbability):
                self.probs_logged.add(n.label)
                return LogProbability(result, n.label)
            return result
        math.log = lambda n, *args, **kwargs: log_wrap(math.oldlog, n, *args, **kwargs)
        math.log10 = lambda n, *args, **kwargs: log_wrap(math.oldlog10, n, *args, **kwargs)
        math.log2 = lambda n, *args, **kwargs: log_wrap(math.oldlog2, n, *args, **kwargs)

        class LogProbability(LabelProbability):
            def __mul__(me, o):
                result = float.__mul__(me, o)
                if result is NotImplemented: return NotImplemented
                if o.__class__ == LabelProbability and o.label == me.label:
                    self.logs_multiplied.add(me.label)
                else:
                    if not me.label in self.log_multiplicands:
                        self.log_multiplicands[me.label] = set()
                    self.log_multiplicands[me.label].add(o)
                
                return LogProbability(result, me.label)
            def __truediv__(me, o):
                return me.__class__(float.__truediv__(me, o), me.label)
            def __rmul__(me, o):
                return me.__mul__(o)
            def __add__(me, o):
                added = float.__add__(me, o)
                if added is NotImplemented: return NotImplemented
                self.products_totaled.add(me.label)
                if o.__class__ == LogProbability:
                    self.products_totaled.add(o.label)
                return added
            def __radd__(me, o):
                return me.__add__(o)
            def __rsub__(me, o):
                sub = float.__rsub__(me, o)
                if sub is NotImplemented: return NotImplemented
                self.products_totaled.add(me.label)
                return sub

    def teardown_tests(self):
        if hasattr(builtins, 'oldlen'):
            builtins.len = builtins.oldlen
            del builtins.oldlen
        if hasattr(math, 'oldlog'):
            math.log = math.oldlog
            del math.oldlog
        if hasattr(math, 'oldlog10'):
            math.log10 = math.oldlog10
            del math.oldlog10
        if hasattr(math, 'oldlog2'):
            math.log2 = math.oldlog2
            del math.oldlog2

    def run(self, compilation_test=False):
        check_a5(self, self.a5)
        self.prep_tests()

        for self.case in data.entropy_cases:
            self.got_total = False
            self.len_calls = []
            self.got_counts = False
            self.unique_calls = []
            self.counts_returned = set()
            self.counts_divided = set()
            self.count_divisors = set()
            self.probs_logged = set()
            self.logs_multiplied = set()
            self.log_multiplicands = {}
            self.products_totaled = set()

            student_result = self.a5.calc_entropy(self.case.classifications)
            if not math.isclose(student_result, self.case.entropy, rel_tol=1e-4):
                # all the other criteria debugging / partial credit; it's okay if they use a different mechanism

                if not self.got_total:
                    self.fail_criterion(GetsTotal, self.case)
                    if self.len_calls:
                        self.fail_criterion(GetsTotal, self.case, problem_code=GetsTotal.WRONG_ARGS, args=self.len_calls)
                if not self.got_counts:
                    self.fail_criterion(CountsClasses, self.case)
                if self.unique_calls:
                    self.fail_criterion(CountsClasses, self.case, problem_code=CountsClasses.WRONG_ARGS, args=self.unique_calls)
                if not self.counts_returned:
                    self.fail_criterion(GetsProbs, self.case, problem_code=GetsProbs.NO_CLASSES)
                # (Python 3.8) "if missing_probs := self.counts_returned - self.counts_divided:"
                missing_probs = self.counts_returned - self.counts_divided
                if missing_probs:
                    self.fail_criterion(GetsProbs, self.case, problem_code=GetsProbs.MISSING_CLASSES, missed=missing_probs)
                if self.count_divisors:
                    self.fail_criterion(GetsProbs, self.case, problem_code=GetsProbs.WRONG_DIVISORS, divisors=self.count_divisors, total=oldlen(self.case.classifications))

                missing_logs = self.counts_returned - self.probs_logged
                if missing_logs:
                    self.fail_criterion(Correctness, self.case, problem_code=Correctness.MISSING_LOGS, missed=missing_logs)
                
                missing_mults = self.counts_returned - self.logs_multiplied
                if missing_mults:
                    self.fail_criterion(Correctness, self.case, problem_code=Correctness.MISSING_MULTS, missed=missing_mults)
                
                for label, multiplicands in self.log_multiplicands.items():
                    self.fail_criterion(Correctness, self.case, problem_code=Correctness.WRONG_MULTS, label=label, multiplicands=multiplicands)

                missing_totals = self.counts_returned - self.products_totaled
                if missing_totals:
                    self.fail_criterion(Correctness, self.case, problem_code=Correctness.MISSING_TOTAL, missed=missing_totals)

                self.fail_criterion(Correctness, self.case, problem_code=Correctness.INCORRECT, returned=student_result, expected=self.case.entropy)

        self.teardown_tests()