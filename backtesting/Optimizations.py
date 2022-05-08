##PYTHON BUILT-IN MODULES##
from copy import deepcopy
import os
import time

##CUSTOM PROJECT MODULES##
from project_classes.contract import Contract
from project_classes.portfolio import Portfolio
from useful_functions.ScreenPrint import blockPrint, enablePrint, fullDataFrame

##PIP INSTALLED MODULES##
import pandas as pd

##STRATEGY OPTIMIZATION TESTING##
##TRAIL STRATEGY OPTIMIZATION_V2##
def trailStrategyOptimization(strategyList, contract: Contract):
    defaultPortfolio = Portfolio()
    defaultPortfolio.setPortfolioWithDefaultsOnly()
    xAxis = int(input("Enter number of buyTrail trail numbers to test: "))
    yAxis = int(input("Enter number of sellTrail trail numbers to test: "))
    xFormula = str(input("Enter a formula for the buy trail percent in terms of f(x) = "))
    yFormula = str(input("Enter a formula for the sell trail percent in terms of f(x) = "))
    xTrailFormula = lambda x: eval(xFormula)
    yTrailFormula = lambda x: eval(yFormula)
    time1 = time.perf_counter()
    print(f"Buy trail range: {xTrailFormula(1)}% - {xTrailFormula(xAxis)}%\n"
          f"Sell trail range: {yTrailFormula(1)}% - {yTrailFormula(yAxis)}%\n"
          f"With buy increments of {xTrailFormula(1)}%\n"
          f"And sell increments of {yTrailFormula(1)}%\n"
          f"Backtest Started")

    optimizationLoop = 0
    dataFrames = dict()
    bestPnl = [-1E10, 0., 0., '', 0]  ##PNL, f(x), f(y), Strategy Function, Number of Transactions##
    # fullDataFrame()
    pd.set_option('display.width', 400)
    pd.set_option('display.max_columns', 20)

    for strategy in strategyList:
        print(f'Current strategy: {strategy.__name__}')
        resultMatrix = [[("") for _ in range(yAxis + 1)] for _ in range(xAxis + 1)]  ##x is buyTrail, y is sellTrail
        for x in range(1, xAxis+1):
            # print(f'Buy trail: {x}% by sellTrail trails:', end=' ')
            for y in range(1, yAxis+1):
                # print(f'{y}%', end='')
                portfolio = deepcopy(defaultPortfolio)
                portfolio.strategyUsedName, portfolio.buy, portfolio.sell = strategy.__name__, xTrailFormula(x), yTrailFormula(y)
                blockPrint()  ##DISABLES PRINTING TO SCREEN##
                strategy(portfolio, contract, portfolio.dataParser, contract.quantity, portfolio.buy, portfolio.sell)
                enablePrint() ##RE-ENABLE PRINT##
                resultMatrix[x-1][y-1] = portfolio.PnL
                if portfolio.PnL > bestPnl[0]:
                    bestPnl[0], bestPnl[1], bestPnl[2], bestPnl[3], bestPnl[4] = portfolio.PnL, portfolio.buy, portfolio.sell, strategy, portfolio.numberOfTransactions
                optimizationLoop += 1
                portfolio.__del__()

        rowIndex = [(str(xTrailFormula(x)) + '%') for x in range(1, xAxis + 1)]
        rowIndex.append(u'\u2191' + ' Buy Trail')
        columnIndex = [(str(yTrailFormula(y)) + '%') for y in range(1, yAxis + 1)]
        columnIndex.append(u'\u2190' + ' Sell Trail')
        df = pd.DataFrame(resultMatrix, index=rowIndex, columns=columnIndex)
        dataFrames[strategy.__name__] = df

    time2 = time.perf_counter()
    print(f"Best Strategy: {bestPnl[3].__name__}")
    print(dataFrames[bestPnl[3].__name__])
    print(f"Number of optimization test scenerios: {optimizationLoop}, Time taken to backtest: {time2 - time1} seconds")
    print(f"Best optimization for {contract.symbol} is the {bestPnl[3].__name__} strategy using a {bestPnl[1]}% buyTrail trai"
        f"l and a {bestPnl[2]}% sellTrail trail\n"
        f"Total number of buyTrail/sellTrail transactions: {bestPnl[4]} - PnL: "
        f"{(bestPnl[0] / (contract.historicalContractData[0].open)) * 100}% or ${bestPnl[0]} profit/loss per {contract.quantity} position(s) (Not compounded)")
    regularPNL = contract.historicalContractData[-1].close - contract.historicalContractData[0].open
    print(f"Regular buyTrail and hold would result in: {(100 * regularPNL) / contract.historicalContractData[0].open}% or ${regularPNL}")
    printResults = input("Would you like a copy of these results in a csv? (y/n): ").lower()

    if printResults == 'y':
        fileName = f'{contract.symbol}-{bestPnl[3].__name__}-OptimizationBacktest.csv'
        print(f"{fileName} saved to your desktop")
        dataFrames[bestPnl[3].__name__].to_csv(f'{os.path.expanduser("~")}\\Desktop/' + fileName)

    return bestPnl, regularPNL