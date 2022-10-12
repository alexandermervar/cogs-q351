import pandas as pd
import numpy as np



import pandas as pd
import numpy as np


def five_fold_cross_val(nn_architecture):
    def chunks(lst, n):
        for i in range(0, len(lst), n): yield lst[i:i + n]

    # create index's for the different chunks
    index = [i for i in range(0, len(df))]

    # seperate for different validation chunks
    index = list(chunks(index, int(len(df) / 5)))
    d1 = index[0]; d2 = index[1]; d3 = index[2]; d4 = index[3]; d5 = index[4]; d5.extend(index[5])
    D = [d1, d2, d3, d4, d5]

    # lists for accuracies
    accuracies_network = []

    # use D-D_i for train and D_i as test
    for i in range(len(D)):
        test = df.iloc[D[i]]
        train_index = []
        for j in range(len(D)):
            if i != j: train_index.extend(D[j])
        train = df.iloc[train_index]
        # create, train and test network
        mlp = MLP(nn_architecture=nn_architecture, seed=9234875)
        mlp.train_network(epochs=200, train=train)
        accuracies_network.append(mlp.test_network(test=test))
    return np.mean(accuracies_network)


def sigmoid(x):
    return 1.0/(1.0 + np.exp(-x))

def softmax(x):
    expScores = np.exp(x)
    return expScores / expScores.sum()


class MLP:
    def __init__(self, nn_architecture, seed=0, eta=0.2):
        self.eta = eta
        self.num_layers = len(nn_architecture)
        self.input_size = nn_architecture[0]['layer_size']
        self.output_size = nn_architecture[-1]['layer_size']
        self.params = self.initialize(nn_architecture=nn_architecture,seed=seed)

    def initialize(self, nn_architecture, seed=0):
        np.random.seed(seed)

        params = {}
        for l in range(1, self.num_layers):
            # add plus one to account for bias
            params['W'+str(l)] = np.random.randn(nn_architecture[l - 1]['layer_size'],
                                                 nn_architecture[l]['layer_size']) * 0.1
            params['B'+str(l)] = np.zeros(nn_architecture[l]['layer_size'])
            params['A'+str(l)] = nn_architecture[l]['activation']
        return params

    # feed the inputs through the neural network and get predictions
    def feed_forward(self, inputs):
        activations = [inputs]

        # feed points forward by multiplying the weights by the activations then
        # adding bias to get the next layers activation
        # first activation is the inputs, last activation will be the predictions
        for l in range(1, self.num_layers):
            activation = np.dot(activations[l-1], self.params['W'+str(l)]) + self.params['B'+str(l)]

            # apply activation function
            if self.params['A'+str(l)] == 'sigmoid': activation = sigmoid(activation)
            if self.params['A' + str(l)] == 'softmax': activation = softmax(activation)
            
            activations.append(activation)

        return activations

    ##################
    #      TODO      #
    ##################
    '''
    - calculate the delta of the output layer using the last activation and the targets
    - calculate the gradient for the weights of the output layer using the second to last activation and the output layers delta
    - calculate the bias gradient for the output layer using the delta of the output layer
    - update the output layers weights using the last weight and the gradient
    - update the output layers bias using the last bias and the bias gradient
    - for the remaining layers (self.numlayers-2 -> 0) 
        - calculate the delta function of the current layer using the weight of the curr layer+1, activation of the
          current layer, and the previous delta function
        - calculate the gradient of the current layer using the previous layers activation and the delta function
          calculated above
        - calculate the bias gradient of the current layer using the delta of the current layer
        - update the current layers weight using the gradient calculated above
        - update the current layers bias using the bias gradient calculated above
    '''
    def back_propagation(self, targets, activations):
        raise NotImplementedError

    ##################
    #      TODO      #
    ##################
    """
    Calculate the derivative of the error w.r.t. to output of the network
    equation: softmax probabilities - actual classes

    """
    def calc_output_layer_delta(self, activation, targets):
        raise NotImplementedError

    ##################
    #      TODO      #
    ################## 
    """
    Calculate the derivative of the error w.r.t. the output of a given layer
    using the chain rule
    equation: delta = (delta . weights^T) * activation*(1 - activation)
    """
    def calc_layer_delta(self, weight, activation, delta):
        raise NotImplementedError

    ##################
    #      TODO      #
    ##################
    """
    Update the weights of the specified layer using the gradient
    with the update rule weights_i+1 = weights_i - eta*gradient
    """
    def update_layer_weights(self, layer, gradient):
        raise NotImplementedError

    ##################
    #      TODO      #
    ##################
    
    """
    Update the biases of the specified layer using the
    bias gradient with the update rule bias_i+1 = bias_i - eta*gradient_bias
    """
    def update_layer_bias(self, layer, gradient):
        raise NotImplementedError

    ##################
    #      TODO      #
    ##################
    """
    Calculate gradient of the weights for a corresponding
    layer
    equation: activation^T . delta
    """
    def calc_layer_gradient(self, activation, delta):
        raise NotImplementedError

    def train_network(self, epochs, train):
        for epoch in range(epochs):
            shuffled_data = train.sample(frac=1)
            # feed points through network sequentially
            for i in range(len(train)):
                # get targets and inputs from sample
                sample = shuffled_data.iloc[i]
                inputs = sample[1:self.input_size+1].values.reshape(1, self.input_size)
                target = sample[0]
                targets = np.zeros(shape=(1, self.output_size))
                targets[0, int(sample[0]) - 1] = 1.0

                # feed point through network and get predictions and hidden layer activation values
                activations = self.feed_forward(inputs)

                # use backprop to update weights
                self.back_propagation(targets, activations)

    def test_network(self, test):
        actual = test[0].values
        predictions = np.zeros(len(test))
        for i in range(len(test)):
            # get targets and inputs from sample
            sample = test.iloc[i]
            inputs = sample[1:self.input_size+1].values.reshape(1, self.input_size)
            target = sample[0]

            # feed point through network to get prediction
            activations = self.feed_forward(inputs)

            # use softmax on predictions
            predictions[i] = activations[-1].argmax() + 1
        
        return sum(actual == predictions)/len(predictions)


