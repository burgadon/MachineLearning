# MachineLearning.py
# Author: Armin Müller
# Created on 19.10.2018
# Last Modified on: 17.04.2019
#
# This project aims to use a neural network to decide which type of step 
# the given step data represents

import numpy as np
from src.Parser import Parser
import repackage
repackage.up()
import sys
import time
import os
import datetime
import serial

class NeuralNetwork:
    def __init__(self):
        #parameters
        self.lastModifiedDay = 0
        self.listen = True
        
        self.inputSize = 9
        self.outputSize = 1
        self.hiddenSize = 3
        
        #weights
        self.W1 = np.random.randn(self.inputSize, self.hiddenSize)  # (9x3) weight matrix from input to hidden layer
        self.W2 = np.random.randn(self.hiddenSize, self.outputSize) # (3x1) weight matrix from hidden to output layer
        
        #hardcoded weights, if they're wanted/needed
#         self.W1 = np.matrix([[-58.17468245205648, -4.352426965518547, -6.694536989324792],
#         [0.21261185107611572, -1.9341255493913152, 8.567297288647586],
#         [-10.696576850984954, -0.20916310437075541, 17.374917838290887],
#         [-14.96391461674491, -6.191260702326583, -46.37156498558644],
#         [-15.793203621045249, -5.654444020625949, 8.999346101224896],
#         [7.4543182333121205, 2.572536592650819, 1.690432599459533],
#         [-20.252352762521976, -5.134002369809387, -23.793922311983586],
#         [-12.915597455972685, -4.509141940967371, -14.093639305179845],
#         [10.89464302328708, -1.4680942999995534, -2.3742310728376346]])   
#         self.W2 = np.matrix([[1.4298028915296566], [-3.002928109567485], [1.7687637949560497]])    

    # Activation function
    def sigmoid(self, t):
        return 1 / (1 + np.exp(-t))
    
    # Derivative of sigmoid function
    def sigmoidDerivative(self, p):
        return p * (1 - p)

    #forward propagation through the network
    def feedForward(self, X):
        self.z = np.dot(X, self.W1)         # weighted input: dot product of X (input) and first set of 9x3 weights
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
        
# ------------------------------------------------------------------------------
# Methods for usage in the context of the IoT-practical

    def saveWeights(self):
        np.savetxt("w1.txt", self.W1, fmt="%s")
        np.savetxt("w2.txt", self.W2, fmt="%s")

    def saveResults(self, resultArray):
        resultPath = "classificationResults.txt"
        date = time.strftime("%Y%m%d")
        currentDate = self.dateToNthDay(date)
        
        if os.path.exists(resultPath) & ((currentDate - self.lastModifiedDay) == 0):
            appendMode = 'a'    # Append only at the end
        else:
            appendMode = 'w'    # Create a new file
        
        file = open(resultPath, appendMode)
        for i in range(len(resultArray)):
            # For DEBUGGING
            #print(str(resultArray[i]))
            
            if int(np.round(resultArray[i] * 10)) != 5:
                file.write(str("noMove"))
            elif int(np.round(resultArray[i] * 10)) == 5:
                file.write(str("slowWalk"))
            else: 
                file.write(str("labelPlaceholder"))
            
            if (i != len(resultArray) - 1):
                file.write(",")
        file.close()
        
        # Update last time modified parameter
        self.lastModifiedDay = currentDate
        
    def dateToNthDay(self, date):
        date = datetime.datetime.strptime(date, "%Y%m%d")
        new_year_day = datetime.datetime(year=date.year, month=1, day=1)
        return (date - new_year_day).days + 1

    def predictWithPrint(self, inputForPrediction):
        print("Predicted data based on trained weights:")
        print("Input: \n" + str(inputForPrediction))
        print("Output: \n" + str(self.feedForward(inputForPrediction)))
        
    def predictWithoutPrint(self, inputForPrediction):
        return self.feedForward(inputForPrediction)
        
    def getUnclassifiedDataToClassify(self, nonInteractive, unclassifiedDataArray):
        if (nonInteractive == True):
            parsedUnclassifiedData = unclassifiedDataArray
        elif (nonInteractive == False):
            unclassifiedDataPath = input("Please enter the path to a file with data, which should be classified: ")
            unclassifedDataParser = Parser()
            unclassifedDataParser.setDestination(unclassifiedDataPath)
            unclassifedDataParser.processData()

            # Retrieve data back
            parsedUnclassifiedData = unclassifedDataParser.getDataArray()
        
        # Set necessary input arrays
        (inputValues, inputLabels) = self.setInputForClassificationScaled(parsedUnclassifiedData)
        
        return (inputValues, inputLabels)

    def setInputForClassificationScaled(self, parsedDataArray):
        # Set X (input step data values) and y (input labels corresponding to the step data values)
        inputValues = []
        inputLabels = []
        
        for i in range(len(parsedDataArray)):
            accArray = np.asarray(parsedDataArray[i].getAccelerationData(), dtype=float)
            labelArray = np.asarray([parsedDataArray[i].getLabel()], dtype=float)
            
            inputValues.append(accArray)
            inputLabels.append(labelArray)
            
        inputValues = np.asarray(inputValues)
        inputLabels = np.asarray(inputLabels)
        
        # scale units
        inputValues /= np.amax(inputValues) # maximum of X array
        inputLabels /= 3                    # max "score" is 3 (amount of different step labels (noMove, slowWalk, labelPlaceholder))
        
        return (inputValues, inputLabels)
        
    def listenOnPort(self):
        # Note that this method might only return when the data stream on the com-port ends
        rawInputData = []
        port = "COM9"
        baudrate = 115200
        ser = serial.Serial(port, baudrate, timeout = None)
        if ser.isOpen():
            print(ser.name + " was successfully opened.")
            while self.listen == True:
                rawInputData.append(ser.readline())
        else:
            raise ValueError("Opening the serial port connection on port \"" + port + "\" failed")
        
        ser.close()
        return rawInputData
    
