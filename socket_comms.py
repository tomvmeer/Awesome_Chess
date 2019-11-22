import socket
import time


def listen(conn, bytes=False):
    while True:
        data = conn.recv(1024)
        if data:
            conn.sendall(data)
            if bytes:
                return data
            return data.decode()


def send(tosend, conn, bytes=False):
    while True:
        if not bytes:
            conn.sendall(tosend.encode())
        else:
            conn.sendall(tosend)
        data = conn.recv(1024)
        if not bytes and tosend == data.decode():
            break
        elif bytes and tosend == data:
            break


def host_game(HOST, PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        print('Connected by', addr)
        conn.settimeout(5)
        while listen(conn) != 'connecting':
            pass
        playername = listen(conn)
        return playername, conn


def connect(HOST, PORT, playername):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
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
