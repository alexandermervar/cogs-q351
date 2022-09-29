#!/usr/bin/python3
from grade import tests

class Completion(tests.Criterion):
    summary = 'Prints your favorite dessert.'
    points = 10
    def generateText(self):
        return tests.Criterion.generateText(self)

class DessertTester(tests.CriterionTester):
    function_name = 'dessert'
    def __init__(self):
        tests.CriterionTester.__init__(self, ['a0'], [Completion])
    def run(self, compilation_test=False): pass