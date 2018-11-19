# StepData.py
# Author: Armin Müller
# Created on 01.11.2018
# Last Modified on: 19.11.2018
#
# This file provides a data object to store step data in it

class StepData(object):
    def __init__(self):
        # parameters
        self.label = 0
        self.accelerationData = []
    
    #getter
    def getLabel(self):
        return self.label
    
    def getAccelerationData(self):
        return self.accelerationData

    #setter
    def setLabel(self, newLabel):
        self.label = newLabel
    
    def setAccelerationData(self, newAccelerationData):
        self.accelerationData = newAccelerationData