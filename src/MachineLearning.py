# MachineLearning.py
# Author: Armin Müller
# Created on 19.10.2018
# Last Modified on: 19.11.2018
#
# This project aims to use a neural network to decide which type of step 
# the given step data represents

import numpy as np
from src.Parser import Parser
import sys
import time

class NeuralNetwork:
    def __init__(self):
        #parameters
        self.inputSize = 9
        self.outputSize = 1
        self.hiddenSize = 3
        
        #weights
        self.W1 = np.random.randn(self.inputSize, self.hiddenSize)  # (9x3) weight matrix from input to hidden layer
        self.W2 = np.random.randn(self.hiddenSize, self.outputSize) # (3x1) weight matrix from hidden to output layer

    # Activation function
    def sigmoid(self, t):
        return 1 / (1 + np.exp(-t))
    
    # Derivative of sigmoid function
    def sigmoidDerivative(self, p):
        return p * (1 - p)

    #forward propagation through our network
    def feedForward(self, X):
        self.z = np.dot(X, self.W1)         # weighted input: dot product of X (input) and first set of 2x3 weights
        self.z2 = self.sigmoid(self.z)      # activation function
        self.z3 = np.dot(self.z2, self.W2)  # weighted intermediate: dot product of hidden layer (z2) and second set of 3x1 weights
        o = self.sigmoid(self.z3)           # final activation function
        return o

    #back-propagate through the network
    def backPropagation(self, X, y, o):
        self.o_error = y - o                                            # error in output (y is the original output/label)
        self.o_delta = self.o_error * self.sigmoidDerivative(o)         # applying derivative of sigmoid to error
    
        self.z2_error = self.o_delta.dot(self.W2.T)                     # z2 error: how much our hidden layer weights contributed to output error
        self.z2_delta = self.z2_error * self.sigmoidDerivative(self.z2) # applying derivative of sigmoid to z2 error
    
        self.W1 += X.T.dot(self.z2_delta)                               # adjusting first set of weights (input --> hidden)
        self.W2 += self.z2.T.dot(self.o_delta)                          # adjusting second set of weights (hidden --> output)

    def train(self, X, y):
        o = self.feedForward(X)
        self.backPropagation(X, y, o)

    def saveWeights(self):
        np.savetxt("w1.txt", self.W1, fmt="%s")
        np.savetxt("w2.txt", self.W2, fmt="%s")

    def predict(self):
        print("Predicted data based on trained weights:")
        print("Input: \n" + str(inputForPrediction))
        print("Output: \n" + str(self.feedForward(inputForPrediction)))
        
# ------------------------------------------------------------------------------
# use NN

if __name__ == "__main__":

# start of example   
#     # X = (hours studying, hours sleeping), y = score on test, xPredicted = 4 hours studying & 8 hours sleeping (input data for prediction)
#     X = np.array(([2, 9], [1, 5], [3, 6]), dtype=float)
#     y = np.array(([92], [86], [89]), dtype=float)
#     xPredicted = np.array(([4,8]), dtype=float)
#     
#     # scale units
#     X = X / np.amax(X, axis=0) # maximum of X array
#     xPredicted = xPredicted / np.amax(xPredicted, axis=0) # maximum of xPredicted (our input data for the prediction)
#     y = y / 100 # max test score is 100
#     
#     nn = NeuralNetwork()
#     
#     # training the NN 100,000 times
#     print("Training: Started ...", end=" ")
#     for i in range(100000):        
#         if (i % 1000) == 0:
#             print("# " + str(i) + "\n")
#             print("Input (scaled): \n" + str(X))
#             print("Actual Output: \n" + str(y))
#             print("Predicted Output: \n" + str(nn.feedForward(X)))
#             print("Loss: \n" + str(np.mean(np.square(y - nn.feedForward(X))))) # mean sum squared loss
#             print("\n")
#         nn.train(X, y)
#     print("DONE!\n", sep=' ', end="", flush=True)
#     
#     print("Save weights:", end=" ")
#     nn.saveWeights()
#     print("DONE!\n\n", sep=' ', end="", flush=True)
#     nn.predict()
    
# end of example
# ------------------------------------------------------------------------------
    
    # initialize and run parser
    parser = Parser()
    parser.askForAverageCalculation()
    
    # ask whether an NN should be trained
    nnTraining = input("Do you want to train a neural network for step recognition? (y(es) / n(o)): ")
    if (nnTraining == "yes") | (nnTraining == "y"):
        parser.askForDestination()
        parser.processData()
        
        # Retrieve parsed data as an array
        parsedData = []
        parsedData = parser.getDataArray()
        
        # Set X (input step data values) and y (input labels corresponding to the step data values)
        X = []
        y = []
        for i in range(len(parsedData) - 1):
            accArray = np.asarray(parsedData[i].getAccelerationData(), dtype=float)
            labelArray = np.asarray([parsedData[i].getLabel()], dtype=float)
            
            X.append(accArray)
            y.append(labelArray)
            
        X = np.asarray(X)
        y = np.asarray(y)
            
        # scale units
        X /= np.amax(X, axis=0) # maximum of X array
        y /= 4                  # max "score" is 4
        
        NN = NeuralNetwork()
        
        # training the NN 100,000 times
        print("Training: Started ...", end=" ")
        t = time.process_time()
        for i in range(100000):        
            if (i % 1000) == 0:
                print("# " + str(i) + "\n")
                print("Input (scaled): \n" + str(X))
                print("Actual Output: \n" + str(y))
                print("Predicted Output: \n" + str(NN.feedForward(X)))
                print("Loss: \n" + str(np.mean(np.square(y - NN.feedForward(X))))) # mean sum squared loss
                print("\n")
            NN.train(X, y)
        elapsedTime = float(int((time.process_time() - t) * 100)) / 100     # only 2 decimal positions
        print("DONE!\n", sep=' ', end="", flush=True)
        print("Time for training: " + str(elapsedTime) + " seconds.")
        
        # Save the weight values in a text-file
        print("Save weights:", end=" ")
        NN.saveWeights()
        print("DONE!\n\n", sep=' ', end="", flush=True)
        
        # Get data which should be classified
        t = parsedData[len(parsedData) - 1].getAccelerationData()   # last data entry in parsedData
        inputForPrediction = np.array((t), dtype=float)
        inputForPrediction /= np.amax(inputForPrediction, axis=0) # maximum of inputForPrediction (our input data for the prediction)
        
        NN.predict()

    elif (nnTraining == "no") | (nnTraining == "n"):
        # nothing to do
        print("Exiting the program!")
        sys.exit()
    else:
        print("Your given answer (" + nnTraining + ") was not recognized. Exiting the program!")
        sys.exit()
