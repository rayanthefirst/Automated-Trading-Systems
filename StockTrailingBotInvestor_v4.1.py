##PYTHON BUILT-IN MODULES##
import os
import sys

##CUSTOM PROJECT MODULES##
from project_classes.StockTrailingBotInvestor import StockTrailingBot, botStart, csvEditor
from useful_functions.ScreenPrint import colorAqua

##V4.1 EXCLUSIVE TO STRATEGIES (TAKES COMMAND LINE ARGS OR USER INPUT)##
def stockBotInterface():
    os.system('cls' if os.name == 'nt' else 'clear')
    colorAqua()
    cmdArgs = sys.argv ##0 FILE, 1 SYMBOL, 2 QUANTITY, 3 BUY TRAIL, 4 BUY TYPE, 5 SELL TRAIL, 6 SELL TYPE, 7 STRATEGY POSITION, 8 PORT, 9 CLIENTID, 10 ACCOUNTNUMB, 11 ACCOUNTTYPE - INPUTTED AS STRINGS - MAKE SURE TO CAST TO CORRECT DATA TYPE##

    ##COMMAND LINE ARGS PASSED FOR AUTOMATION##
    if len(cmdArgs) > 1:
        app = StockTrailingBot()
        app.botContract.setStockContract(cmdArgs[1], int(cmdArgs[2]))
        app.autoBotParameters(float(cmdArgs[3]), cmdArgs[4], float(cmdArgs[5]), cmdArgs[6], int(cmdArgs[7]))
        app.partialConnecionInputAndStart(int(cmdArgs[8]), int(cmdArgs[9]))
        app.autoSetAccount(cmdArgs[10], cmdArgs[11])
        app.checkInitialConnection()
        botStart(app)

    ##MANUAL INPUT##
    else:
        csvEditor()

if __name__ == '__main__':
    stockBotInterface()