import pygame
import pygame_textinput
import socket_comms as comms
import random
import time
import pickle

black = (0, 0, 0)
gray = (169, 169, 169)
white = (255, 255, 255)


def get_sprite(piece):
    sel = False
    if piece[0] == 'b':
        color = 'black'
        piece = piece[1:]
    elif piece[0] == 'w':
        color = 'white'
        piece = piece[1:]
    elif piece[0] == 's':
        color = 'black' if piece[1] == 'b' else 'white'
        piece = piece[2:]
        sel = True
    elif piece[0] == '-':
        color = 'black'  # color of selection indicator doesnt matter.
        piece = piece[1:]
    img = pygame.image.load(f'pieces/{color}/{piece}.png')
    width, height = img.get_rect().size
    return img, width, height, sel


def get_square_from_click(x, y):
    return x // 100, y // 100


class grid:
    def __init__(self, team):
        self.team = team
        self.squares = [[None for i in range(8)] for i in range(8)]
        for i in range(8):
            self.squares[1][i] = 'bpawn' if team == 0 else 'wpawn'
            self.squares[-2][i] = 'wpawn' if team == 0 else 'bpawn'
        cs = ['b', 'w'] if team == 0 else ['w', 'b']
        for i, c in zip([0, -1], cs):
            self.squares[i][0] = c + 'rook'
            self.squares[i][-1] = c + 'rook'
            self.squares[i][1] = c + 'knight'
            self.squares[i][-2] = c + 'knight'
            self.squares[i][2] = c + 'bishop'
            self.squares[i][-3] = c + 'bishop'
        self.squares[0][3] = 'bqueen' if team == 0 else 'wqueen'
        self.squares[0][-4] = 'bking' if team == 0 else 'wking'
        self.squares[-1][-4] = 'wqueen' if team == 0 else 'bqueen'
        self.squares[-1][3] = 'wking' if team == 0 else 'bking'

    def show_moves(self, x, y):
        piece = self.squares[y][x][1:]
        move = False
        if piece == 'pawn':
            first_move = True if y == 6 else False  # Check if pawn on original position.
            # Check if positions are free, if so mark as valid moves.
            if self.squares[y - 1][x] is None:
                self.squares[y - 1][x] = '-selected'
                if first_move and self.squares[y - 2][x] is None:  # Get extra move.
                    self.squares[y - 2][x] = '-selected'
                return True
            ## Check for none first
            if x - 1 >= 0 and y - 1 >= 0:
                if (self.squares[y - 1][x - 1][0] == 'w' and team == 1) or (
                                self.squares[y - 1][x - 1][0] == 'b' and team == 0):
                    self.squares[y - 1][x - 1] = 's' + self.squares[y - 1][x - 1]
                    move = True
            if x + 1 < 8 and y - 1 >= 0:
                if (self.squares[y - 1][x + 1][0] == 'w' and team == 1) or (
                                self.squares[y - 1][x + 1][0] == 'b' and team == 0):
                    self.squares[y - 1][x + 1] = 's' + self.squares[y - 1][x + 1]
                    move = True
            return move
        elif piece == 'rook':
            ver, hor = self.vert_check(x, y), self.hor_check(x, y)
            if ver or hor:
                return True
            else:
                return False
        elif piece == 'bishop':
            succes = False
            # Forward
            for i in range(1, 8):
                if x - i < 0 or y - i < 0:
                    break
                if self.squares[y - i][x - i] is None:
                    self.squares[y - i][x - i] = '-selected'
                    succes = True
                elif (self.squares[y - i][x - i][0] == 'b' and self.team == 0) or (
                                self.squares[y - i][x - i][0] == 'w' and self.team == 1):
                    self.squares[y - i][x - i] = 's' + self.squares[y - i][x - i]
                    succes = True
                    break
                else:
                    break
            for i in range(1, 8):
                if x + i > 7 or y - i < 0:
                    break
                if self.squares[y - i][x + i] is None:
                    self.squares[y - i][x + i] = '-selected'
                    succes = True
                elif (self.squares[y - i][x + i][0] == 'b' and self.team == 0) or (
                                self.squares[y - i][x + i][0] == 'w' and self.team == 1):
                    self.squares[y - i][x + i] = 's' + self.squares[y - i][x + i]
                    succes = True
                    break
                else:
                    break
            # Backward
            for i in range(1, 8):
                if x - i < 0 or y + i > 7:
                    break
                if self.squares[y + i][x - i] is None:
                    self.squares[y + i][x - i] = '-selected'
                    succes = True
                elif (self.squares[y + i][x - i][0] == 'b' and self.team == 0) or (
                                self.squares[y + i][x - i][0] == 'w' and self.team == 1):
                    self.squares[y + i][x - i] = 's' + self.squares[y + i][x - i]
                    succes = True
                    break
                else:
                    break
            for i in range(1, 8):
                if x + i > 7 or y + i > 7:
                    break
                if self.squares[y + i][x + i] is None:
                    self.squares[y + i][x + i] = '-selected'
                    succes = True
                elif (self.squares[y + i][x + i][0] == 'b' and self.team == 0) or (
                                self.squares[y + i][x + i][0] == 'w' and self.team == 1):
                    self.squares[y + i][x + i] = 's' + self.squares[y + i][x + i]
                    succes = True
                    break
                else:
                    break
            return succes

    def hor_check(self, x, y):
        success = False
        for xpos in range(-1 * (8 - x) - 1, -9, -1):
            if self.squares[y][xpos] is None:
                self.squares[y][xpos] = '-selected'
                success = True
            elif (self.squares[y][xpos][0] == 'b' and self.team == 0) or (
                            self.squares[y][xpos][0] == 'w' and self.team == 1):
                self.squares[y][xpos] = 's' + self.squares[y][xpos]
                success = True
                break
            else:
                break
        for xpos in range(x + 1, 8, 1):
            if self.squares[y][xpos] is None:
                self.squares[y][xpos] = '-selected'
                success = True
            elif (self.squares[y][xpos][0] == 'b' and self.team == 0) or (
                            self.squares[y][xpos][0] == 'w' and self.team == 1):
                self.squares[y][xpos] = 's' + self.squares[y][xpos]
                success = True
                break
            else:
                break
        return success

    def vert_check(self, x, y):
        success = False
        for ypos in range(-1 * (8 - y) - 1, -9, -1):
            if self.squares[ypos][x] is None:
                self.squares[ypos][x] = '-selected'
                success = True
            elif (self.squares[ypos][x][0] == 'b' and self.team == 0) or (
                            self.squares[ypos][x][0] == 'w' and self.team == 1):
                self.squares[ypos][x] = 's' + self.squares[ypos][x]
                success = True
                break
            else:
                break
        for ypos in range(y + 1, 8, 1):
            if self.squares[ypos][x] is None:
                self.squares[ypos][x] = '-selected'
                success = True
            elif (self.squares[ypos][x][0] == 'b' and self.team == 0) or (
                            self.squares[ypos][x][0] == 'w' and self.team == 1):
                self.squares[ypos][x] = 's' + self.squares[ypos][x]
                success = True
                break
            else:
                break
        return success

    def deselect(self):
        for y in range(8):
            for x in range(8):
                self.squares[y][x] = None if self.squares[y][x] == '-selected' else self.squares[y][x]
                if self.squares[y][x] is not None:
                    self.squares[y][x] = self.squares[y][x][1:] if self.squares[y][x][0] == 's' else self.squares[y][x]

    def move(self, oldx, oldy, newx, newy):
        if self.squares[newy][newx] is not None:
            if (self.squares[newy][newx] == '-selected' and self.squares[oldy][oldx] != '-selected') or \
                            self.squares[newy][newx][0] == 's':
                self.squares[newy][newx] = self.squares[oldy][oldx]
                self.deselect()
                self.squares[oldy][oldx] = None
                return True
        return False


