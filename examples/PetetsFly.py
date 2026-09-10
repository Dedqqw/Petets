import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -6.5
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # Milliseconds

# Display Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PetetsFly")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32, bold=True)

# --- BASE DIR SETUP ---
# Ensures Python looks for images inside the script's actual directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_asset(path):
    full_path = os.path.join(BASE_DIR, path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Could not find asset at path: {full_path}")
    return full_path

# --- LOAD IMAGE SKINS ---
try:
    BG_IMG = pygame.image.load(load_asset("fotos/Petersbg.png")).convert()
    BG_IMG = pygame.transform.scale(BG_IMG, (SCREEN_WIDTH, SCREEN_HEIGHT))

    BIRD_IMG = pygame.image.load(load_asset("fotos/peddle.png")).convert_alpha()
    BIRD_IMG = pygame.transform.scale(BIRD_IMG, (45, 45))

    PIPE_IMG = pygame.image.load(load_asset("fotos/nick.png")).convert_alpha()
    PIPE_IMG = pygame.transform.scale(PIPE_IMG, (52, 400))

except Exception as e:
    print(f"\n[ASSET ERROR]: {e}\n")
    print("Folder Structure Checklist:")
    print(" └── your_script.py")
    print(" └── fotos/")
    print("      ├── Petetsbg.png")
    print("      ├── peddle.png")
    print("      └── nick.png\n")
    input("Press Enter to exit...")  # Keeps window open so you can read the error
    sys.exit()

PIPE_TOP_IMG = pygame.transform.flip(PIPE_IMG, False, True)


class Bird:
    def __init__(self):
        self.x = 80
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.image = BIRD_IMG
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        rotated_bird = pygame.transform.rotozoom(self.image, -self.velocity * 3, 1)
        surface.blit(rotated_bird, rotated_bird.get_rect(center=self.rect.center))


class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.passed = False

        self.top_rect = PIPE_TOP_IMG.get_rect(bottomleft=(self.x, self.height))
        self.bottom_rect = PIPE_IMG.get_rect(topleft=(self.x, self.height + PIPE_GAP))

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, surface):
        surface.blit(PIPE_TOP_IMG, self.top_rect)
        surface.blit(PIPE_IMG, self.bottom_rect)


def main():
    bird = Bird()
    pipes = []
    score = 0
    last_pipe_time = pygame.time.get_ticks()
    game_over = False

    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_over:
                        bird.flap()
                    else:
                        bird = Bird()
                        pipes.clear()
                        score = 0
                        game_over = False

        if not game_over:
            bird.update()

            if current_time - last_pipe_time > PIPE_FREQUENCY:
                pipes.append(Pipe())
                last_pipe_time = current_time

            for pipe in pipes[:]:
                pipe.update()

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    score += 1

                if pipe.x < -60:
                    pipes.remove(pipe)

                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    game_over = True

            if bird.rect.top <= 0 or bird.rect.bottom >= SCREEN_HEIGHT:
                game_over = True

        screen.blit(BG_IMG, (0, 0))

        for pipe in pipes:
            pipe.draw(screen)

        bird.draw(screen)

        score_surface = font.render(str(score), True, (255, 255, 255))
        screen.blit(score_surface, (SCREEN_WIDTH // 2 - score_surface.get_width() // 2, 30))

        if game_over:
            msg_surface = font.render("PRESS SPACE TO RESTART", True, (255, 255, 255))
            screen.blit(msg_surface, (SCREEN_WIDTH // 2 - msg_surface.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
