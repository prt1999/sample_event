from web3 import Web3
from time import time
from datetime import datetime


def timestamp():
    timestamp = time()
    dt_object = datetime.fromtimestamp(timestamp)
    return dt_object

def wait_for_open_trade(token, methodid):
    openTrade = False
    tx_filter = client.eth.filter({"filter_params": "pending", "address": token})

    while openTrade == False:
        try:
            for tx_event in tx_filter.get_new_entries():

                txHash = tx_event['transactionHash']
                txHashDetails = client.eth.get_transaction(txHash)
                txFunction = txHashDetails.input[:10]
                if txFunction.lower() in methodid:
                    openTrade = True
                    print(timestamp(), " MethodID: ", txFunction, " Block: ", tx_event['blockNumber'], " Found Signal")
                    #break
                else:
                    print(timestamp(), " MethodID: ", txFunction, " Block: ", tx_event['blockNumber'])
        except:
            print(timestamp(), " Error")
            wait_for_open_trade(token, methodid)

# WitcherVerse (WCH)
#token = Web3.toChecksumAddress("0xD2f71875d66188F96BaDBF98a5F020894209E34b")
# Function: preSaleAfter()
#methodId = "0xbccce037"

# Jade
token = Web3.toChecksumAddress("0x7ad7242a99f21aa543f9650a56d141c57e4f6081")
# Function: Transfer
methodId = "0x7ff36ab5"

#my_provider = "https://bsc-dataseed4.defibit.io"
my_provider = "http://localhost:8545"
client = Web3(Web3.HTTPProvider(my_provider))

wait_for_open_trade(token, methodId)
