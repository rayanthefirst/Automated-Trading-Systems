##IBAPI MODULES##
from ibapi.common import BarData

##CANDLESTICK_V1##
class CandleStick(BarData):
    def __init__(self):
        BarData.__init__(self)

        ##ADDED ATTRIBUTES##
        self.openClose = [self.open, self.close]
        self.time = '00:00:00'

        ##EXTRA YAHOO FINANCE ATTRIBUTES##
        self.adj_close = 0

    def __str__(self):
        return ",".join((
            str(self.date),
            str(self.time),
            str(self.open),
            str(self.high),
            str(self.low),
            str(self.close),
            str(self.adj_close),
            str(self.volume)))

    def ibapiData(self, barData: BarData):
        self.open = barData.open
        self.close = barData.close
        self.high = barData.high
        self.low = barData.low
        self.volume = barData.volume
        self.openClose = [barData.open, barData.close]
        dateTimeList = barData.date.split()
        self.date = dateTimeList[0]
        if len(dateTimeList) > 1:
            self.time = barData.date.split()[1]

    def ibapiDataCsv(self, date, time, open, high, low, close, volume):
        self.date = date
        self.time = time
        self.openClose = [open, close]
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def yFinanceData(self, date, open, high, low, close, adj_close, volume):
        self.date = date.split()[0]
        self.openClose = [open, close]
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.adj_close = adj_close
        self.volume = volume