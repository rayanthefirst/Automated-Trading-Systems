##PYTHON BUILT-IN MODULES##
import datetime
import os
import threading
import time

##CUSTOM PROJECT MODULES##
from project_classes.TrailingBotInvestor import TrailingBot
from useful_functions.EmailSender import sendEmail
from useful_functions.ScreenPrint import fullDataFrame, colourRed

##IBAPI MODULES##
from ibapi.commission_report import CommissionReport
from ibapi.execution import Execution
from ibapi.order import *

##PIP INSTALLED MODULES##
import pandas as pd

##STOCKTRAILINGBOTINVESTOR_V2## todo maybe move client ID and deafults files and writing to files into trailingbot or ibapi defaults
class StockTrailingBot(TrailingBot):
    def __init__(self):
        TrailingBot.__init__(self)

        ##CSV VARIABLES##
        self.csvReqId = None
        self.csvExecution = None
        self.csvCommission = None

        ##DEFAULT STOCK FILE## todo use config file
        self.file = f'{self.__class__.__name__}Defaults.csv'
        self.pathFile = f'{os.path.expanduser("~")}\\Desktop/{self.file}'

    def __del__(self):
        pass

    ##INTERNALLY USED##
    def execDetails(self, reqId, contract, execution: Execution):
        self.newHighStop = UNSET_DOUBLE
        self.newLowStop = UNSET_DOUBLE
        self.cancelRelatedOrders()

        if execution.side == 'BOT':
            self.botContract.dailyAvgExecPrice.append(-execution.price)
        else:
            self.botContract.dailyAvgExecPrice.append(execution.price)
        sendEmail((f'Client: {self.clientIdNumber} - {execution.side} {execution.shares} positions of '
                   f'{contract.symbol} {contract.secType} @ ${execution.price}'),
                  (f'Request ID: {reqId}\n'
                   f'Order ID: {execution.orderId}\n'
                   f'Client ID {self.clientIdNumber} running {self.__class__.__name__} using the {self.strategyUsed.__name__} '
                   f'{execution.side} {execution.shares} positions of {contract.symbol} {contract.secType} @ ${execution.price}\n'
                   f'Account: {self.account[0]}\n'
                   f'Time of purchase: {execution.time}\n'
                   f'Average Price: ${execution.avgPrice}\n'
                   f'Number of positions: {self.botContract.numbPos}\n'
                   f'Bot session PnL: {sum(self.botContract.dailyAvgExecPrice)} - Bot session execution prices {self.botContract.dailyAvgExecPrice}'))

        self.csvReqId, self.csvExecution = reqId, execution

        t1 = time.perf_counter()
        while self.csvReqId == None or self.csvExecution == None:
            time.sleep(1)
            t2 = time.perf_counter()
            if t1-t2 > self.portfolioCheckInterval:
                print("Stuck in loop - execution did not change csv reqid or csv exec in 5 min")
                sendEmail('ERROR - Stuck in loop', 'execution did not change csv reqid or csv exec in 5 min')
                break

    def commissionReport(self, commissionReport: CommissionReport):
        self.csvCommission = commissionReport

        t1 = time.perf_counter()
        while self.csvCommission == None:
            time.sleep(1)
            t2 = time.perf_counter()
            if t1 - t2 > self.portfolioCheckInterval:
                print("Stuck in loop - execution did not change csv commission report in 5 min")
                sendEmail('ERROR - Stuck in loop', 'execution did not change csv commission report in 5 min')
                break

        csvWriteExecThread = threading.Thread(target=self.recordExecAndCommissionToCsv)
        csvWriteExecThread.start()

    def recordExecAndCommissionToCsv(self):
        recordCsv = f'{self.__class__.__name__}_{self.botContract.symbol}Executions.csv'
        if recordCsv not in os.listdir(f'{os.path.expanduser("~")}\\Desktop'):
            with open(f'{os.path.expanduser("~")}\\Desktop/{recordCsv}', 'w') as w:
                w.write(f'Account,AccountType,ClientId,OrderId,Stock,Action,Quantity,Strategy,BuyTrail,BuyType,'
                        f'SellTrail,SellType,Total Price,Price,Commission,Average Price,Realized PnL,Date,Time,ReqId,ExecId,PermId,Yield')
        execTime = self.csvExecution.time.split()

        if self.csvExecution.side == 'SLD':
            self.csvExecution.shares *= -1
        elif self.csvExecution.side == 'BOT':
            self.csvExecution.price *= -1

        with open(f'{os.path.expanduser("~")}\\Desktop/{recordCsv}', 'a') as a:
            a.write(f'\n{self.account[0]},{self.account[1]},{self.clientIdNumber},'
                    f'{self.csvExecution.orderId if self.csvExecution != None else self.csvReqId},' ##fixme - figure out why csvexec is none after loops-  PRINTS REQUEST ID if none for now
                    f'{self.botContract.symbol},{self.csvExecution.side},{self.csvExecution.shares},'
                    f'{self.strategyUsed.__name__},{self.buyTrail},{self.buyType},{self.sellTrail},{self.sellType},'
                    f'{self.csvExecution.price + -self.csvCommission.commission},'
                    f'{self.csvExecution.price},{-self.csvCommission.commission},'
                    f'{self.csvExecution.avgPrice},{self.csvCommission.realizedPNL},'
                    f'{execTime[0]},{execTime[1]},{self.csvReqId},{self.csvExecution.execId},'
                    f'{self.csvExecution.permId},{self.csvCommission.yield_}')
        self.csvCommission, self.csvExecution, self.csvReqId = None, None, None

    ##CALLED IN IBKRDEFAULTS - GETCURRENTSTOCKPORTFOLIOINFO##
    ##INTERNALLY USED##
    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName):
        if contract.secType == self.botContract.secType and contract.symbol == self.botContract.symbol:
            self.botContract.numbPos = position

    ##GETS CURRENT OPEN ORDERS##
    def openOrder(self, orderId, contract, order, orderState):
        if contract.secType == self.botContract.secType and contract.symbol == self.botContract.symbol:
            self.botContract.activeOrders[orderId] = [contract, order, orderState]

    ##ERROR AND MESSAGE RETURNS##
    def error(self, reqId, errorCode, errorString):
        ##ERROR CODES FOR A LOST CONNECTION BETWEEN THE IB SERVERS TO TWS/IBGW OR CLIENT TO TWS/IBGW##
        if errorCode == 1100 or errorCode == 2103 or errorCode == 2105 or errorCode == 2157:
            if self.errorMsgConnectionIndicator == False:
                self.errorMsgConnectionIndicator = True
            sendEmail((f'Client: {self.clientIdNumber}, Stock: {self.botContract.symbol} - {errorString}'),
                      (f'Request ID: {reqId} \nError Code: {errorCode} \nClient ID {self.clientIdNumber} runni'
                              f'ng {self.__class__.__name__} has encountered the following connectivity error message: {errorString}\n'
                       f'Time: {datetime.datetime.now().strftime("%H:%M:%S")}'))
        ##ERROR CODES IF IB SERVER TO TWS/IBGW OR CLIENT TO TWS/IBGW ARE MAINTAINED - WILL SEND AN EMAIL IF CONNECTION WAS BROKEN THEN REESTABLISHED##
        elif errorCode == 1101 or errorCode == 1102 or errorCode == 2104 or errorCode == 2106 or errorCode == 2158:
            if self.errorMsgConnectionIndicator == True:
                self.errorMsgConnectionIndicator = False
                sendEmail((f'Client: {self.clientIdNumber}, Stock: {self.botContract.symbol} - {errorString}'),
                          (f'Request ID: {reqId} \nError Code: {errorCode} \nClient ID {self.clientIdNumber} runni'
                              f'ng {self.__class__.__name__} has encountered the following connectivity reconnection message: {errorString} \n'
                           f'Note: one reconnection ocurring indicates that all connections are reestablished and will not send additional emails\n'
                           f'Time: {datetime.datetime.now().strftime("%H:%M:%S")}'))
            else:
                pass
        # ##UNNEEDED ERRORCODES##
        # elif errorCode == 2100: #or errorCode == 10147: # or errorCode == 10148: todo test to see if this still appears
        #     pass
        ##OTHER ERRORCODES##
        ##DUPLICATE ORDER ID (103) OR CANCELLED ORDERS (202)##
        else:
            sendEmail((f'Client: {self.clientIdNumber}, Stock: {self.botContract.symbol} - {errorString}'),
                      (f'Request ID: {reqId} \nError Code: {errorCode} \nClient ID {self.clientIdNumber} runni'
                       f'ng {self.__class__.__name__} has encountered the following error message: {errorString}\n'
                       f'Time: {datetime.datetime.now().strftime("%H:%M:%S")}'))

        time.sleep(3)

    def openDefaults(self):
        if self.file not in os.listdir(f'{os.path.expanduser("~")}\\Desktop'):
            with open(f'{os.path.expanduser("~")}\\Desktop/{self.file}', 'w') as w:
                w.write(f'Account,AccountType,ClientId,Stock,Quantity,Strategy,StrategyPos,BuyTrail,BuyType,SellTrail,SellType')
        df = pd.read_csv(self.pathFile)
        fullDataFrame()
        print(df)
        return df

    def removeDefault(self, stock, df):
        for index, row in df.iterrows():
            if row['Stock'] == stock:
                df = df.drop([index])
                print('Stock removed!')
            df.to_csv(self.pathFile, index=False)

    def getNextValidClientId(self, df):
        clientIds = df['ClientId'].tolist()
        for i in range(1, 32): ##32 IS MAX NUMBER OF CLIENTIDS FOR EACH INSTANCE, 31 WILL BE THE MAX AND 1 WILL SAVED FOR CLIENT ID 0 IN THE CASE FOR TESTING##
            if i not in clientIds:
                return i
        print('Max number of client applications are assigned for this instance of TWS/IBGW')

    def writeNewToStockDefaultsCsv(self, df):
        if self.botContract.symbol in df.values: ##IF STOCK IS ALREADY IN DEFAULTS##
            for index, row in df.iterrows():
                if row['Stock'] == self.botContract.symbol:
                    df.loc[index, 'Account'] = self.account[0]
                    df.loc[index, 'AccountType'] = self.account[1]
                    df.loc[index, 'Quantity'] = self.botContract.quantity
                    df.loc[index, 'Strategy'] = self.strategyUsed.__name__
                    df.loc[index, 'StrategyPos'] = (self.marginAccountStrategies.index(self.strategyUsed) + 1)
                    df.loc[index, 'BuyTrail'] = self.buyTrail
                    df.loc[index, 'BuyType'] = self.buyType
                    df.loc[index, 'SellTrail'] = self.sellTrail
                    df.loc[index, 'SellType'] = self.sellType
                    break

        else: ##ADD NEW STOCK##
            clientId = self.getNextValidClientId(df)
            if clientId == None:
                return
            newStock = pd.DataFrame({'Account':[self.account[0]],'AccountType':[self.account[1]], 'ClientId':[clientId],
                                     'Stock':[self.botContract.symbol],'Quantity':[self.botContract.quantity],
                                     'Strategy':[self.strategyUsed.__name__],
                                     'StrategyPos':[self.marginAccountStrategies.index(self.strategyUsed) + 1],
                                     'BuyTrail':[self.buyTrail], 'BuyType':[self.buyType], 'SellTrail':[self.sellTrail],
                                     'SellType':[self.sellType]})
            df = pd.concat([df, newStock], ignore_index=True, axis=0)
        df = df.sort_values(by='ClientId')
        df.to_csv(self.pathFile, index=False)

