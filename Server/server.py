import queue
import socket
import time
import ssl
import _thread
import pprint
from OpenSSL import SSL
hostname = '127.0.0.1'
port = 8888


"""
The info stored in the queue should be like this:
"sender|receiver|timestamp|msg"
and all item is str.
"""
MsgQ = {}

def Sender(sock, UserID):
    """
    Fetch 'info' from queue send to UserID.
    """
    Q = MsgQ[UserID]
    print("sender")
    try:
        while True:
            # get methord will be blocked if empty
            info = Q.get()
            sock.send(info.encode())
    except Exception as e:
        print(e)
        sock.close()
        _thread.exit_thread()


def Receiver(sock):
    """
    Receive 'msg' from UserID and store 'info' into queue.
    """
    try:
        while True:
            info = sock.recv(1024).decode()
            print(info)
            info_unpack = info.split("|")
            receiver = info_unpack[1]

            exit_cmd = receiver == "SEVER" and info_unpack[3] == "EXIT"
            assert not exit_cmd, "{} exit".format(info_unpack[0])

            if receiver not in MsgQ:
                MsgQ[receiver] = queue.Queue()
            MsgQ[receiver].put(info)

    except Exception as e:
        print(e)
        sock.close()
        _thread.exit_thread()


class Server:
    def __init__(self):
        self.crtfile = 'server.crt'
        self.keyfile = 'server.pem'
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        self.context.load_cert_chain(certfile=self.crtfile, keyfile=self.keyfile)
        self.Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.Sock = socket.socket()
        self.Sock.bind((hostname, port))
        self.Sock.listen()
        # self.threads = []

    def run(self):
        print("\033[35;40m[ Server is running ]\033[0m")
        # print("[ Server is running ]")
        while True:
            sock, _ = self.Sock.accept()
            # Start two threads
            connstream = self.context.wrap_socket(sock, server_side=True)
            # Register for new Client
            UserID = connstream.recv(1024).decode()
            print("Connect to {}".format(UserID))
            # UserID = '1'
            # Build a message queue for new Client
            if UserID not in MsgQ:
                MsgQ[UserID] = queue.Queue()
            _thread.start_new_thread(Sender, (connstream, UserID))
            _thread.start_new_thread(Receiver, (connstream,))

    def close(self):
        self.Sock.close()


if __name__ == "__main__":
    server = Server()
    try:
        server.run()
    except KeyboardInterrupt as e:
        server.close()
        print("Server exited")
