import OpenSSL
import hashlib
import json
import pickle
from socket import *
import sys
sys.path.append('/Users/xiaoxiaoyan/PycharmProjects/X509/Class')
from Class import Class

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

HOST = '127.0.0.1'

BANK_POST = 21567
BUFSIZ = 4096
BANK_ADDR = (HOST, BANK_POST)

STORE_POST = 21565
STORE_ADDR = (HOST, STORE_POST)


tcpCliSock_store = socket(AF_INET, SOCK_STREAM)
tcpCliSock_store.connect(STORE_ADDR)

# tcpCliSock_bank = socket(AF_INET, SOCK_STREAM)
# tcpCliSock_bank.connect(BANK_ADDR)


def cryto(data, cert_path):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    cert_path = open(cert_path).read()
    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_path)
    pub_key = OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, cert.get_pubkey()).decode("utf-8")
    public_key = serialization.load_pem_public_key(
        pub_key.encode(),
        backend=default_backend()
    )
    out_data = public_key.encrypt(
        data,
        padding.PKCS1v15()
    )
    return out_data

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


print("*"*50,
      "\n悄咪咪课程匿名评价系统                                             \n",
      "*"*50)

login = False
while True:
    if not login:
        data = input('>>>[@scan]:for getting class list\n'
                     '>>>[@comment]:for rating class\n'
                     '>>>[@exit]:for quitting\n'
                     '>>>[@log]:for login'
                     '\n')
    else:
        data = input('>>>[@scan]:for getting class list\n'
                     '>>>[@comment]:for rating class\n'
                     '>>>[@exit]:for quitting'
                     '\n')
    if not data:
        break
    if data == "@exit":
        break
    if data == "@log":
        tcpCliSock_store.send(data.encode("utf8"))
        student_ID = input("Log in with your student_ID\n:")
        tcpCliSock_store.send(student_ID.encode("utf8"))
        if tcpCliSock_store.recv(BUFSIZ).decode("utf8") != "OK":
            print("Wrong ID! input again!")
            continue
        print("Log in succeed")
        login = True
    if data == "@scan":
        tcpCliSock_store.send(data.encode("utf8"))
        class_list = tcpCliSock_store.recv(BUFSIZ)
        class_list = pickle.loads(class_list)
        print("Classes are as follows:")
        print(class_list.keys())
        print("details:")
        for k, v in class_list.items():
            print("*"*20)
            print(k, "\naverage score:%f \ncomments: "%float(v.get_avg_score()))
            v.print_comments()
        print("*" * 20)
    if data == "@comment":
        tcpCliSock_store.send(data.encode("utf8"))
        to_class = input("Please input the class you want to rate:\n") # class
        score = input("Please score for this class:[0-10]\n") # 打分
        comments = input("Please rate this class:[within 500 chs]\n") # 评论
        # to_class = "CV"
        # score = 9
        # comments = "hao"
        original_data = {
            "PI": {
                'account': student_ID,
            },
            "OI":{
                "to_class": to_class,
                "score": score,
                "comments": comments
            }
        }
        print("before encryption...")
        print(original_data["OI"])
        original_data["OI"] = cryto(pickle.dumps(original_data["OI"]), 'server.crt')
        print("after encryption...")
        print(original_data["OI"])
        to_bank_data = to_bank(original_data)
        to_store_data = to_store(original_data)
        send_data = {
            'to_verify': to_bank_data,
            'to_comment': to_store_data
        }
        tcpCliSock_store.send(repr(send_data).encode("utf8"))

tcpCliSock_store.close()
