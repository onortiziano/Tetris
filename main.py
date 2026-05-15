import pygame
import random
import sys

# --- CONFIGURAZIONE ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 500
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Colori
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Colori Tetrominoes originali (approssimati)
COLORS = {
    'I': (0, 255, 255),   # Cyan
    'O': (255, 255, 0),   # Yellow
    'T': (128, 0, 128),   # Purple
    'S': (0, 255, 0),     # Green
    'Z': (255, 0, 0),     # Red
    'J': (0, 0, 255),     # Blue
    'L': (255, 165, 0),   # Orange
}

# Definizioni Forme (Matrici)
SHAPES = {
    'I': [[(0, 1), (1, 1), (2, 1), (3, 1)]],
    'O': [[(0, 0), (1, 0), (0, 1), (1, 1)]],
    'T': [[(1, 0), (0, 1), (1, 1), (2, 1)]],
    'S': [[(1, 0), (2, 0), (0, 1), (1, 1)]],
    'Z': [[(0, 0), (1, 0), (1, 1), (2, 1)]],
    'J': [[(0, 0), (0, 1), (1, 1), (2, 1)]],
    'L': [[(2, 0), (0, 1), (1, 1), (2, 1)]],
}

class Piece:
    def __init__(self, x, y, shape_type):
        self.x = x
        self.y = y
        self.type = shape_type
        self.color = COLORS[shape_type]
        self.shape = SHAPES[shape_type]
        self.rotation = 0

    def get_blocks(self):
        shape = self.shape[0]
        blocks = []
        for bx, by in shape:
            for _ in range(self.rotation):
                bx, by = -by, bx
            blocks.append((self.x + bx, self.y + by))
        return blocks

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4

class Tetris:
    def __init__(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0

    def new_piece(self):
        shape_type = random.choice(list(SHAPES.keys()))
        return Piece(GRID_WIDTH // 2 - 1, 0, shape_type)

    def valid_move(self, piece, dx=0, dy=0, rotate=False):
        test_piece = Piece(piece.x + dx, piece.y + dy, piece.type)
        test_piece.rotation = piece.rotation + (1 if rotate else 0)
        
        for x, y in test_piece.get_blocks():
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return False
            if y >= 0 and self.grid[y][x] != BLACK:
                return False
        return True

    def lock_piece(self):
        for x, y in self.current_piece.get_blocks():
            if y >= 0:
                self.grid[y][x] = self.current_piece.color
        
        self.clear_lines()
        self.current_piece = self.new_piece()
        
        if not self.valid_move(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y][x] != BLACK for x in range(GRID_WIDTH)):
                lines_to_clear.append(y)
        
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
            self.score += 100

    def update(self):
        if self.valid_move(self.current_piece, dy=1):
            self.current_piece.y += 1
        else:
            self.lock_piece()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python Tetris")
    clock = pygame.time.Clock()
    
    game = Tetris()
    fall_time = 0
    fall_speed = 500 # ms

    while True:
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time > fall_speed:
            game.update()
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if not game.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and game.valid_move(game.current_piece, dx=-1):
                        game.current_piece.x -= 1
                    if event.key == pygame.K_RIGHT and game.valid_move(game.current_piece, dx=1):
                        game.current_piece.x += 1
                    if event.key == pygame.K_DOWN and game.valid_move(game.current_piece, dy=1):
                        game.current_piece.y += 1
                    if event.key == pygame.K_UP and game.valid_move(game.current_piece, rotate=True):
                        game.current_piece.rotate()

        screen.fill(BLACK)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(screen, game.grid[y][x], 
                                 (x*BLOCK_SIZE + 50, y*BLOCK_SIZE + 50, BLOCK_SIZE-1, BLOCK_SIZE-1))
        
        if game.current_piece:
            for x, y in game.current_piece.get_blocks():
                if y >= 0:
                    pygame.draw.rect(screen, game.current_piece.color, 
                                     (x*BLOCK_SIZE + 50, y*BLOCK_SIZE + 50, BLOCK_SIZE-1, BLOCK_SIZE-1))

        font = pygame.font.SysFont('Arial', 24)
        score_text = font.render(f"Score: {game.score}", True, WHITE)
        screen.blit(score_text, (250, 50))

        if game.game_over:
            over_text = font.render("GAME OVER", True, WHITE)
            screen.blit(over_text, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2))

        pygame.display.flip()

if __name__ == "__main__":
    main()
