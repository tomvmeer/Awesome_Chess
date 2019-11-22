import socket_comms
import pickle
import os
import time
import config
import random
import socket


def inform_game_process(data):
    global filename
    with open(filename, 'wb') as f:
        f.write(pickle.dumps(data))


def get_status_from_game_process():
    global filename
    with open(filename, 'rb') as f:
        return pickle.loads(f.read())


dir = path = config.load_config('app_path')

while True:
    old = os.listdir(dir)
    time.sleep(0.01)
    filename = [i for i in os.listdir(dir) if i not in old]
    if len(filename) == 1:
        break
filename = filename[0]
print('> Communication file:', filename)

data = {
    'state': 'waiting'
}
inform_game_process(data)
crashed = False

while not crashed:
    data = get_status_from_game_process()
    if data['state'] == 'host waiting':
        while True:
            try:
                data['opponent_name'], conn = socket_comms.host_game(data['HOST'], data['PORT'])
            except socket.timeout:
                data = get_status_from_game_process()
                if data['state'] == 'quitting':
                    crashed = True
                    break
            else:
                break
        if crashed:
            break
        time.sleep(1)
        socket_comms.send(data['player_name'], conn)
        print('> Player connected:', data['opponent_name'])
        time.sleep(1)
        data['state'] = 'connected'
        team = random.randint(0, 1)
        socket_comms.send('1' if team == 0 else '0', conn)
        data['team'] = team
        data['is_turn'] = True if team == 0 else False
        print('Team:', team)
        inform_game_process(data)
    elif data['state'] == 'joining':
        try:
            conn = socket_comms.connect(data['HOST'], data['PORT'], data['player_name'])
        except ConnectionRefusedError:
            break
        data['opponent_name'] = socket_comms.listen(conn)
        print('> Connected to player:', data['opponent_name'])
        data['state'] = 'connected'
        team = int(socket_comms.listen(conn))
        data['is_turn'] = True if team == 0 else False
        data['team'] = team
        print('Team:', team)
        inform_game_process(data)
    elif data['state'] == 'connected':
        if data['is_turn'] == 'done':
            socket_comms.send(pickle.dumps(data['board']), conn, bytes=True)
            print('> Send board')
            send_board = True
            data['is_turn'] = False
        if not data['is_turn']:
            print('> Waiting to receive new board...')
            while True:
                try:
                    data['board'] = pickle.loads(socket_comms.listen(conn, bytes=True))
                except socket.timeout:
                    data = get_status_from_game_process()
                    if data['state'] == 'quitting':
                        crashed = True
                        break
                else:
                    break
            if crashed:
                break
            print('> Got new board')
            data['is_turn'] = True
            inform_game_process(data)
    elif data['state'] == 'quitting':
        crashed = True
    time.sleep(0.5)

print('> network is quitting')
os.remove(filename)
