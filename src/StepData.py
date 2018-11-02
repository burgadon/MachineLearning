# StepData.py
# Author: Armin Müller
# Created on 01.11.2018
# Last Modified on: 02.11.2018
#
# This file provides a data object to store step data in it

class StepData:
    def __init__(self, label, accelerationX, accelerationY, accelerationZ):
        # parameters
        self.label = label
        self.accelerationX = accelerationX
        self.accelerationY = accelerationY
        self.accelerationZ = accelerationZ
    
    #getter
    def getLabel(self):
        return self.label
    
    def getAccelerationX(self):
        return self.accelerationX
    
    def getAccelerationY(self):
        return self.accelerationY
    
    def getAccelerationZ(self):
        return self.accelerationZ

    #setter
    def setLabel(self, newLabel):
        self.label = newLabel
    
    def setAccelerationX(self, newAccelerationX):
        self.accelerationX = newAccelerationX
    
    def setAccelerationY(self, newAccelerationY):
        self.accelerationY = newAccelerationY
    
    def setAccelerationZ(self, newAccelerationZ):
        self.accelerationZ = newAccelerationZ