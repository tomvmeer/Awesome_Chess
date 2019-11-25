import pygame
import copy


class Grid:
    def __init__(self, team):
        self.team = team
        self.squares = [[None for i in range(8)] for i in range(8)]  # Create empty board.
        for i in range(8):  # Put pawns in place:
            self.squares[1][i] = 'bpawn' if team == 0 else 'wpawn'
            self.squares[-2][i] = 'wpawn' if team == 0 else 'bpawn'
        cs = ['b', 'w'] if team == 0 else ['w', 'b']
        for i, c in zip([0, -1], cs):  # Put other pieces in place:
            self.squares[i][0] = c + 'rook'
            self.squares[i][-1] = c + 'rook'
            self.squares[i][1] = c + 'knight'
            self.squares[i][-2] = c + 'knight'
            self.squares[i][2] = c + 'bishop'
            self.squares[i][-3] = c + 'bishop'
        self.squares[0][3] = 'bqueen' if team == 0 else 'wking'
        self.squares[0][-4] = 'bking' if team == 0 else 'wqueen'
        self.squares[-1][3] = 'wqueen' if team == 0 else 'bking'
        self.squares[-1][-4] = 'wking' if team == 0 else 'bqueen'
        self.highlighted = None
        self.checked = None

        self.first_move = {'rook_left': True, 'rook_right': True, 'king': True}

    def show_moves(self, x, y):
        piece = self.squares[y][x][1:]
        if piece == 'pawn':  # Show moves for pawn:
            success = False
            first_move = True if y == 6 else False  # Check if pawn on original position.
            # Check if positions are free, if so mark as valid moves.
            # Check front:
            if y - 1 >= 0:
                if self.squares[y - 1][x] is None:
                    self.squares[y - 1][x] = '-selected'
                    if first_move and self.squares[y - 2][x] is None:  # Get extra move.
                        self.squares[y - 2][x] = '-selected'
                    success = True
            # Check front left:
            if y - 1 >= 0 and x - 1 >= 0:
                if self.squares[y - 1][x - 1] is not None:
                    if x - 1 >= 0 and y - 1 >= 0:
                        if (self.squares[y - 1][x - 1][0] == 'w' and self.team == 1) or (
                                self.squares[y - 1][x - 1][0] == 'b' and self.team == 0):
                            self.squares[y - 1][x - 1] = 's' + self.squares[y - 1][x - 1]
                            success = True
            # Check front right:
            if y - 1 >= 0 and x + 1 <= 7:
                if self.squares[y - 1][x + 1] is not None:
                    if x + 1 < 8 and y - 1 >= 0:
                        if (self.squares[y - 1][x + 1][0] == 'w' and self.team == 1) or (
                                self.squares[y - 1][x + 1][0] == 'b' and self.team == 0):
                            self.squares[y - 1][x + 1] = 's' + self.squares[y - 1][x + 1]
                            success = True
            return success  # True if a valid move could be found for this piece, otherwise false.

        elif piece == 'rook':  # Show moves for rook:
            ver, hor = self.vert_check(x, y), self.hor_check(x, y)
            if ver or hor:
                return True
            return False

        elif piece == 'bishop':
            return self.bishop_check(x, y)

        elif piece == 'knight':
            success = False
            if y - 2 >= 0:
                if x + 1 <= 7:
                    if self.squares[y - 2][x + 1] is None:
                        self.squares[y - 2][x + 1] = '-selected'
                        success = True
                    elif (self.squares[y - 2][x + 1][0] == 'b' and self.team == 0) or (
                            self.squares[y - 2][x + 1][0] == 'w' and self.team == 1):
                        self.squares[y - 2][x + 1] = 's' + self.squares[y - 2][x + 1]
                        success = True
                if x - 1 >= 0:
                    if self.squares[y - 2][x - 1] is None:
                        self.squares[y - 2][x - 1] = '-selected'
                        success = True
                    elif (self.squares[y - 2][x - 1][0] == 'b' and self.team == 0) or (
                            self.squares[y - 2][x - 1][0] == 'w' and self.team == 1):
                        self.squares[y - 2][x - 1] = 's' + self.squares[y - 2][x - 1]
                        success = True
            if y + 2 <= 7:
                if x + 1 <= 7:
                    if self.squares[y + 2][x + 1] is None:
                        self.squares[y + 2][x + 1] = '-selected'
                        success = True
                    elif (self.squares[y + 2][x + 1][0] == 'b' and self.team == 0) or (
                            self.squares[y + 2][x + 1][0] == 'w' and self.team == 1):
                        self.squares[y + 2][x + 1] = 's' + self.squares[y + 2][x + 1]
                        success = True
                if x - 1 >= 0:
                    if self.squares[y + 2][x - 1] is None:
                        self.squares[y + 2][x - 1] = '-selected'
                        success = True
                    elif (self.squares[y + 2][x - 1][0] == 'b' and self.team == 0) or (
                            self.squares[y + 2][x - 1][0] == 'w' and self.team == 1):
                        self.squares[y + 2][x - 1] = 's' + self.squares[y + 2][x - 1]
                        success = True
            if x + 2 <= 7:
                if y - 1 >= 0:
                    if self.squares[y - 1][x + 2] is None:
                        self.squares[y - 1][x + 2] = '-selected'
                        success = True
                    elif (self.squares[y - 1][x + 2][0] == 'b' and self.team == 0) or (
                            self.squares[y - 1][x + 2][0] == 'w' and self.team == 1):
                        self.squares[y - 1][x + 2] = 's' + self.squares[y - 1][x + 2]
                        success = True
                if y + 1 <= 7:
                    if self.squares[y + 1][x + 2] is None:
                        self.squares[y + 1][x + 2] = '-selected'
                        success = True
                    elif (self.squares[y + 1][x + 2][0] == 'b' and self.team == 0) or (
                            self.squares[y + 1][x + 2][0] == 'w' and self.team == 1):
                        self.squares[y + 1][x + 2] = 's' + self.squares[y + 1][x + 2]
                        success = True
            if x - 2 >= 0:
                if y - 1 >= 0:
                    if self.squares[y - 1][x - 2] is None:
                        self.squares[y - 1][x - 2] = '-selected'
                        success = True
                    elif (self.squares[y - 1][x - 2][0] == 'b' and self.team == 0) or (
                            self.squares[y - 1][x - 2][0] == 'w' and self.team == 1):
                        self.squares[y - 1][x - 2] = 's' + self.squares[y - 1][x - 2]
                        success = True
                if y + 1 <= 7:
                    if self.squares[y + 1][x - 2] is None:
                        self.squares[y + 1][x - 2] = '-selected'
                        success = True
                    elif (self.squares[y + 1][x - 2][0] == 'b' and self.team == 0) or (
                            self.squares[y + 1][x - 2][0] == 'w' and self.team == 1):
                        self.squares[y + 1][x - 2] = 's' + self.squares[y + 1][x - 2]
                        success = True
            return success

        elif piece == 'queen':
            ver, hor, bish = self.vert_check(x, y), self.hor_check(x, y), self.bishop_check(x, y)
            if ver or hor or bish:
                return True
            return False

        elif piece == 'king':
            success = False
            for yi in [1, -1, 0]:
                for xi in [1, -1, 0]:
                    if y + yi >= 0 and y + yi <= 7 and x + xi >= 0 and x + xi <= 7:
                        if self.squares[y + yi][x + xi] is None:
                            self.squares[y + yi][x + xi] = '-selected'
                            success = True
                        elif (self.squares[y + yi][x + xi][0] == 'b' and self.team == 0) or (
                                self.squares[y + yi][x + xi][0] == 'w' and self.team == 1):
                            self.squares[y + yi][x + xi] = 's' + self.squares[y + yi][x + xi]
                            success = True
            if len(self.castling()) > 0:
                for direction in self.castling():
                    if direction == 'left':
                        self.squares[y][x - 2] = '-selected'
                        success = True
                    if direction == 'right':
                        self.squares[y][x + 2] = '-selected'
                        success = True

            return success

    def bishop_check(self, x, y):
        success = False
        # Forward left:
        for i in range(1, 8):
            if x - i < 0 or y - i < 0:
                break
            if self.squares[y - i][x - i] is None:
                self.squares[y - i][x - i] = '-selected'
                success = True
            elif (self.squares[y - i][x - i][0] == 'b' and self.team == 0) or (
                    self.squares[y - i][x - i][0] == 'w' and self.team == 1):
                self.squares[y - i][x - i] = 's' + self.squares[y - i][x - i]
                success = True
                break
            else:
                break
        # Forward right:
        for i in range(1, 8):
            if x + i > 7 or y - i < 0:
                break
            if self.squares[y - i][x + i] is None:
                self.squares[y - i][x + i] = '-selected'
                success = True
            elif (self.squares[y - i][x + i][0] == 'b' and self.team == 0) or (
                    self.squares[y - i][x + i][0] == 'w' and self.team == 1):
                self.squares[y - i][x + i] = 's' + self.squares[y - i][x + i]
                success = True
                break
            else:
                break
        # Backward left:
        for i in range(1, 8):
            if x - i < 0 or y + i > 7:
                break
            if self.squares[y + i][x - i] is None:
                self.squares[y + i][x - i] = '-selected'
                success = True
            elif (self.squares[y + i][x - i][0] == 'b' and self.team == 0) or (
                    self.squares[y + i][x - i][0] == 'w' and self.team == 1):
                self.squares[y + i][x - i] = 's' + self.squares[y + i][x - i]
                success = True
                break
            else:
                break
        # Backward right:
        for i in range(1, 8):
            if x + i > 7 or y + i > 7:
                break
            if self.squares[y + i][x + i] is None:
                self.squares[y + i][x + i] = '-selected'
                success = True
            elif (self.squares[y + i][x + i][0] == 'b' and self.team == 0) or (
                    self.squares[y + i][x + i][0] == 'w' and self.team == 1):
                self.squares[y + i][x + i] = 's' + self.squares[y + i][x + i]
                success = True
                break
            else:
                break
        return success  # True if a valid move could be found for this piece, otherwise false.

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

    def castling(self):
        castle_to = []
        left_unmoved = False
        right_unmoved = False
        left_free = 0
        right_free = 0

        if self.first_move['king'] and self.first_move['rook_right']:
            right_unmoved = True
        if self.first_move['king'] and self.first_move['rook_left']:
            left_unmoved = True

        if self.team == 1:
            for x in range(1, 3):
                if self.squares[7][x] is not None and self.squares[7][x] != '-selected':
                    left_free += 1
            for x in range(4, 7):
                if self.squares[7][x] is not None and self.squares[7][x] != '-selected':
                    right_free += 1

            if left_unmoved == True and left_free == 0:
                no_check = True
                for x in range(1, 3):
                    move_king = Grid(self.team)
                    move_king.squares = copy.deepcopy(self.squares)
                    move_king.squares[7][x] = move_king.squares[7][3]
                    move_king.squares[7][3] = None
                    move_king.check_check()
                    if move_king.checked != None:
                        no_check = False
                if no_check:
                    castle_to.append('left')

            if right_unmoved == True and right_free == 0:
                no_check = True
                for x in range(4, 7):
                    move_king = Grid(self.team)
                    move_king.squares = copy.deepcopy(self.squares)
                    move_king.squares[7][x] = move_king.squares[7][3]
                    move_king.squares[7][3] = None
                    move_king.check_check()
                    if move_king.checked != None:
                        no_check = False
                if no_check:
                    castle_to.append('right')
            return castle_to

        elif self.team == 0:
            for x in range(1, 4):
                if self.squares[7][x] is not None and self.squares[7][x] != '-selected':
                    left_free += 1
            for x in range(5, 7):
                if self.squares[7][x] is not None and self.squares[7][x] != '-selected':
                    right_free += 1

            if left_unmoved == True and left_free == 0:
                no_check = True
                for x in range(1, 4):
                    move_king = Grid(self.team)
                    move_king.squares = copy.deepcopy(self.squares)
                    move_king.squares[7][x] = move_king.squares[7][4]
                    move_king.squares[7][4] = None
                    move_king.check_check()
                    if move_king.checked != None:
                        no_check = False
                if no_check:
                    castle_to.append('left')

            if right_unmoved == True and right_free == 0:
                no_check = True
                for x in range(5, 7):
                    move_king = Grid(self.team)
                    move_king.squares = copy.deepcopy(self.squares)
                    move_king.squares[7][x] = move_king.squares[7][4]
                    move_king.squares[7][4] = None
                    move_king.check_check()
                    if move_king.checked != None:
                        no_check = False
                if no_check:
                    castle_to.append('right')
            return castle_to

    def deselect(self):
        ''''Deselect all squares marked by prefix 's' or empty squares marked '-selected'.'''
        for y in range(8):
            for x in range(8):
                self.squares[y][x] = None if self.squares[y][x] == '-selected' else self.squares[y][x]
                if self.squares[y][x] is not None:
                    self.squares[y][x] = self.squares[y][x][1:] if self.squares[y][x][0] == 's' else self.squares[y][x]

    def move(self, oldx, oldy, newx, newy):
        ''''Makes a move only if the new location is selected.'''
        piece = self.squares[oldy][oldx][1:]
        if self.squares[newy][newx] is not None:
            if (self.squares[newy][newx] == '-selected' and self.squares[oldy][oldx] != '-selected') or \
                    self.squares[newy][newx][0] == 's':
                self.squares[newy][newx] = self.squares[oldy][oldx]
                self.deselect()
                position = ''
                if piece in ['rook', 'king']:
                    if oldx == 0:
                        position = '_left'
                    if oldx == 7:
                        position = '_right'
                    self.first_move[piece + position] = False
                self.squares[oldy][oldx] = None
                print('checking castling: ', oldx, newx, piece)
                if piece == 'king' and newx == oldx + 2:
                    self.squares[7][newx - 1] = self.squares[7][7]
                    self.squares[7][7] = None
                if piece == 'king' and newx == oldx - 2:
                    self.squares[7][newx + 1] = self.squares[7][0]
                    self.squares[7][0] = None

                return True
        return False

    @staticmethod
    def get_sprite(piece):
        ''''Getting image of specific piece to blit onto screen.'''
        sel = False
        high = False
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
        elif piece == '-selected':
            color = 'black'  # team color of selection indicator doesnt matter.
            piece = piece[1:]
        elif piece == '-highlighted':
            color = 'black'  # team color of hover indicator doesnt matter.
            piece = piece[1:]
        elif piece[0] == 'h':
            color = 'black' if piece[1] == 'b' else 'white'
            piece = piece[2:]
            high = True
        elif piece == 'checked':
            color = 'black'  # team color of check indicator doesnt matter.
        img = pygame.image.load(f'pieces/{color}/{piece}.png')
        width, height = img.get_rect().size
        return img, width, height, sel, high

    def draw_board(self, gameDisplay, display_width, display_height):
        ''''Draw the pieces onto the board based on the state of the squares.'''
        board = pygame.image.load('board.png')
        gameDisplay.blit(board, (0, 0))
        block_size = display_width // 8
        yc = 0
        for y in range(0, display_height, block_size):
            xc = 0
            for x in range(0, display_width, block_size):
                piece = self.squares[yc][xc]
                if piece:
                    piece_img, width, height, sel, high = self.get_sprite(piece)
                    gameDisplay.blit(piece_img, (x + (block_size - width) // 2, y + (block_size - height) // 2))
                    if sel:
                        piece_img, width, height, sel, high = self.get_sprite('-selected')
                        gameDisplay.blit(piece_img, (x + (block_size - width) // 2, y + (block_size - height) // 2))
                    if high:
                        piece_img, width, height, sel, high = self.get_sprite('-highlighted')
                        gameDisplay.blit(piece_img, (x + (block_size - width) // 2, y + (block_size - height) // 2))
                if [yc, xc] == self.checked:
                    piece_img, width, height, sel, high = self.get_sprite('checked')
                    gameDisplay.blit(piece_img, (x + (block_size - width) // 2, y + (block_size - height) // 2))
                xc += 1
            yc += 1

    def remove_highlight(self):
        # Removing old highlighted square:
        for ys in range(8):
            for xs in range(8):
                if self.squares[xs][ys]:
                    if self.squares[xs][ys] == '-highlighted':
                        self.squares[xs][ys] = None
                    elif self.squares[xs][ys][0] == 'h':
                        self.squares[xs][ys] = self.squares[xs][ys][1:]

    def highlight_moves(self, x, y):
        # Calculating highlighted square:
        opponent_team = 0 if self.team == 1 else 1
        opponent_grid = Grid(opponent_team)
        opponent_grid.squares = [[k for k in reversed(i)] for i in reversed(self.squares)]
        if self.squares[y][x]:
            if ('b' == self.squares[y][x][0] and self.team == 0) or (
                    'w' == self.squares[y][x][0] and self.team == 1):
                if opponent_grid.show_moves(7 - x, 7 - y):
                    moves = [[k for k in reversed(i)] for i in reversed(opponent_grid.squares)]
                    for y in range(8):
                        for x in range(8):
                            if moves[y][x] is not None:
                                if moves[y][x] == '-selected':
                                    self.squares[y][x] = '-highlighted'
                                    self.highlighted = [y, x]
                                if moves[y][x][0] == 's':
                                    self.squares[y][x] = 'h' + moves[y][x][1:]
                                    self.highlighted = [y, x]

    def check_check(self):
        self.checked = None
        for ys in range(8):
            for xs in range(8):
                self.highlight_moves(xs, ys)
        color = 'w' if self.team == 0 else 'b'
        for y in range(8):
            for x in range(8):
                if self.squares[y][x] == 'h' + color + 'king':
                    self.checked = [y, x]
        self.remove_highlight()
