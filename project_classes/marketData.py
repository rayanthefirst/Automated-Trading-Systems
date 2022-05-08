##PYTHON BUILT-IN MODULES##
import configparser
import datetime
import os
import time

##CUSTOM PROJECT MODULES##
from backtesting.Strategies import marginStrategies
from project_classes.candlestick import CandleStick
from project_classes.contract import Contract
from project_classes.IBAPIProjectDefaults import IBAPIDefaults

##PIP INSTALLED MODULES##
import pandas as pd

##MARKETDATA_V1##
class MarketData(IBAPIDefaults):
    ##DEFAULT SETTINGS##
    dateFormat = '%Y-%m-%d'
    previousStartYearInterval = 5

    def __init__(self):
        IBAPIDefaults.__init__(self)

        ##CONTRACT##
        self.btContract = Contract()
        # self.multiProcessed = False ##fixme multiprocessing seperate process instead of subprocesses

        ##ATTRIBUTE VARIABLES##
        self.earliestDate = None

    def __del__(self):
        pass

    def chooseMarketDataSource(self):
        choiceInput = input("Choose data source\n"
                            "1: IBKR API data (IBKR TWS/IBGW with historical data subscription must be active)\n"
                            "2: Yahoo Finance data (only daily open and close available)\n"
                            "3: Use saved data from csv\n"
                            "Data source: ")
        while True:
            if choiceInput == "1":
                if self.initialHandShakeOrderIndicator == False:
                    self.partialConnecionInputAndStart()
                    self.checkInitialConnection()
                else:
                    self.checkConnection()
                self.getEarliestDataDate()
                self.ibapiInputHistoricalDataParameters()
                self.disconnect()
                self.historicalDataToCsv()
            elif choiceInput == "2":
                df = self.yFinanceHistoricalData()
                self.yFinanceHistoricalDataToCsv(df)
                self.setYFinanceImport(df)
            elif choiceInput == "3":
                self.useCsv()
            else:
                print("Invalid entry, please re-enter")
                continue
            break

        print("Start Date: ", self.btContract.historicalContractData[0].date, self.btContract.historicalContractData[0].time)
        print("End Date: ", self.btContract.historicalContractData[-1].date, self.btContract.historicalContractData[-1].time)
        print(f'Number of Candles: {len(self.btContract.historicalContractData)}')

    def useCsv(self):
        fileName = input("Enter name of csv file, make sure it is in the desktop file - CASE SENSITIVE: ")
        df = pd.read_csv(f'{os.path.expanduser("~")}\\Desktop/' + fileName)
        if input("Would you like to set start and end dates for the backtest? (y/n): ").lower() == "y":
            startDate = datetime.datetime.strptime(str(input('Enter start date (yyyy-mm-dd): ')), self.dateFormat)
            endDate = datetime.datetime.strptime(str(input('Enter end date (yyyy-mm-dd): ')), self.dateFormat)
            if "Time" in df.columns:
                for index, row in df.iterrows():
                    formatDate = datetime.datetime.strptime(row['Date'], self.dateFormat)
                    if formatDate >= startDate and formatDate <= endDate:
                        # print(formatDate)
                        candlestickIndex = CandleStick()
                        candlestickIndex.ibapiDataCsv(row['Date'], row['Time'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume'])
                        self.btContract.historicalContractData.append(candlestickIndex)
            else:
                for index, row in df.iterrows():
                    formatDate = datetime.datetime.strptime(row['Date'], self.dateFormat)
                    if formatDate >= startDate and formatDate <= endDate:
                        # print(formatDate)
                        candlestickIndex = CandleStick()
                        candlestickIndex.yFinanceData(row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Adj Close'], row['Volume'])
                        self.btContract.historicalContractData.append(candlestickIndex)
        else:
            if "Time" in df.columns:
                for index, row in df.iterrows():
                    candlestickIndex = CandleStick()
                    candlestickIndex.ibapiDataCsv(row['Date'], row['Time'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume'])
                    self.btContract.historicalContractData.append(candlestickIndex)
            else:
                for index, row in df.iterrows():
                    candlestickIndex = CandleStick()
                    candlestickIndex.yFinanceData(row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Adj Close'], row['Volume'])
                    self.btContract.historicalContractData.append(candlestickIndex)

    ##GET HISTORICAL DATA## todo adjust for forex time frame?? maybe not neccessary
    def ibapiInputHistoricalDataParameters(self):
        print("Time interval chart\n"
              "S - Seconds\n"
              "D - Day\n"
              "W - Week\n"
              "M - Month\n"
              "Y - Year")

        interval = input("Enter time interval: ").upper()
        splitInterval = interval.split()
        intervalConversion = 0
        if splitInterval[1] == "S":
            intervalConversion = 1 ##ONE SECOND##
        elif splitInterval[1] == 'D':
            intervalConversion = 23400 ##SECONDS IN A DAY##
        elif splitInterval[1] == 'W':
            intervalConversion = 117000 ##SECONDS IN FIVE DAYS##
        elif splitInterval[1] == 'M':
            intervalConversion = 468000 ##SECONDS IN 20 DAYS - 19 IS THE SHORTEST NUMBER OF TRADING DAYS IN A MONTH##
        elif splitInterval[1] == 'Y':
            intervalConversion = 5616000 ##SECONDS IN 12 * 20 DAYS (240 DAYS) - APPROXIMATE NUMBER OF TRADING DAYS IN A YEAR##

        print("Bar sizes chart\n"
              "1 secs 5 secs 10 secs 15 secs 30 secs\n"
              "1 min 2 mins 3 mins 5 mins 10 mins 15 mins 20 mins 30 mins\n"
              "1 hour 2 hours 3 hours 4 hours 8 hours\n"
              "1 day\n"
              "1 week\n"
              "1 month")
        barDuration = input("Enter bar size: ").lower()
        splitBarDuration = barDuration.split()
        barDurationConversion = 0
        if splitBarDuration[1] == 'secs':
            barDurationConversion = 1 ##ONE SECOND##
        elif splitBarDuration[1] == 'min' or splitBarDuration[1] == 'mins':
            barDurationConversion = 60 ##60 SECONDS##
        elif splitBarDuration[1] == 'hour' or splitBarDuration[1] == 'hours':
            barDurationConversion = 3600 ##SECONDS IN AN HOUR##
        elif splitBarDuration[1] == 'day':
            barDurationConversion = 23400 ##SECONDS IN A DAY##
        elif splitBarDuration[1] == 'week':
            barDurationConversion = 117000 ##SECONDS IN FIVE DAYS
        elif splitBarDuration[1] == 'month':
            barDurationConversion = 468000 ##SECONDS IN 20 DAYS - 19 IS THE SHORTEST NUMBER OF TRADING DAYS IN A MONTH##

        numbCandles = (int(splitInterval[0]) * intervalConversion) / (int(splitBarDuration[0]) * barDurationConversion)

        self.getNextValidId()
        self.ibapiHistoricalData(numbCandles, self.nextValidOrderId, self.btContract, '', interval, barDuration, 'BID')
        self.getNextValidIdIncrement()

    def ibapiHistoricalData(self, numbCandles, reqID, contract, endDate, interval, timePeriod, dataType, rth=1, timeFormat=1, streaming=False):
        self.reqHistoricalData(reqID, contract, endDate, interval, timePeriod, dataType, rth, timeFormat, streaming, [])
        while len(self.btContract.historicalContractData) < numbCandles:
            time.sleep(3)

    def historicalDataToCsv(self):
        csvInput = input("Would you like to save these results into a csv? (y/n): ").lower()
        if csvInput == "y":
            barDate = []
            barTime = []
            open = []
            high = []
            low = []
            close = []
            volume = []
            for candle in self.btContract.historicalContractData:
                barDate.append(datetime.datetime.strptime(candle.date, "%Y%m%d"))
                barTime.append(candle.time)
                open.append(candle.open)
                high.append(candle.high)
                low.append(candle.low)
                close.append(candle.close)
                volume.append(candle.volume)
            df = pd.DataFrame()
            df['Date'] = barDate
            df['Time'] = barTime
            df['Open'] = open
            df['High'] = high
            df['Low'] = low
            df['Close'] = close
            df['Volume'] = volume
            fileName = self.btContract.symbol + '.csv'
            df.to_csv(f'{os.path.expanduser("~")}\\Desktop/' + fileName)
            print(f"{fileName} saved to your desktop")

    ##INTERNALLY USED##
    def historicalData(self, reqId, bar):
        candleStick = CandleStick()
        # print(bar)
        candleStick.ibapiData(bar)
        self.btContract.historicalContractData.append(candleStick)

    ##GET EARLIEST AVAILABLE DATE##
    def getEarliestDataDate(self):
        self.getNextValidId()
        self.reqHeadTimeStamp(self.nextValidOrderId, self.btContract, 'BID', 1, 1)
        while self.earliestDate == None:
            pass
        print("Earliest available data date: ", self.earliestDate)

    ##INTERNALLY USED##
    def headTimestamp(self, reqId, headTimestamp):
        self.earliestDate = headTimestamp

    def yFinanceHistoricalData(self):
        year = datetime.date.today().year
        month = datetime.date.today().month
        day = datetime.date.today().day
        hour = datetime.datetime.now().time().hour
        minute = datetime.datetime.now().time().minute
        period1 = int(time.mktime(datetime.datetime((year - self.previousStartYearInterval), month, day, hour, minute).timetuple()))
        period2 = int(time.mktime(datetime.datetime(year, month, day, hour, minute).timetuple()))
        interval = '1d'  ##1wk, 1mo, 1d##
        query = f'https://query1.finance.yahoo.com/v7/finance/download/{self.btContract.symbol}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'
        df = pd.read_csv(query)
        print(df)
        return df

    def yFinanceHistoricalDataToCsv(self, df):
        if str(input(f"Would you like to save a csv file of the ticker symbol's historical data for a "
                     f"{self.previousStartYearInterval} year time frame? (y/n): ").lower()) == 'y':
            fileName = self.btContract.symbol + '.csv'
            df.to_csv(f'{os.path.expanduser("~")}\\Desktop/' + fileName)
            print(f"{fileName} saved to your desktop")

    ##SETS YFINANCE BACKTEST DATES## todo is datetime objects neccessary?? if not get rid of them
    def setYFinanceImport(self, df):
        if input("Would you like to set start and end dates for the backtest? (y/n): ").lower() == "y":
            startDate = datetime.datetime.strptime(str(input('Enter start date (yyyy-mm-dd): ')), self.dateFormat)
            endDate = datetime.datetime.strptime(str(input('Enter end date (yyyy-mm-dd): ')), self.dateFormat)
            for index, row in df.iterrows():
                formatDate = datetime.datetime.strptime(row['Date'], self.dateFormat)
                if formatDate >= startDate and formatDate <= endDate:
                    candlestickIndex = CandleStick()
                    candlestickIndex.yFinanceData(row['Date'], row['Open'], row['High'], row['Low'],
                                                                row['Close'], row['Adj Close'],row['Volume'])
                    self.btContract.historicalContractData.append(candlestickIndex)
        else:
            for index, row in df.iterrows():
                candlestickIndex = CandleStick()
                candlestickIndex.yFinanceData(row['Date'], row['Open'], row['High'], row['Low'], row['Close'],
                                               row['Adj Close'], row['Volume'])
                self.btContract.historicalContractData.append(candlestickIndex)

    def changeBestPnl(self, file, bestPnl: list): ##bestPnl: PNL, f(x), f(y), Strategy Function, Number of Transactions##
        df = pd.read_csv(f'{os.path.expanduser("~")}\\Desktop/{file}')
        for index, row in df.iterrows():
            if row['Stock'] == self.btContract.symbol:
                df.loc[index, 'Quantity'] = self.btContract.quantity
                df.loc[index, 'Strategy'] = bestPnl[3].__name__
                df.loc[index, 'StrategyPos'] = (marginStrategies.index(bestPnl[3]) + 1)
                df.loc[index, 'BuyTrail'] = bestPnl[1]
                df.loc[index, 'BuyType'] = '%' ##todo change to buytype once amt optimization is added
                df.loc[index, 'SellTrail'] = bestPnl[2]
                df.loc[index, 'SellType'] = '%' ##todo change to sellType once amt optimization is added
                break

