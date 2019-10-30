import pygame
import pygame_textinput
import socket_comms as comms
import random
import chess
import time
import pickle

black = (0, 0, 0)
gray = (169, 169, 169)
white = (255, 255, 255)


def draw_button(ypos, xpos, width, height, text, gameDisplay):
    edge = pygame.Rect(xpos, ypos, width, height)
    button = pygame.Rect(xpos + 3, ypos + 3, width - 6, height - 6)

    pygame.draw.rect(gameDisplay, black, edge)
    pygame.draw.rect(gameDisplay, gray, button)

    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(text, True, black)
    textRect = text.get_rect()
    textRect.center = (xpos + (width // 2), ypos + (height // 2))
    gameDisplay.blit(text, textRect)


def draw_wait():
    display_width = 800
    display_height = 800
    gameDisplay = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption('Awesome Chess')
    gameDisplay.fill(white)
    draw_button(50, 50, 250, 50, 'Join game', gameDisplay)
    draw_button(125, 50, 250, 50, 'Host game', gameDisplay)


def draw_hosting(events):
    global playername, opponent, conn, HOST
    white = (255, 255, 255)
    display_width = 800
    display_height = 800
    gameDisplay = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption('Awesome Chess')
    gameDisplay.fill(white)
    if textinput.update(events):
        playername = textinput.get_text()
        textinput.clear_text()
    if not playername:
        draw_button(90, 150, 250, 50, '', gameDisplay)
        gameDisplay.blit(textinput.get_surface(), (155, 103))
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render('Enter player name:', True, black)
        textRect = text.get_rect()
        xpos, ypos = 300, 50
        textRect.center = xpos, ypos
        gameDisplay.blit(text, textRect)
    elif not opponent and playername:
        font = pygame.font.Font('freesansbold.ttf', 32)
        HOST = '127.0.0.1'
        text = font.render(f'Waiting, hosting on {HOST}.', True, black)
        textRect = text.get_rect()
        xpos, ypos = 300, 50
        textRect.center = xpos, ypos
        gameDisplay.blit(text, textRect)
        pygame.display.update()
        opponent, conn = comms.host_game(HOST, PORT)
        time.sleep(1)
        comms.send(playername, conn)
    elif opponent and playername:
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render('Playing against: ' + opponent, True, black)
        textRect = text.get_rect()
        xpos, ypos = 300, 50
        textRect.center = xpos, ypos
        gameDisplay.blit(text, textRect)
        pygame.display.update()
        return True


def draw_join(events):
    global playername, opponent, conn, HOST, team
    white = (255, 255, 255)
    display_width = 800
    display_height = 800
    gameDisplay = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption('Awesome Chess')
    gameDisplay.fill(white)
    if textinput.update(events):
        if not playername:
            playername = textinput.get_text()
            textinput.clear_text()
        elif playername and not opponent and not conn:
            HOST = textinput.get_text()
            textinput.clear_text()

    if not playername:
        draw_button(90, 150, 250, 50, '', gameDisplay)
        gameDisplay.blit(textinput.get_surface(), (155, 103))
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render('Enter player name:', True, black)
        textRect = text.get_rect()
        xpos, ypos = 300, 50
        textRect.center = xpos, ypos
        gameDisplay.blit(text, textRect)
    elif not opponent and playername and not conn and not HOST:
        draw_button(90, 150, 250, 50, '', gameDisplay)
        gameDisplay.blit(textinput.get_surface(), (155, 103))
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render('Enter host adres:', True, black)
        textRect = text.get_rect()
        xpos, ypos = 300, 50
        textRect.center = xpos, ypos
        gameDisplay.blit(text, textRect)
    elif not opponent and playername and not conn and HOST:
        conn = comms.connect(HOST, PORT, playername)
        opponent = comms.listen(conn)
        team = int(comms.listen(conn))
    elif opponent and playername and conn:
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render('Playing against: ' + opponent, True, black)
        textRect = text.get_rect()
        xpos, ypos = 300, 50
        textRect.center = xpos, ypos
        gameDisplay.blit(text, textRect)
        pygame.display.update()
        return True


if __name__ == '__main__':
    pygame.init()
    HOST = None
    PORT = 65432
    clock = pygame.time.Clock()
    crashed = False
    conn = None
    turn = False
    gamestate = 'waiting'
    playername = None
    opponent = None
    team = None
    textinput = pygame_textinput.TextInput()
    selected = False
    display_width = 800
    display_height = 800

    gameDisplay = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption('Awesome Chess')

    while not crashed:
        # Handling events:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                crashed = True
            if gamestate == 'playing' and turn:
                # Handling a click on a square to then show available moves:
                if event.type == pygame.MOUSEBUTTONDOWN and not selected and event.button == 1:
                    x, y = event.pos
                    oldx, oldy = x // 100, y // 100
                    if game_grid.squares[oldy][oldx]:
                        if ('w' == game_grid.squares[oldy][oldx][0] and team == 0) or (
                                        'b' == game_grid.squares[oldy][oldx][0] and team == 1):
                            if game_grid.show_moves(oldx, oldy):
                                selected = True
                # Handling a click on a square to move a piece:
                elif event.type == pygame.MOUSEBUTTONDOWN and selected and event.button == 1:
                    x, y = event.pos
                    newx, newy = x // 100, y // 100
                    if game_grid.move(oldx, oldy, newx, newy):
                        selected = False
                        turn = False

                        # Turn is over after a move, sending the state of the board to the opponent.
                        game_grid.squares = [[k for k in reversed(i)] for i in reversed(game_grid.squares)]
                        data = pickle.dumps(game_grid)
                        comms.send(data, conn, bytes=True)
                        # Reverse it back for display on own screen next iteration.
                        game_grid.squares = [[k for k in reversed(i)] for i in reversed(game_grid.squares)]
                # Handling a left click on a square to deselect.
                elif event.type == pygame.MOUSEBUTTONDOWN and selected and event.button == 3:
                    game_grid.deselect()
                    selected = False
            # When it's not our turn, wait until we receive the state of the board:
            elif gamestate == 'playing' and not turn:
                game_grid = pickle.loads(comms.listen(conn, bytes=True))
                turn = True
            # Process clicks in the main menu:
            elif gamestate == 'waiting':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if (x >= 50 and x <= 300) and (y >= 50 and y <= 100):
                        gamestate = 'joining'
                    elif (x >= 50 and x <= 300) and (y >= 125 and y <= 175):
                        gamestate = 'host_waiting'
            elif gamestate == 'host_waiting':
                pass
            elif gamestate == 'joining':
                pass

        if pygame.display.get_active():  # When the application window is open.
            # Drawing the screens:
            if gamestate == 'playing':
                game_grid.draw_board(gameDisplay, display_width, display_height)
            elif gamestate == 'waiting':
                draw_wait()
            elif gamestate == 'host_waiting':
                if draw_hosting(events):  # When the hosting menu is successfully navigated.
                    # team = random.randint(0, 1)
                    team = 0
                    time.sleep(2)
                    comms.send('1' if team == 0 else '0', conn)
                    game_grid = chess.Grid(team)
                    gamestate = 'playing'
                    if team == 0:
                        turn = True
                    else:
                        game_grid.draw_board(gameDisplay, display_width, display_height)
            elif gamestate == 'joining':
                if draw_join(events):  # When the joining menu is successfully navigated.
                    game_grid = chess.Grid(team)
                    time.sleep(2)
                    gamestate = 'playing'
                    if team == 0:
                        turn = True
                    else:
                        game_grid.draw_board(gameDisplay, display_width, display_height)

            pygame.display.update()
            clock.tick(30)

    pygame.quit()
    quit()
