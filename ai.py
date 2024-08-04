"""
TO DO

2. Upload to Github!!!
3. Improve Scoring function
"""

from checker import Checker
from board import Board
from random import randrange

class AI():
    # Static Variables
    max_depth = 5

    def __init__(self):
        self.num_white = 12
        self.num_black = 12

        self.num_white_king = 0
        self.num_black_king = 0

        self.board = [[0,-1,0,-1,0,-1,0,-1],
                      [-1,0,-1,0,-1,0,-1,0],
                      [0,-1,0,-1,0,-1,0,-1],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [1,0,1,0,1,0,1,0],
                      [0,1,0,1,0,1,0,1],
                      [1,0,1,0,1,0,1,0]]
        
        self.move_stack = []
        self.capture_stack = []


    def update_move(self, board: Board):
        self.num_black = 0
        self.num_white = 0

        for i in range(8):
            for j in range(8):
                self.board[i][j] = board.get_piece(j, i)
                
                if self.board[i][j] == 1:
                    self.num_black += 1

                elif self.board[i][j] == 2:
                    self.num_black_king += 1

                elif self.board[i][j] == -1:
                    self.num_white += 1

                elif self.board[i][j] == -2:
                    self.num_white_king += 1


    def get_legal(self, x, y, color):
        possible_moves = [(x + 1, y - color),
                          (x - 1, y - color)]
        
        if self.board[y][x] == 2 or self.board[y][x] == -2:
            possible_moves.extend([(x + 1, y + color),
                                   (x - 1, y + color)])

        legal = []
        for move in possible_moves:
            if Checker.in_bounds(move):
                legal.append(move)

        return legal
    

    def capturable(self, x, y, color, capture_depth):
        captures = []
        self.promote(x, y)
        legal_moves = self.get_legal(x, y, color)

        for move in legal_moves:
            if self.board[move[1]][move[0]] and self.board[move[1]][move[0]] / color < 0:
                move_x, move_y = move
                if Checker.in_bounds((2 * move_x - x, 2 * move_y - y)) and not self.board[2 * move_y - y][2 * move_x - x]:
                    capture_chain = self.capturable(2 * move_x - x, 2 * move_y - y, color, capture_depth + 1)
                    
                    if capture_chain:
                        for cap in capture_chain:
                            chain = [cap[0], x, y] + [i for i in cap[1:]]
                            captures.append(tuple(chain))

                    else:
                        captures.append((capture_depth, x, y, 2 * move_x - x, 2 * move_y - y))

        self.demote(x, y)
        return captures
    

    def possible_captures(self, color):
        captures = []
        
        for i in range(8):
            for j in range(8):
                if self.board[i][j] / color > 0:
                    captures.extend(self.capturable(j, i, color, 1))

        return captures

    
    def movable(self, x, y, color):
        moves = []
        legal_moves = self.get_legal(x, y, color)

        for move in legal_moves:
            if not self.board[move[1]][move[0]]:
                moves.append((0, x, y, move[0], move[1]))
        
        return moves
    

    def possible_moves(self, color):
        moves = []
        
        for i in range(8):
            for j in range(8):
                if self.board[i][j] / color > 0:
                    moves.extend(self.movable(j, i, color))

        return moves

    
    def get_best_move(self, color, depth):
        if depth <= self.max_depth:
            best = float("inf") if color == -1 else float("-inf")
            
            captures = self.possible_captures(color)
            if captures:
                best = self.backtrack(captures, color, depth)
            
            else:
                moves = self.possible_moves(color)
                if moves:
                    best = self.backtrack(moves, color, depth)

            return best

        else:
            return self.evaluate()

    
    def backtrack(self, moves, color, depth):
        best_move = (-1)
        best_eval = float("inf") if color == -1 else float("-inf")

        for move in moves:
            self.move_stack.append(move)
            self.make_move()
            
            move_eval = self.get_best_move(-color, depth + 1)
            if move_eval and (move_eval < best_eval if color == -1 else move_eval > best_eval):
                best_move = move
                best_eval = move_eval

            self.undo_move()
            self.move_stack.pop()
        
        return best_eval if depth else best_move
    

    def evaluate(self):
        piece_diff = self.num_black - self.num_white + 2 * (self.num_black_king - self.num_white_king)
        return piece_diff + randrange(-10, 11) / 35 # Simulating additional constraints
    

    def make_move(self):
        move = self.move_stack[-1]
        
        if move[0]:
            start = 1
            num_moves = move[0]
            while num_moves:
                cap_x, cap_y = (move[start] + move[start + 2]) // 2, (move[start + 1] + move[start + 3]) // 2
                
                self.capture_stack.append(self.board[cap_y][cap_x])

                if self.board[cap_y][cap_x] == 1:
                    self.num_black -= 1
                elif self.board[cap_y][cap_x] == -1:
                    self.num_white -= 1
                elif self.board[cap_y][cap_x] == 2:
                    self.num_black_king -= 1
                elif self.board[cap_y][cap_x] == -2:
                    self.num_white_king -= 1
                
                self.board[cap_y][cap_x] = 0
                self.board[move[start + 3]][move[start + 2]] = self.board[move[start + 1]][move[start]]
                self.board[move[start + 1]][move[start]] = 0
                self.promote(move[start + 2], move[start + 3])
                
                num_moves -= 1
                start += 2
        
        else:
            self.board[move[4]][move[3]] = self.board[move[2]][move[1]]
            self.board[move[2]][move[1]] = 0
            self.promote(move[3], move[4])
    

    def undo_move(self):
        move = self.move_stack[-1]

        if move[0]:
            num_moves = move[0]
            start = 2 * (num_moves - 1) + 1
            
            while num_moves:
                self.demote(move[start + 2], move[start + 3])
                cap_x, cap_y = (move[start] + move[start + 2]) // 2, (move[start + 1] + move[start + 3]) // 2
                
                self.board[cap_y][cap_x] = self.capture_stack.pop()

                if self.board[cap_y][cap_x] == 1:
                    self.num_black += 1
                elif self.board[cap_y][cap_x] == -1:
                    self.num_white += 1
                elif self.board[cap_y][cap_x] == 2:
                    self.num_black_king += 1
                elif self.board[cap_y][cap_x] == -2:
                    self.num_white_king += 1

                self.board[move[start + 1]][move[start]] = self.board[move[start + 3]][move[start + 2]]
                self.board[move[start + 3]][move[start + 2]] = 0
                
                num_moves -= 1
                start -= 2
        
        else:
            self.demote(move[3], move[4])
            self.board[move[2]][move[1]] = self.board[move[4]][move[3]]
            self.board[move[4]][move[3]] = 0

    
    def promote(self, x, y):
        if (self.board[y][x] == -1 and y == 7) or (self.board[y][x] == 1 and y == 0):
            self.board[y][x] *= 2


    def demote(self, x, y):
        if (self.board[y][x] == -2 and y == 7) or (self.board[y][x] == 2 and y == 0):
            self.board[y][x] //= 2
