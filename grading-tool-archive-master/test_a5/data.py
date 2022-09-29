#!/usr/bin/python3

import os
from grade import tests
from math import inf
import urllib, json

path = os.path.dirname(__file__)

class EntropyCase(tests.Case):
    def __init__(self, classifications, entropy):
        self.classifications = classifications
        self.entropy = entropy
    def represent(self):
        return f"entropy({self.classifications!r})"
    def __repr__(self):
        return f'EntropyCase(classifications={self.classifications!r}, entropy={self.entropy!r})'

class InfoGainCase(tests.Case):
    def __init__(self, parent_classifications, classifications_by_val, val_freqs, info_gain):
        self.parent_classifications = parent_classifications
        self.classifications_by_val = classifications_by_val
        self.val_freqs = val_freqs
        self.info_gain = info_gain
    def represent(self):
        return f"information_gain({self.parent_classifications!r}, {self.classifications_by_val!r}, {self.val_freqs!r})"
    def __repr__(self):
        return f'InfoGainCase(parent_classifications={self.parent_classifications!r}, classifications_by_val={self.classifications_by_val!r}, val_freqs={self.val_freqs!r}, info_gain={self.info_gain!r})'

class ClassifyCase(tests.Case):
    def __init__(self, tree_string, points, labels):
        self.tree_string = tree_string
        self.points = points
        self.labels = labels
    def represent(self):
        return self.tree_string+'.classify_point'
    def __repr__(self):
        return f'ClassifyCase(tree_string={self.tree_string!r}, points={self.points!r}, labels={self.labels!r})'

class DistanceCase(tests.Case):
    def __init__(self, point1, point2, distance):
        self.point1 = point1
        self.point2 = point2
        self.distance = distance
    def represent(self):
        return f'self.euclidean_distance({self.point1}, {self.point2})'
    def __repr__(self):
        return f'DistanceCase(point1={self.point1!r}, point2={self.point2!r}, distance={self.distance})'

class PickLabelCase(tests.Case):
    def __init__(self, labels, valid):
        self.labels = labels
        self.valid  = valid
    def represent(self):
        return f'self.get_top_label({self.labels})'
    def __repr__(self):
        return f'PickLabelCase(labels={self.labels!r}, valid={self.valid!r})'

class KNNClassifyCase(tests.Case):
    def __init__(self, k, points, labels, test_point, closest_k):
        self.k = k
        self.points = points
        self.labels = labels
        self.test_point = test_point
        self.closest_k = closest_k
    def represent(self):
        return f'KNN_Classifier({self.k}).classify_point({self.test_point}, {self.points}, {self.labels})'
    def __repr__(self):
        return f'KNNClassifyCase(k={self.k!r}, points={self.points!r}, labels={self.labels!r}, test_point={self.test_point!r}, closest_k={self.closest_k!r})'


