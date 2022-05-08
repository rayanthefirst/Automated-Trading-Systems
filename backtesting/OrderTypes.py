#CUSTOM PROJECT MODULES##
from project_classes.contract import Contract
from project_classes.portfolio import Portfolio

##ORDER TYPES##
##MKTBUY_V2##
def buyOrder(buyPrice, portfolio: Portfolio, contract: Contract, quantity):
    if portfolio.portfolioValue < ((buyPrice * quantity) + portfolio.commission):
        print(f"WARNING: YOU DO NOT HAVE ENOUGH CASH TO COMPLETE THIS ORDER. A negative portfolio value will be the res"
              f"ult and represent a margin call. "
              f"Missing: ${(buyPrice * quantity) + portfolio.commission - portfolio.portfolioValue}")
    portfolio.portfolioValue -= ((buyPrice * quantity) + portfolio.commission)
    portfolio.numbPos += quantity
    portfolio.updateMarginRequirements(buyPrice)
    portfolio.numberOfTransactions += 1
    if portfolio.regularTrailIndicator == True:
        portfolio.recordBuy(buyPrice, contract)
    print(f"BOT {quantity} pos of {contract.symbol} @ ${buyPrice}, new portfolio value is "
          f"${portfolio.portfolioValue}, current number of position(s) in portfolio is {portfolio.numbPos} and "
          f"new margin requirement is ${portfolio.marginRequirements}")

##MKTSELL_V1##
def sellOrder(sellPrice, portfolio: Portfolio, contract: Contract, quantity):
    portfolio.portfolioValue += ((sellPrice * quantity) - portfolio.commission)
    portfolio.numbPos -= quantity
    portfolio.updateMarginRequirements(sellPrice)
    portfolio.numberOfTransactions += 1
    if portfolio.regularTrailIndicator == True:
        portfolio.recordSell(sellPrice, contract)
    print(f"SOLD {quantity} pos of {contract.symbol} @ ${sellPrice}, new portfolio value is "
          f"${portfolio.portfolioValue}, current number of position(s) in portfolio is {portfolio.numbPos} and "
          f"new margin requirement is ${portfolio.marginRequirements}")

#TRAILINGSTOPBUY_V2##
def trailingStopBuy(portfolio: Portfolio, contract: Contract, dataParser, quantity, trailPercent):
    print("BUY TRAIL")
    lowValue = contract.historicalContractData[dataParser[0]].openClose[dataParser[1]]
    for index, candle in enumerate(contract.historicalContractData):
        ##CHECKS FOR LAST VALUE##
        if dataParser[0] == (len(contract.historicalContractData) - 1) and dataParser[1] == 1:
            print("End of Data")
            return None
        ##AVOIDS ALL PREVIOUSLY USED DATA##
        elif index < dataParser[0]:
            continue
        #CHECKS SCENERIO WHERE INDEX USED OPEN PRICE AND NOT CLOSE##
        elif index == dataParser[0]:
            if dataParser[1] == 1:
                continue
            elif dataParser[1] == 0:
                print(index+1, candle.date, candle.time, candle.openClose)
                dataParser[0], dataParser[1] = index, 1
                if candle.close <= lowValue:
                    lowValue = candle.close
                    continue
                elif candle.close >= (lowValue * ((100 + trailPercent) / 100)):
                    buyPrice = (lowValue * ((100 + trailPercent + portfolio.trailPercentOffset) / 100))
                    buyOrder(buyPrice, portfolio, contract, quantity)
                    return buyPrice
                else:
                    continue
        ##CONTINUES PARSING THROUGH CONTRACTDATA##
        elif index > dataParser[0]:
            print(index+1, candle.date, candle.time, candle.openClose)
            for i in range(len(candle.openClose)):
                dataParser[0], dataParser[1] = index, i
                if candle.openClose[i] <= lowValue:
                    lowValue = candle.openClose[i]
                    continue
                elif candle.openClose[i] >= (lowValue * ((100 + trailPercent) / 100)):
                    if i == 0 and contract.historicalContractData[index - 1].date != candle.date:
                        buyPrice = (candle.openClose[i] * ((100 + portfolio.trailPercentOffset) / 100))
                    else:
                        buyPrice = (lowValue * ((100 + trailPercent + portfolio.trailPercentOffset) / 100))
                    buyOrder(buyPrice, portfolio, contract, quantity)
                    return buyPrice

                else:
                    continue

##TRAILINGSTOPSELL_V2##
def trailingStopSell(portfolio: Portfolio, contract: Contract, dataParser, quantity, trailPercent):
    print("SELL TRAIL")
    highValue = contract.historicalContractData[dataParser[0]].openClose[dataParser[1]]
    for index, candle in enumerate(contract.historicalContractData):
        ##CHECKS FOR LAST VALUE##
        if dataParser[0] == (len(contract.historicalContractData) - 1) and dataParser[1] == 1:
            print("End of Data")
            return None
        ##AVOIDS ALL PREVIOUSLY USED DATA##
        elif index < dataParser[0]:
            continue
        #CHECKS SCENERIO WHERE INDEX USED OPEN PRICE AND NOT CLOSE##
        elif index == dataParser[0]:
            if dataParser[1] == 1:
                continue
            elif dataParser[1] == 0:
                print(index+1, candle.date, candle.time, candle.openClose)
                dataParser[0], dataParser[1] = index, 1
                if candle.close >= highValue:
                    highValue = candle.close
                    continue
                elif candle.close <= (highValue * ((100 - trailPercent) / 100)):
                    sellPrice = (highValue * ((100 - trailPercent - portfolio.trailPercentOffset) / 100))
                    sellOrder(sellPrice, portfolio, contract, quantity)
                    return sellPrice
                else:
                    continue
        ##CONTINUES PARSING THROUGH CONTRACTDATA##
        elif index > dataParser[0]:
            print(index+1, candle.date, candle.time, candle.openClose)
            for i in range(len(candle.openClose)):
                dataParser[0], dataParser[1] = index, i
                if candle.openClose[i] >= highValue:
                    highValue = candle.openClose[i]
                    continue
                elif candle.openClose[i] <= (highValue * ((100 - trailPercent) / 100)):
                    if i == 0 and contract.historicalContractData[index - 1].date != candle.date:
                        sellPrice = (candle.openClose[i] * ((100 - portfolio.trailPercentOffset) / 100))
                    else:
                        sellPrice = (highValue * ((100 - trailPercent - portfolio.trailPercentOffset) / 100))
                    sellOrder(sellPrice, portfolio, contract, quantity)
                    return sellPrice
                else:
                    continue