# ------------------------------------------------------------------------------
# Usage of the NN

if __name__ == "__main__":
    # Initialize and run parser
    parser = Parser()
    #parser.askForAverageCalculation()           # Asks whether new average values should be calculated
    
    # Ask whether an NN should be trained
    nnTraining = input("Do you want to train a neural network for step recognition? (y(es) / n(o)): ")
    if (nnTraining == "yes") or (nnTraining == "y"):
        NN = NeuralNetwork()
         
        #NN.listen = True
        #inArray = NN.listenOnPort()
        #parser.processDataArray(inArray)
        parser.askForDestination()
        parser.processData()
         
        # Retrieve parsed data as an array
        parsedData = []
        parsedData = parser.getDataArray()
         
        # Set X (input step data values) and y (input labels corresponding to the step data values)
        X = []
        y = []
        (X, y) = NN.setInputForClassificationScaled(parsedData)
         
        # Start new training
        print("Training: Started ...\n", end=" ")
        t = time.process_time()
        loss = 1.0      # initialize loss
        trainingCounter = 0
        maxLossValue = 0.0225
        while (loss > maxLossValue):    # train as long as the loss is greater than the maxLossValue
            NN.train(X, y)
            loss = np.mean(np.square(y - NN.feedForward(X)))    # mean sum squared loss
             
            if (trainingCounter % 10000) == 0:
                print("# " + str(trainingCounter) + "\n")
                print("Input (scaled): \n" + str(X))
                print("Actual Output: \n" + str(y))
                print("Predicted Output: \n" + str(NN.feedForward(X)))
                print("Loss: \n" + str(loss))
                print("\n")
             
            trainingCounter += 1
             
        elapsedTime = float(int((time.process_time() - t) * 100)) / 100     # only 2 decimal positions
        print("DONE!\n", sep=' ', end="", flush=True)
        print("Time for training: " + str(elapsedTime) + " seconds.")
        print("The neural net was trained through " + str(trainingCounter) + " runs.")
         
        # Save the weight values in a text-file
        print("Save weights:", end=" ")
        NN.saveWeights()
        print("DONE!\n", sep=' ', end="", flush=True)
        print("Final loss: " + str(loss) + "\n")
         
        # Get data which should be classified
        (XTemp, yTemp) = NN.getUnclassifiedDataToClassify(False, "");   # Interactive version of the getUnclassifiedDataToClassify() method
        inForPrediction = np.array((XTemp), dtype=float)
        inForPrediction /= np.amax(inForPrediction, axis=0)             # maximum of inForPrediction (our input data for the prediction)
         
        # Predict
        result = []
        for j in range(len(inForPrediction)):
            result.append(NN.predictWithoutPrint(inForPrediction[j]))
         
        # Save the resulting weights in a file
        NN.saveResults(result)
 
    elif (nnTraining == "no") or (nnTraining == "n"):
        # nothing to do
        print("Exiting the program!")
        sys.exit(0)
    else:
        print("Your given answer (" + nnTraining + ") was not recognized. Exiting the program!")
        sys.exit(0)

#-------------------------------------------------------------------------------
# NN usage without text and statistics:
#     NN = NeuralNetwork()
#     # Get data which should be classified
#     (XTemp, yTemp) = NN.getUnclassifiedDataToClassify(False, "");   # Interactive version
#     inForPrediction = np.array((XTemp), dtype=float)
#     inForPrediction /= np.amax(inForPrediction, axis=0)             # maximum of inForPrediction (our input data for the prediction)
#      
#     # Predict
#     result = []
#     for j in range(len(inForPrediction)):
#         result.append(NN.predictWithoutPrint(inForPrediction[j]))
#     #NN.predictWithPrint(inForPrediction)
#      
#     # Save results in a file
#     NN.saveResults(result)
    