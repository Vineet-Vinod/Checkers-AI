from checker import Checker
from board import Board
from random import randrange

class AI():
    # Static Variables
    max_depth = 5

    def __init__(self) -> None:
        self.__num_white = 12
        self.__num_black = 12

        self.__num_white_king = 0
        self.__num_black_king = 0

        self.__board = [[0,-1,0,-1,0,-1,0,-1],
                      [-1,0,-1,0,-1,0,-1,0],
                      [0,-1,0,-1,0,-1,0,-1],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [1,0,1,0,1,0,1,0],
                      [0,1,0,1,0,1,0,1],
                      [1,0,1,0,1,0,1,0]]
        
        self.__move_stack = []
        self.__capture_stack = []
        self.__king_stack = []


    def update_move(self, board: Board) -> None: # Update the AI's copy of the board
        self.__num_black = 0
        self.__num_white = 0
        self.__num_black_king = 0
        self.__num_white_king = 0

        for i in range(8):
            for j in range(8):
                self.__board[i][j] = board.get_piece(j, i)
                
                if 1 == self.__board[i][j]:
                    self.__num_black += 1

                elif 2 == self.__board[i][j]:
                    self.__num_black_king += 1

                elif -1 == self.__board[i][j]:
                    self.__num_white += 1

                elif -2 == self.__board[i][j]:
                    self.__num_white_king += 1


    def get_legal(self, x: int, y: int, color: int) -> list[tuple]: # Return all moves of a Checker that are within the board boundary
        possible_moves = [(x + 1, y - color),
                          (x - 1, y - color)]
        
        if 2 == self.__board[y][x] or -2 == self.__board[y][x]:
            possible_moves.extend([(x + 1, y + color),
                                   (x - 1, y + color)])

        legal = []
        for move in possible_moves:
            if Checker.in_bounds(move):
                legal.append(move)

        return legal
    

    def capturable(self, x: int, y: int, color: int, capture_depth: int) -> list[tuple]: # Return capture chains for the given Checker
        captures = []
        self.promote(x, y) # Promote if possible
        legal_moves = self.get_legal(x, y, color)

        for move in legal_moves:
            if self.__board[move[1]][move[0]] and self.__board[move[1]][move[0]] / color < 0: # Check if an enemy piece is on the target square
                move_x, move_y = move
                if Checker.in_bounds((2 * move_x - x, 2 * move_y - y)) and not self.__board[2 * move_y - y][2 * move_x - x]: # Check if the square after jumping is in bounds and empty
                    self.__board[2 * move_y - y][2 * move_x - x] = self.__board[y][x] # Place the piece on new square
                    capture_chain = self.capturable(2 * move_x - x, 2 * move_y - y, color, capture_depth + 1) # Recursively grow capture chain
                    self.__board[2 * move_y - y][2 * move_x - x] = 0 # Remove piece from new square (post recursion cleanup)

                    if capture_chain: # Add capture chain to list if it exists
                        for cap in capture_chain:
                            chain = [cap[0], x, y] + [i for i in cap[1:]]
                            captures.append(tuple(chain))

                    else: # Add single capture otherwise
                        captures.append((capture_depth, x, y, 2 * move_x - x, 2 * move_y - y))

        self.demote(x, y) # Demote if necessary
        return captures
    

    def possible_captures(self, color: int) -> list[tuple]: # Loop through side's checkers and check for possible captures
        captures = []
        
        for i in range(8):
            for j in range(8):
                if self.__board[i][j] / color > 0:
                    captures.extend(self.capturable(j, i, color, 1))

        return captures

    
    def movable(self, x: int, y: int, color: int) -> list[tuple]: # Return legal moves for given checker
        moves = []
        legal_moves = self.get_legal(x, y, color)

        for move in legal_moves:
            if not self.__board[move[1]][move[0]]:
                moves.append((0, x, y, move[0], move[1]))
        
        return moves
    

    def possible_moves(self, color: int) -> list[tuple]: # Loop through side's checkers and check for possible moves
        moves = []
        
        for i in range(8):
            for j in range(8):
                if self.__board[i][j] / color > 0:
                    moves.extend(self.movable(j, i, color))

        return moves

    
    def get_best_move(self, color: int, depth: int) -> float | tuple: # Return the best move/evaluation of current position
        if depth <= self.max_depth:
            best = float("inf") if color == -1 else float("-inf")
            
            # First check for possible captures and act on that
            captures = self.possible_captures(color)
            if captures:
                best = self.backtrack(captures, color, depth)
            
            # If no captures, look for legal moves
            else:
                moves = self.possible_moves(color)
                if moves:
                    best = self.backtrack(moves, color, depth)

            return best

        else:
            return self.evaluate(color)

    
    def backtrack(self, moves: list[tuple], color: int, depth: int) -> float | tuple: # Implement backtracking algorithm to traverse all decision trees
        best_move = best_eval = float("inf") if color == -1 else float("-inf")

        for move in moves:
            self.__move_stack.append(move)
            self.make_move()
            
            # Update position evaluation based on minimax algorithm
            move_eval = self.get_best_move(-color, depth + 1)
            if move_eval and (move_eval <= best_eval if color == -1 else move_eval >= best_eval):
                best_move = move
                best_eval = move_eval

            self.undo_move()
            self.__move_stack.pop()
        
        return best_eval if depth else best_move # Return best evaluation at every step; at first step, return best move to execute
    

    def evaluate(self, color: int) -> float: # Evaluation function
        # Count difference in pieces; give extra weight to difference in number of kings
        piece_diff = self.__num_black - self.__num_white + 3 * (self.__num_black_king - self.__num_white_king)
        
        # Count number of moves (Having more moves/options - good)
        pos_moves_eval = 0

        pos_moves = self.possible_captures(color)
        if pos_moves:
            pos_moves_eval = len(pos_moves) * 0.55 * color # Give high evaluations to positions with multiple captures

        else:
            pos_moves = self.possible_moves(color)
            if not pos_moves: # If no moves or captures are possible, the game is lost
                pos_moves_eval = float("inf") if color == -1 else float("-inf")
            
            else:
                pos_moves_eval = len(pos_moves) * 0.08 * color # Give low evaluations to positions with moves since on average there are more possible moves than captures
        
        # Calculate central control
        central_control_eval = sum([sum(row[2:6]) for row in self.__board[3:5]]) * 0.2 # Give a medium evaluation for central control
        
        # Calculate opponent's proximity to promotion
        consider_rows = self.__board[1:3] if -1 == color else self.__board[5:7]
        promotion_proximity_eval = sum([-color for row in consider_rows for elem in row if elem == -color]) * 0.45 # Give a high medium weightage to prevent opponent from promoting

        # Evaluation calculation
        evaluation = piece_diff + pos_moves_eval + central_control_eval + promotion_proximity_eval
        return evaluation + randrange(-50, 51) / 715 # Adding some random noise to ensure minor differentiation between 2 "equally good" moves
    

    def make_move(self) -> None: # Execute a move locally to generate new positions during backtracking algorithm
        move = self.__move_stack[-1]
        
        # Execute capture chain
        if move[0]:
            start = 1
            num_moves = move[0]
            while num_moves:
                cap_x, cap_y = (move[start] + move[start + 2]) // 2, (move[start + 1] + move[start + 3]) // 2
                
                self.__capture_stack.append(self.__board[cap_y][cap_x]) # Add captured piece stack to restore non destructively

                if 1 == self.__board[cap_y][cap_x]:
                    self.__num_black -= 1
                elif -1 == self.__board[cap_y][cap_x]:
                    self.__num_white -= 1
                elif 2 == self.__board[cap_y][cap_x]:
                    self.__num_black_king -= 1
                elif -2 == self.__board[cap_y][cap_x]:
                    self.__num_white_king -= 1
                
                self.__board[cap_y][cap_x] = 0
                self.__board[move[start + 3]][move[start + 2]] = self.__board[move[start + 1]][move[start]]
                self.__board[move[start + 1]][move[start]] = 0
                self.promote(move[start + 2], move[start + 3]) # Check and promote as necessary
                
                num_moves -= 1
                start += 2
        
        # Execute normal move otherwise
        else:
            self.__board[move[4]][move[3]] = self.__board[move[2]][move[1]]
            self.__board[move[2]][move[1]] = 0
            self.promote(move[3], move[4]) # Check and promote as necessary
    

    def undo_move(self) -> None: # Undo executed move while unravelling backtracking
        move = self.__move_stack[-1]

        # Undo capture chain
        if move[0]:
            num_moves = move[0]
            start = 2 * (num_moves - 1) + 1
            
            while num_moves:
                self.demote(move[start + 2], move[start + 3]) # Check and demote as necessary
                cap_x, cap_y = (move[start] + move[start + 2]) // 2, (move[start + 1] + move[start + 3]) // 2
                
                self.__board[cap_y][cap_x] = self.__capture_stack.pop() # Restore previously captured piece by popping from stack

                if 1 == self.__board[cap_y][cap_x]:
                    self.__num_black += 1
                elif -1 == self.__board[cap_y][cap_x]:
                    self.__num_white += 1
                elif 2 == self.__board[cap_y][cap_x]:
                    self.__num_black_king += 1
                elif -2 == self.__board[cap_y][cap_x]:
                    self.__num_white_king += 1

                self.__board[move[start + 1]][move[start]] = self.__board[move[start + 3]][move[start + 2]]
                self.__board[move[start + 3]][move[start + 2]] = 0
                
                num_moves -= 1
                start -= 2
        
        # Undo normal move otherwise
        else:
            self.demote(move[3], move[4]) # Check and demote as necessary
            self.__board[move[2]][move[1]] = self.__board[move[4]][move[3]]
            self.__board[move[4]][move[3]] = 0

    
    def promote(self, x, y) -> None: # Promote piece to a king as necessary during backtracking
        if (-1 == self.__board[y][x] and 7 == y) or (1 == self.__board[y][x] and 0 == y):
            self.__board[y][x] *= 2
            self.__king_stack.append((x,y)) # Store promotion square to non-destructively demote while unravelling backtracking


    def demote(self, x, y) -> None: # Check and demote a king as necessary during backtracking
        if self.__king_stack and (x,y) == self.__king_stack[-1] and ((-2 == self.__board[y][x] and 7 == y) or (2 == self.__board[y][x] and 0 == y)):
            self.__king_stack.pop()
            self.__board[y][x] //= 2
