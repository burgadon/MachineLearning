# MachineLearning.py
# Author: Armin Müller
# Created on 19.10.2018
# Last Modified on: 19.10.2018
#
# This project aims to use a neural network to decide if given step data is a 
# step or not

import numpy as np

# Activation function
def sigmoid(t):
    return 1 / (1 + np.exp(-t))

# Derivative of sigmoid function
def sigmoidDerivative(p):
    return p * (1 - p)

class NeuralNetwork:
    def __init__(self, x, y):
        self.input = x
        self.w1 = np.random.rand(self.input.shape[1],4) 
        self.w2 = np.random.rand(4,1)                 
        self.y = y
        self.output = np.zeros(self.y.shape)

    def feedForward(self):
        self.layer1 = sigmoid(np.dot(self.input, self.w1))
        self.output = sigmoid(np.dot(self.layer1, self.w2))

    def backPropagation(self):
        # application of the chain rule to find derivative of the loss function
        # with respect to the weights w1 and w2
        d_w2 = np.dot(self.layer1.T, (2 * (self.y - self.output) 
            * sigmoidDerivative(self.output)))
        d_w1 = np.dot(self.input.T, (np.dot(2 * (self.y - self.output) 
            * sigmoidDerivative(self.output), self.w2.T) 
            * sigmoidDerivative(self.layer1)))

        # update the weights with the derivative (slope) of the loss function
        self.w1 += d_w1
        self.w2 += d_w2
        
    def train(self, X, y):
        self.feedForward()
        self.backPropagation()
        
        
# -----------------------------------------------------------------------------
# use NN for the XOR problem

if __name__ == "__main__":
    # Each row is a training example, each column is a feature  [X1, X2, X3]
    X = np.array(([0,0,1], [0,1,1], [1,0,1], [1,1,1]), dtype=float)
    y = np.array(([0], [1], [1], [0]), dtype=float)
    
    nn = NeuralNetwork(X, y)
    
    # trains the NN 1500 times
    for i in range(200001):
        #nn.feedForward()
        #nn.backPropagation()
        nn.train(X, y)
        
        if i % 100000 == 0: 
            print ("for iteration # " + str(i) + "\n")
            print ("Input : \n" + str(X))
            print ("Actual Output: \n" + str(y))
            print ("Predicted Output: \n" + str(nn.output))
            # mean sum squared loss
            print ("Loss: \n" + str(np.mean(np.square(y - nn.output))))
            print ("\n")

print("Training: DONE!")