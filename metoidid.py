from web3 import Web3
from web3.middleware import geth_poa_middleware
import argparse
import datetime
import asyncio


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--scan", type=str, help="Start mempool scan method: 1 (client.eth.filter), 2 (geth.txpool.content), 3 eth.get_block")
parser.add_argument("-v", "--verbose", action='store_true', help="Show only valid matches in the mempool")
parser.add_argument("-a", "--address", type=str, help="Address of the token you are looking for")
parser.add_argument("-m", "--methodid", type=str, help="The methoid you are looking for")
parser.add_argument("-p", "--provider", type=str, help="Blockchain Provider, support https/wss/ipc")
command_line_args = parser.parse_args()


def scan_mempool1(token, methodid):
    count = 0
    openTrade = False
    tx_filter = client.eth.filter({"filter_params": "pending", "address": token})

    while openTrade == False:
        try:
            for tx_event in tx_filter.get_new_entries():
                txHash = tx_event['transactionHash']
                txHashDetails = client.eth.get_transaction(txHash)
                txFunction = txHashDetails.input[:10]
                if txFunction.lower() in methodid:
                    #openTrade = True
                    print(datetime.datetime.now(), txHashDetails['blockNumber'], '\033[32m', txFunction, txHashDetails['to'], txHashDetails['from'], Web3.toHex(txHashDetails['hash']), '\033[0m')
                else:
                    if command_line_args.verbose == False:
                        print(datetime.datetime.now(), txHashDetails['blockNumber'], txFunction, txHashDetails['to'], txHashDetails['from'],  Web3.toHex(txHashDetails['hash']))
        except Exception as e:
                    print(e)
                    continue

def scan_mempool2(token, methodid):
    openTrade = False
    while openTrade == False:
        try:
            tx_pool = client.geth.txpool.content()['pending'].items()
            for k,v in tx_pool:
                for k1, v1 in v.items():
                    if v1['to'] == token.lower() and v1['input'][:10] in methodid:
                        print(datetime.datetime.now(), client.eth.block_number, '\033[32m', v1['input'][:10], v1['to'], v1['from'], v1['hash'], '\033[0m')
                        #openTrade = True
                    else:
                        if command_line_args.verbose == False:
                            print(datetime.datetime.now(), client.eth.block_number, v1['input'][:10], v1['to'], v1['from'],v1['hash'])
        except Exception as e:
            print(e)
            continue


def scan_mempool3(token, methodid):
    openTrade = False
    while openTrade == False:
        try:
            pending_block = client.eth.get_block('pending', full_transactions=True)
            tx_pool = pending_block['transactions']
            for v1 in tx_pool:
                if v1['to'] == token and v1['input'][:10] in methodid:
                    print(datetime.datetime.now(), v1['blockNumber'], '\033[32m', v1['input'][:10], v1['to'], v1['from'], Web3.toHex(v1['hash']), '\033[0m')
                    # openTrade = True
                else:
                    if command_line_args.verbose == False:
                        print(datetime.datetime.now(), v1['blockNumber'], v1['input'][:10], v1['to'], v1['from'], Web3.toHex(v1['hash']))
        except Exception as e:
            print(e)
            continue


def handle_event(event, methodid, filter_id,id_pending,id_latest):
    f_id = 0
    openTrade = False
    if filter_id == id_pending: f_id = 'pending'
    if filter_id == id_latest: f_id = 'latest'

    while openTrade == False:
        try:
                txHash = event['transactionHash']
                txHashDetails = client.eth.get_transaction(txHash)
                txFunction = txHashDetails.input[:10]

                if txFunction.lower() in methodid:
                    #openTrade = True
                    print(datetime.datetime.now(), txHashDetails['blockNumber'], f_id, '\033[32m', txFunction, txHashDetails['to'], txHashDetails['from'], Web3.toHex(txHashDetails['hash']),  '\033[0m')
                    return True
                else:
                    if command_line_args.verbose == False:
                        print(datetime.datetime.now(), txHashDetails['blockNumber'], f_id, txFunction, txHashDetails['to'], txHashDetails['from'],  Web3.toHex(txHashDetails['hash']))
                    return False
        except Exception as e:
                    print(e)
                    continue

async def log_loop(event_filter, methodid, poll_interval, id_pend, id_last):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event, methodid, event_filter.filter_id, id_pend, id_last)
        await asyncio.sleep(poll_interval)

def scan_mempool4(token, methodid):
    block_filter = client.eth.filter({"filter_params": "latest", "address": token})
    id_last = block_filter.filter_id
    tx_filter = client.eth.filter({"filter_params": "pending", "address": token})
    id_pend = tx_filter.filter_id
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(block_filter, methodid, 0.0001, id_pend, id_last),
                log_loop(tx_filter, methodid, 0.0001, id_pend, id_last)))
    finally:
        loop.close()


# Default function: approve, transfer
methodId = ["0x095ea7b3", "0xa9059cbb"]
methodId2 = "0x095ea7b3"

# Default token: Cake
token = Web3.toChecksumAddress("0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82")
# Default Provider
my_provider = Web3.HTTPProvider("https://bsc-dataseed3.defibit.io")

if command_line_args.methodid:
    methodId = command_line_args.methodid

if command_line_args.provider:
    my_provider = command_line_args.provider
    if my_provider[0].lower() == 'h': my_provider = Web3.HTTPProvider(my_provider)
    elif my_provider[0].lower() == 'w': my_provider = Web3.HTTPProvider(my_provider)
    else: my_provider = Web3.IPCProvider(my_provider)

client = Web3(my_provider)
print('MethodID scan utility v0.4 - pRT 2022')
print('Web3 Client version:', client.api)
print('Client Connected:', client.isConnected())
print('Chain ID:', client.eth.chain_id)
print('Provider version:', client.clientVersion)
print('Search Methodids:', methodId)

client.middleware_onion.inject(geth_poa_middleware, layer=0)

# Start mempool scan:

if command_line_args.address: token = Web3.toChecksumAddress(command_line_args.address)
if command_line_args.scan:
    meth = command_line_args.scan
    if meth == '1': scan_mempool1(token, methodId)
    elif meth == '2': scan_mempool2(token, methodId)
    elif meth == '3': scan_mempool3(token, methodId)
    elif meth == '4': scan_mempool4(token, methodId)

else:
    print('Missing/Bad parameter')
print('end.')
