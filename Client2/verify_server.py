from socket import *
from time import ctime
import OpenSSL
import json
import pickle
import hashlib
import sys
sys.path.append('/Users/xiaoxiaoyan/PycharmProjects/X509/Class')
from Class import Class
HOST = '127.0.0.1'
PORT = 21565
BUFSIZ = 4096
ADDR = (HOST, PORT)

BANK_POST = 21567
BANK_ADDR = (HOST, BANK_POST)

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

student_list = {
    '1001': False,
    '1002': False
}

def verify(data):
    # rec_data = eval(data)
    rec_data = data
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
        return True
    except OpenSSL.crypto.Error:
        return False
        print('Verifying sign failed...')

def transferData(addr, data):
    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    tcpCliSock.connect(addr)
    tcpCliSock.send(repr(data).encode("utf8"))
    tcpCliSock.close()

def updateClassInfo(addr):
    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    tcpCliSock.connect(addr)
    tcpCliSock.send('@update'.encode("utf8"))
    data = tcpCliSock.recv(BUFSIZ)
    tcpCliSock.close()
    return data


# 服务器通信
while True:
    print('Store is waiting for connection...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('...connnecting from:', addr)
    while True:
        data = tcpCliSock.recv(BUFSIZ)
        if not data:
            break
        if data.decode("utf8") == '@log':
            data = tcpCliSock.recv(BUFSIZ)
            data_rev = data.decode("utf8")
            if data_rev in student_list.keys():
                if student_list[data_rev]:
                    tcpCliSock.send(b"OK")
                else:
                    student_list[data_rev] = True
                    tcpCliSock.send(b"OK")
            else:
                tcpCliSock.send(b"Wrong ID")
        if data.decode("utf8") == '@scan':
            tcpCliSock.send(updateClassInfo(BANK_ADDR))
        if data.decode("utf8") == '@comment':
            data = tcpCliSock.recv(BUFSIZ)
            data_rev = eval(data.decode("utf8"))
            to_verify = data_rev['to_verify']
            to_comment = data_rev['to_comment']
            print(data_rev)
            if verify(to_verify):
                transferData(BANK_ADDR, to_comment)
    tcpCliSock.close()
tcpSerSock.close()
