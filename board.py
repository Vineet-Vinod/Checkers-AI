import pygame
from collections import defaultdict
from checker import Checker

class Board:
    # Static Variables
    sqr_size = 80
    dark = (118,150,86)
    light = (238,238,210)
    black = (0,0,0)
    white = (255,255,255)
    highlight = (192,192,192)
    board_size = 8
    dark_squares = []
    
    colors = [(255,0,0),
                (0,255,0),
                (0,0,255),
                (0,255,255),
                (255,255,0),
                (255,0,255)
                ]
    
    def __init__(self) -> None:
        self.capture_highlight = True
        self.last_capture = 0
        self.num_white = 12
        self.num_black = 12
        
        self.moves = []
        self.capture_moves = defaultdict(list)
        self.capture = False
        self.radius = 25
        self.selection = ()

        self.board = [[0,-1,0,-1,0,-1,0,-1],
                      [-1,0,-1,0,-1,0,-1,0],
                      [0,-1,0,-1,0,-1,0,-1],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [1,0,1,0,1,0,1,0],
                      [0,1,0,1,0,1,0,1],
                      [1,0,1,0,1,0,1,0]]
        
        self.mapping = defaultdict(Checker)
        for i in range(8):
            for j in range(8):
                if self.board[j][i] == -1:
                    self.mapping[(i,j)] = Checker(i, j, self.white)
                elif self.board[j][i] == 1:
                    self.mapping[(i,j)] = Checker(i, j, self.black)

        for i in range(4):
            for j in range(4):
                self.dark_squares.append((2 * i * self.sqr_size, (2 * j + 1) * self.sqr_size, self.sqr_size, self.sqr_size))
                self.dark_squares.append(((2 * i + 1) * self.sqr_size, 2 * j * self.sqr_size, self.sqr_size, self.sqr_size))


    def draw(self, WIN: pygame.Surface) -> None:
        WIN.fill(self.light)
        
        for square in self.dark_squares:
            pygame.draw.rect(WIN, self.dark, square)

        for i in range(8):
            for j in range(8):
                if self.board[i][j]:
                    self.mapping[(j,i)].draw(WIN)

        idx = 0
        if not self.selection and self.capture and self.capture_highlight:
            for capturer in self.capture_moves.keys():
                for pos in self.capture_moves[capturer]:
                    pygame.draw.circle(WIN, self.colors[idx], ((capturer[0] * 80 + 40), (capturer[1] * 80 + 40)), self.radius - 10)
                    pygame.draw.circle(WIN, self.colors[idx], ((pos[0] * 80 + 40), (pos[1] * 80 + 40)), self.radius)
                
                idx += 1

        else:
            for move in self.moves:
                pygame.draw.circle(WIN, self.highlight, ((move[0] * 80 + 40), (move[1] * 80 + 40)), self.radius)


    def pos_to_idx(self, x: int, y: int) -> tuple:
        return (x // self.sqr_size, y // self.sqr_size)
    

    def get_color(self, x: int, y: int) -> int:
        x_idx, y_idx = self.pos_to_idx(x, y)
        if (x_idx, y_idx) in self.mapping:
            return self.mapping[(x_idx, y_idx)].get_color()
        return -1
    

    def get_legal(self, x: int, y: int) -> None:
        x_idx, y_idx = self.pos_to_idx(x, y)
        self.selection = (x_idx, y_idx)

        if self.capture:
            for move in self.capture_moves[self.selection]:
                self.moves.append(move)
            if len(self.moves) == 0:
                self.selection = ()

        else:        
            legal_moves = self.mapping[self.selection].get_legal()
            for move in legal_moves:
                if move not in self.mapping:
                    self.moves.append(move)


    def clear_highlight(self) -> None:
        self.moves.clear()
        self.selection = ()
        self.capture_highlight = True


    def toggle_capture_highlight(self) -> None:
        self.capture_highlight = not self.capture_highlight
        self.clear_highlight()


    def in_legal(self, x: int, y: int) -> bool:
        return self.pos_to_idx(x, y) in self.moves
    

    def move(self, x: int, y: int) -> None:
        piece = self.mapping[self.selection]
        cur_pos = piece.get_pos()
        self.board[cur_pos[1]][cur_pos[0]] = 0

        piece.move(self.pos_to_idx(x, y))
        self.mapping.pop(self.selection, None)
        piece = piece.convert()
        cur_pos = piece.get_pos()
        self.mapping[cur_pos] = piece

        self.board[cur_pos[1]][cur_pos[0]] = 1 if piece.get_color() else -1
        self.last_capture += 1

    
    def capturable(self, piece: Checker) -> bool:
        ret_val = False
        x_idx, y_idx = piece.get_pos()
        moves = piece.get_legal()

        for move in moves:
            if move in self.mapping and self.mapping[move].get_color() != piece.get_color():
                move_x, move_y = move
                if Checker.in_bounds((2 * move_x - x_idx, 2 * move_y - y_idx)) and (2 * move_x - x_idx, 2 * move_y - y_idx) not in self.mapping:
                    self.capture_moves[(x_idx, y_idx)].append((2 * move_x - x_idx, 2 * move_y - y_idx))
                    ret_val = True

        self.capture = ret_val
        return ret_val
                    

    def captures(self, color: int) -> bool:
        ret_val = False
        for piece in self.mapping.values():
            if piece.get_color() == color:
                if self.capturable(piece):
                    ret_val = True

        self.capture = ret_val
        return ret_val
    

    def capture_piece(self, x: int, y: int) -> Checker:
        piece = self.mapping[self.selection]
        cur_pos = piece.get_pos()
        self.board[cur_pos[1]][cur_pos[0]] = 0

        capture_x = (cur_pos[0] + x // self.sqr_size) // 2
        capture_y = (cur_pos[1] + y // self.sqr_size) // 2
        if self.board[capture_y][capture_x] == 1:
            self.num_black -= 1 
        else:
            self.num_white -= 1

        self.mapping.pop((capture_x, capture_y), None)
        self.board[capture_y][capture_x] = 0

        piece.move(self.pos_to_idx(x, y))
        self.mapping.pop(self.selection, None)
        piece = piece.convert()
        cur_pos = piece.get_pos()
        self.mapping[cur_pos] = piece

        self.board[cur_pos[1]][cur_pos[0]] = 1 if piece.get_color() else -1

        self.capture_moves.clear()
        self.selection = ()
        self.capture = False
        self.last_capture = 0
        return piece
    

    def game_not_over(self, color: int) -> bool:
        if self.num_black == 0 or self.num_white == 0 or not self.can_move(color) or self.last_capture > 80:
            return False
        
        return True


    def winner(self) -> str:
        if self.num_black == 0 or not self.can_move(1):
            return "White"
        
        elif self.num_white == 0 or not self.can_move(0):
            return "Black"

        return "No One"
    

    def movable(self, piece: Checker) -> bool:
        ret_val = False
        moves = piece.get_legal()

        for move in moves:
            if move not in self.mapping:
                ret_val = True
                break

        return ret_val
                    

    def can_move(self, color: int) -> bool:
        ret_val = False
        for piece in self.mapping.values():
            if piece.get_color() == color and self.movable(piece):
                    ret_val = True
                    break

        return ret_val
    

    def get_piece(self, x: int, y: int) -> int:
        if (x,y) in self.mapping:
            return self.mapping[(x,y)].get_id()
        
        return 0


    def make_ai_move(self, move: float | tuple) -> None:
        if not isinstance(move, tuple) or move == (-1,):
            self.num_white = 0
            return
        
        if move[0]:
            start = 1
            num_moves = move[0]
            while num_moves:
                self.selection = (move[start], move[start + 1])
                self.capture_piece(move[start + 2] * self.sqr_size + 10, move[start + 3] * self.sqr_size + 10)
                start += 2
                num_moves -= 1
        else:
            self.selection = (move[1], move[2])
            self.move(move[3] * self.sqr_size + 10, move[4] * self.sqr_size + 10)
