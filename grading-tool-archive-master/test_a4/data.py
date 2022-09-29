#!/usr/bin/python3

import os
from grade import tests
from math import inf
import urllib, json

path = os.path.dirname(__file__)

class LogicCase(tests.Case):
    def __init__(self, trace):
        self.trace = trace
    def represent(self):
        return "trace " + self.trace
    def __repr__(self):
    	return f'LogicCase(trace={self.trace!r})'

class VersusCase(tests.Case):
    def __init__(self, trace):
        self.trace = trace
    def represent(self):
        return "trace " + self.trace
    def __repr__(self):
        return f'VersusCase(trace={self.trace!r})'

class MinimaxCorrectnessCase(tests.Case):
    def __init__(self, trace, depth, movesTree, scores):
        self.trace = trace
        self.depth = depth
        self.movesTree = movesTree
        self.scores = scores
    def represent(self):
        return f"trace {self.trace} at depth {self.depth}"

class ABCorrectnessCase(tests.Case):
    def __init__(self, trace, depth, movesTree, call_ab, pruned, scores):
        self.trace = trace
        self.depth = depth
        self.movesTree = movesTree
        self.scores = scores
        self.call_ab = call_ab
        self.pruned = pruned
    def represent(self):
        return f"trace {self.trace} at depth {self.depth}"

class CompetencyCase(tests.Case):
    def __init__(self, trace, rating):
        self.trace = trace
        self.rating = rating
    def represent(self):
        return f"trace {self.trace}"
    def __repr__(self):
    	return f'CompetencyCase(trace={self.trace!r}, rating={self.rating!r})'

def rateResults(trace):
	s = ''
	for c in trace:
		s += str(int(c)+1)

	# sorry for the fake header :(
	request = urllib.request.Request('http://connect4.gamesolver.org/solve?pos='+s, headers={'User-Agent': 'Mozilla/5.0'})

	with urllib.request.urlopen(request) as response:
		rating = json.loads(response.read())['score']

	for i, val in enumerate(rating):
		if val == 100: rating[i] = None

	print(len(trace), rating)

	return rating

logic_cases = eval(open(path+'/data/logic.txt').read())
minimax_correctness_cases = eval(open(path+'/data/minimax_correctness.txt').read())
ab_correctness_cases = eval(open(path+'/data/alphabeta_correctness.txt').read())
competency_cases = eval(open(path+'/data/competency.txt').read())
versus_cases = eval(open(path+'/data/versus.txt').read())
