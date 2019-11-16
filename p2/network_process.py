import socket_comms
import pickle
import time


def inform_game_process(data):
    with open('status.dat', 'wb') as f:
        f.write(pickle.dumps(data))


def get_status_from_game_process():
    with open('status.dat', 'rb') as f:
        return pickle.loads(f.read())


data = {
    'state': 'waiting'
}
inform_game_process(data)

while True:
    data = get_status_from_game_process()
    if data['state'] == 'host waiting':
        data['opponent_name'], conn = socket_comms.host_game(data['HOST'], data['PORT'])
        time.sleep(1)
        socket_comms.send(data['player_name'], conn)
        print('> Player connected:', data['opponent_name'])
        data['state'] = 'connected'
        data['is_turn'] = True
        data['team'] = 0
        inform_game_process(data)
    elif data['state'] == 'joining':
        conn = socket_comms.connect(data['HOST'], data['PORT'], data['player_name'])
        data['opponent_name'] = socket_comms.listen(conn)
        print('> Connected to player:', data['opponent_name'])
        data['state'] = 'connected'
        data['is_turn'] = False
        data['team'] = 1
        inform_game_process(data)
    elif data['state'] == 'connected':
        if data['is_turn'] == 'done':
            socket_comms.send(pickle.dumps(data['board']), conn, bytes=True)
            print('> Send board')
            send_board = True
            data['is_turn'] = False
        if not data['is_turn']:
            print('> Waiting to receive new board...')
            data['board'] = pickle.loads(socket_comms.listen(conn, bytes=True))
            print('> Got new board')
            data['is_turn'] = True
            inform_game_process(data)
    elif data['state'] == 'quitting':
        print('> network is quitting')
        break
    time.sleep(0.5)
