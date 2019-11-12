import socket_comms
import pickle
import time


def inform_game_process(data):
    with open('status.dat', 'wb') as f:
        f.write(pickle.dumps(data))


def get_status_from_game_process():
    with open('status.dat', 'rb') as f:
        return pickle.loads(f.read())


while True:
    data = get_status_from_game_process()
    print(data)
    send_board = False
    if data['state'] == 'host waiting':
        data['opponent_name'], conn = socket_comms.host_game(data['HOST'], data['PORT'])
        time.sleep(1)
        socket_comms.send(data['player_name'], conn)
        data['state'] = 'connected'
        data['is_turn'] = True
        data['team'] = 0
        inform_game_process(data)
    elif data['state'] == 'joining':
        conn = socket_comms.connect(data['HOST'], data['PORT'], data['player_name'])
        data['opponent_name'] = socket_comms.listen(conn)
        data['state'] = 'connected'
        data['is_turn'] = False
        data['team'] = 1
        inform_game_process(data)
    elif data['state'] == 'connected':
        if not data['is_turn'] and not send_board:
            socket_comms.send(pickle.dumps(data['board']), conn, bytes=True)
            send_board = True
        if not data['is_turn'] and send_board:
            data['board'] = pickle.loads(socket_comms.listen(conn, bytes=True))
            data['is_turn'] = True
            inform_game_process(data)
    time.sleep(1)