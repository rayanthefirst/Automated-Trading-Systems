##IBAPI MODULES##
from ibapi.contract import Contract as IBAPIContract

##CONTRACT_V1##
class Contract(IBAPIContract):
    def __init__(self):
        IBAPIContract.__init__(self)

        ##BACKTESTING PARAMETERS##
        self.historicalContractData = []

        ##BOT PARAMETERS##
        self.quantity = 0

        ##PORTFOLIO PARAMETERS - BOT ONLY (BACKTESTING PARAMETERS IN PORTFOLIO CLASS)##
        self.numbPos = 0
        self.activeOrders = dict()  ##EMPTY {}: NO ORDERS, NOT EMPTY {}: ORDERS - STORES ACTIVE ORDERS##
        self.dailyAvgExecPrice = []  ##todo maybe get rid since u save results to csv

    ##CHOOSE CONTRACT TYPE##
    def chooseContractType(self):
        while True:
            print("Which security type would you like to use?\n"
                  "1: Stock - Yahoo Finance and IBKR Data available\n"
                  "2: Option - Only IBKR Data available\n"
                  "3: Forex - Enter correct symbol for corresponding data source")
            secChoice = input("Enter number corresponding to security type: ")
            if secChoice == '1':
                self.setStockContract()
                break
            elif secChoice == '2':
                self.setOptionContract()
                break
            elif secChoice == '3':
                self.setForexContract()
                break
            else:
                print("Invalid input, please re-try")
                continue

    ##SET IBKR STOCK CONTRACT##
    def setStockContract(self, symbol='', quantity=0):
        while True:
            try:
                self.symbol = str(input("Enter stock ticker symbol to automate trading strategies: ")).upper() if symbol == '' else symbol
                self.quantity = abs(int(input("Enter quantity to trade with (Quantity will be adjutsed if positions exists): "))) if quantity == 0 else quantity
            except Exception:
                print("Invalid input, please re-enter contract parameters")
                continue
            else:
                break
        self.secType = 'STK'
        self.exchange = 'SMART'
        self.currency = 'USD'

    ##SET IBKR OPTION CONTRACT##
    def setOptionContract(self):
        self.symbol = str(input("Enter underlying stock ticker symbol to automate trading strategies: ")).upper()
        self.quantity = abs(int(input("Enter quantity to trade with (Quantity will be adjutsed if positions exists): ")))
        self.right = input("Enter C for call side or P for put side: ").upper()
        self.lastTradeDateOrContractMonth = input("Enter option expiry date (yyyymmdd): ")
        self.strike = int(input("Enter strike price: "))
        self.secType = 'OPT'
        self.exchange = 'SMART'
        self.currency = 'USD'
        self.multiplier = '100'

    ##SET IBKR FOREX CONTRACT##
    def setForexContract(self):
        symbol = str(input("Enter forex symbol corresponding to data source to automate trading strategies: ")).upper().split('.')
        self.symbol = symbol[0]
        self.quantity = abs(int(input("Enter quantity to trade with (Quantity will be adjutsed if positions exists): ")))
        self.secType = 'CASH'
        self.currency = symbol[1] if len(symbol) > 1 else 'CAD'
        self.exchange = 'IDEALPRO'