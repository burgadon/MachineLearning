# MachineLearning.py
# Author: Armin Müller
# Created on 19.10.2018
# Last Modified on: 10.12.2018
#
# This project aims to use a neural network to decide which type of step 
# the given step data represents

import numpy as np
from src.Parser import Parser
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
        self.W1 = np.matrix([[10.007343465980664, 5.113687635194334, 10.743692465400681],
        [-5.482072882025064, 1.710683866674025, -11.273259210070421],
        [-6.210177219251583, -4.299305906476425, -7.137855498482551],
        [0.053834364631157004, -0.11361658909616405, 0.9349942111048926],
        [-1.6344774151722814, -0.5800769180741111, 0.6968202422204991],
        [0.21503462895170905, -0.20637675331092015, -2.648316104798255],
        [6.485511882359739, 6.001813741534642, -2.070565449704359],
        [-12.845249376060709, -5.249647815044626, -26.120509434158624],
        [-3.201236245906119, -5.249431273873157, 0.2093727359358657]])
        self.W2 = np.matrix([[-11.288591202763781], [4.982001257876912], [5.114694548460975]])       
        
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
        
# ------------------------------------------------------------------------------
# Methods for usage

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
            if int(np.round(resultArray[i] * 10)) != 5:
                file.write(str("noMove"))
            elif int(np.round(resultArray[i] * 10)) == 5:
                file.write(str("oneStep"))
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
        
    def predictWithoutPrint(self, inputForPrediction):
        return self.feedForward(inputForPrediction)
        
    def getUnclassifiedDataToClassify(self, nonInteractive, unclassifiedDataArray):
        unclassifedDataParser = Parser()
        
        if (nonInteractive == True):
            unclassifedDataParser.processDataArray(unclassifiedDataArray)
            
            # Retrieve data back
            parsedUnclassifiedData = unclassifedDataParser.getDataArray()
        else:
            unclassifiedDataPath = input("Enter path to file with data, which is to be classified: ")
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
        inputLabels /= 3                    # max "score" is 3 (amount of different step labels)
        
        return (inputValues, inputLabels)
        
    def listenOnPort(self):
        rawInputData = []
        port = "COM9"
        baudrate = 9600
        timeout = 0.25
        ser = serial.Serial(port, baudrate, timeout)
        if ser.isOpen():
            print(ser.name + " was successfully opened.")
            while self.listen == True:
                rawInputData.append(ser.readline())
        else:
            raise ValueError("Opening the serial port connection on port \"" + port + "\" failed")
        
        ser.close()
        return rawInputData

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    NN = NeuralNetwork()
    
    # Get data which should be classified
    rawDataFromPort = NN.listenOnPort()
    (XTemp, yTemp) = NN.getUnclassifiedDataToClassify(True, rawDataFromPort);   # non-interactive version
    inForPrediction = np.array((XTemp), dtype=float)
    inForPrediction /= np.amax(inForPrediction, axis=0)                         # maximum of inForPrediction (our input data for the prediction)
     
    # Predict
    result = []
    for j in range(len(inForPrediction)):
        result.append(NN.predictWithoutPrint(inForPrediction[j]))

    # Save results in a file
    NN.saveResults(result)
    