import traceback
import csv
import requests
from datetime import datetime
import smtplib
import ssl
import re

path = '/Users/emilyfong/Desktop/Propel/deposit_tracking/'
today = datetime.today().strftime('%Y-%m-%d')
read_name = path + "raw/" + today
store_name = path + "storage.csv"


def downloadFile(url):

    #download file from metabase
    try:
        r = requests.get(url)

        with open(read_name, 'wb') as f:
            f.write(r.content)

    except:
        traceback.print_exc()

def readCSV(file):
    deposit_types = []

    #read file and hideously filter out incorrect transactions
    #please don't shame me I'll refactor later
    with open(file,'rt')as f:
        data = csv.reader(f)
        for row in data:
            if len(row) > 0 and "html" not in row[0] and "<head>" not in row[0] and "<body>" not in row[0] and "<center>" not in row[0] and "</body>" not in row[0] and "transaction_type" not in row[0] and "Purchase" not in row[0] and "Expunge" not in row[0] and "$" not in row[0]:
                deposit_types.append(row[0])
            else:
                continue

    return deposit_types

def compareCSV(old_deposits_file, new_deposits_array):

    #arrays to store old deposits from storage and new deposits to alert us with
    old_deposit_types = []
    alert_new_deposits = []
    email_string = "New Transaction Types Found\n"

    #create array of old deposit_types from storage
    with open(old_deposits_file, 'rt')as f:
        data = csv.reader(f)
        for row in data:
            old_deposit_types = row

    #check new deposits for anything we've missed
    #if there are new deposits, add them to the alert and storage arrays
    for new_item in new_deposits_array:
        if new_item not in old_deposit_types:
            alert_new_deposits.append(new_item)
            old_deposit_types.append(new_item)
            email_string = email_string + new_item.strip() +"\n"

    #email us with a list of the new deposit types
    if len(alert_new_deposits) > 0:
         sendEmail(email_string)

    #write updated old_deposit_types to storage
    converted_deposits = [old_deposit_types]
    writeCSV(converted_deposits)


def writeCSV(deposit_array):

    #write filtered deposits to storage file
    with open(store_name, 'w') as f:
        wr = csv.writer(f)
        wr.writerows(deposit_array)

def sendEmail(email_contents_string):

    #set up message and email credentials
    sender_email = "emilypropeldeposits@gmail.com"
    receiver_email = "emily.fong@nyu.edu"
    message = 'Subject: {}{}'.format("(PROPEL) ", email_contents_string).encode("utf-8")
    username = 'emilypropeldeposits@gmail.com'
    password = "propelbot100"

    # open server, login to email account, send email, close server
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(sender_email, receiver_email, message)
    server.quit()

def main():
    #edit path to input csv
    downloadFile("https://metabase.easyfoodstamps.com/public/question/d980e0da-b8de-447a-8d3c-024d7698222c.csv")
    deposits = readCSV(read_name)
    compareCSV(store_name, deposits)

main()
