from socket import *
from time import ctime
import OpenSSL
import json
import hashlib

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
bank_private_key_path = open('server.pem').read()

bank_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, bank_crt_path)
store_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, store_crt_path)
customer_crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, customer_crt_path)
customer_private_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, bank_private_key_path)

AI_comments = []
CV_comments = []
Crypto_comments = []


class Class:
    scores = []
    comments = []

    def __init__(self, scores=[], comments=[]):
        self.scores = scores
        self.comments = comments

    def get_avg_score(self):
        if len(self.scores) > 0:
            return sum(self.scores) / float(len(self.scores))

    def print_comments(self):
        if len(comments) == 0:
            print('This class has\'nt been rated...')
        for i in comments:
            print(i)

    def set_score(self, score):
        self.scores.append(score)

    def set_comment(self, comment):
        self.comments.append(comment)


AI = Class()
CV = Class()
Crypto = Class()

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


while True:
    print('waiting for connection...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('...connnecting from:', addr)
    while True:
        data = tcpCliSock.recv(BUFSIZ)
        if not data:
            break
        if verify(eval(data.decode())):
            rec_data = eval(data.decode())["OI"]
            to_class = rec_data['to_class']
            score = float(rec_data['score'])
            comments = rec_data['comments']
            class_list[to_class].set_comment(comments)
            class_list[to_class].set_score(score)
            print("Now, the average score of %s is %f" % (to_class, class_list[to_class].get_avg_score()))
    tcpCliSock.close()
tcpSerSock.close()
