##PYTHON BUILT-IN MODULES##
from copy import deepcopy

##CUSTOM PROJECT MODULES##
from backtesting.OrderTypes import buyOrder, sellOrder, trailingStopBuy, trailingStopSell
from project_classes.contract import Contract
from project_classes.portfolio import Portfolio

##TRAIL TRADING STRATEGIES##
##LONGBUYSELLTRAILAUTOMATION_V2##
def longBuySellTrailAutomation(portfolio: Portfolio, contract: Contract, dataParser, quantity, buyTrail, sellTrail):
    while True:
        if dataParser[0] == (len(contract.historicalContractData) - 1) and dataParser[1] == 1:
            print("Backtest Complete")
            portfolio.portfolioInfo(contract)
            return portfolio.PnL
        if portfolio.numbPos <= 0:
            trailingStopBuy(portfolio, contract, dataParser, (abs(portfolio.numbPos) + quantity), buyTrail)
        elif portfolio.numbPos > 0:
            trailingStopSell(portfolio, contract, dataParser, portfolio.numbPos, sellTrail)

##SHORTSELLBUYTRAILAUTOMATION_V2##
def shortSellBuyTrailAutomation(portfolio: Portfolio, contract: Contract, dataParser, quantity, buyTrail, sellTrail):
    while True:
        if dataParser[0] == (len(contract.historicalContractData) - 1) and dataParser[1] == 1:
            print("Backtest Complete")
            portfolio.portfolioInfo(contract)
            return portfolio.PnL
        if portfolio.numbPos >= 0:
            trailingStopSell(portfolio, contract, dataParser, (portfolio.numbPos + quantity), sellTrail)
        elif portfolio.numbPos < 0:
            trailingStopBuy(portfolio, contract, dataParser, abs(portfolio.numbPos), buyTrail)

##LONGSHORTBUYSELLTRAILAUTOMATION_V3##
def longShortBuySellTrailAutomation(portfolio: Portfolio, contract: Contract, dataParser, quantity, buyTrail, sellTrail):
    while True:
        if dataParser[0] == (len(contract.historicalContractData) - 1) and dataParser[1] == 1:
            print("Backtest Complete")
            portfolio.portfolioInfo(contract)
            return portfolio.PnL
        if portfolio.numbPos == 0:
            getFirstTrail(portfolio, contract, dataParser, quantity, buyTrail, sellTrail)
        elif portfolio.numbPos < 0:
            trailingStopBuy(portfolio, contract, dataParser, (abs(portfolio.numbPos) + quantity), buyTrail)
        elif portfolio.numbPos > 0:
            trailingStopSell(portfolio, contract, dataParser, (portfolio.numbPos + quantity), sellTrail)

##LONGSHORTNEUTRALBUYSELLTRAILAUTOMATION_V1##
def longShortNeutralBuySellTrailAutomation(portfolio: Portfolio, contract: Contract, dataParser, quantity, buyTrail, sellTrail):
    while True:
        if dataParser[0] == (len(contract.historicalContractData) - 1) and dataParser[1] == 1:
            print("Backtest Complete")
            portfolio.portfolioInfo(contract)
            return portfolio.PnL
        if portfolio.numbPos == 0:
            getFirstTrail(portfolio, contract, dataParser, quantity, buyTrail, sellTrail)
        elif portfolio.numbPos < 0:
            trailingStopBuy(portfolio, contract, dataParser, (abs(portfolio.numbPos)), buyTrail)
        elif portfolio.numbPos > 0:
            trailingStopSell(portfolio, contract, dataParser, portfolio.numbPos, sellTrail)

##INTERNALLY USED##
def getFirstTrail(portfolio: Portfolio, contract: Contract, dataParser, quantity, buyTrail, sellTrail):
    print('BUY/SELL TRAIL')
    portfolioBuyTest = deepcopy(portfolio)
    portfolioSellTest = deepcopy(portfolio)

    portfolioBuyTest.regularTrailIndicator = False
    portfolioSellTest.regularTrailIndicator = False

    buyParser = [None] * 2
    sellParser = [None] * 2

    buyParser[0], buyParser[1] = dataParser[0], dataParser[1]
    sellParser[0], sellParser[1] = dataParser[0], dataParser[1]

    buyPrice = trailingStopBuy(portfolioBuyTest, contract, buyParser, quantity, buyTrail)
    sellPrice = trailingStopSell(portfolioSellTest, contract, sellParser, quantity, sellTrail)

    if buyPrice == None and sellPrice == None:
        dataParser[0], dataParser[1] = buyParser[0], buyParser[1]

    elif buyPrice != None and sellPrice == None:
        dataParser[0], dataParser[1] = buyParser[0], buyParser[1]
        buyOrder(buyPrice, portfolio, contract, quantity)

    elif buyPrice == None and sellPrice != None:
        dataParser[0], dataParser[1] = sellParser[0], sellParser[1]
        sellOrder(sellPrice, portfolio, contract, quantity)

    elif buyParser[0] < sellParser[0]:
        dataParser[0], dataParser[1] = buyParser[0], buyParser[1]
        buyOrder(buyPrice, portfolio, contract, quantity)

    elif buyParser[0] == sellParser[0]:
        if buyParser[1] <= sellParser[1]:
            dataParser[0], dataParser[1] = buyParser[0], buyParser[1]
            buyOrder(buyPrice, portfolio, contract, quantity)

        else:
            dataParser[0], dataParser[1] = sellParser[0], sellParser[1]
            sellOrder(sellPrice, portfolio, contract, quantity)

    elif sellParser[0] < buyParser[0]:
        dataParser[0], dataParser[1] = sellParser[0], sellParser[1]
        sellOrder(sellPrice, portfolio, contract, quantity)

    portfolioBuyTest.__del__()
    portfolioSellTest.__del__()

##LIST OF STRATEGY FUNCTIONS##
marginStrategies = [longBuySellTrailAutomation, shortSellBuyTrailAutomation, longShortBuySellTrailAutomation, longShortNeutralBuySellTrailAutomation]
noMarginStrategy = [longBuySellTrailAutomation]

def chooseBackTestStrategies(allStrategies):
    while True:
        strategies = []
        for index in range(len(allStrategies)):
            print(index + 1, ": ", allStrategies[index].__name__)
        strategyIndex = [i + 1 for i in range(len(allStrategies))]
        print(f"Enter strategies to use in the backtest {strategyIndex} then enter 0"
              f" to indicate end of strategy list, or leave blank and enter 0 to use all strategies")
        count = 1
        while count <= len(allStrategies):
            try:
                position = int(input(f"Add strategy #{count}: "))
            except ValueError:
                print("Invalid entry, please retry")
                continue
            else:
                if position in strategyIndex:
                    count += 1
                    strategies.append(allStrategies[position - 1])
                elif position == 0:
                    break
                else:
                    print("Invalid entry, please retry")
                    continue
        if strategies == []:
            print("Strategy list is empty, all strategies will be used")
            strategies = allStrategies
        for index in range(len(strategies)):
            print(index + 1, ": ", strategies[index].__name__)
        if str(input("Are you sure you want to use the following strategies in the backtest? (y/n): ")).lower() == 'y':
            break
    return strategies