import pygame
import time
from board import Board
from ai import AI

pygame.init()
pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 40)

WIN_WID = WIN_HEIGHT = 640
WIN = pygame.display.set_mode((WIN_WID, WIN_HEIGHT))

board = Board()
ai = AI()

def draw() -> None: # Draw the board and pieces
    board.draw(WIN)
    pygame.display.update()


def main() -> None: # Game loop
    clock = pygame.time.Clock()
    run = True
    end = False
    move = 1 # Change to 0 to play second
    capturable = False

    while run:
        clock.tick(30)
        run = board.game_not_over(move % 2)
        end = not run

        for event in pygame.event.get():
            if pygame.QUIT == event.type: # Close game by hitting top right X button
                run = False
                break
            
            if move % 2: # Get User's Move
                if not capturable: # Checks if any enemy checkers can be captured
                    capturable = board.captures(move % 2)

                if pygame.mouse.get_pressed()[0]: # Get user mouse inputs
                    x, y = pygame.mouse.get_pos()
                    color = board.get_color(x, y)
                
                    if move % 2 == color:
                        if capturable: # Capturing is forced
                            board.toggle_capture_highlight()
                        else: # No possible captures
                            board.clear_highlight()
                        
                        board.get_legal(x, y)
                    
                    else:
                        if board.in_legal(x, y):
                            if capturable: # Any capturing move
                                capturer = board.capture_piece(x, y)
                                board.toggle_capture_highlight()
                                capturable = board.capturable(capturer)
                                if capturable:
                                    move -= 1

                            else: # Any legal move
                                board.move(x, y)
                            
                            board.clear_highlight()
                            move += 1

            else: # AI's move
                ai.update_move(board)
                best_move = ai.get_best_move(-1, 0)
                board.make_ai_move(best_move)
                move += 1

        draw()
        
    if end: # Display Winner at the end of the game and exit
        winner = board.winner().upper()
        text = STAT_FONT.render(f"{winner} IS THE WINNER!", 1, (255, 255, 255) if winner == "WHITE" else (0,0,0))
        WIN.blit(text, (WIN_WID - text.get_width() - (WIN_WID - text.get_width()) // 2, WIN_HEIGHT - text.get_height() - (WIN_HEIGHT - text.get_height()) // 2))
        pygame.display.update()

        time.sleep(5)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()
