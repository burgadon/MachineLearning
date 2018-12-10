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
                    
    # If the data is gathered through listening on a port, use this method
    def processDataArray(self, rawDataArray):
        # Reset processed data array
        self.data = []
        
        for line in rawDataArray:
            # if line is empty: skip it
            lineWithoutSpacesAndLineFeeds = line.replace(" ", "").rstrip()
            if len(lineWithoutSpacesAndLineFeeds) == 0:
                continue

            if len(line) < 20:
                # line too short, skip it
                continue
            else:
                # normal data processing
                stepData = StepData()   # create new step data object

                self.processLine(line.replace(" ", "").rstrip(), stepData)
                self.data.append(stepData)
                self.lineCtr += 1

    def processLine(self, line, stepData):
        line = self.processRubbishAtStart(line)
        line = self.processRubbishAtEnd(line)
        line = self.processPairOfLeadingAndTrailingBrackets(line)
        line = self.processLabel(line, stepData)
        line = self.processAccelerationData(line, stepData)

    def processRubbishAtStart(self, line):
        # check for undefined start characters
        if line.startswith("[{"):
            # found valid beginning
            return line
        if len(line) < 2:
            # invalid line format/content
            raise ValueError("Error processing line " + str(self.lineCtr)
                + ": Start of line wasn't found and/or line is too short.")
            return None
        else:
            # search for beginning of json
            line = line[1:] # cut off first character and check again
            line = self.processRubbishAtStart(line)

        return line

    def processRubbishAtEnd(self, line):
        # check for undefined end characters
        if line.endswith(",}}]"):
            # found valid end
            return line
        if len(line) < 3:
            # invalid line format/content
            raise ValueError("Error processing line " + str(self.lineCtr)
                + ": End of line wasn't found and/or line is too short.")
            return None
        else:
            # search for ending of json
            line = line[:-1] # cut off last character and check again
            line = self.processRubbishAtEnd(line)

        return line

    def processPairOfLeadingAndTrailingBrackets(self, line):
        # check for matching brackets
        if line.startswith("[{"):
            if line.endswith("}]"):
                # matching brackets --> delete them
                line = line.replace("[{", "", 1)
                line = line[:-2]
            else:
                print("Error processing line " + str(self.lineCtr)
                    + ": No closing brackets (\"}]\") found at end of line.")
                line = ""
        else:
            print("Error processing line " + str(self.lineCtr)
                    + ": No opening brackets (\"[{\") found at start of line.")
            line = ""

        return line

    def processLabel(self, line, stepData):
        # check for the "Label" keyword and delete it
        if line.startswith("\"Label\""):
            line = line.replace("\"Label\":", "")
        else:
            raise ValueError("Error processing line " + str(self.lineCtr)
                    + ": The \"Label\" keyword was not found.")

        # process the actual label
        if line.startswith("noMove"):
            #found label
            line = line.replace("noMove,", "")
            stepData.setLabel(1)
            return line
        elif line.startswith("slowWalk"):
            #found label
            line = line.replace("slowWalk,", "")
            stepData.setLabel(2)
            return line
        elif line.startswith("casualWalk"):
            #found label
            line = line.replace("casualWalk,", "")
            stepData.setLabel(2)
            return line
        elif line.startswith("fastWalk"):
            #found label
            line = line.replace("fastWalk,", "")
            stepData.setLabel(2)
            return line
        elif line.startswith("labelPlaceholder"):
            #found label
            line = line.replace("labelPlaceholder,", "")
            stepData.setLabel(0)
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
            for i in range(len(splittedLine)):
                splittedLine[i] = float(splittedLine[i])
            stepData.setAccelerationData(splittedLine)
        else:
            raise ValueError("Error processing line " + str(self.lineCtr)
                    + ": The \"Acceleration\" keyword was not found.")

        return line

    # getter
    def getDataArray(self):
        return self.data

    # setter
    def setDestination(self, destinationPath):
        self.destination = destinationPath
