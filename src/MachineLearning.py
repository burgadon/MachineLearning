# MachineLearning.py
# Author: Armin Müller
# Created on 19.10.2018
# Last Modified on: 02.11.2018
#
# This project aims to use a neural network to decide if given step data is a 
# step or not

import numpy as np
from src.Parser import Parser

class NeuralNetwork:
    def __init__(self):
        #parameters
        self.inputSize = 2
        self.outputSize = 1
        self.hiddenSize = 3
        
        #weights
        self.W1 = np.random.randn(self.inputSize, self.hiddenSize) # (3x2) weight matrix from input to hidden layer
        self.W2 = np.random.randn(self.hiddenSize, self.outputSize) # (3x1) weight matrix from hidden to output layer

    # Activation function
    def sigmoid(self, t):
        return 1 / (1 + np.exp(-t))
    
    # Derivative of sigmoid function
    def sigmoidDerivative(self, p):
        return p * (1 - p)

    #forward propagation through our network
    def feedForward(self, X):
        self.z = np.dot(X, self.W1) # dot product of X (input) and first set of 3x2 weights
        self.z2 = self.sigmoid(self.z) # activation function
        self.z3 = np.dot(self.z2, self.W2) # dot product of hidden layer (z2) and second set of 3x1 weights
        o = self.sigmoid(self.z3) # final activation function
        return o

    #back-propagate through the network
    def backPropagation(self, X, y, o):
        self.o_error = y - o # error in output
        self.o_delta = self.o_error*self.sigmoidDerivative(o) # applying derivative of sigmoid to error
    
        self.z2_error = self.o_delta.dot(self.W2.T) # z2 error: how much our hidden layer weights contributed to output error
        self.z2_delta = self.z2_error*self.sigmoidDerivative(self.z2) # applying derivative of sigmoid to z2 error
    
        self.W1 += X.T.dot(self.z2_delta) # adjusting first set (input --> hidden) weights
        self.W2 += self.z2.T.dot(self.o_delta) # adjusting second set (hidden --> output) weights

    def train(self, X, y):
        o = self.feedForward(X)
        self.backPropagation(X, y, o)

    def saveWeights(self):
        np.savetxt("w1.txt", self.W1, fmt="%s")
        np.savetxt("w2.txt", self.W2, fmt="%s")

    def predict(self):
        print("Predicted data based on trained weights: \n")
        print("Input: \n" + str(xPredicted))
        print("Output: \n" + str(self.feedForward(xPredicted)))
        
# -----------------------------------------------------------------------------
# use NN

if __name__ == "__main__":
    
    # X = (hours studying, hours sleeping), y = score on test, xPredicted = 4 hours studying & 8 hours sleeping (input data for prediction)
    X = np.array(([2, 9], [1, 5], [3, 6]), dtype=float)
    y = np.array(([92], [86], [89]), dtype=float)
    xPredicted = np.array(([4,8]), dtype=float)
    
    # scale units
    X = X / np.amax(X, axis=0) # maximum of X array
    xPredicted = xPredicted / np.amax(xPredicted, axis=0) # maximum of xPredicted (our input data for the prediction)
    y = y / 100 # max test score is 100
    
    # initialize and run parser
    parser = Parser()
    parser.aksForDestination()
    # parser.setDestination(destinationPath)
    parser.processData()
    parsedData = parser.getData()
    # TODO: X = np.array(parsedData[0].)
    
    nn = NeuralNetwork()
    
    # trains the NN 15000 times
    for i in range(150001):        
        if (i % 1000) == 0:
            print("# " + str(i) + "\n")
            print("Input (scaled): \n" + str(X))
            print("Actual Output: \n" + str(y))
            print("Predicted Output: \n" + str(nn.feedForward(X)))
            print("Loss: \n" + str(np.mean(np.square(y - nn.feedForward(X))))) # mean sum squared loss
            print("\n")
            
        nn.train(X, y)
        
    print("Training: DONE!\n")
    print("Save weights:", end=" ")
    nn.saveWeights()
    print("DONE!\n", sep=' ', end="", flush=True)
    print("\n")
    nn.predict()
