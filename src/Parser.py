# Parser.py
# Author: Armin Müller
# Created on 01.11.2018
# Last Modified on: 02.11.2018
#
# This file provides a parser to extract the data out of input files for
# the walking-NN-project

from src.StepData import StepData

class Parser(object):
    def __init__(self):
        # parameters
        self.destination = ""
        self.data
        self.lineCtr = 1
        
    def askForDestination(self):
        self.destination = input("Type in the destination of the file, which should be parsed:\n")
        print("Input Destination: " + self.destination)
    
    def processData(self):
        with open(self.destination, "r") as file:
            data = file.readlines()
            
            for line in data:
                stepData = StepData("", 0.0, 0.0, 0.0)
                
                self.processLine(line.replace(" ", ""), stepData)
                self.data.append(stepData)
                self.lineCtr += 1

    def processLine(self, line, stepData):
        line = self.processPairOfLeadingAndTrailingBracket(line)
        line = self.processLabel(line, stepData)
        line = self.processAccelerationData(line, stepData)
        
        if not line.isEmpty():
            raise ValueError("Error processing line " + self.lineCtr
                + ": The processed line should be empty at this point, but \""
                + line + "\" was found.")
    
    def processPairOfLeadingAndTrailingBracket(self, line):
        # check for matching brackets
        if line.startswith("{"):
            if line.endswith("}"):
                # matching brackets --> delete them
                line.replace("{", "", 1)
                line = line[:-1]
            else:
                raise ValueError("Error processing line " + self.lineCtr
                    + ": No closing bracket (\"}\") found at end of line.")
        else:
            raise ValueError("Error processing line " + self.lineCtr
                    + ": The first character is no opening bracket (\"{\").")
        
        return line

    def processLabel(self, line, stepData):
        # check for the "Label" keyword and delete it
        if line.startswith("\"Label\""):
            line = line.replace("\"Label\":\"", "")
        else:
            raise ValueError("Error processing line " + self.lineCtr
                    + ": The \"Label\" keyword was not found.")

        # process the actual label
        if line.startswith("One_Step_right_foot"):
            #found label
            line = line.replace("One_Step_right_foot\",", "")
            stepData.setLabel("One_Step_right_foot")
            return line
        elif line.startswith("One_Step_left_foot"):
            #found label
            line = line.replace("One_Step_left_foot\",", "")
            stepData.setLabel("One_Step_left_foot")
            return line
        else:
            raise ValueError("Error processing line " + self.lineCtr
                    + ": The label is not supported or missing.")

    def processAccelerationData(self, line, stepData):
        if line.startswith("\"Acceleration\":"):
            line = line.replace("\"Acceleration\":", "")
            line = self.processPairOfLeadingAndTrailingBracket(line)
        else:
            raise ValueError("Error processing line " + self.lineCtr
                    + ": The \"Acceleration\" keyword was not found.")
        # replace keywords for axes
        line = line.replace("\"x-Axes\":\"", "")
        line = line.replace("\",\"y-Axes\":\"", ";")
        line = line.replace("\",\"z-Axes\":\"", ";")
        line = line.replace("\"", "") # trailing quotation marks
        
        splittedLine = line.split(";")
        stepData.setAccelerationX(splittedLine[0])
        stepData.setAccelerationY(splittedLine[1])
        stepData.setAccelerationZ(splittedLine[2])
        
        return line
    
    # getter
    def getData(self):
        return self.data
    
    # setter
    def setDestination(self, destinationPath):
        self.destination = destinationPath
    
    # currently unused
    def rreplace(self, string, old, new, occurrence):
        # replaces a char/string from the ending
        # s = "1232425"
        # rreplace(s, '2', ' ', 2) leads to "123 4 5"
        # rreplace(s, '2', ' ', 3) leads to "1 3 4 5"
        # rreplace(s, '2', ' ', 4) leads to "1 3 4 5"
        # rreplace(s, '2', ' ', 0) leads to "1232425"
        
        li = string.rsplit(old, occurrence)
        return new.join(li)
