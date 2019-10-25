import socket


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
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        print('Connected by', addr)
        while listen(conn) != 'connecting':
            pass
        playername = listen(conn)
        return playername, conn