def botStart(app: StockTrailingBot):
    while True:
        try:
            print(f'Account: {app.account[0]}, Account Type: {app.account[1]}, ClientId: {app.clientIdNumber}\n'
                  f'Stock traded: {app.botContract.symbol}, Quantity: {app.botContract.quantity}\n'
                  f'Strategy being used: {app.strategyUsed.__name__}, Buy {app.buyType}: {app.buyTrail}, Sell {app.sellType}: {app.sellTrail}')
            app.strategyUsed(app.botContract, app.botContract.quantity, app.buyTrail, app.sellTrail)

        except Exception:
            colourRed()
            sendEmail((f'Client {app.clientIdNumber} has encountered a problem and an exception has been triggered, Please manually fix the code'),
                      (f'Client ID: {app.clientIdNumber} running {app.__class__.__name__} on {app.botContract.symbol} encountered'
                          f'an error that triggered an except block, the bot will restart\n'
                          f'Time: {datetime.datetime.now().strftime("%H:%M:%S")}'))
            print("Re-trying Strategy")
            continue

##CSV DEFAULTS AND CONFIGURATIONS##
def csvEditor():
    while True:
        app = StockTrailingBot()
        df = app.openDefaults()
        while True:
            choice = input("1: Add/Edit/Start a default bot\n"
              "2: Remove a default bot\n"
              "What would you like to do (1 or 2): ")
            if choice == '1' or choice == '2':
                break
            else:
                print("Invalid input, please try again")
        if choice == '1':
            app.botContract.setStockContract()
            app.chooseAccount()
            app.setBotParameters()
            app.writeNewToStockDefaultsCsv(df)
            if input("Would you like to run this new stock configuration (Only select yes if no active bot is already running on this stock)? (y/n): ").lower() == 'y':
                app.partialConnecionInputAndStart()
                app.checkInitialConnection()
                botStart(app)
        elif choice == '2':
            stock = input("Enter stock symbol to remove: ").upper()
            app.removeDefault(stock, df)
        if input("Would you like to make another edit? (y/n): ").lower() != 'y':
            break
        app.__del__()