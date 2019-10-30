import pygame


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
        self.squares[0][3] = 'bqueen' if team == 0 else 'wqueen'
        self.squares[0][-4] = 'bking' if team == 0 else 'wking'
        self.squares[-1][-4] = 'wqueen' if team == 0 else 'bqueen'
        self.squares[-1][3] = 'wking' if team == 0 else 'bking'

    def show_moves(self, x, y):
        piece = self.squares[y][x][1:]
        if piece == 'pawn':  # Show moves for pawn:
            success = False
            first_move = True if y == 6 else False  # Check if pawn on original position.
            # Check if positions are free, if so mark as valid moves.
            # Check front:
            if self.squares[y - 1][x] is None:
                self.squares[y - 1][x] = '-selected'
                if first_move and self.squares[y - 2][x] is None:  # Get extra move.
                    self.squares[y - 2][x] = '-selected'
                success = True
            # Check front left:
            if self.squares[y - 1][x - 1] is not None:
                if x - 1 >= 0 and y - 1 >= 0:
                    if (self.squares[y - 1][x - 1][0] == 'w' and self.team == 1) or (
                            self.squares[y - 1][x - 1][0] == 'b' and self.team == 0):
                        self.squares[y - 1][x - 1] = 's' + self.squares[y - 1][x - 1]
                        success = True
            # Check front right:
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
            else:
                return False

        elif piece == 'bishop':
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

    def deselect(self):
        ''''Deselect all squares marked by prefix 's' or empty squares marked '-selected'.'''
        for y in range(8):
            for x in range(8):
                self.squares[y][x] = None if self.squares[y][x] == '-selected' else self.squares[y][x]
                if self.squares[y][x] is not None:
                    self.squares[y][x] = self.squares[y][x][1:] if self.squares[y][x][0] == 's' else self.squares[y][x]

    def move(self, oldx, oldy, newx, newy):
        ''''Makes a move only if the new location is selected.'''
        if self.squares[newy][newx] is not None:
            if (self.squares[newy][newx] == '-selected' and self.squares[oldy][oldx] != '-selected') or \
                    self.squares[newy][newx][0] == 's':
                self.squares[newy][newx] = self.squares[oldy][oldx]
                self.deselect()
                self.squares[oldy][oldx] = None
                return True
        return False

    @staticmethod
    def get_sprite(piece):
        ''''Getting image of specific piece to blit onto screen.'''
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
                    piece_img, width, height, sel = self.get_sprite(piece)
                    gameDisplay.blit(piece_img, (x + (block_size - width) // 2, y + (block_size - height) // 2))
                    if sel:
                        piece_img, width, height, sel = self.get_sprite('-selected')
                        gameDisplay.blit(piece_img, (x + (block_size - width) // 2, y + (block_size - height) // 2))
                xc += 1
            yc += 1
