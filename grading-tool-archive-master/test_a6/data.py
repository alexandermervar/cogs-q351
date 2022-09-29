import os
from grade import tests

path = os.path.dirname(__file__)

class TrainCase(tests.Case):
    def __init__(self, start_weight, weights):
        self.start_weight = start_weight
        self.weights = weights
    def represent(self):
        return f'self.train()'
    def __repr__(self):
        return f'TrainCase(start_weight={self.start_weight!r}, weights={self.weights!r})'

class TrainSampleCase(tests.Case):
    def __init__(self, input, target, update, start_weight):
        self.input = input
        self.target = target
        self.update = update
        self.start_weight = start_weight
    def represent(self):
        return f'self.train_sample({self.input}, {self.target})'
    def __repr__(self):
        return f'TrainSampleCase(input={self.input!r}, target={self.target!r}, update={self.update!r}, start_weight={self.start_weight!r})'

class PredictCase(tests.Case):
    def __init__(self, input, prediction, weights):
        self.input = input
        self.prediction = prediction
        self.weights = weights
    def represent(self):
        return f'self.predict({self.input})'
    def __repr__(self):
        return f'PredictCase(input={self.input!r}, prediction={self.prediction!r}, weights={self.weights!r})'

class ActivationCase(tests.Case):
    def __init__(self, n, activation):
        self.n = n
        self.activation = activation
    def represent(self):
        return f'self.activation({self.n})'
    def __repr__(self):
        return f'ActivationCase(n={self.n!r}, activation={self.activation!r})'

class DotCase(tests.Case):
    def __init__(self, a, b, output):
        self.a = a
        self.b = b
        self.output = output
    def represent(self):
        return f'self.dot({self.a},{self.b})'
    def __repr__(self):
        return f'DotCase(a={self.a!r}, b={self.b!r}, output={self.output!r})'

class AddCase(tests.Case):
    def __init__(self, a, b, output):
        self.a = a
        self.b = b
        self.output = output
    def represent(self):
        return f'self.add({self.a},{self.b})'
    def __repr__(self):
        return f'AddCase(a={self.a!r}, b={self.b!r}, output={self.output!r})'

class SubCase(tests.Case):
    def __init__(self, a, b, output):
        self.a = a
        self.b = b
        self.output = output
    def represent(self):
        return f'self.sub({self.a},{self.b})'
    def __repr__(self):
        return f'SubCase(a={self.a!r}, b={self.b!r}, output={self.output!r})'

class BackPropCase(tests.Case):
    def __init__(self, targets, activations, weights):
        self.targets = targets
        self.activations = activations
        self.weights = weights
    def represent(self):
        return f'self.back_propagation({self.targets},{self.activations})'
    def __repr__(self):
        return f'BackPropCase(targets={self.targets!r}, activations={self.activations!r}, weights={self.weights!r})'

class UpdateNodeCase(tests.Case):
    def __init__(self, start, target, node, result):
        self.start = start
        self.target = target
        self.node = node
        self.result = result
    def represent(self):
        return f'self.update_node({self.node})'
    def __repr__(self):
        return f'UpdateNodeCase(start={self.start!r}, target={self.target!r}, node={self.node!r}, result={self.result!r})'

class CycleStableCase(tests.Case):
    def __init__(self, start, target, result):
        self.start = start
        self.target = target
        self.result = result
    def represent(self):
        return f'self.cycle_until_stable()'
    def __repr__(self):
        return f'CycleStableCase(start={self.start!r}, target={self.target!r}, result={self.result!r})'


