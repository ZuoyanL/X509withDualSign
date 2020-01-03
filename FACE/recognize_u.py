import cv2
import os
import numpy as np
import imagehash
import json
from socket import *
import pickle

#现场拍照
picture = []
detector=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml') 
cap=cv2.VideoCapture(0)
print('press s to save, esc to quit')
while(1):
    ret ,frame = cap.read()
    k=cv2.waitKey(1)
    if k==27:
        break
    elif k==ord('s'):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 1)
        for (x, y, w, h) in faces:
            picture.append(frame[(y+h//2)-h//3:(y+h//2)+h//3, (x+w//2)-w//3:(x+w//2)+w//3])
    cv2.imshow("capture", frame)
cap.release()
cv2.destroyAllWindows()



###发起与服务器的通信过程，传输加密照片
HOST = '127.0.0.1'
POST = 21567
BUFSIZ = 10240
ADDR = (HOST, POST)
tcpCliSock = socket(AF_INET, SOCK_STREAM)
tcpCliSock.connect(ADDR)

name =None
while True:    
    data = picture[0]
    tcpCliSock.send(pickle.dumps(data))
    data = tcpCliSock.recv(BUFSIZ)
    name = data.decode()
tcpCliSock.close()

        