def draw_board(game_grid):
    display_width = 800
    display_height = 800

    gameDisplay = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption('Awesome Chess')
    board = pygame.image.load('board.png')
    gameDisplay.blit(board, (0, 0))
    block_size = display_width // 8
    yc = 0
    for y in range(0, display_height, block_size):
        xc = 0
        for x in range(0, display_width, block_size):
            piece = game_grid.squares[yc][xc]
            if piece:
                piece_img, width, height, sel = get_sprite(piece)
                gameDisplay.blit(piece_img, (x + (block_size - width) // 2, y + (block_size - height) // 2))
                if sel:
                    piece_img, width, height, sel = get_sprite('-selected')
                    gameDisplay.blit(piece_img, (x + (block_size - width) // 2, y + (block_size - height) // 2))
            xc += 1
        yc += 1


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
    while not crashed:
        # Handling events:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                crashed = True
            if gamestate == 'playing' and turn:
                if event.type == pygame.MOUSEBUTTONDOWN and not selected and event.button == 1:
                    x, y = event.pos
                    oldx, oldy = get_square_from_click(x, y)
                    if game_grid.squares[oldy][oldx]:
                        if ('w' == game_grid.squares[oldy][oldx][0] and team == 0) or (
                                        'b' == game_grid.squares[oldy][oldx][0] and team == 1):
                            if game_grid.show_moves(oldx, oldy):
                                selected = True
                elif event.type == pygame.MOUSEBUTTONDOWN and selected and event.button == 1:
                    x, y = event.pos
                    newx, newy = get_square_from_click(x, y)
                    if game_grid.move(oldx, oldy, newx, newy):
                        selected = False
                        turn = False
                        game_grid.squares = [i for i in reversed(game_grid.squares)]
                        data = pickle.dumps(game_grid)
                        comms.send(data, conn, bytes=True)
                        # Reverse it back for display on own screen next iteration.
                        game_grid.squares = [i for i in reversed(game_grid.squares)]
                elif event.type == pygame.MOUSEBUTTONDOWN and selected and event.button == 3:
                    game_grid.deselect()
                    selected = False
            elif gamestate == 'playing' and not turn:
                game_grid = pickle.loads(comms.listen(conn, bytes=True))
                turn = True
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

        if pygame.display.get_active():
            # Drawing the screen:
            if gamestate == 'playing':
                draw_board(game_grid)
            elif gamestate == 'waiting':
                draw_wait()
            elif gamestate == 'host_waiting':
                if draw_hosting(events):
                    # team = random.randint(0, 1)
                    team = 0
                    time.sleep(2)
                    comms.send('1' if team == 0 else '0', conn)
                    game_grid = grid(team)
                    gamestate = 'playing'
                    if team == 0:
                        turn = True
                    else:
                        draw_board(game_grid)
            elif gamestate == 'joining':
                if draw_join(events):
                    game_grid = grid(team)
                    time.sleep(2)
                    gamestate = 'playing'
                    if team == 0:
                        turn = True
                    else:
                        draw_board(game_grid)

            pygame.display.update()
            clock.tick(30)

    pygame.quit()
    quit()
