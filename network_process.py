import socket_comms
import pickle
import os
import time
import config
import random
import socket


def inform_game_process(data):
    global filename
    while True:
        try:
            with open(filename, 'wb') as f:
                f.write(pickle.dumps(data))
        except EOFError:
            pass
        else:
            break


def get_status_from_game_process():
    global filename
    while True:
        try:
            with open(filename, 'rb') as f:
                return pickle.loads(f.read())
        except EOFError:
            pass


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
        connection = socket_comms.Connection(data['HOST'], data['PORT'])
        while not connection.host_game():
            data = get_status_from_game_process()
            if data['state'] == 'quitting':
                crashed = True
                break
        if not crashed:
            data['state'] = 'hosting'
    if data['state'] == 'hosting':
        while not connection.send(data['player_name']):
            data = get_status_from_game_process()
            if data['state'] == 'quitting':
                crashed = True
                break
        while not crashed:
            received = connection.listen()
            data = get_status_from_game_process()
            if received != False:
                opponent = received
                break
            elif not received and data['state'] == 'quitting':
                crashed = True
        if not crashed:
            print('> Player connected:', opponent)
            team = random.randint(0, 1)
            while not connection.send('1' if team == 0 else '0'):
                data = get_status_from_game_process()
                if data['state'] == 'quitting':
                    crashed = True
                    break
            if not crashed:
                data['opponent_name'] = opponent
                data['state'] = 'connected'
                data['team'] = team
                data['is_turn'] = True if team == 0 else False
                print('Team:', team)
                inform_game_process(data)
    elif data['state'] == 'joining':
        connection = socket_comms.Connection(data['HOST'], data['PORT'])
        while not connection.connect():
            data = get_status_from_game_process()
            if data['state'] == 'quitting':
                crashed = True
                break
        while not crashed:
            received = connection.listen()
            data = get_status_from_game_process()
            if received != False:
                opponent = received
                break
            elif not received and data['state'] == 'quitting':
                crashed = True
        if not crashed:
            print('> Connected to player:', opponent)
            while not connection.send(data['player_name']):
                data = get_status_from_game_process()
                if data['state'] == 'quitting':
                    crashed = True
                    break
            while not crashed:
                received = connection.listen()
                data = get_status_from_game_process()
                if received != False:
                    team = int(received)
                    break
                elif not received and data['state'] == 'quitting':
                    crashed = True
            if not crashed:
                data['opponent_name'] = opponent
                data['state'] = 'connected'
                data['is_turn'] = True if team == 0 else False
                data['team'] = team
                print('Team:', team)
                inform_game_process(data)
    elif data['state'] == 'connected':
        if data['is_turn'] == 'done':
            while not connection.send(pickle.dumps([data['board'], data['ghost']]), bytes=True):
                data = get_status_from_game_process()
                if data['state'] == 'quitting':
                    crashed = True
                    break
            if not crashed:
                print('> Send board')
                send_board = True
                data['is_turn'] = False
        if not data['is_turn']:
            print('> Waiting to receive new board...')
            while not crashed:
                received = connection.listen(bytes=True)
                data = get_status_from_game_process()
                if received != False:
                    data['board'], data['ghost'] = pickle.loads(received)
                    print('> Got new board')
                    data['is_turn'] = True
                    inform_game_process(data)
                    break
                elif not received and data['state'] == 'quitting':
                    crashed = True
    elif data['state'] == 'quitting':
        crashed = True
    time.sleep(0.5)

print('> network is quitting')
os.remove(filename)
