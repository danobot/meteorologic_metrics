from .const import *

def toK(self, celsius):
    return celsius + KELVIN_CONVERSION



def toC(self, celsius):
    return celsius - KELVIN_CONVERSION    

def FtoC(self, f):
    return (f - 32) * 5/9

def CtoF(self, c):
    return c * (9/5) + 32 

def KtoF(self, k):
    return toC(k) * (9/5) + 32 

