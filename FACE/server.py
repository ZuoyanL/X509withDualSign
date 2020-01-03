#服务器端负责计算，存储
import cv2
import os
import numpy as np
import imagehash
import json
from socket import *
import matplotlib.pyplot as plt
import pickle
#计算汉明距离
def Hamming_distance(hash1,hash2): 
    num = 0
    for index in range(len(hash1)): 
        if hash1[index] != hash2[index]: 
            num += 1
    return num

#均值哈希
def aHash(image):
    '''返回图像哈希值'''
    image=cv2.resize(image,(8,8),interpolation=cv2.INTER_CUBIC)
    image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    average = np.mean(image)
    hash = []
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i,j] > average:
                hash.append(1)
            else:
                hash.append(0)
    return hash




# 加载数据
filename='dataset.json'
with open(filename) as file_obj:
    dataset = json.load(file_obj)

##计算过程
def get_id(data):
    with open('dataset.json') as file_obj:
        dataset = json.load(file_obj)
    capture_hash = aHash(data)
    distance_dict = {}
    for k,v in dataset.items():
        distance_dict[k]= Hamming_distance(capture_hash, v)
    return min(distance_dict, key=distance_dict.get)
    


## 通信模块
HOST = '127.0.0.1'
PORT = 21567
BUFSIZ = 10240
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)
name = None
while True:
    print('waiting for connection...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('...connnecting from:', addr)
    data = b""
    while True:
        packet = tcpCliSock.recv(BUFSIZ)
        if not packet:
            break
        data = data + packet
    img = pickle.loads(data)
    #print(img)
    #reply = get_id(img)
    #tcpCliSock.send(reply.encode()) 
          
    tcpCliSock.close()
tcpSerSock.close()
