import socket
import time


class Connection:
    def __init__(self, host, port):
        self.conn = None
        self.host = host
        self.port = port

    def listen(self, bytes=False):
        try:
            data = self.conn.recv(1024)
            if data:
                self.conn.sendall(data)
                if bytes:
                    return data
                return data.decode()
            return False
        except Exception as e:
            print(e)
            return False

    def send(self, tosend, bytes=False):
        try:
            if not bytes:
                self.conn.sendall(tosend.encode())
            else:
                self.conn.sendall(tosend)
            data = self.conn.recv(1024)
        except Exception as e:
            print(e)
            return False
        if not bytes and tosend == data.decode():
            return True
        elif bytes and tosend == data:
            return True
        return False

    def host_game(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.bind((self.host, self.port))
            s.listen()
            try:
                self.conn, addr = s.accept()
                print('Connected by', addr)
                self.conn.settimeout(5)
                return True
            except Exception as e:
                print(e)
                return False

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((self.host, self.port))
            self.conn = s
            return True
        except Exception as e:
            print(e)
            return False
