from socket import *
from time import ctime
import OpenSSL
import json
import hashlib

HOST = '127.0.0.1'
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)

customer_crt_path = open('client1.crt').read()
store_crt_path = open('client2.crt').read()
bank_crt_path = open('server.crt').read()
bank_private_key_path = open('server.pem').read()

bank_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, bank_crt_path)
store_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, store_crt_path)
customer_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, customer_crt_path)
customer_private_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, bank_private_key_path)


countList = {
    '1001': {'balance': 1000.0},
    '1002': {'balance': 500.0}
}


def transfer(acc_from, acc_to, count_list, amount):
    a = count_list[acc_from]
    b = count_list[acc_to]
    if a['balance'] < amount:
        print("Trade failed, balance is not adequate")
        return False
    else:
        a['balance'] -= amount
        b['balance'] += amount
        print("Trade succeed!")
    return True


def verify(data):
    rec_data = eval(data)
    PI = rec_data['PI']
    OIMD = rec_data['OIMD']
    DS = rec_data['DS']

    sha1_PI = hashlib.sha1()
    sha1_PI.update(repr(PI).encode("utf8"))
    PIMD = sha1_PI.hexdigest()

    sha1_POMD = hashlib.sha1()
    sha1_POMD.update((PIMD+OIMD).encode("utf8"))
    POMD = sha1_POMD.hexdigest()

    try:
        OpenSSL.crypto.verify(customer_crt, DS, POMD, "sha1")
        print("Verifying sign succeed...")
    except OpenSSL.crypto.Error:
        print('Verifying sign failed...')


def process(data, countList, sock):
    rec_data = eval(data)
    PI = rec_data['PI']
    if transfer(PI['account'], '1002', countList, amount=PI['amount']):
        sock.send("Succeed".encode('utf-8'))
    else:
        sock.send("You have nn money".encode('utf-8'))


while True:
    print('waiting for connection...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('...connnecting from:', addr)
    while True:
        data = tcpCliSock.recv(BUFSIZ)
        if not data:
            break
        verify(data)
        process(data, countList, tcpCliSock)
        print(countList['1001']['balance'])
        print(countList['1002']['balance'])
    tcpCliSock.close()
tcpSerSock.close()
