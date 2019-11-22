import pygame
import pygame_textinput
import socket_comms as comms
import sys
import random
import chess
import time
import pickle
import os
import socket
import config

black = (0, 0, 0)
gray = (169, 169, 169)
white = (255, 255, 255)
path = config.load_config('app_path')
i = [i for i in range(2) if f'data_{i}.dat' not in os.listdir(path)][0]


class Game:
    def __init__(self):
        pygame.init()
        self.display_width = 800
        self.display_height = 800
        self.display = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption('Awesome Chess')
        self.clock = pygame.time.Clock()
        self.crashed = False
        self.buttons = []

    def handle_quit(self, event):
        if event.type == pygame.QUIT:
            print('> Game is now exiting')
            self.crashed = True
            data = {
                'state': 'quitting'
            }
            self.inform_network_process(data)
            return True
        return False

    def draw_button(self, ypos, xpos, width, height, text):
        edge = pygame.Rect(xpos, ypos, width, height)
        button = pygame.Rect(xpos + 3, ypos + 3, width - 6, height - 6)

        pygame.draw.rect(self.display, black, edge)
        pygame.draw.rect(self.display, gray, button)

        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(text, True, black)
        textRect = text.get_rect()
        textRect.center = (xpos + (width // 2), ypos + (height // 2))
        self.display.blit(text, textRect)

    @staticmethod
    def inform_network_process(data):
        while True:
            try:
                with open(f'data_{i}.dat', 'wb') as f:
                    f.write(pickle.dumps(data))
            except EOFError:
                pass
            else:
                break

    @staticmethod
    def get_status_from_network_process():
        while True:
            try:
                with open(f'data_{i}.dat', 'rb') as f:
                    return pickle.loads(f.read())
            except EOFError:
                pass


class Joining(Game):
    def __init__(self):
        super().__init__()
        print('> Game is now in state: Joining')
        self.state = 0
        self.t = 0
        self.text_input = pygame_textinput.TextInput()
        self.PORT = 65432
        self.player_name, self.opponent_name = None, None

    def draw(self):
        self.display.fill(white)
        if self.state == 0:
            # Drawing textbox:
            self.draw_button(90, 150, 250, 50, '')
            self.display.blit(self.text_input.get_surface(), (155, 103))

            # Drawing text:
            font = pygame.font.Font('freesansbold.ttf', 32)
            text = font.render('Enter player name:', True, black)
            textRect = text.get_rect()
            xpos, ypos = 300, 50
            textRect.center = xpos, ypos
            self.display.blit(text, textRect)
        if self.state == 1:
            # Drawing textbox:
            self.draw_button(90, 150, 250, 50, '')
            self.display.blit(self.text_input.get_surface(), (155, 103))

            # Drawing text:
            font = pygame.font.Font('freesansbold.ttf', 32)
            text = font.render('Enter host adres:', True, black)
            textRect = text.get_rect()
            xpos, ypos = 300, 50
            textRect.center = xpos, ypos
            self.display.blit(text, textRect)
        if self.state == 2 or self.state == 3:
            font = pygame.font.Font('freesansbold.ttf', 32)
            loading_symbols = ['   ', '.  ', '.. ', '...']
            text = font.render(f'Joining "{self.HOST}"{loading_symbols[self.t//10]}', True, black)
            textRect = text.get_rect()
            xpos, ypos = 300, 50
            textRect.center = xpos, ypos
            self.display.blit(text, textRect)
            self.t = self.t + 1 if self.t < 39 else 0
        if self.state == 4:
            font = pygame.font.Font('freesansbold.ttf', 32)
            text = font.render('Playing against: ' + self.opponent_name, True, black)
            textRect = text.get_rect()
            xpos, ypos = 300, 50
            textRect.center = xpos, ypos
            self.display.blit(text, textRect)

    def handle_events(self):
        events = pygame.event.get()
        # Text input handling:
        if self.state == 0:
            if self.text_input.update(events):
                player_name = self.text_input.get_text()
                print('> Got text input:', player_name)
                if player_name != '':
                    self.player_name = player_name
                    self.text_input.clear_text()
                    self.state += 1
        if self.state == 1:
            if self.text_input.update(events):
                HOST = self.text_input.get_text()
                print('> Got text input:', HOST)
                if HOST != '':
                    self.HOST = HOST
                    self.text_input.clear_text()
                    self.state += 1
        # Network event handling:
        if self.state == 2:
            data = {
                'state': 'joining',
                'player_name': self.player_name,
                'HOST': self.HOST,
                'PORT': self.PORT
            }
            self.inform_network_process(data)
            self.state += 1
        if self.state == 3:
            data = self.get_status_from_network_process()
            if data['state'] == 'connected':
                self.opponent_name = data['opponent_name']
                self.state += 1
                self.t = 0
        if self.state == 4:
            self.t += 1
            if self.t == 200:
                print('> Returning playing')
                return Playing()
        # Other event handling:
        for event in events:
            if self.handle_quit(event):
                return


class Hosting(Game):
    def __init__(self):
        super().__init__()
        print('> Game is now in state: Hosting')
        self.state = 0  # 0: Entering player name, 1: Initializing host, 2: Waiting for players, 3: Launching game
        self.text_input = pygame_textinput.TextInput()
        self.t = 0
        self.HOST = '127.0.0.1'
        self.PORT = 65432
        self.player_name, self.opponent_name = None, None

    def draw(self):
        self.display.fill(white)
        if self.state == 0:
            # Drawing textbox:
            self.draw_button(90, 150, 250, 50, '')
            self.display.blit(self.text_input.get_surface(), (155, 103))

            # Drawing text:
            font = pygame.font.Font('freesansbold.ttf', 32)
            text = font.render('Enter player name:', True, black)
            textRect = text.get_rect()
            xpos, ypos = 300, 50
            textRect.center = xpos, ypos
            self.display.blit(text, textRect)
        if self.state == 2:
            font = pygame.font.Font('freesansbold.ttf', 32)
            loading_symbols = ['   ', '.  ', '.. ', '...']
            text = font.render(f'Waiting, hosting on "{self.HOST}"{loading_symbols[self.t//10]}', True, black)
            textRect = text.get_rect()
            xpos, ypos = 300, 50
            textRect.center = xpos, ypos
            self.display.blit(text, textRect)
            self.t = self.t + 1 if self.t < 39 else 0
        if self.state == 3:
            font = pygame.font.Font('freesansbold.ttf', 32)
            text = font.render('Playing against: ' + self.opponent_name, True, black)
            textRect = text.get_rect()
            xpos, ypos = 300, 50
            textRect.center = xpos, ypos
            self.display.blit(text, textRect)

    def handle_events(self):
        events = pygame.event.get()
        # Text input handling:
        if self.state == 0:
            if self.text_input.update(events):
                player_name = self.text_input.get_text()
                print('> Got text input:', player_name)
                if player_name != '':
                    self.player_name = player_name
                    self.text_input.clear_text()
                    self.state += 1
        # Network event handling:
        if self.state == 1:
            data = {
                'state': 'host waiting',
                'player_name': self.player_name,
                'HOST': self.HOST,
                'PORT': self.PORT
            }
            self.inform_network_process(data)
            self.state += 1
        if self.state == 2:
            data = self.get_status_from_network_process()
            if data['state'] == 'connected':
                self.opponent_name = data['opponent_name']
                self.state += 1
                self.t = 0
        if self.state == 3:
            self.t += 1
            if self.t == 200:
                return Playing()
        # Other event handling:
        for event in events:
            if self.handle_quit(event):
                return


class Waiting(Game):
    def __init__(self):
        super().__init__()
        print('> Game is now in state: Waiting')
        data = {
            'state': 'waiting'
        }
        self.inform_network_process(data)

    def draw(self):
        self.display.fill(white)
        self.draw_button(50, 50, 250, 50, 'Join game')
        self.draw_button(125, 50, 250, 50, 'Host game')

    def handle_events(self):
        events = pygame.event.get()
        # Other event handling:
        for event in events:
            if self.handle_quit(event):
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if (x >= 50 and x <= 300) and (y >= 50 and y <= 100):
                    print('> Advance game state to joining')
                    return Joining()
                elif (x >= 50 and x <= 300) and (y >= 125 and y <= 175):
                    print('> Advance game state to hosting')
                    return Hosting()


class Playing(Game):
    def __init__(self):
        super().__init__()
        print('> Game is now in state: Playing')
        data = self.get_status_from_network_process()
        self.turn = data['is_turn']
        self.team = data['team']
        self.player_name, self.opponent_name = data['player_name'], data['opponent_name']
        self.game_grid = chess.Grid(self.team)
        self.selected = False
        data['board'] = [[k for k in reversed(i)] for i in reversed(self.game_grid.squares)]
        self.inform_network_process(data)
        self.display.fill(white)
        pygame.display.set_caption('Awesome Chess, player: ' + self.player_name)
        self.highlighted = None

    def draw(self):
        self.game_grid.draw_board(self.display, self.display_width, self.display_height)

    def handle_events(self):
        events = pygame.event.get()
        # Other event handling:
        for event in events:
            if event.type == pygame.MOUSEMOTION and not self.selected:
                x, y = event.pos
                x, y = x // 100, y // 100
                if [x, y] != self.highlighted:
                    self.highlighted = [x, y]
                    self.game_grid.remove_highlight()
                    self.game_grid.highlight_moves(x, y)

            if self.handle_quit(event):
                return
            if self.turn is True:
                # Handling a click on a square to then show available moves:
                if event.type == pygame.MOUSEBUTTONDOWN and not self.selected and event.button == 1:
                    x, y = event.pos
                    self.oldx, self.oldy = x // 100, y // 100
                    if self.game_grid.squares[self.oldy][self.oldx]:
                        if ('w' == self.game_grid.squares[self.oldy][self.oldx][0] and self.team == 0) or (
                                        'b' == self.game_grid.squares[self.oldy][self.oldx][0] and self.team == 1):
                            if self.game_grid.show_moves(self.oldx, self.oldy):
                                self.selected = True
                # Handling a click on a square to move a piece:
                elif event.type == pygame.MOUSEBUTTONDOWN and self.selected and event.button == 1:
                    x, y = event.pos
                    newx, newy = x // 100, y // 100
                    if self.game_grid.move(self.oldx, self.oldy, newx, newy):
                        self.selected = False
                        self.turn = False
                        print('> Turn is over')
                        self.game_grid.check_check()
                        data = {
                            'is_turn': 'done',
                            'team': self.team,
                            'player_name': self.player_name,
                            'opponent_name': self.opponent_name,
                            'board': [[k for k in reversed(i)] for i in reversed(self.game_grid.squares)],
                            'state': 'connected'
                        }
                        self.inform_network_process(data)
                # Handling a left click on a square to deselect.
                elif event.type == pygame.MOUSEBUTTONDOWN and self.selected and event.button == 3:
                    self.game_grid.deselect()
                    self.selected = False
        # Handling network driven events:
        if not self.turn:
            data = self.get_status_from_network_process()
            if data['is_turn'] is True:
                print('> Update:', data)
                self.turn = True
                self.game_grid.squares = data['board']
                self.game_grid.check_check()


game = Waiting()
while not game.crashed:
    game.draw()
    pygame.display.update()
    changed_state = game.handle_events()
    if changed_state is not None:
        print(changed_state)
        game = changed_state
    game.clock.tick(30)
