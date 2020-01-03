from socket import *
from time import ctime
import OpenSSL
import json
import hashlib
import pickle
import sys
sys.path.append('/Users/xiaoxiaoyan/PycharmProjects/X509/Class')
from Class import Class
HOST = '127.0.0.1'
PORT = 21567
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
# bank_private_key_path = open('server.pem').read()

bank_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, bank_crt_path)
store_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, store_crt_path)
customer_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, customer_crt_path)
# customer_private_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, bank_private_key_path)


A = []
B = []
C = []
A_ = []
B_ = []
C_ = []
AI = Class(A, A_)
CV = Class(B, B_)
Crypto = Class(C, C_)

class_list = {
    'AI': AI,
    'CV': CV,
    'Crypto': Crypto
}


def verify(data):
    # rec_data = eval(data)
    rec_data = data
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
        return True
        print("Verifying sign succeed...")
    except OpenSSL.crypto.Error:
        return False
        print('Verifying sign failed...')


def decrpto(data, pri_path):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    from cryptography.hazmat.primitives.asymmetric import padding
    pri_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, open(pri_path).read())
    pri_key = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pri_key).decode("utf-8")
    private_key = serialization.load_pem_private_key(
        pri_key.encode(),
        password=None,
        backend=default_backend()
    )
    out_data = private_key.decrypt(
        data,
        padding.PKCS1v15()
    )
    return out_data

while True:
    print('waiting for connection...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('...connnecting from:', addr)
    while True:
        data = tcpCliSock.recv(BUFSIZ)
        if not data:
            break
        if data.decode("utf8") == "@update":
            tcpCliSock.send(pickle.dumps(class_list))
        elif verify(eval(data.decode())):
            rec_data = eval(data.decode())["OI"]
            rec_data = pickle.loads(decrpto(rec_data, 'server.pem'))
            to_class = rec_data['to_class']
            score = float(rec_data['score'])
            comments = rec_data['comments']
            print(eval(data.decode()))
            print("Decrption....")
            print(rec_data)
            class_list[to_class].set_comment(comments)
            class_list[to_class].set_score(score)

    tcpCliSock.close()
tcpSerSock.close()
