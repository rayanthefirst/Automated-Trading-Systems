##PYTHON BUILT-IN MODULES##
from datetime import datetime
import configparser
import os
import subprocess

##CUSTOM PROJECT MODULES##
from useful_functions.EmailSender import sendEmail

##PIP INSTALLED MODULES##
import pandas as pd

##OPEN CONFIG FILE IN DESKTOP## todo change all self.file and path in stocktrailing bot to use this config file in sys args
config = configparser.ConfigParser()
config.read(f'{os.path.expanduser("~")}\\Desktop/fileConfig.ini')

stockBotInvestorVersion = config['STOCKTRAILINGBOT']['stockbotversion']##MUST USE COMMAND LINE ARGS##
file = config['STOCKTRAILINGBOT']['stockbotdefaults']
botIBC = config['IBC']['IBCbotlocation']

##START UP MANAGER V1.1## todo add - DOES NOT HAVE BACKTESTER YET and contains defaults, such as cash account and port
if file not in os.listdir(f'{os.path.expanduser("~")}\\Desktop'):
    sendEmail('No pre-existing default stock file was found, please manually set up the bot!', 'please manually add stocks and restart the program')
    subprocess.Popen('start 'f'{os.path.expanduser("~")}\\Desktop/{stockBotInvestorVersion}', shell=True)

elif '09:00:00' < datetime.now().strftime("%H:%M:%S") < '16:15:00':
    subprocess.Popen(botIBC, shell=True) ##DEFAULT LOCATION OF IBC##
    sendEmail('VM deploying stock bots!', 'Virtual machine has stock defaults in desktop and is now opening each bot.')

    df = pd.read_csv(f'{os.path.expanduser("~")}\\Desktop/{file}')
    for index, row in df.iterrows():
        sym, quantity, buyTrail, buyType, sellTrail, sellType, stratPos, port, clientId, accNumb, accType = row['Stock'], row['Quantity'], row['BuyTrail'], row['BuyType'], row['SellTrail'], row['SellType'], row['StrategyPos'], 4001, row['ClientId'], row['Account'], row['AccountType']
        subprocess.Popen('start 'f'{os.path.expanduser("~")}\\Desktop/{stockBotInvestorVersion} {sym} {quantity} {buyTrail} {buyType} {sellTrail} {sellType} {stratPos} {port} {clientId} {accNumb} {accType}', shell=True)

# if '16:30:00' < todo add backtester in next version
