##PYTHON BUILT-IN MODULES##
from email.message import EmailMessage
import configparser
import os
import smtplib

##OPEN CONFIG FILE IN DESKTOP##
config = configparser.ConfigParser()
config.read(f'{os.path.expanduser("~")}\\Desktop/fileConfig.ini')

EMAIL_ADDRESS = config['EMAIL']['emailfrom']
PASSWORD = config['EMAIL']['appspecificpassword']
EMAIL_ADDRESS_RECEIVED = config['EMAIL']['emailto']

def sendEmail(subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS_RECEIVED
    msg['X-Priority'] = '1' ##todo check if this is correct
    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, PASSWORD)

        smtp.send_message(msg)