if __name__ == '__main__':
    import sys, random
    sys.path.append('/Users/rowlavel/Documents/Programming/Python/admin/assignments/a6/reference-solutions')

    import perceptron
    inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
    targets = [0, 1, 1, 1]

    tests = []
    for i in range(2,10):
        l1 = [round(random.uniform(0,10)) for _ in range(i)]
        l2 = [round(random.uniform(0,10)) for _ in range(i)]
        tests.append([l1,l2])

    dot_cases = []
    for pair in tests:
        a = pair[0]; b = pair[1]
        dot_cases.append(DotCase(a,b,perceptron.Perceptron(inputs,targets).dot(a,b)))

    add_cases = []
    for pair in tests:
        a = pair[0]; b = pair[1]
        add_cases.append(AddCase(a,b,perceptron.Perceptron(inputs,targets).add(a,b)))

    sub_cases = []
    for pair in tests:
        a = pair[0]; b = pair[1]
        sub_cases.append(SubCase(a,b,perceptron.Perceptron(inputs,targets).sub(a,b)))

    activation_cases = []
    nums = [random.uniform(-1,1) for _ in range(1000)]
    for n in nums:
        activation_cases.append(ActivationCase(n,perceptron.Perceptron(inputs,targets).activation(n)))

    predict_cases = []
    for i in range(1000):
        pcn = perceptron.Perceptron(inputs, targets)
        input = [round(random.uniform(0,1)) for _ in range(round(random.uniform(1,10)))]
        pcn.weights = [random.random() for _ in range(len(input))]
        predict_cases.append(PredictCase(input,pcn.predict(input), pcn.weights))

    train_sample_cases = []
    for i in range(1000):
        pcn = perceptron.Perceptron(inputs, targets)
        input = [round(random.uniform(0, 1)) for _ in range(round(random.uniform(1, 10)))]
        target = round(random.uniform(0,1))
        start_weight = [random.random() for _ in range(len(input))]
        pcn.weights = start_weight
        train_sample_cases.append(TrainSampleCase(input, target, pcn.train_sample(input,target), start_weight))

    train_cases = []
    for i in range(1000):
        pcn = perceptron.Perceptron([[0, 0], [0, 1], [1, 0], [1, 1]], [0, 1, 1, 1])
        start_weight = [random.random() for _ in range(3)]
        pcn.weights = start_weight
        train_cases.append(TrainCase(start_weight, pcn.train()))

    import backpropagation
    import pandas as pd
    import numpy as np
    backprop_cases = []
    # read data in
    df = pd.read_csv('data/wine.csv', header=None)
    # normalize data based on mean and standard deviation
    dfNorm = df[df.columns[1:14]]
    dfNorm = (dfNorm - dfNorm.mean(axis=0)) / (dfNorm.std(axis=0))
    df[df.columns[1:14]] = dfNorm
    train = df
    shuffled_data = train.sample(frac=1)
    nn_architecture = [
        {"layer_size": 13, "activation": "none"},  # input layer
        {"layer_size": 6, "activation": "sigmoid"},  # hidden layer
        {"layer_size": 3, "activation": "softmax"}  # output layer
    ]

    mlp = backpropagation.MLP(nn_architecture=nn_architecture, seed=9234875)

    for i in range(len(train)):
        sample = shuffled_data.iloc[i]
        inputs = sample[1:mlp.input_size+1].values.reshape(1, mlp.input_size)
        targets = np.zeros(shape=(1, mlp.output_size))
        targets[0, int(sample[0]) - 1] = 1.0
        activations = mlp.feed_forward(inputs)
        backprop_cases.append(BackPropCase(targets.tolist(), [activation.tolist() for activation in activations],
                                           mlp.back_propagation(targets, activations)['W1'].tolist()))

    import hopfieldnetwork
    update_node_cases = []
    for i in range(2000):
        length = random.choice(range(8)[4:])
        start = [random.choice([-1, -1, 1]) for _ in range(length)]
        target = [random.choice([1, 1, -1]) for _ in range(length)]
        node = random.choice(range(length))
        hn = hopfieldnetwork.HopfieldNetwork(start_nodes=start, target_stable=target)
        start = start.copy()
        hn.update_node(node)
        update_node_cases.append(UpdateNodeCase(start, target, node, hn.nodes))

    cycle_stable_cases = []
    for i in range(2000):
        length = random.choice(range(8)[4:])
        start = [random.choice([-1, 1]) for _ in range(length)]
        target = [random.choice([-1, 1]) for _ in range(length)]
        hn = hopfieldnetwork.HopfieldNetwork(start_nodes=start, target_stable=target)
        start = start.copy()
        hn.cycle_until_stable()
        cycle_stable_cases.append(CycleStableCase(start, target, hn.nodes))

    open(path + '/data/dot.txt', 'w').write(repr(dot_cases))
    open(path + '/data/add.txt', 'w').write(repr(add_cases))
    open(path + '/data/sub.txt', 'w').write(repr(sub_cases))
    open(path + '/data/activation.txt', 'w').write(repr(activation_cases))
    open(path + '/data/predict.txt', 'w').write(repr(predict_cases))
    open(path + '/data/train_sample.txt', 'w').write(repr(train_sample_cases))
    open(path + '/data/train.txt', 'w').write(repr(train_cases))
    open(path + '/data/backpropagation.txt', 'w').write(repr(backprop_cases))
    open(path + '/data/update_node.txt', 'w').write(repr(update_node_cases))
    open(path + '/data/cycle_stable.txt', 'w').write(repr(cycle_stable_cases))

else:
    dot_cases = eval(open(path + '/data/dot.txt').read())
    add_cases = eval(open(path + '/data/add.txt').read())
    sub_cases = eval(open(path + '/data/sub.txt').read())
    activation_cases = eval(open(path + '/data/activation.txt').read())
    predict_cases = eval(open(path + '/data/predict.txt').read())
    train_sample_cases = eval(open(path + '/data/train_sample.txt').read())
    train_cases = eval(open(path + '/data/train.txt').read())
    backprop_cases = eval(open(path + '/data/backpropagation.txt').read())
    update_node_cases = eval(open(path + '/data/update_node.txt').read())
    cycle_stable_cases = eval(open(path + '/data/cycle_stable.txt').read())