if __name__ == "__main__":
    # read data in
    df = pd.read_csv('wine.csv', header=None)

    # normalize data based on mean and standard deviation
    dfNorm = df[df.columns[1:14]]
    dfNorm = (dfNorm - dfNorm.mean(axis=0)) / (dfNorm.std(axis=0))
    df[df.columns[1:14]] = dfNorm
    

    # make architectures
    nn_architecture_1 = [
        {"layer_size": 13, "activation": "none"},    # input layer
        {"layer_size": 10, "activation": "sigmoid"},  # hidden layer
        {"layer_size": 7, "activation": "sigmoid"},  # hidden layer
        {"layer_size": 3, "activation": "softmax"}   # output layer
    ]

    
    
    nn_architecture_2 = [
        {"layer_size": 13, "activation": "none"},  # input layer
        {"layer_size": 18, "activation": "sigmoid"},  # hidden layer
        {"layer_size": 9, "activation": "sigmoid"},  # hidden layer
        {"layer_size": 3, "activation": "softmax"}  # output layer
    ]

    nn_architecture_3 = [
        {"layer_size": 13, "activation": "none"},  # input layer
        {"layer_size": 6, "activation": "sigmoid"},  # hidden layer
        {"layer_size": 3, "activation": "softmax"}  # output layer
    ]



    acc1 = five_fold_cross_val(nn_architecture_1)
    acc2 = five_fold_cross_val(nn_architecture_2)
    acc3 = five_fold_cross_val(nn_architecture_3)
    print('Expected: 0.8854135338345864 0.9016541353383458 0.9542857142857143')
    print('Returned: '+str(acc1)+' '+str(acc2)+' '+str(acc3))
