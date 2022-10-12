import random


class Perceptron:
    def __init__(self, inputs, targets):
        self.inputs = inputs
        self.targets = targets

        # size of input and output
        self.input_size = len(self.inputs[0])
        self.output_size = len(self.targets)

        # total number of inputs
        self.num_inputs = len(self.inputs)

        # initialize weights
        self.weights = [random.random() for _ in range(self.input_size + 1)]

        # add one to end of each input to account for bias
        for i in range(self.num_inputs): self.inputs[i].append(1)

    ##################
    #      TODO      #
    ##################
    """
    Implement the perceptron training algorithm and return the weights
    """
    def train(self):
        raise NotImplementedError


    ##################
    #      TODO      #
    ##################
    """
    Implement one iteration of the training algorithm
    Return true of false depending on if you update weight
    """
    def train_sample(self, input, target):
        raise NotImplementedError

    ##################
    #      TODO      #
    ##################
    """
    Implement a function that returns a prediction based on the input
    """
    def predict(self, input):
        raise NotImplementedError

    ##################
    #      TODO      #
    ##################
    """
    Implement the threshold activation function
    Return the activation value
    """
    def activation(self, n):
        raise NotImplementedError

    ##################
    #      TODO      #
    ##################
    """
    Return dot product of two vectors
    """
    def dot(self, a, b):
        raise NotImplementedError

    ##################
    #      TODO      #
    ##################
    """
    Return addition of two vectors
    """
    def add(self, a, b):
        raise NotImplementedError

    ##################
    #      TODO      #
    ##################
    """
    Return subtraction of two vectors
    """
    def sub(self, a, b):
        raise NotImplementedError


if __name__ == "__main__":
    # OR gate
    inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
    targets = [0, 1, 1, 1]

    pcn = Perceptron(inputs, targets)
    pcn.train()
    outputs = [pcn.predict(p) for p in inputs]
    assert outputs == targets

    # AND gate
    inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
    targets = [0, 0, 0, 1]

    pcn = Perceptron(inputs, targets)
    pcn.train()
    outputs = [pcn.predict(p) for p in inputs]
    assert outputs == targets

    print("ALL TESTS PASSED")
