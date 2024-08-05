import pygame

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 30)

class Checker:
    # Static Variables
    radius = 25
    id = 1
    sqr_size = 80
    offset = 40
    white = (255,255,255)
    black = (0,0,0)

    def __init__(self, x: int, y: int, color: tuple) -> None:
        self.x = x
        self.y = y
        self.__color = color
        self.__negative_color = tuple([(not i) * 255 for i in self.__color])


    def draw(self, WIN: pygame.Surface) -> None: # Draw Checker
        pygame.draw.circle(WIN, self.__color, ((self.x * self.sqr_size + self.offset), (self.y * self.sqr_size + self.offset)), self.radius)
        pygame.draw.circle(WIN, self.__negative_color, ((self.x * self.sqr_size + self.offset), (self.y * self.sqr_size + self.offset)), self.radius + 1, 2)


    def get_pos(self) -> tuple: # Return Checker Position
        return (self.x, self.y)
    

    def get_color(self) -> int: # Return Checker Color
        if self.white == self.__color:
            return 0
        return 1
    

    def move(self, idx: tuple) -> None: # Move Checker
        self.x = idx[0]
        self.y = idx[1]


    def get_legal(self) -> list[tuple]: # Get checker's legal moves 
        y_delta = -1 if self.get_color() else 1
        possible_moves = [(self.x + 1, self.y + y_delta),
                          (self.x - 1, self.y + y_delta)]

        legal = []
        for move in possible_moves:
            if self.in_bounds(move):
                legal.append(move)

        return legal


    def convert(self) -> 'Checker': # Promote the checker to a king
        if 1 == self.id and ((7 == self.y and self.white == self.__color) or (0 == self.y and self.black == self.__color)):
            king = King(self.x, self.y, self.__color)
            return king
        
        return self
    

    def get_id(self) -> int: # Get Piece ID
        return self.id * (1 if self.get_color() else -1)

    
    @staticmethod
    def in_bounds(coordinates: tuple) -> bool: # Check if a checker is in the board
        if coordinates[0] < 8 and coordinates[0] >= 0 and coordinates[1] < 8 and coordinates[1] >= 0:
            return True
        return False


class King(Checker):
    # Static Variables
    id = 2
    red = (255,0,0)

    def __init__(self, x: int, y: int, color: int) -> None:
        super().__init__(x, y, color)


    def draw(self, WIN: pygame.Surface) -> None: # Draw King
        super().draw(WIN)
        text = STAT_FONT.render("K", 1, self.red)
        WIN.blit(text, ((self.x * self.sqr_size + 30), (self.y * self.sqr_size + 15)))


    def get_legal(self) -> list[tuple]: # Get King's legal moves
        possible_moves = [(self.x + 1, self.y + 1),
                          (self.x + 1, self.y - 1),
                          (self.x - 1, self.y + 1),
                          (self.x - 1, self.y - 1)]

        legal = []
        for move in possible_moves:
            if self.in_bounds(move):
                legal.append(move)

        return legal
