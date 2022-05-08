##PYTHON BUILT-IN MODULES##
import os

##CUSTOM PROJECT MODULES##
from backtesting.OptimizationsMultiprocessed import trailStrategyOptimization
from backtesting.Strategies import chooseBackTestStrategies, marginStrategies
from project_classes.marketData import MarketData
from useful_functions.ScreenPrint import enablePrint

def startBackTester():
    os.system('cmd /c "color a"')
    os.system('cls' if os.name == 'nt' else 'clear')

    # while True:
    md = MarketData()
    md.btContract.chooseContractType()
    md.chooseMarketDataSource()
        # try:
    strategies = chooseBackTestStrategies(marginStrategies)
    trailStrategyOptimization(strategies, md.btContract)
        # except Exception:
        #     enablePrint()
        #     print("Input error encountered, please try again")
        #     md.__del__()
        #     continue
        # md.__del__()
        # if input("Would you like to run another backtest? (y/n): ").lower() != 'y':
        #     input("Press enter to exit")
        #     break

if __name__ == '__main__':
    startBackTester()