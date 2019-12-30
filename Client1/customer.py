import OpenSSL
import hashlib
import json
from socket import *

### 处理证书
ca_crt_path = open('../ca.crt').read()
customer_crt_path = open('client1.crt').read()
store_crt_path = open('client2.crt').read()
bank_crt_path = open('server.crt').read()
customer_private_key_path = open('client1.pem').read()

ca_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, ca_crt_path)
bank_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, bank_crt_path)
store_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, store_crt_path)
customer_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, customer_crt_path)

ca_public_key = ca_crt.get_pubkey()
customer_private_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, customer_private_key_path)
# print(customer_private_key)

# PI = '62222'
# OI = 'apple:100, price:1000'
# #
# sha1_PI = hashlib.sha1()
# sha1_PI.update(PI.encode("utf8"))
# PIMD = sha1_PI.hexdigest()
#
# sha1_OI = hashlib.sha1()
# sha1_OI.update(OI.encode("utf8"))
# OIMD = sha1_OI.hexdigest()
#
# sha1_POMD = hashlib.sha1()
# sha1_POMD.update((sha1_PI.hexdigest()+sha1_OI.hexdigest()).encode("utf8"))
# POMD = sha1_POMD.hexdigest()
#
# sha1_POMD_Store = hashlib.sha1()
# sha1_POMD_Store.update((PIMD+hashlib.sha1(OI.encode("utf8")).hexdigest()).encode("utf8"))
# POMD_Store = sha1_POMD_Store.hexdigest()
# print(bank_crt.get_signature_algorithm())
# sign = OpenSSL.crypto.sign(customer_private_key, POMD, "sha1")
#
# try:
#     OpenSSL.crypto.verify(customer_crt, sign, POMD_Store, "sha1")
#     print("true")
# except OpenSSL.crypto.Error:
#     print('false')
#


HOST = '127.0.0.1'

BANK_POST = 21567
BUFSIZ = 1024
BANK_ADDR = (HOST, BANK_POST)

STORE_POST = 21569
STORE_ADDR = (HOST, STORE_POST)


tcpCliSock_store = socket(AF_INET, SOCK_STREAM)
tcpCliSock_store.connect(STORE_ADDR)

tcpCliSock_bank = socket(AF_INET, SOCK_STREAM)
tcpCliSock_bank.connect(BANK_ADDR)


# 利用私钥签名，得到DS
def sign(original_data=None, hash_mode='sha1'):
    PI = original_data['PI']
    OI = original_data['OI']

    sha1_PI = hashlib.sha1()
    sha1_PI.update(repr(PI).encode("utf8"))
    PIMD = sha1_PI.hexdigest()

    sha1_OI = hashlib.sha1()
    sha1_OI.update(repr(OI).encode("utf8"))
    OIMD = sha1_OI.hexdigest()

    sha1_POMD = hashlib.sha1()
    sha1_POMD.update((sha1_PI.hexdigest()+sha1_OI.hexdigest()).encode("utf8"))
    POMD = sha1_POMD.hexdigest()

    signed_data = OpenSSL.crypto.sign(customer_private_key, POMD, hash_mode)

    return signed_data


# 发送给商店的签名信息
def to_store(original_data):
    signed_data = sign(original_data)
    PI = original_data['PI']
    OI = original_data['OI']

    sha1_PI = hashlib.sha1()
    sha1_PI.update(repr(PI).encode("utf8"))
    PIMD = sha1_PI.hexdigest()

    to_store_data = {
        'PIMD': PIMD,
        'OI': OI,
        'DS': signed_data
    }
    return to_store_data


# 发送给银行的签名信息
def to_bank(original_data):
    signed_data = sign(original_data)
    PI = original_data['PI']
    OI = original_data['OI']

    sha1_OI = hashlib.sha1()
    sha1_OI.update(repr(OI).encode("utf8"))
    OIMD = sha1_OI.hexdigest()

    to_bank_data = {
        'PI': PI,
        'OIMD': OIMD,
        'DS': signed_data
    }
    return to_bank_data

# 处理命令行输入 ... TO BE DONE
def cmd_chose_commodity():
    print('chose what you want to buy:\n')


commodity_info = {}

while True:
    data = input('>>>scan store:@scan, buy something: @buy\n')
    if not data:
        break
    if data == "@scan":
        tcpCliSock_store.send(data.encode("utf8"))
        data = tcpCliSock_store.recv(BUFSIZ)
        if not data:
            break
        data = eval(data.decode("utf8"))
        commodity_info = data
        for name, info in data.items():
            print(name, ':', info)
    if data == "@buy":
        tcpCliSock_store.send(data.encode("utf8"))
        apple = input() #输入购买多少APPLE
        orange = input() #输入购买多少ORANGE
        apple_price = commodity_info['apple']['price'] * float(apple)
        orange_price = commodity_info['orange']['price'] * float(orange)
        original_data = {
            "PI": {
                'account': '1001',
                'amount': orange_price + apple_price
            },
            "OI":{
                "apple": {
                    "price": commodity_info['apple']['price'],
                    "amount": apple
                },
                "orange": {
                    "price": commodity_info['orange']['price'],
                    "amount": orange
                }
            }
        }

        to_bank_data = to_bank(original_data)
        to_store_data = to_store(original_data)
        tcpCliSock_store.send(repr(to_store_data).encode("utf8"))
        tcpCliSock_bank.send(repr(to_bank_data).encode("utf8"))

tcpCliSock_store.close()
tcpCliSock_bank.close()