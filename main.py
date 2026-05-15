import pygame
import random
import json
import os
from enum import Enum

# --- CONFIGURAZIONE ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 700
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 100

# Tipi di stato del gioco
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

# Colori
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)

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
    'I': [[(0, 1), (1, 1), (2, 1), (3, 1)],
          [(2, 0), (2, 1), (2, 2), (2, 3)],
          [(0, 2), (1, 2), (2, 2), (3, 2)],
          [(1, 0), (1, 1), (1, 2), (1, 3)]],
    
    'O': [[(0, 0), (1, 0), (0, 1), (1, 1)],
          [(0, 0), (1, 0), (0, 1), (1, 1)],
          [(0, 0), (1, 0), (0, 1), (1, 1)],
          [(0, 0), (1, 0), (0, 1), (1, 1)]],
          
    'T': [[(1, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (2, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (1, 2)],
          [(1, 0), (0, 1), (1, 1), (1, 2)]],
          
    'S': [[(1, 0), (2, 0), (0, 1), (1, 1)],
          [(1, 0), (1, 1), (2, 1), (2, 2)],
          [(1, 1), (2, 1), (0, 2), (1, 2)],
          [(0, 0), (0, 1), (1, 1), (1, 2)]],
          
    'Z': [[(0, 0), (1, 0), (1, 1), (2, 1)],
          [(2, 0), (1, 1), (2, 1), (1, 2)],
          [(0, 1), (1, 1), (1, 2), (2, 2)],
          [(1, 0), (0, 1), (1, 1), (0, 2)]],
          
    'J': [[(0, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (2, 0), (1, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (2, 2)],
          [(1, 0), (1, 1), (0, 2), (1, 2)]],
          
    'L': [[(2, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (1, 2), (2, 2)],
          [(0, 1), (1, 1), (2, 1), (0, 2)],
          [(0, 0), (1, 0), (1, 1), (1, 2)]],
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
        shape = self.shape[self.rotation]
        blocks = []
        for bx, by in shape:
            blocks.append((self.x + bx, self.y + by))
        return blocks

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)

class Tetris:
    def __init__(self):
        self.reset_game()
        self.load_high_scores()

    def reset_game(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_state = GameState.PLAYING
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 500  # ms

    def new_piece(self):
        shape_type = random.choice(list(SHAPES.keys()))
        return Piece(GRID_WIDTH // 2 - 1, 0, shape_type)

    def valid_move(self, piece, dx=0, dy=0, rotation=None):
        if rotation is None:
            rotation = piece.rotation
            
        test_rotation = rotation % len(piece.shape)
        shape = piece.shape[test_rotation]
        
        for bx, by in shape:
            x, y = piece.x + bx + dx, piece.y + by + dy
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
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        if not self.valid_move(self.current_piece):
            self.game_state = GameState.GAME_OVER
            self.update_high_scores()

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y][x] != BLACK for x in range(GRID_WIDTH)):
                lines_to_clear.append(y)
        
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
            self.lines_cleared += 1
        
        # Update score and level
        if lines_to_clear:
            points = [0, 100, 300, 500, 800][len(lines_to_clear)] * self.level
            self.score += points
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 50)

    def update(self):
        if self.game_state == GameState.PLAYING:
            if self.valid_move(self.current_piece, dy=1):
                self.current_piece.y += 1
            else:
                self.lock_piece()

    def move_piece(self, dx):
        if self.game_state == GameState.PLAYING and self.valid_move(self.current_piece, dx=dx):
            self.current_piece.x += dx

    def rotate_piece(self):
        if self.game_state == GameState.PLAYING:
            new_rotation = (self.current_piece.rotation + 1) % len(self.current_piece.shape)
            if self.valid_move(self.current_piece, rotation=new_rotation):
                self.current_piece.rotate()

    def drop_piece(self):
        if self.game_state == GameState.PLAYING:
            while self.valid_move(self.current_piece, dy=1):
                self.current_piece.y += 1
            self.lock_piece()

    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r') as f:
                self.high_scores = json.load(f)
        except FileNotFoundError:
            self.high_scores = []

    def update_high_scores(self):
        self.high_scores.append(self.score)
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:5]  # Keep top 5
        
        with open('high_scores.json', 'w') as f:
            json.dump(self.high_scores, f)

def draw_button(screen, text, rect, color, font):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, WHITE, rect, 2)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return rect

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris Mobile")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    
    game = Tetris()
    fall_time = 0
    
    # Touch control areas
    left_button = pygame.Rect(20, SCREEN_HEIGHT - 150, 80, 80)
    right_button = pygame.Rect(110, SCREEN_HEIGHT - 150, 80, 80)
    rotate_button = pygame.Rect(SCREEN_WIDTH - 190, SCREEN_HEIGHT - 150, 80, 80)
    drop_button = pygame.Rect(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150, 80, 80)
    pause_button = pygame.Rect(SCREEN_WIDTH - 50, 10, 40, 40)
    
    # Button states for visual feedback
    left_pressed = False
    right_pressed = False
    rotate_pressed = False
    drop_pressed = False

    while True:
        delta_time = clock.tick(60)
        fall_time += delta_time

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Game controls
                if left_button.collidepoint(pos):
                    left_pressed = True
                    game.move_piece(-1)
                elif right_button.collidepoint(pos):
                    right_pressed = True
                    game.move_piece(1)
                elif rotate_button.collidepoint(pos):
                    rotate_pressed = True
                    game.rotate_piece()
                elif drop_button.collidepoint(pos):
                    drop_pressed = True
                    game.drop_piece()
                elif pause_button.collidepoint(pos):
                    if game.game_state == GameState.PLAYING:
                        game.game_state = GameState.PAUSED
                    elif game.game_state == GameState.PAUSED:
                        game.game_state = GameState.PLAYING
                
                # Menu/Game Over handling
                if game.game_state in [GameState.MENU, GameState.GAME_OVER]:
                    # We'll handle menu buttons separately
                    
            if event.type == pygame.MOUSEBUTTONUP:
                # Reset button states
                left_pressed = False
                right_pressed = False
                rotate_pressed = False
                drop_pressed = False

        # Game logic
        if game.game_state == GameState.PLAYING and fall_time > game.fall_speed:
            game.update()
            fall_time = 0

        # Drawing
        screen.fill(BLACK)
        
        # Draw grid background
        pygame.draw.rect(screen, DARK_GRAY, 
                         (GRID_OFFSET_X - 5, GRID_OFFSET_Y - 5, 
                          GRID_WIDTH * 30 + 10, GRID_HEIGHT * 30 + 10))
        
        # Draw grid cells
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(screen, game.grid[y][x], 
                               (x * 30 + GRID_OFFSET_X, y * 30 + GRID_OFFSET_Y, 29, 29))
        
        # Draw current piece
        if game.current_piece and game.game_state == GameState.PLAYING:
            for x, y in game.current_piece.get_blocks():
                if y >= 0:
                    pygame.draw.rect(screen, game.current_piece.color, 
                                   (x * 30 + GRID_OFFSET_X, y * 30 + GRID_OFFSET_Y, 29, 29))
        
        # Draw UI elements
        score_text = font.render(f"Score: {game.score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        level_text = font.render(f"Level: {game.level}", True, WHITE)
        screen.blit(level_text, (20, 60))
        
        # Draw next piece preview
        next_text = font.render("Next:", True, WHITE)
        screen.blit(next_text, (SCREEN_WIDTH - 120, 20))
        
        if game.next_piece:
            for x, y in game.next_piece.get_blocks():
                # Adjust position for next piece preview
                px = (x - game.next_piece.x + 0.5) * 20 + SCREEN_WIDTH - 100
                py = (y - game.next_piece.y + 1) * 20 + 60
                pygame.draw.rect(screen, game.next_piece.color, (px, py, 19, 19))
        
        # Draw touch controls
        left_color = GRAY if left_pressed else DARK_GRAY
        right_color = GRAY if right_pressed else DARK_GRAY
        rotate_color = GRAY if rotate_pressed else DARK_GRAY
        drop_color = GRAY if drop_pressed else DARK_GRAY
        
        draw_button(screen, "<", left_button, left_color, font)
        draw_button(screen, ">", right_button, right_color, font)
        draw_button(screen, "↻", rotate_button, rotate_color, font)
        draw_button(screen, "⬇", drop_button, drop_color, font)
        
        # Draw pause/resume button
        pause_symbol = "▶" if game.game_state == GameState.PAUSED else "||"
        draw_button(screen, pause_symbol, pause_button, DARK_GRAY, font)
        
        # Draw game state overlays
        if game.game_state == GameState.PAUSED:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            pause_text = font.render("PAUSED", True, WHITE)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(pause_text, text_rect)
            
        elif game.game_state == GameState.GAME_OVER:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = font.render("GAME OVER", True, WHITE)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            screen.blit(game_over_text, text_rect)
            
            final_score = font.render(f"Score: {game.score}", True, WHITE)
            score_rect = final_score.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(final_score, score_rect)
            
            restart_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 40, 200, 50)
            draw_button(screen, "RESTART", restart_button, DARK_GRAY, font)
            
            # Handle restart button click
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if restart_button.collidepoint(pos):
                    game.reset_game()
        
        pygame.display.flip()

if __name__ == "__main__":
    main()
