import socket


def listen(conn):
    while True:
        data = conn.recv(1024)
        if data:
            conn.sendall(data)
            return data.decode()


def send(tosend, conn):
    while True:
        conn.sendall(tosend.encode())
        data = conn.recv(1024)
        if tosend == data.decode():
            break


def host_game(HOST, PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        print('Connected by', addr)
        while listen(conn) != 'connecting':
            pass
        playername = listen(conn)
        return playername, conn