if __name__ == '__main__':
    import sys, collections, random
    sys.path.append('/Users/yohlo/Dev/IU/b351/admin/assignments/a5/reference-solutions')

    import a5

    Scenario = collections.namedtuple('Scenario', ['labels', 'attributes'])

    sunburn = Scenario(labels=['burn', 'tan', 'none'], attributes={'haircolor': ['black', 'brown', 'blonde', 'red'], 'height': ['short', 'medium', 'tall'], 'sunscreen': ['yes', 'no'], 'weather': ['sun', 'cloud', 'rain', 'snow']})
    movie = Scenario(labels=['watch', 'decline'], attributes={'genre': ['action', 'romance', 'comedy', 'anime'], 'length': ['short', 'medium', 'long'], 'invitedby': ['partner', 'friend', 'sibling', 'enemy'], 'busy': ['extremely', 'busy', 'free', 'bored']})
    fruit = Scenario(labels=['apple', 'peach', 'banana', 'berry'], attributes={'appetite': ['famished', 'hungry', 'neutral', 'full'], 'thirst': ['parched', 'thirsty', 'neutral', 'quenched'], 'preference': ['sweet', 'sour', 'neutral', 'spicy']})

    entropy_cases   = []
    info_gain_cases = []
    classify_cases  = []

    for scenario in [sunburn, movie, fruit]:
        # generate entropy cases
        for _ in range(100):
            labels = []
            for label in scenario.labels:
                for _ in range(random.randint(3,12)):
                    labels.append(label)
            random.shuffle(labels)
            entropy_cases.append(EntropyCase(labels, a5.entropy(labels)))
        entropy_cases.sort(key=lambda case: len(case.classifications))

        for _ in range(100):
            labels = []
            for label in scenario.labels:
                for _ in range(random.randint(3,16)):
                    labels.append(label)
            random.shuffle(labels)
            attrib = random.choice(list(scenario.attributes.keys()))
            
            cuts = [random.randint(0, len(labels)) for val in scenario.attributes[attrib]]
            cuts[-1] = len(labels)
            cuts.append(0)
            cuts.sort()

            classifications_by_val = {}
            val_freqs = {}

            for i, val in enumerate(scenario.attributes[attrib]):
                start, end = cuts[i], cuts[i+1]
                val_freqs[val] = end - start
                classifications_by_val[val] = labels[start:end]

            info_gain = a5.information_gain(labels, classifications_by_val, val_freqs)
            info_gain_cases.append(InfoGainCase(labels, classifications_by_val, val_freqs, info_gain))
        info_gain_cases.sort(key=lambda case: len(case.parent_classifications))

        trees = set()
        while len(trees) < 25:
            points = []
            labels = []
            for _ in range(random.randint(1,15)): # extremely sparse training sets to render interesting (non-uniform) trees
                points.append({attrib: random.choice(values) for attrib, values in scenario.attributes.items()})
                labels.append(random.choice(scenario.labels))
            tree = a5.Node()
            tree.train(points, labels)
            trees.add(repr(tree))
        for tree_string in trees:
            tree = eval(tree_string, a5.__dict__)
            points = [{attrib: random.choice(values) for attrib, values in scenario.attributes.items()} for _ in range(10)]
            labels = [tree.classify_point(point) for point in points]
            classify_cases.append(ClassifyCase(tree_string, points, labels))

    distance_cases = []

    upper = 25

    from itertools import permutations
    points = permutations(range(upper), 2)
    tests = permutations(points, 2)

    for point1, point2 in tests:
        distance_cases.append(DistanceCase(point1, point2, a5.KNN_Classifier(3).euclidean_distance(point1, point2)))


    pick_label_cases = []
    tests = [[random.choice(range(10)) for i in range(10)] for j in range(100)]

    for labels in tests:
        max_occurrance = max([labels.count(i) for i in labels])
        valid = set([i for i in labels if labels.count(i) == max_occurrance])
        pick_label_cases.append(PickLabelCase(labels, valid))

    knn_classify_cases = []
    import random
    import heapq

    for i in range(190, 0, -1):
        points = []
        while len(points) < (200-i*1):
            point = random.choice(range(-10, 10)), random.choice(range(-10, 10))
            if point not in points: points.append(point)
        labels = [random.choice(range(4)) for _ in range(len(points) - 1)]
        test_point = points.pop()

        ks = [1, 3, 5]
        for k in ks:
            neighbors = []
            for i in range(len(points)):
                heapq.heappush(neighbors, (a5.KNN_Classifier(k).euclidean_distance(points[i], test_point), labels[i]))
            closest = [heapq.heappop(neighbors) for i in range(k)]
            valid = [point for dist, point in closest]
            kth = closest[-1]
            while True:
                dist, point = heapq.heappop(neighbors)
                if dist > kth[0]: break
                valid.append(point)
            knn_classify_cases.append(KNNClassifyCase(k, points, labels, test_point, valid))


    open(path+'/data/entropy.txt','w').write(repr(entropy_cases))
    open(path+'/data/info_gain.txt','w').write(repr(info_gain_cases))
    open(path+'/data/classify.txt','w').write(repr(classify_cases))
    open(path+'/data/distance.txt','w').write(repr(distance_cases))
    open(path+'/data/pick_label.txt','w').write(repr(pick_label_cases))
    open(path+'/data/knn_classify.txt','w').write(repr(knn_classify_cases))
else:
    entropy_cases = eval(open(path+'/data/entropy.txt').read())
    info_gain_cases = eval(open(path+'/data/info_gain.txt').read())
    classify_cases = eval(open(path+'/data/classify.txt').read())
    distance_cases = eval(open(path+'/data/distance.txt').read())
    pick_label_cases = eval(open(path+'/data/pick_label.txt').read())
    knn_classify_cases = eval(open(path+'/data/knn_classify.txt').read())