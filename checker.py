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

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.negative_color = tuple([(not i) * 255 for i in self.color])


    def draw(self, WIN): # Draw Checker
        pygame.draw.circle(WIN, self.color, ((self.x * self.sqr_size + self.offset), (self.y * self.sqr_size + self.offset)), self.radius)
        pygame.draw.circle(WIN, self.negative_color, ((self.x * self.sqr_size + self.offset), (self.y * self.sqr_size + self.offset)), self.radius + 1, 2)


    def get_pos(self): # Return Checker Position
        return (self.x, self.y)
    

    def get_color(self): # Return Checker Color
        if self.color == self.white:
            return 0
        return 1
    

    def move(self, idx): # Move Checker
        self.x = idx[0]
        self.y = idx[1]


    def get_legal(self): # Get checker's legal moves 
        y_delta = -1 if self.get_color() else 1
        possible_moves = [(self.x + 1, self.y + y_delta),
                          (self.x - 1, self.y + y_delta)]

        legal = []
        for move in possible_moves:
            if self.in_bounds(move):
                legal.append(move)

        return legal


    def convert(self): # Promote the checker to a king
        if self.id == 1 and ((self.y == 7 and self.color == self.white) or (self.y == 0 and self.color == self.black)):
            king = King(self.x, self.y, self.color)
            return king
        
        return self
    

    def get_id(self): # Get Piece ID
        return self.id * (1 if self.get_color() else -1)

    
    @staticmethod
    def in_bounds(coordinates): # Check if a checker is in the board
        if coordinates[0] < 8 and coordinates[0] >= 0 and coordinates[1] < 8 and coordinates[1] >= 0:
            return True
        return False


class King(Checker):
    # Static Variables
    id = 2
    red = (255,0,0)

    def __init__(self, x, y, color):
        super().__init__(x, y, color)


    def draw(self, WIN): # Draw King
        super().draw(WIN)
        text = STAT_FONT.render("K", 1, self.red)
        WIN.blit(text, ((self.x * self.sqr_size + 30), (self.y * self.sqr_size + 15)))


    def get_legal(self): # Get King's legal moves
        possible_moves = [(self.x + 1, self.y + 1),
                          (self.x + 1, self.y - 1),
                          (self.x - 1, self.y + 1),
                          (self.x - 1, self.y - 1)]

        legal = []
        for move in possible_moves:
            if self.in_bounds(move):
                legal.append(move)

        return legal
