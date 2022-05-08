###PYTHON BUILT-IN MODULES##
import configparser
import os
import sys

##CUSTOM PROJECT MODULES##
from backtesting.Optimizations import trailStrategyOptimization
from backtesting.Strategies import chooseBackTestStrategies, marginStrategies
from project_classes.marketData import MarketData
from useful_functions.ScreenPrint import enablePrint, colorAqua


def startBackTester():
    while True:
        md = MarketData()
        md.btContract.chooseContractType()
        md.chooseMarketDataSource()
        try:
            strategies = chooseBackTestStrategies(marginStrategies)
            trailStrategyOptimization(strategies, md.btContract)
        except Exception:
            enablePrint()
            print("Input error encountered, please try again")
            md.__del__()
            continue
        md.__del__()
        if input("Would you like to run another backtest? (y/n): ").lower() != 'y':
            input("Press enter to exit")
            break

def stockBackTesterInterface():
    os.system('cls' if os.name == 'nt' else 'clear')
    colorAqua()
    cmdArgs = sys.argv  ##0 FILE, 1 SYMBOL, 2 QUANTITY, 3 BUY TRAIL, 4 BUY TYPE, 5 SELL TRAIL, 6 SELL TYPE, 7 STRATEGY POSITION, 8 PORT, 9 CLIENTID, 10 ACCOUNTNUMB, 11 ACCOUNTTYPE - INPUTTED AS STRINGS - MAKE SURE TO CAST TO CORRECT DATA TYPE##

    ##COMMAND LINE ARGS PASSED FOR AUTOMATION##
    if len(cmdArgs) > 1:
        md = MarketData()
        md.btContract.setStockContract(cmdArgs[1], int(cmdArgs[2]))
        md.partialConnecionInputAndStart(int(cmdArgs[8]), int(cmdArgs[9]))
        md.checkInitialConnection()
        # md.getEarliestDataDate() todo you might not need this in the auto version
        md.getNextValidId() ##todo make a function that looks for stock csv, changes it to 1 min daily and caches candles
        ##todo add loop to do 1 Y, 6M, 3M, 1M , 1W and make formula using trails and stratgey to refine bot
        md.ibapiHistoricalData(93600, md.nextValidOrderId, md.btContract, '', '1 Y', '1 min', 'BID') ##fixme hardcoded to 1 Y 1 min, make a cache file and diff time frames??
        # md.historicalDataToCsv() todo create cache
        md.disconnect()
        bestPnl = trailStrategyOptimization(marginStrategies, md.btContract) ##fixme assuming CASH cause using all strategies add logic using sys args abput account
        config = configparser.ConfigParser()
        config.read(f'{os.path.expanduser("~")}\\Desktop/fileConfig.ini')
        file = config['STOCKTRAILINGBOT']['stockbotdefaults']
        md.changeBestPnl(file, bestPnl)
        ##Add more logic for other time frames
        ##ADD function for best Pnl to edit StockBotDefaults csv

        ##MANUAL INPUT##
    else:
        startBackTester()

if __name__ == '__main__':
    stockBackTesterInterface()