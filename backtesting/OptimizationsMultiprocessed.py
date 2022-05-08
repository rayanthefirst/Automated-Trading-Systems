##PYTHON BUILT-IN MODULES##
import os
from copy import deepcopy
from multiprocessing import Array, Lock, Process
import time

##CUSTOM PROJECT MODULES##
from project_classes.contract import Contract
from project_classes.portfolio import Portfolio
from useful_functions.ScreenPrint import blockPrint, enablePrint

##STRATEGY OPTIMIZATION TESTING##
##TRAIL STRATEGY OPTIMIZATION_V2##
def multiStrategy(funcList: list, func, bestPnl: Array, lock: Lock, portfolio, contract, dataParser, quantity, buy, sell):
    blockPrint()
    pnl = func(portfolio, contract, dataParser, quantity, buy, sell)
    enablePrint()
    lock.acquire()
    if pnl > bestPnl[0]:
        bestPnl[0], bestPnl[1], bestPnl[2], bestPnl[3], bestPnl[4] = portfolio.PnL, portfolio.buy, portfolio.sell, funcList.index(func), portfolio.numberOfTransactions
    lock.release()

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
    l = Lock()
    bestPnl = Array('d', 5)  ##PNL, f(x), f(y), Strategy Function, Number of Transactions
    bestPnl[0] = -10E10
    processes = []

    for strategy in strategyList:
        print(f'Current strategy: {strategy.__name__}')
        for x in range(1, xAxis+1):
            for y in range(1, yAxis+1):
                portfolio = deepcopy(defaultPortfolio)
                portfolio.strategyUsedName, portfolio.buy, portfolio.sell = strategy.__name__, xTrailFormula(x), yTrailFormula(y)
                p = Process(target=multiStrategy, args=(strategyList, strategy, bestPnl, l, portfolio, contract, portfolio.dataParser, contract.quantity, portfolio.buy, portfolio.sell))
                processes.append(p)
                # p.start() TODO FOR MORE PROCESSES THAN PROCCESSORS
                optimizationLoop += 1

    osProcess = [] ##fixme TEST FOR MULTIPROCESSING IN BATCHES EQUAL TO OS COUNT
    for index, process in enumerate(processes):
        osProcess.append(process)
        if len(osProcess) == os.cpu_count():
            for p in osProcess:
                p.start()
            for p in osProcess:
                p.join()
            osProcess.clear()

    # for process in processes: TODO FOR MORE PROCESSES THAN PROCESSORS
    #     process.join()


    time2 = time.perf_counter()
    print(f"Best Strategy: {strategyList[int(bestPnl[3])].__name__}")
    print(f"Number of optimization test scenerios: {optimizationLoop}, Time taken to backtest: {time2 - time1} seconds")
    print(f"Best optimization for {contract.symbol} is the {strategyList[int(bestPnl[3])].__name__} strategy using a {bestPnl[1]}% buyTrail trai"
        f"l and a {bestPnl[2]}% sellTrail trail\n"
        f"Total number of buyTrail/sellTrail transactions: {bestPnl[4]} - PnL: "
        f"{(bestPnl[0] / (contract.historicalContractData[0].open)) * 100}% or ${bestPnl[0]} profit/loss per {contract.quantity} position(s) (Not compounded)")
    regularPNL = contract.historicalContractData[-1].close - contract.historicalContractData[0].open
    print(f"Regular buyTrail and hold would result in: {(100 * regularPNL) / contract.historicalContractData[0].open}% or ${regularPNL}")

    return bestPnl