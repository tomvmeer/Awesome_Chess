import socket
import time


def send(tosend, s):
    while True:
        s.sendall(tosend.encode())
        data = s.recv(1024)
        if tosend == data.decode():
            break


def listen(s):
    while True:
        data = s.recv(1024)
        if data:
            s.sendall(data)
            return data.decode()


def connect(HOST, PORT, playername):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    time.sleep(1)
    send('connecting', s)
    time.sleep(1)
    send(playername, s)
    return s


if __name__ == '__main__':
    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 65432  # The port used by the server
    host = connect(HOST, PORT, 'Maren')
    print(listen(host))
    print(listen(host))
