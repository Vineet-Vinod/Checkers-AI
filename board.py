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
    radius = 25
    
    colors = [(255,0,0),
                (0,255,0),
                (0,0,255),
                (0,255,255),
                (255,255,0),
                (255,0,255)
                ]
    
    def __init__(self) -> None:
        self.__capture_highlight = True
        self.__last_capture = 0
        self.__num_white = 12
        self.__num_black = 12
        
        self.__moves = []
        self.__capture_moves = defaultdict(list)
        self.__capture = False
        self.__selection = ()

        self.__board = [[0,-1,0,-1,0,-1,0,-1],
                      [-1,0,-1,0,-1,0,-1,0],
                      [0,-1,0,-1,0,-1,0,-1],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [1,0,1,0,1,0,1,0],
                      [0,1,0,1,0,1,0,1],
                      [1,0,1,0,1,0,1,0]]
        
        # Store the checkers' positions in a dictionary for easy retrieval
        self.__mapping = defaultdict(Checker)
        for i in range(8):
            for j in range(8):
                if -1 == self.__board[j][i]:
                    self.__mapping[(i,j)] = Checker(i, j, self.white)
                elif 1 == self.__board[j][i]:
                    self.__mapping[(i,j)] = Checker(i, j, self.black)

        # Store the dark colored squares in a list for drawing
        for i in range(4):
            for j in range(4):
                self.dark_squares.append((2 * i * self.sqr_size, (2 * j + 1) * self.sqr_size, self.sqr_size, self.sqr_size))
                self.dark_squares.append(((2 * i + 1) * self.sqr_size, 2 * j * self.sqr_size, self.sqr_size, self.sqr_size))


    def draw(self, WIN: pygame.Surface) -> None: # Draw board, pieces and move highlighting
        WIN.fill(self.light)
        
        for square in self.dark_squares: # Draw board
            pygame.draw.rect(WIN, self.dark, square)

        # Draw pieces
        for i in range(8):
            for j in range(8):
                if self.__board[i][j]:
                    self.__mapping[(j,i)].draw(WIN)

        # Draw capture/move highlighting
        idx = 0
        if not self.__selection and self.__capture and self.__capture_highlight:
            for capturer in self.__capture_moves.keys():
                for pos in self.__capture_moves[capturer]:
                    pygame.draw.circle(WIN, self.colors[idx], ((capturer[0] * 80 + 40), (capturer[1] * 80 + 40)), self.radius - 10)
                    pygame.draw.circle(WIN, self.colors[idx], ((pos[0] * 80 + 40), (pos[1] * 80 + 40)), self.radius)
                
                idx += 1

        else:
            for move in self.__moves:
                pygame.draw.circle(WIN, self.highlight, ((move[0] * 80 + 40), (move[1] * 80 + 40)), self.radius)


    def pos_to_idx(self, x: int, y: int) -> tuple: # Convert position on board to indices
        return (x // self.sqr_size, y // self.sqr_size)
    

    def get_color(self, x: int, y: int) -> int: # Get the integer code for the checker's color
        x_idx, y_idx = self.pos_to_idx(x, y)
        if (x_idx, y_idx) in self.__mapping:
            return self.__mapping[(x_idx, y_idx)].get_color()
        return -1
    

    def get_legal(self, x: int, y: int) -> None: # Return all legal moves of a checker
        x_idx, y_idx = self.pos_to_idx(x, y)
        self.__selection = (x_idx, y_idx)

        # If a checker can be captured, only include those moves (forced capturing)
        if self.__capture:
            for move in self.__capture_moves[self.__selection]:
                self.__moves.append(move)
            if 0 == len(self.__moves):
                self.__selection = ()
        
        # Any move if capturing is not forced
        else:        
            legal_moves = self.__mapping[self.__selection].get_legal()
            for move in legal_moves:
                if move not in self.__mapping:
                    self.__moves.append(move)


    def clear_highlight(self) -> None: # Clear move highlighting
        self.__moves.clear()
        self.__selection = ()
        self.__capture_highlight = True


    def toggle_capture_highlight(self) -> None: # Toggle between highlighting possible captures
        self.__capture_highlight = not self.__capture_highlight
        self.clear_highlight()


    def in_legal(self, x: int, y: int) -> bool: # Check if user's move is valid
        return self.pos_to_idx(x, y) in self.__moves
    

    def movable(self, piece: Checker) -> bool: # Check if a move is valid
        ret_val = False
        moves = piece.get_legal()

        for move in moves:
            if move not in self.__mapping:
                ret_val = True
                break

        return ret_val
                    

    def can_move(self, color: int) -> bool: # Loop through user's checkers and check for possible moves
        ret_val = False
        for piece in self.__mapping.values():
            if piece.get_color() == color and self.movable(piece):
                ret_val = True
                break

        return ret_val
    

    def move(self, x: int, y: int) -> None: # Execute user's move
        # Set piece's current position to zero
        piece = self.__mapping[self.__selection]
        cur_pos = piece.get_pos()
        self.__board[cur_pos[1]][cur_pos[0]] = 0

        # Move piece to new square and update position dictionary
        piece.move(self.pos_to_idx(x, y))
        self.__mapping.pop(self.__selection, None)
        piece = piece.convert()
        cur_pos = piece.get_pos()
        self.__mapping[cur_pos] = piece

        self.__board[cur_pos[1]][cur_pos[0]] = 1 if piece.get_color() else -1
        self.__last_capture += 1

    
    def capturable(self, piece: Checker) -> bool: # Check for possible captures by a checker and add them to a list
        ret_val = False
        x_idx, y_idx = piece.get_pos()
        moves = piece.get_legal()

        for move in moves:
            if move in self.__mapping and self.__mapping[move].get_color() != piece.get_color():
                move_x, move_y = move
                if Checker.in_bounds((2 * move_x - x_idx, 2 * move_y - y_idx)) and (2 * move_x - x_idx, 2 * move_y - y_idx) not in self.__mapping:
                    self.__capture_moves[(x_idx, y_idx)].append((2 * move_x - x_idx, 2 * move_y - y_idx)) # Add checker's final position post capture to list
                    ret_val = True

        self.__capture = ret_val
        return ret_val
                    

    def captures(self, color: int) -> bool: # Loop through user's checkers and check for possible captures
        ret_val = False
        for piece in self.__mapping.values():
            if piece.get_color() == color:
                if self.capturable(piece):
                    ret_val = True

        self.__capture = ret_val
        return ret_val
    

    def capture_piece(self, x: int, y: int) -> Checker: # Execute user's capture
        # Set current position to zero
        piece = self.__mapping[self.__selection]
        cur_pos = piece.get_pos()
        self.__board[cur_pos[1]][cur_pos[0]] = 0

        # Calculate position of piece to be captured and set it to zero; remove from position dictionary
        capture_x = (cur_pos[0] + x // self.sqr_size) // 2
        capture_y = (cur_pos[1] + y // self.sqr_size) // 2
        if 1 == self.__board[capture_y][capture_x]:
            self.__num_black -= 1 
        else:
            self.__num_white -= 1

        self.__mapping.pop((capture_x, capture_y), None)
        self.__board[capture_y][capture_x] = 0

        # Move piece to new position
        piece.move(self.pos_to_idx(x, y))
        self.__mapping.pop(self.__selection, None)
        piece = piece.convert()
        cur_pos = piece.get_pos()
        self.__mapping[cur_pos] = piece

        self.__board[cur_pos[1]][cur_pos[0]] = 1 if piece.get_color() else -1

        # Clean up board instance variables post capture
        self.__capture_moves.clear()
        self.__selection = ()
        self.__capture = False
        self.__last_capture = 0
        return piece
    

    def game_not_over(self, color: int) -> bool: # Conditions to determine game state
        if 0 == self.__num_black or 0 == self.__num_white or not self.can_move(color) or self.__last_capture > 80:
            return False
        
        return True


    def winner(self) -> str: # Return the winner/indicate it is a draw
        if 0 == self.__num_black or not self.can_move(1):
            return "White"
        
        elif 0 == self.__num_white or not self.can_move(0):
            return "Black"

        return "No One"


    def get_piece(self, x: int, y: int) -> int: # If there's a piece at the given indices, return its ID; else return 0
        if (x,y) in self.__mapping:
            return self.__mapping[(x,y)].get_id()
        
        return 0


    def make_ai_move(self, move: float | tuple) -> None: # Process and execute AI's move
        # Catch all for instance AI provides an illegal move
        if not isinstance(move, tuple):
            self.__num_white = 0
            return
        
        # Execute AI's chain capture if possible
        if move[0]:
            start = 1
            num_moves = move[0]
            while num_moves:
                self.__selection = (move[start], move[start + 1])
                self.capture_piece(move[start + 2] * self.sqr_size + 10, move[start + 3] * self.sqr_size + 10)
                start += 2
                num_moves -= 1

        # Execute AI's regular move
        else:
            self.__selection = (move[1], move[2])
            self.move(move[3] * self.sqr_size + 10, move[4] * self.sqr_size + 10)
