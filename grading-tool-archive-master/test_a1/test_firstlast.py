#!/usr/bin/python3

import random
import inspect

from grade import tests

class LengthOneListIdentity(tests.Criterion):
  summary = 'If the given sequence has one element, returns the tuple containing only that element.'
  points = 4
  NOT_TUPLE = 1
  WRONG_LENGTH = 2
  WRONG_ELEMENT = 3
  def generateText(self):
    if self.problem_code == self.NOT_TUPLE:
      return f'For firstLast({self.orig_argument!r}), output should be of type tuple' +\
          f', not {self.student_output!r} ({type(self.student_output)}).'
    elif self.problem_code == self.WRONG_LENGTH:
      return f'For firstLast({self.orig_argument!r}), output should have length 1 --'+\
          f' {self.student_output!r} has length {len(self.student_output)}.'
    elif self.problem_code == self.WRONG_ELEMENT:
      return f'For firstLast({self.orig_argument!r}), output should be same as input'+\
          f' -- not {self.student_output!r}.'
    else: return tests.Criterion.generateText(self)

class FirstLastLongLists(tests.Criterion):
  summary = 'If the given sequence has more than one element, returns the tuple containing only its first and last elements.'
  points = 6
  NOT_TUPLE = 1
  FIRST_ISNT_FIRST = 2
  LAST_ISNT_LAST = 3
  TOO_LONG = 4
  def generateText(self):
    if self.problem_code == self.NOT_TUPLE:
      return f'For firstLast({self.orig_argument!r}), output should be of type tuple' +\
          f', not {self.student_output!r} ({type(self.student_output)}).'
    elif self.problem_code == self.FIRST_ISNT_FIRST:
      return f'First element of firstLast({self.orig_argument!r}) should be ' +\
          f'{self.orig_argument[0]!r}, not {self.student_output[0]!r}.'
    elif self.problem_code == self.LAST_ISNT_LAST:
      return f'Last element of firstLast({self.orig_argument!r}) should be ' +\
          f'{self.orig_argument[-1]!r}, not {self.student_output[-1]!r}.'
    elif self.problem_code == self.TOO_LONG:
      return f'Output of firstLast({self.orig_argument!r}) should have length 2,' +\
          f'whereas {self.student_output!r} has length {len(self.student_output)!r}.'
    else: return tests.Criterion.generateText(self)

class FirstLastTester(tests.CriterionTester):
  function_name = 'firstLast'
  def __init__(self):
    tests.CriterionTester.__init__(self, ['a1'], [LengthOneListIdentity, FirstLastLongLists])
  def run(self, compilation_test=False):
    student_firstLast = self.a1.firstLast

    if 'n' in inspect.signature(student_firstLast).parameters:
      self.set_plagiarism_flag()

    def random_lists(how_many=60):
      lists = []
      for i in range(how_many):
        # Test for short and long lists
        length = 1 if i < (how_many//8)+1 else random.randint(3,10)
        next_random_list = []
        for _ in range(length):
          next_random_list.append(random.randint(-20,20))
        lists.append(next_random_list)
      return lists

    def ref_firstLast(seq):
      if len(n) <= 1: return tuple(seq)
      else: return seq[0], seq[-1]

    if compilation_test:
      test_lists = random_lists(4)
    else:
      test_lists = random_lists(100)
    for lst in test_lists:
      if len(lst) == 1:
        value = student_firstLast(lst.copy())
        if type(value) is list:
          self.set_plagiarism_flag()
        if type(value) is not tuple:
          self.fail_criterion(LengthOneListIdentity,
              problem_code=LengthOneListIdentity.NOT_TUPLE, orig_argument=lst,
              student_output=value)
        else:
          if len(value) != 1:
            self.fail_criterion(LengthOneListIdentity,
                problem_code=LengthOneListIdentity.WRONG_LENGTH, orig_argument=lst,
                student_output=value)
          if value and value[0] != lst[0]:
            self.fail_criterion(LengthOneListIdentity,
                problem_code=LengthOneListIdentity.WRONG_ELEMENT, orig_argument=lst,
                student_output=value)
      else:
        value = student_firstLast(lst.copy())
        if type(value) is list:
          self.set_plagiarism_flag()
        if type(value) is not tuple:
          self.fail_criterion(FirstLastLongLists,
              problem_code=FirstLastLongLists.NOT_TUPLE, orig_argument=lst,
              student_output=value)
        else:
          if value and value[0] != lst[0]:
            self.fail_criterion(FirstLastLongLists,
                problem_code=FirstLastLongLists.FIRST_ISNT_FIRST, orig_argument=lst,
                student_output=value)
          if value and value[-1] != lst[-1]:
            self.fail_criterion(FirstLastLongLists,
                problem_code=FirstLastLongLists.LAST_ISNT_LAST, orig_argument=lst,
                student_output=value)
          if len(value) != 2:
            self.fail_criterion(FirstLastLongLists,
                problem_code=FirstLastLongLists.TOO_LONG, orig_argument=lst,
                student_output=value)
