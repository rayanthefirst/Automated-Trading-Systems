##PYTHON BUILT-IN MODULES##
import time

##CUSTOM PROJECT MODULES##
from project_classes.contract import Contract
from project_classes.IBAPIProjectDefaults import IBAPIDefaults
from useful_functions.ScreenPrint import blockPrint, enablePrint

##IBAPI MODULES##
from ibapi.order import *

##TRAILINGBOTDEFAULTS_V1##
class TrailingBot(IBAPIDefaults):
    ##DEFAULT SETTINGS##
    portfolioCheckInterval = 300  ##SECONDS##

    def __init__(self):
        IBAPIDefaults.__init__(self)

        ##BOT CONTRACT INSTANCE##
        self.botContract = Contract()

        ##ALL POSSIBLE BOT TRAILING STRATEGIES - MANUALLY KEEP UP TO DATE##
        self.marginAccountStrategies = [self.longBuySellTrailAutomation, self.shortSellBuyTrailAutomation,
                                        self.longShortBuySellTrailAutomation, self.longShortNeutralBuySellTrailAutomation]
        self.noMarginStrategy = [self.longBuySellTrailAutomation]

        ##BOT PARAMETERS##
        self.strategyUsed = '' ##STORES THE USED STRATEGY FUNCTION##
        self.buyTrail = 0.
        self.sellTrail = 0.
        self.buyType = '' ##todo add logic into entire program for amt option
        self.sellType = ''

        ##PREVIOUS DAY HIGH/LOW##
        self.firstCycle = True ##TRACKS FIRST CYCLE##
        self.newHighStop = UNSET_DOUBLE
        self.newLowStop = UNSET_DOUBLE

    ##IBKR STRATEGIES - EQUIVALENT TO BACKTESTING STRATEGIES##
    ##LONGBUYSELLTRAILAUTOMATION_V1##
    def longBuySellTrailAutomation(self, botContract, quantity, buyTrail, sellTrail):
        self.getCurrentPortfolioInfo()  ##OPEN SUBSCRIPTION TO ACCOUNT##
        while True:
            if self.firstCycle == True:
                self.checkPreviousSessionOrders(botContract)
            posCurrent = botContract.numbPos
            if botContract.numbPos <= 0:
                self.placeTrailingStopBuyTrail(botContract, (abs(botContract.numbPos) + quantity), buyTrail)
            elif botContract.numbPos > 0:
                self.placeTrailingStopSellTrail(botContract, botContract.numbPos, sellTrail)
            self.waitForPosChange(botContract, posCurrent)

    ##SHORTSELLBUYTRAILAUTOMATION_V1##
    def shortSellBuyTrailAutomation(self, botContract, quantity, buyTrail, sellTrail):
        self.getCurrentPortfolioInfo()  ##OPEN SUBSCRIPTION TO ACCOUNT##
        while True:
            if self.firstCycle == True:
                self.checkPreviousSessionOrders(botContract)
            posCurrent = botContract.numbPos
            if botContract.numbPos >= 0:
                self.placeTrailingStopSellTrail(botContract, (botContract.numbPos + quantity), sellTrail)
            elif botContract.numbPos < 0:
                self.placeTrailingStopBuyTrail(botContract, abs(botContract.numbPos), buyTrail)
            self.waitForPosChange(botContract, posCurrent)

    ##LONGSHORTBUYSELLTRAILAUTOMATION_V2##
    def longShortBuySellTrailAutomation(self, botContract: Contract, quantity, buyTrail, sellTrail): #todo add buyType sellType
        self.getCurrentPortfolioInfo()  ##OPEN SUBSCRIPTION TO ACCOUNT##
        while True:
            if self.firstCycle == True:
                self.checkPreviousSessionOrders(botContract)
            posCurrent = botContract.numbPos
            if botContract.numbPos == 0:
                self.getFirstTrail(botContract, quantity, buyTrail, sellTrail)
            elif botContract.numbPos < 0:
                self.placeTrailingStopBuyTrail(botContract, (abs(botContract.numbPos) + quantity), buyTrail)
            elif botContract.numbPos > 0:
                self.placeTrailingStopSellTrail(botContract, (botContract.numbPos + quantity), sellTrail)
            self.waitForPosChange(botContract, posCurrent)

    ##LONGSHORTNEUTRALBUYSELLTRAILAUTOMATION_V1##
    def longShortNeutralBuySellTrailAutomation(self, botContract, quantity, buyTrail, sellTrail):
        self.getCurrentPortfolioInfo()  ##OPEN SUBSCRIPTION TO ACCOUNT##
        while True:
            if self.firstCycle == True:
                self.checkPreviousSessionOrders(botContract)
            posCurrent = botContract.numbPos
            if botContract.numbPos == 0:
                self.getFirstTrail(botContract, quantity, buyTrail, sellTrail)
            elif botContract.numbPos < 0:
                self.placeTrailingStopBuyTrail(botContract, (abs(botContract.numbPos)), buyTrail)
            elif botContract.numbPos > 0:
                self.placeTrailingStopSellTrail(botContract, botContract.numbPos, sellTrail)
            self.waitForPosChange(botContract, posCurrent)

    def checkPreviousSessionOrders(self, botContract: Contract):
        self.firstCycle = False
        self.reqOpenOrders()
        time.sleep(5)
        if botContract.activeOrders != {}:
            print("PRE-EXISTING TRAIL(S) DETECTED - RE-SUBMITTING ORDERS")
            for k, v in botContract.activeOrders.items():
                if v[1].trailStopPrice != UNSET_DOUBLE:
                    if v[1].action == 'BUY':
                        if self.buyType == '%':
                            self.newLowStop = round((v[1].trailStopPrice / ((100 + v[1].trailingPercent)/100)) * ((100 + self.buyTrail) / 100), 2)
                        else:
                            pass # self.newLowStop = round((v[1].trailStopPrice) fixme add trail amt
                    else:
                        if self.sellType == '%':
                            self.newHighStop = round((v[1].trailStopPrice / ((100 - v[1].trailingPercent)/100)) * ((100 - self.sellTrail) / 100), 2)
                        else:
                            pass ## todo add trail amt
        self.cancelRelatedOrders()

    ##INTERNALLY USED##
    def waitForPosChange(self, botContract: Contract, posCurrent):
        while posCurrent == botContract.numbPos:
            time.sleep(1)

    ##CANCEL ALL POSITION RELATED ORDERS##
    def cancelRelatedOrders(self):
        self.reqOpenOrders()
        time.sleep(5)
        if self.botContract.activeOrders != {}:
            for k in self.botContract.activeOrders:
                self.cancelOrder(k)
                time.sleep(1)
            self.botContract.activeOrders.clear()

    def getFirstTrail(self, botContract: Contract, quantity, buyTrail, sellTrail):
        print("BUY/SELL TRAIL")
        blockPrint()
        self.placeTrailingStopBuyTrail(botContract, quantity, buyTrail)
        self.placeTrailingStopSellTrail(botContract, quantity, sellTrail)
        enablePrint()

    ##INTERNALLY USED##
    ##BUY TRAIL## todo add orderId in args for both buyTrail and sellTrail, and somethong for percent/ amt
    def placeTrailingStopBuyTrail(self, botContract: Contract, quantity, buyTrail):
        print("BUY TRAIL")
        buyTrailOrder = Order()
        buyTrailOrder.action = "BUY"
        buyTrailOrder.totalQuantity = quantity
        buyTrailOrder.orderType = "TRAIL"
        buyTrailOrder.trailingPercent = buyTrail
        buyTrailOrder.trailStopPrice = self.newLowStop
        buyTrailOrder.tif = 'GTC'
        buyTrailOrder.account = self.account[0]
        # buyTrailOrder.outsideRth = ##ADD RTH?
        self.getNextValidId()
        self.placeOrder(self.nextValidOrderId, botContract, buyTrailOrder)
        self.getNextValidId()

    ##INTERNALLY USED##
    #SELL TRAIL##
    def placeTrailingStopSellTrail(self, botContract: Contract, quantity, sellTrail):
        print("SELL TRAIL")
        sellTrailOrder = Order()
        sellTrailOrder.action = "SELL"
        sellTrailOrder.totalQuantity = quantity
        sellTrailOrder.orderType = "TRAIL"
        sellTrailOrder.trailingPercent = sellTrail
        sellTrailOrder.trailStopPrice = self.newHighStop
        sellTrailOrder.tif = 'GTC'
        sellTrailOrder.account = self.account[0]
        # sellTrailOrder.outsideRth = ##ADD RTH?
        self.getNextValidId()
        self.placeOrder(self.nextValidOrderId, botContract, sellTrailOrder)
        self.getNextValidId()

    ##INTERNALLY USED##
    ##BOT PARAMETERS SETUP##
    def setBotParameters(self, buy='', buyType='', sell='', sellType='', strategyPos=0): ##STRATEGYPOS IS INDEX OF INTENDED STRATEGY IN SELF.MARGINSTRATEGIES STARTING AT INDEX 1##
        while self.buyType != '%' and self.buyType != 'amt':
            self.buyType = input('Choose buy type - (% or amt): ') if buyType == '' else buyType
        self.buyTrail = float(input(f"What would you like the buy trail ({self.buyType}) to be: ")) if buy == '' else buy
        while self.sellType != '%' and self.sellType != 'amt':
            self.sellType = input('Choose sell type - (% or amt): ') if sellType == '' else sellType
        self.sellTrail = float(input(f"What would you like the sell trail ({self.sellType}) to be: ")) if sell == '' else sell
        print(f"Choose from the following strategies (Make sure to choose an appropriate strategy for the {self.account[1]} account): ")
        for index in range(len(self.marginAccountStrategies)):
            print(index + 1, ": ", self.marginAccountStrategies[index].__name__)

        numbStrategies = [i for i in range(1, len(self.marginAccountStrategies) + 1)]
        self.strategyUsed = self.marginAccountStrategies[((int(input(f"Which strategy do you want {str(numbStrategies)}? ")) if strategyPos == 0 else strategyPos) - 1)]

    def autoBotParameters(self, buy, buyType, sell, sellType, strategyPos):
        self.buyTrail = buy
        self.buyType = buyType
        self.sellTrail = sell
        self.sellType = sellType
        self.strategyUsed = self.marginAccountStrategies[strategyPos - 1]