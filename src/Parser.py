# Parser.py
# Author: Armin Müller
# Created on 01.11.2018
# Last Modified on: 19.11.2018
#
# This file provides a parser to extract the data out of input files for
# the walking-NN-project

from src.StepData import StepData

class Parser(object):
    def __init__(self):
        # parameters
        self.destination = ""
        self.data = []
        self.lineCtr = 1
        self.dataArrayIndex = 1
        self.average = [0.0, 0.0, 0.0]
        
    def askForDestination(self):
        self.destination = input("Type in the destination of the file, which should be parsed:\n")
        print("Input Destination: " + self.destination)
    
    def askForAverageCalculation(self):
        result = input("Do you want to calculate the average for noise reduction purposes? (yes/no): ")
        if result == "yes":
            # calculate the average for noise reduction
            self.askForDestination()
            self.processData()
            for i in len(self.average):
                self.average[i] /= self.lineCtr
            
            print("The average values are: x = " + str(self.average[0]) + ", y = " + str(self.average[1]) + ", z = " + str(self.average[2]) + ".")
            
        elif result == "no":
            # nothing to do
            return None
        else:
            print("Your given answer (" + result + ") was not recognized. Try again!")
            self.askForAverageCalculation()
    
    def processData(self):
        with open(self.destination, "r") as file:
            data = file.readlines()
            self.lineCtr = 1    # reset line counter
            
            for line in data:
                # if line is empty: skip it
                if line.replace(" ", "").replace("\n", "").replace("\r", "").isEmpty():
                    continue
                
                # for noise reduction purposes
                if line.contains("noise"):                    
                    sum = [0.0, 0.0, 0.0]
                    self.processNoiseDataLine(line.replace(" ", "").replace("\n", "").replace("\r", ""), sum)
                    self.lineCtr += 1
                    self.average += sum
                
                else:
                    # normal data processing
                    # set index for data array
                    if (self.lineCtr % 3) == 0:
                        self.dataArrayIndex += 1
                    
                    # create new step data object
                    stepData = StepData()
                    
                    self.processLine(line.replace(" ", "").replace("\n", "").replace("\r", ""), stepData)
                    self.data[self.dataArrayIndex].append(stepData)     # TODO: do we need 3 in one line or just self.data.append(stepData)?
                    self.lineCtr += 1

    def processLine(self, line, stepData):
        line = self.processRubbishAtStart(line)
        line = self.processRubbishAtEnd(line)
        line = self.processPairOfLeadingAndTrailingBrackets(line)
        line = self.processLabel(line, stepData)
        line = self.processAccelerationData(line, stepData)
        
        if not line.isEmpty():
            raise ValueError("Error processing line " + str(self.lineCtr)
                + ": The processed line should be empty at this point, but \""
                + line + "\" was found.")
            
    def processNoiseDataLine(self, line, sum):
        line = self.processRubbishAtStart(line)
        line = self.processRubbishAtEnd(line)
        line = self.processPairOfLeadingAndTrailingBrackets(line)
        line = self.processNoiseData(line, sum)
        
        if not line.isEmpty():
            raise ValueError("Error processing line " + str(self.lineCtr)
                + ": The processed line should be empty at this point, but \""
                + line + "\" was found.")
    
    def processRubbishAtStart(self, line):
        # check for undefined start characters
        if line.startswith("[{"):
            # found valid beginning
            return line
        if len(line) < 2:
            # invalid line format/content
            raise ValueError("Error processing line " + str(self.lineCtr)
                + ": Start of line wasn't found and/or line is too short.")
        else:
            # search for beginning of json
            for i in range(len(line)):
                line = line[1:] # cut off first character and check again
                line = self.processRubbishAtStart(line)
                
        return line
    
    def processRubbishAtEnd(self, line):
        # check for undefined end characters
        if line.endswith("}]"):
            # found valid end
            return line
        if len(line) < 2:
            # invalid line format/content
            raise ValueError("Error processing line " + str(self.lineCtr)
                + ": End of line wasn't found and/or line is too short.")
        else:
            # search for ending of json
            for i in range(len(line)):
                line = line[:-1] # cut off last character and check again
                line = self.processRubbishAtEnd(line)
                
        return line  
    
    def processPairOfLeadingAndTrailingBrackets(self, line):
        # check for matching brackets
        if line.startswith("[{"):
            if line.endswith("}]"):
                # matching brackets --> delete them
                line.replace("[{", "", 1)
                line = line[:-2]
            else:
                raise ValueError("Error processing line " + str(self.lineCtr)
                    + ": No closing brackets (\"}]\") found at end of line.")
        else:
            raise ValueError("Error processing line " + str(self.lineCtr)
                    + ": No opening brackets (\"[{\") found at start of line.")
        
        return line

    def processLabel(self, line, stepData):
        # check for the "Label" keyword and delete it
        if line.startswith("\"Label\""):
            line = line.replace("\"Label\":", "")
        else:
            raise ValueError("Error processing line " + str(self.lineCtr)
                    + ": The \"Label\" keyword was not found.")

        # process the actual label
        if line.startswith("slowWalk"):
            #found label
            line = line.replace("slowWalk,", "")
            stepData.setLabel("slowWalk")
            return line
        elif line.startswith("noMove"):
            #found label
            line = line.replace("noMove,", "")
            stepData.setLabel("noMove")
            return line
        elif line.startswith("casualWalk"):
            #found label
            line = line.replace("casualWalk,", "")
            stepData.setLabel("casualWalk")
            return line
        elif line.startswith("fastWalk"):
            #found label
            line = line.replace("fastWalk,", "")
            stepData.setLabel("fastWalk")
            return line
        else:
            raise ValueError("Error processing line " + str(self.lineCtr)
                    + ": The label is not supported or missing.")

    def processAccelerationData(self, line, stepData):
        if line.startswith("\"Acceleration\":"):
            line = line.replace("\"Acceleration\":{", "", 3)
            line = line.replace("}", "", 3)     # delete matching closing brackets
            
            # replace keywords for axes
            line = line.replace("\"x-Axes\":", "", 1)
            line = line.replace(",\"x-Axes\":", ";", 2)
            line = line.replace(",\"y-Axes\":", ";", 3)
            line = line.replace(",\"z-Axes\":", ";", 3)
            line = line.replace(",", "")        # delete trailing comma
            
            splittedLine = line.split(";")
            stepData.setAccelerationData(splittedLine)        
        else:
            raise ValueError("Error processing line " + str(self.lineCtr)
                    + ": The \"Acceleration\" keyword was not found.")
        
        return line

    def processNoiseData(self, line, sum):
        if line.contains("noise"):
            line = line.replace("noise,", "")
            line = line.replace("\"Acceleration\":{", "", 3)
            line = line.replace("}", "", 3)     # delete matching closing brackets
            
            # replace keywords for axes
            line = line.replace("\"x-Axes\":", "", 1)
            line = line.replace(",\"x-Axes\":", ";", 2)
            line = line.replace(",\"y-Axes\":", ";", 3)
            line = line.replace(",\"z-Axes\":", ";", 3)
            line = line.replace(",", "")        # delete trailing comma
            
            splittedLine = line.split(";")
            
            for i in range(3):
                sum[i] += splittedLine[i] + splittedLine[i + 3] + splittedLine[i + 6]
            
        else:
            raise ValueError("Error processing line " + str(self.lineCtr)
                    + ": The \"noise\" keyword was not found.")
        
        return line

    # getter
    def getData(self):
        return self.data

    def getAverage(self):
        return self.average

    # setter
    def setDestination(self, destinationPath):
        self.destination = destinationPath
    
    # reverse replace (currently unused)
    def rreplace(self, string, old, new, occurrence):
        # replaces a char/string from the ending
        # s = "1232425"
        # rreplace(s, '2', ' ', 2) leads to "123 4 5"
        # rreplace(s, '2', ' ', 3) leads to "1 3 4 5"
        # rreplace(s, '2', ' ', 4) leads to "1 3 4 5"
        # rreplace(s, '2', ' ', 0) leads to "1232425"
        
        li = string.rsplit(old, occurrence)
        return new.join(li)
