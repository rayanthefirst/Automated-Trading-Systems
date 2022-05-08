##PYTHON BUILT-IN MODULES##
import os
import sys

##PIP INSTALLED MODULES##
import pandas as pd

##DISABLE PRINT OUTPUT##
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

##RENABLE PRINT OUTPUT##
def enablePrint():
    sys.stdout = sys.__stdout__

##COLOUR GREEN - CONNECTED TO BOT##
def colourGreen():
    blockPrint()
    os.system('cmd /c "color 2"')
    enablePrint()

##COLOUR YELLOW - NOT CONNECTED/WAITING FOR CONNECTION##
def colourYellow():
    blockPrint()
    os.system('cmd /c "color 6"')
    enablePrint()

##COLOUR RED - ERROR/UNABLE TO CONNECT##
def colourRed():
    blockPrint()
    os.system('cmd /c "color 4"')
    enablePrint()

##COLOUR AQUA - USER INPUT##
def colorAqua():
    blockPrint()
    os.system('cmd /c "color 3"')
    enablePrint()

##MAKE DATA FRAME FULL SCREEN##
def fullDataFrame():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)