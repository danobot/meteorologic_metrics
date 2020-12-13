from .const import *

def toK(celsius):
    return celsius + KELVIN_CONVERSION



def toC(celsius):
    return celsius - KELVIN_CONVERSION    

def FtoC(f):
    return (f - 32) * 5/9

def CtoF(c):
    return c * (9/5) + 32 

def KtoF(k):
    return toC(k) * (9/5) + 32 

