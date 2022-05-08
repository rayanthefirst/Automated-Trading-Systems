##PYTHON BUILT-IN MODULES##
import threading
import time

##CUSTOM PROJECT MODULES##
from project_classes.contract import Contract
from useful_functions.EmailSender import sendEmail
from useful_functions.ScreenPrint import colourGreen, colourRed, colourYellow

##IBAPI MODULES##
from ibapi.client import EClient
from ibapi.order import Order
from ibapi.wrapper import EWrapper

##IBAPIDEFAULTS_V1##
class IBAPIDefaults (EWrapper, EClient):
    ##EWRAPPER AND ECLIENT CONSTRUCTOR##
    def __init__(self):
        EClient.__init__(self, self)

        ##CONNECTION AND EXECUTION PARAMETERS##
        self.hostIP = None
        self.portNumber = None
        self.clientIdNumber = None
        self.apiThread = threading.Thread(target=self.run_loop, daemon=True)

        ##ACCOUNT PARAMETERS##
        self.accounts = []
        self.account = ['', ''] ##ACCOUNT NUMBER/ALIAS AND ACCOUNT TYPE##
        self.nextValidOrderId = None
        self.initialHandShakeOrderIndicator = False ##IF SET TO TRUE - INITIAL HANDSHAKE HAS OCCURED##
        self.errorMsgConnectionIndicator = False ##IF SET TO FALSE, TWS/IBGW CONNECTION TO CLIENT OR TWS/IBGW CONNECTION TO IB SERVERS ARE CONNECTED##

    ##SET UP DEFAULT PARAMETERS AND START CONNECTION##
    def connectionInput(self):
        self.hostIP = str(input("Enter the IP for computer hosting the TWS/IBGW instance, or enter 'localhost' for default (127.0.0.1): ")).lower()
        self.portNumber = int(input("Enter port that is being listened to by TWS/IBGW instance: "))
        self.clientIdNumber = int(input("Enter clientID for this application to use, DO NOT USE 0: "))
        return self.hostIP, self.portNumber, self.clientIdNumber

    def connectionStart(self):
        self.connect(self.hostIP, self.portNumber, self.clientIdNumber)
        time.sleep(1)
        self.apiThread.start()

    def partialConnecionInputAndStart(self, port=0, clientId=0):
        self.hostIP = 'localhost'
        while True:
            try:
                while not isinstance(self.portNumber, int):
                    try:
                        self.portNumber = int(input("Enter port that is being listened to by TWS/IBGW instance: ")) if port == 0 else port
                    except Exception:
                        print("Invalid input, please re-enter port being listened to by TWS/IBGW instance")

                while not isinstance(self.clientIdNumber, int):
                    try:
                        self.clientIdNumber = int(input("Enter clientID for this application to use, DO NOT USE 0: ")) if clientId == 0 else clientId
                    except Exception:
                        print("Invalid input, please re-enter client Id")

                self.connect(self.hostIP, self.portNumber, self.clientIdNumber)
                time.sleep(1)
            except Exception:
                colourRed()
                time.sleep(3)
                self.portNumber = None
                self.clientIdNumber = None
                self.disconnect()
                sendEmail("BOTS UNABLE TO CONNECT TO IBGW", "MANUALLY FIX IBGW CONNECTION")
                print("Could not connect to instance of TWS/IBGW with defined parameters, please re-enter port and clie"
                      "nt Id and make sure TWS/IBGW instance is active")
                continue
            else:
                break
        self.apiThread.start()

    ##CONNECT WITH MASTER CLIENT ID##
    def masterConnection(self):
        self.connect(self.hostIP, self.portNumber, 0)

    ##FOR TESTING PURPOSES##
    def defaultTestConfigurations(self):
        self.connect('localhost', 4001, 1)
        time.sleep(1)
        self.apiThread.start()

    ##GETS NEXT VALID ID BY INCREMENTING BY 1##
    def getNextValidIdIncrement(self):
        self.nextValidOrderId += 1

    ##GETS NEXT VALID ORDER ID USING ECLINET.REQIDS##
    def getNextValidId(self):
        self.nextValidOrderId = None
        self.reqIds(0)
        while True:
            if isinstance(self.nextValidOrderId, int):
                break
            else:
                time.sleep(1)

    ##INTERNALLY USED - ON INITIAL HANDSHAKE THIS WILL RETURN THE ORDER ID##
    def nextValidId(self, orderId):
        self.nextValidOrderId = orderId
        if self.initialHandShakeOrderIndicator == False:
            self.initialHandShakeOrderIndicator = True
            print("Initial Handshake Valid Order Id:", orderId)

    ##GETS MANAGED ACCOUNTS FROM TWS/IBGW USERNAME ACCOUNT INSTANCE##
    ##CHOOSE ACCOUNT TO TRADE IN##
    def chooseAccount(self):
        print(self.accounts)
        self.account[0] = str(input("Which account would you like to trade in (enter account number or alias - CASH, TFSA, RRSP): ")).upper()
        self.account[1] = str(input("What type is this account (CASH, TFSA, RRSP)? ")).upper()

    def autoSetAccount(self, accountNumb, accountType):
        self.account[0] = accountNumb
        self.account[1] = accountType

    ##INTERNALLY USED##
    def managedAccounts(self, accountsList):
        self.accounts = accountsList.split(',')
        self.accounts.pop(-1)

    ##INTERNALLY USED##
    ##CHECK INITIAL CONNECTION - GRAPHICAL VERSION##
    def checkInitialConnection(self):
        while True:
            if isinstance(self.nextValidOrderId, int):
                time.sleep(0.2)
                print(f'{self.__class__.__name__} Connecting [   ]')
                time.sleep(0.2)
                print(f'{self.__class__.__name__} Connecting [-  ]')
                time.sleep(0.2)
                print(f'{self.__class__.__name__} Connecting [-- ]')
                time.sleep(0.2)
                colourGreen()
                print(f'{self.__class__.__name__} Connected  [---]')
                break
            else:
                colourYellow()
                print('Waiting For Connection')
                time.sleep(1)

    ##CHECK CONNECTION##
    def checkConnection(self):
        while True:
            if isinstance(self.nextValidOrderId, int):
                colourGreen()
                print(f'{self.__class__.__name__} Connected')
                break
            else:
                print('Waiting For Connection')
                time.sleep(1)

    ##INTERNALLY USED##
    ##PROGRAM RUN DAEMON THREAD##
    def run_loop(self):
        self.run()

    ##ERROR AND MESSAGE RETURNS##
    def error(self, reqId, errorCode, errorString):
        print(reqId, ": ", errorCode, " - ", errorString)

    ##TURN ON PORTFOLIO SUBSCRIPTION FOR FIVE SECONDS##
    def getCurrentPortfolioInfo(self):
        self.reqAccountUpdates(True, self.account[0])
        time.sleep(15)
        # time.sleep(5) ##todo IDEA: what if we just let the account keep updating info? - clients subbed to same account dont interfere with eachother
        # self.reqAccountUpdates(False, self.account[0])
        # time.sleep(10)

    ##RETURNS OPEN ORDERS##
    def openOrder(self, orderId, contract, order, orderState):
        print("openOrder")
        print(orderId, contract.symbol, contract.secType, order.trailStopPrice, order.trailingPercent, order.auxPrice,
              order.outsideRth, order.triggerMethod)

    ##PLACE MKT TEST ORDER - FOR TESTING PURPOSES##
    def placeMktBuyOrder(self, botContract: Contract, quantity):
        orderTest = Order()
        orderTest.action = "BUY"
        orderTest.totalQuantity = quantity
        orderTest.orderType = "TRAIL"
        # orderTest.lmtPrice = 440
        orderTest.auxPrice = 5
        orderTest.tif = 'GTC'
        self.getNextValidId()
        self.placeOrder(self.nextValidOrderId, botContract, orderTest)
        self.getNextValidId()

    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL,
                        accountName):

        print(contract.symbol, contract.secType, position, accountName)