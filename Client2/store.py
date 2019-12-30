from socket import *
from time import ctime
import OpenSSL
import json
import hashlib

HOST = '127.0.0.1'
PORT = 21569
BUFSIZ = 1024
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)

customer_crt_path = open('client1.crt').read()
store_crt_path = open('client2.crt').read()
bank_crt_path = open('server.crt').read()
store_private_key_path = open('client2.pem').read()

bank_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, bank_crt_path)
store_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, store_crt_path)
customer_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, customer_crt_path)
store_private_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, store_private_key_path)


class Commodity:
    def __init__(self, name, number, price):
        self.name = name
        self.number = number
        self.price = price


apple = Commodity('apple', 100, 1.5)
orange = Commodity('orange', 20, 5.0)

# 商品列表...
# 本来想用个实体类的，算了...
list = {
    'apple': {
        'amount': 100,
        'price': 1.5
    },
    'orange': {
        'amount': 20,
        'price': 5.0
    }
}

# 处理订单
def orderProcess(data):
    rec_data = eval(data.decode("utf8"))
    rec_data = rec_data['OI']
    apple = rec_data['apple']
    orange = rec_data['orange']
    if float(apple['amount']) <= float(list['apple']['amount']):
        list['apple']['amount'] -= float(apple['amount'])
        print("Now apple:", list['apple']['amount'])
    else:
        return False
    if float(orange['amount']) <= float(list['orange']['amount']):
        list['orange']['amount'] -= float(orange['amount'])
        print("Now orange:", list['orange']['amount'])
    else:
        return False
    return True

def verify(data):
    rec_data = eval(data)
    OI = rec_data['OI']
    PIMD = rec_data['PIMD']
    DS = rec_data['DS']

    sha1_OI = hashlib.sha1()
    sha1_OI.update(repr(OI).encode("utf8"))
    OIMD = sha1_OI.hexdigest()

    sha1_POMD = hashlib.sha1()
    sha1_POMD.update((PIMD + OIMD).encode("utf8"))
    POMD = sha1_POMD.hexdigest()
    try:
        OpenSSL.crypto.verify(customer_crt, DS, POMD, "sha1")
        print("Verifying sign succeed...")
    except OpenSSL.crypto.Error:
        print('Verifying sign failed...')


# 服务器通信
while True:
    print('Store is waiting for connection...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('...connnecting from:', addr)
    while True:
        data = tcpCliSock.recv(BUFSIZ)
        if not data:
            break
        if data.decode("utf8") == '@scan':
            tcpCliSock.send(repr(list).encode("utf8"))
        if data.decode("utf8") == '@buy':
            print("buying...")
            data = tcpCliSock.recv(BUFSIZ)
            verify(data)
            if not orderProcess(data):
                print("failed")
    tcpCliSock.close()
tcpSerSock.close()
