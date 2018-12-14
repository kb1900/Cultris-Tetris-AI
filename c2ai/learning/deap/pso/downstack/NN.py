import numpy as np

# scipy.special for the sigmoid function expit()
import scipy.special


class neuralNetwork:
    def __init__(self, inputnodes, hiddennodes, outputnodes):
        # set number of nodes in each input, hidden, output layer
        self.inodes = inputnodes
        self.hnodes = hiddennodes
        self.onodes = outputnodes

        self.wih = np.random.normal(
            0.0, pow(self.inodes, -0.5), (self.hnodes, self.inodes)
        )
        self.who = np.random.normal(
            0.0, pow(self.hnodes, -0.5), (self.onodes, self.hnodes)
        )

        self.activation_function = lambda x: scipy.special.expit(x)

    def compute(self, inputs_list):
        # convert inputs list to 2d array
        inputs = np.array(inputs_list, ndmin=2).T

        # calculate signals into hidden layer
        hidden_inputs = np.dot(self.wih, inputs)
        # calculate the signals emerging from hidden layer
        hidden_outputs = self.activation_function(hidden_inputs)

        # calculate signals into final output layer
        final_inputs = np.dot(self.who, hidden_outputs)
        # calculate the signals emerging from final output layer
        final_outputs = self.activation_function(final_inputs)

        return final_outputs


if __name__ == "__main__":
    input_nodes = 6
    hidden_nodes = 1
    output_nodes = 1
    n = neuralNetwork(input_nodes, hidden_nodes, output_nodes)

    print(n.wih)
    print(n.who)
