##PYTHON BUILT-IN MODULES##
import os

##CUSTOM PROJECT MODULES##
from project_classes.contract import Contract

##PORTFOLIO_V1##
class Portfolio():
    def __init__(self):
        ##BROKER PARAMETERS##
        self.commission = 0.
        self.marginRequirementsPercent = 0.

        ##PORTFOLIO PARAMETERS##
        self.portfolioValue = 0.
        self.initialPortfolioValue = 0.
        self.numbPos = 0
        self.marginRequirements = 0.
        self.numberOfTransactions = 0
        self.PnL = 0.
        self.liquidity = 0.
        self.trailPercentOffset = 0.

        ##BACKTESTING BOT PARAMETERS##
        self.strategyUsedName = ''
        self.buy = 0.
        self.sell = 0.
        self.regularTrailIndicator = True
        self.dataParser = [0, 0]  ##SAVES LAST USED INDEX IN CONTRACT.HISTORICALCONTRACTDATA AND LAST USED OPEN OR CLOSE IN CANDLESTICK.OPENCLOSE##

    def __del__(self):
        # print("Portfolio Deleted")
        pass

    def setPortfolio(self):
        self.portfolioValue = float(input("Enter starting portfolio cash value (base currency same as stock base currency): "))
        self.initialPortfolioValue = self.portfolioValue
        self.commission = float(input("Enter broker commission fee per transaction: "))
        self.marginRequirementsPercent = float(float(input("Enter margin requirement in %: ")) / 100)
        self.trailPercentOffset = float(input("Enter trail offset in percent for simulated purchasing offset: "))

        ##MAINLY USED IN OPTIMIZATION##
    def setPortfolioWithDefaultsOnly(self):
        self.portfolioValue = float(input("Enter principal investment: "))
        self.initialPortfolioValue = self.portfolioValue
        self.numbPos = int(input("Enter number of positions already in the portfolio (negative integer represents a short): "))
        self.commission = float(input("Enter broker commission fee per transaction: "))
        self.trailPercentOffset = float(input("Enter trail offset percent for purchasing offset: "))
        self.regularTrailIndicator = True if input("Would you like to record trades for backtests (Seperate trades for "
                                                   "each combination of strategy and percents)? (y/n) ").lower() == 'y' else False

    def portfolioInfo(self, contract: Contract):
        self.calculateFinalValue(contract)
        print(f"Final portfolio - Initial portfolio cash value: {self.initialPortfolioValue}, Final portfolio cash value"
              f": {self.portfolioValue}, Number of positions: {self.numbPos}, Total account value: {self.liquidity}, "
              f"PnL: {self.PnL}, Outstanding margin requirements: {self.marginRequirements}, Number of buy or sell "
              f"transactions: {self.numberOfTransactions}")

    def updateMarginRequirements(self, currentPrice):
        if self.numbPos < 0:
            self.marginRequirements = currentPrice * self.marginRequirementsPercent * abs(self.numbPos)
            if self.marginRequirements > self.portfolioValue:
                print("Margin requirements exceed portfolio value")
        else:
            self.marginRequirements = 0.

    def calculateFinalValue(self, contract: Contract):
        if self.numbPos < 0:
            self.liquidity = self.portfolioValue - (abs(self.numbPos) * contract.historicalContractData[-1].openClose[1]) - self.commission
        elif self.numbPos > 0:
            self.liquidity = self.portfolioValue + (abs(self.numbPos) * contract.historicalContractData[-1].openClose[1]) - self.commission
        elif self.numbPos == 0:
            self.liquidity = self.portfolioValue
        self.PnL = (self.liquidity - self.initialPortfolioValue)

    def recordBuy(self, buyPrice, contract: Contract):
        csvFile = f'buy-{self.buy}sell-{self.sell}{contract.symbol}{self.strategyUsedName}BacktestExecutions.csv'
        if csvFile not in os.listdir(f'{os.path.expanduser("~")}\\Desktop'):
            with open(f'{os.path.expanduser("~")}\\Desktop/{csvFile}', 'w') as w:
                w.write(f'Strategy,BuyTrail%,SellTrail%,Stock,Action,Quantity,Price,Commission,Total Price,Date,Time')

        with open(f'{os.path.expanduser("~")}\\Desktop/{csvFile}', 'a') as a:
            a.write(f'\n{self.strategyUsedName},{self.buy},{self.sell},{contract.symbol},BOT,{contract.quantity},'
                    f'{-buyPrice},{-self.commission},{-buyPrice + -self.commission},'
                    f'{contract.historicalContractData[self.dataParser[0]].date},'
                    f'{contract.historicalContractData[self.dataParser[0]].time}')

    def recordSell(self, sellPrice, contract: Contract):
        csvFile = f'buy-{self.buy}sell-{self.sell}{contract.symbol}{self.strategyUsedName}BacktestExecutions.csv'
        if csvFile not in os.listdir(f'{os.path.expanduser("~")}\\Desktop'):
            with open(f'{os.path.expanduser("~")}\\Desktop/{csvFile}', 'w') as w:
                w.write(f'Strategy,BuyTrail%,SellTrail%,Stock,Action,Quantity,Price,Commission,Total Price,Date,Time')

        with open(f'{os.path.expanduser("~")}\\Desktop/{csvFile}', 'a') as a:
            a.write(f'\n{self.strategyUsedName},{self.buy},{self.sell},{contract.symbol},SLD,{-contract.quantity},'
                    f'{sellPrice},{-self.commission},{sellPrice + -self.commission},'
                    f'{contract.historicalContractData[self.dataParser[0]].date},'
                    f'{contract.historicalContractData[self.dataParser[0]].time}')