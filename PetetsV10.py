import pygame
import random
import sys
import json
import os

# Initialize Pygame
pygame.init()

# ---------------- SETTINGS & DISPLAY ----------------
W, H = 550, 600
FPS = 60
MAX_LIVES = 3

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("PetetsV10")
clock = pygame.time.Clock()

# ---------------- FONTS & COLORS ----------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

title_font = pygame.font.SysFont("arial", 40, bold=True)
font = pygame.font.SysFont("arial", 24)

# ---------------- SAVE SYSTEM ----------------
SAVE_FILE = "save.json"

if not os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "w") as f:
        json.dump({
            "money": 0,
            "owned_skins": ["Peters"],
            "owned_bg": ["Petets"],
            "owned_blocks": ["Sam"],
            "current_skin": "Peters",
            "current_bg": "Petets",
            "current_blocks": "Sam",
            "leaderboard": [],
            "flappy_high_score": 0
        }, f)

with open(SAVE_FILE, "r") as f:
    save = json.load(f)

def save_game():
    with open(SAVE_FILE, "w") as f:
        json.dump(save, f, indent=4)

money = save["money"]
leaderboard = save.get("leaderboard", [])
flappy_high_score = save.get("flappy_high_score", 0)

# ---------------- BASE DIR & ASSET HELPER ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_img(path, size, convert_alpha=True):
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        full_path = os.path.join(sys._MEIPASS, path)
    else:
        full_path = os.path.join(BASE_DIR, path)

    if os.path.exists(full_path):
        img = pygame.image.load(full_path)
        img = img.convert_alpha() if convert_alpha else img.convert()
        return pygame.transform.scale(img, size)
    else:
        surf = pygame.Surface(size)
        surf.fill((200, 50, 50))
        return surf

# ---------------- LOAD IMAGES ----------------
menu_bg = load_img("fotos/anthony.png", (W, H), convert_alpha=False)
good_block_img = load_img("fotos/nota.png", (100, 100))
bad_block_img = load_img("fotos/penmakers.png", (100, 100))
rare_block_img = load_img("fotos/le-bon-bon-lebron-james.png", (100, 100))
heart_img = load_img("fotos/heart.png", (32, 32))
broken_heart_img = load_img("fotos/broken-heart.png", (32, 32))

# Skins
paddle_skins = {
    "Peters": {"img": load_img("fotos/peddle.png", (120, 120)), "price": 0},
    "heil Nick": {"img": load_img("fotos/nick.png", (120, 120)), "price": 50},
    "kian": {"img": load_img("fotos/kain.png", (120, 120)), "price": 100},
    "anthony": {"img": load_img("fotos/anthony.png", (120, 120)), "price": 150},
    "sam": {"img": load_img("fotos/sam.png", (120, 120)), "price": 200},
    "nigel": {"img": load_img("fotos/nigel.png", (120, 120)), "price": 250},
    "OG Emil": {"img": load_img("fotos/og emil.png", (120, 120)), "price": 300}
}
owned_skins = save["owned_skins"]
current_skin = save.get("current_skin", "Peters")

bg_skins = {
    "Petets": {"img": load_img("fotos/Petersbg.png", (W, H), convert_alpha=False), "price": 0},
    "Nick": {"img": load_img("fotos/nick.png", (W, H), convert_alpha=False), "price": 50},
}
owned_bg = save["owned_bg"]
current_bg = save.get("current_bg", "Petets")

block_skins = {
    "Sam": {"img": load_img("fotos/penmakers.png", (100, 100)), "price": 0},
    "heil Nick": {"img": load_img("fotos/nick.png", (100, 100)), "price": 50},
}
owned_blocks = save["owned_blocks"]
current_blocks = save.get("current_blocks", "Sam")

# Pipes for Flappy Game
PIPE_IMG = load_img("fotos/nick.png", (52, 400))
PIPE_TOP_IMG = pygame.transform.flip(PIPE_IMG, False, True)

# ---------------- BUTTON CLASS ----------------
class Button:
    def __init__(self, text, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)
        txt = font.render(self.text, True, BLACK)
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, e):
        return e.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos)

# ---------------- MENU BUTTONS ----------------
play_catch_btn = Button("PLAY CATCH", 175, 180, 200, 45)
play_fly_btn = Button("PLAY FLY", 175, 235, 200, 45)
shop_btn = Button("SHOP", 175, 290, 200, 45)
leader_btn = Button("LEADERBOARD", 175, 345, 200, 45)

back_btn = Button("BACK", 20, 20, 120, 40)
skin_btn = Button("SKINS PEDDLE", 10, 420, 170, 45)
bg_btn = Button("BG SKINS", 370, 420, 170, 45)
blocks_btn = Button("BLOCK SKINS", 190, 420, 170, 45)

# ---------------- GAME STATES ----------------
MENU = "menu"
CATCH_GAME = "catch_game"
FLAPPY_GAME = "flappy_game"
SHOP = "shop"
LEADERBOARD = "leaderboard"
SKINS_BG = "skins_bg"
SKINS_PEDDLE = "skins_peddle"
SKINS_BLOCKS = "skins_blocks"
state = MENU

# ---------------- GAME 1: CATCH OBJECTS ----------------
paddle = paddle_skins[current_skin]["img"].get_rect(midbottom=(W // 2, H - 10))
block = good_block_img.get_rect()
catch_score = 0
lives = MAX_LIVES
fall_speed = 5
block_type = "good"
catch_game_over = False

def spawn_block():
    global block_type
    r = random.random()
    block_type = "rare" if r < 0.01 else "bad" if r < 0.25 else "good"
    img = block_skins[current_blocks]["img"] if block_type == "bad" else (rare_block_img if block_type == "rare" else good_block_img)
    block.width = img.get_width()
    block.height = img.get_height()
    block.x = random.randint(0, W - block.width)
    block.y = 0

def reset_catch_game():
    global catch_score, lives, fall_speed, catch_game_over
    catch_score = 0
    lives = MAX_LIVES
    fall_speed = 5
    catch_game_over = False
    paddle.midbottom = (W // 2, H - 10)
    spawn_block()

# ---------------- GAME 2: FLAPPY BIRD ----------------
GRAVITY = 0.25
FLAP_STRENGTH = -6.5
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500

class Bird:
    def __init__(self):
        self.x = 80
        self.y = H // 2
        self.velocity = 0
        self.image = pygame.transform.scale(paddle_skins[current_skin]["img"], (45, 45))
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
        self.x = W
        self.height = random.randint(100, H - PIPE_GAP - 100)
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

bird = Bird()
pipes = []
flappy_score = 0
last_pipe_time = 0
flappy_game_over = False

def reset_flappy_game():
    global bird, pipes, flappy_score, last_pipe_time, flappy_game_over
    bird = Bird()
    pipes.clear()
    flappy_score = 0
    last_pipe_time = pygame.time.get_ticks()
    flappy_game_over = False

# ---------------- MAIN LOOP ----------------
run = True
while run:
    clock.tick(FPS)
    current_time = pygame.time.get_ticks()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            save_game()
            run = False

        # --- MENU & SHOP EVENTS ---
        if state == MENU:
            if play_catch_btn.clicked(e):
                reset_catch_game()
                state = CATCH_GAME
            elif play_fly_btn.clicked(e):
                reset_flappy_game()
                state = FLAPPY_GAME
            elif shop_btn.clicked(e):
                state = SHOP
            elif leader_btn.clicked(e):
                state = LEADERBOARD

        elif state in (LEADERBOARD, SHOP, SKINS_BG, SKINS_PEDDLE, SKINS_BLOCKS):
            if back_btn.clicked(e) or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                state = SHOP if state in (SKINS_BG, SKINS_PEDDLE, SKINS_BLOCKS) else MENU
                save_game()

            if state == SHOP:
                if skin_btn.clicked(e): state = SKINS_PEDDLE
                elif bg_btn.clicked(e): state = SKINS_BG
                elif blocks_btn.clicked(e): state = SKINS_BLOCKS

            elif state == SKINS_BG and e.type == pygame.MOUSEBUTTONDOWN:
                y = 180
                for name, bg_item in bg_skins.items():
                    rect = pygame.Rect(120, y, 300, 30)
                    if rect.collidepoint(e.pos):
                        if name in owned_bg:
                            current_bg = name
                        elif money >= bg_item["price"]:
                            money -= bg_item["price"]
                            owned_bg.append(name)
                            current_bg = name
                        save.update({"money": money, "owned_bg": owned_bg, "current_bg": current_bg})
                        save_game()
                    y += 40

            elif state == SKINS_PEDDLE and e.type == pygame.MOUSEBUTTONDOWN:
                y = 180
                for name, skin_item in paddle_skins.items():
                    rect = pygame.Rect(120, y, 300, 30)
                    if rect.collidepoint(e.pos):
                        if name in owned_skins:
                            current_skin = name
                        elif money >= skin_item["price"]:
                            money -= skin_item["price"]
                            owned_skins.append(name)
                            current_skin = name
                        save.update({"money": money, "owned_skins": owned_skins, "current_skin": current_skin})
                        save_game()
                    y += 40

            elif state == SKINS_BLOCKS and e.type == pygame.MOUSEBUTTONDOWN:
                y = 180
                for name, block_item in block_skins.items():
                    rect = pygame.Rect(120, y, 300, 30)
                    if rect.collidepoint(e.pos):
                        if name in owned_blocks:
                            current_blocks = name
                        elif money >= block_item["price"]:
                            money -= block_item["price"]
                            owned_blocks.append(name)
                            current_blocks = name
                        save.update({"money": money, "owned_blocks": owned_blocks, "current_blocks": current_blocks})
                        save_game()
                    y += 40

        # --- CATCH GAME EVENTS ---
        elif state == CATCH_GAME:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    state = MENU
                elif catch_game_over and e.key == pygame.K_r:
                    reset_catch_game()

        # --- FLAPPY GAME EVENTS ---
        elif state == FLAPPY_GAME:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    state = MENU
                elif e.key == pygame.K_SPACE:
                    if not flappy_game_over:
                        bird.flap()
                    else:
                        reset_flappy_game()

    # ---------------- GAME LOGIC ----------------
    if state == CATCH_GAME and not catch_game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: paddle.x -= 8
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: paddle.x += 8
        paddle.x = max(0, min(W - paddle.width, paddle.x))

        block.y += fall_speed

        if block.colliderect(paddle):
            if block_type == "good":
                catch_score += 1
                fall_speed += 0.3
            elif block_type == "rare":
                catch_score += 10
            elif block_type == "bad":
                lives -= 1
            spawn_block()

        if block.y > H:
            if block_type != "bad":
                lives -= 1
            spawn_block()

        if lives <= 0:
            catch_game_over = True
            money += catch_score
            leaderboard.append(catch_score)
            leaderboard.sort(reverse=True)
            leaderboard[:] = leaderboard[:5]
            save.update({"money": money, "leaderboard": leaderboard})
            save_game()

    elif state == FLAPPY_GAME and not flappy_game_over:
        bird.update()

        if current_time - last_pipe_time > PIPE_FREQUENCY:
            pipes.append(Pipe())
            last_pipe_time = current_time

        for pipe in pipes[:]:
            pipe.update()

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                flappy_score += 1

            if pipe.x < -60:
                pipes.remove(pipe)

            if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                flappy_game_over = True

        if bird.rect.top <= 0 or bird.rect.bottom >= H:
            flappy_game_over = True

        if flappy_game_over:
            money += flappy_score
            if flappy_score > flappy_high_score:
                flappy_high_score = flappy_score
            save.update({"money": money, "flappy_high_score": flappy_high_score})
            save_game()

    # ---------------- RENDERING ----------------
    if state == MENU:
        screen.blit(menu_bg, (0, 0))
        title_txt = title_font.render("PETETS GAMES", True, BLACK)
        screen.blit(title_txt, title_txt.get_rect(center=(W // 2, 110)))
        play_catch_btn.draw()
        play_fly_btn.draw()
        shop_btn.draw()
        leader_btn.draw()
        screen.blit(font.render(f"Money: {money}", True, BLACK), (10, 10))

    elif state == SHOP:
        screen.blit(menu_bg, (0, 0))
        title_txt = title_font.render("SHOP", True, BLACK)
        screen.blit(title_txt, title_txt.get_rect(center=(W // 2, 120)))
        blocks_btn.draw()
        skin_btn.draw()
        back_btn.draw()
        bg_btn.draw()
        screen.blit(font.render(f"Money: {money}", True, BLACK), (W - 150, 20))

    elif state == SKINS_PEDDLE:
        screen.blit(menu_bg, (0, 0))
        screen.blit(title_font.render("PADDLE SKINS", True, BLACK), (W // 2 - 130, 100))
        y = 180
        for name, skin_item in paddle_skins.items():
            status = "SELECTED" if name == current_skin else ("OWNED" if name in owned_skins else f"{skin_item['price']} coins")
            screen.blit(font.render(f"{name.upper()} - {status}", True, BLACK), (120, y))
            y += 40
        back_btn.draw()

    elif state == SKINS_BG:
        screen.blit(menu_bg, (0, 0))
        screen.blit(title_font.render("BG SKINS", True, BLACK), (W // 2 - 90, 100))
        y = 180
        for name, bg_item in bg_skins.items():
            status = "SELECTED" if name == current_bg else ("OWNED" if name in owned_bg else f"{bg_item['price']} coins")
            screen.blit(font.render(f"{name.upper()} - {status}", True, BLACK), (120, y))
            y += 40
        back_btn.draw()

    elif state == SKINS_BLOCKS:
        screen.blit(menu_bg, (0, 0))
        screen.blit(title_font.render("BLOCK SKINS", True, BLACK), (W // 2 - 130, 100))
        y = 180
        for name, block_item in block_skins.items():
            status = "SELECTED" if name == current_blocks else ("OWNED" if name in owned_blocks else f"{block_item['price']} coins")
            screen.blit(font.render(f"{name.upper()} - {status}", True, BLACK), (120, y))
            y += 40
        back_btn.draw()

    elif state == LEADERBOARD:
        screen.blit(menu_bg, (0, 0))
        screen.blit(title_font.render("TOP SCORES (CATCH)", True, BLACK), (W // 2 - 180, 100))
        y = 180
        for i, s in enumerate(leaderboard):
            screen.blit(font.render(f"{i + 1}. {s}", True, BLACK), (230, y))
            y += 40
        back_btn.draw()

    elif state == CATCH_GAME:
        screen.blit(bg_skins[current_bg]["img"], (0, 0))
        screen.blit(paddle_skins[current_skin]["img"], paddle)
        active_block_img = block_skins[current_blocks]["img"] if block_type == "bad" else (rare_block_img if block_type == "rare" else good_block_img)
        screen.blit(active_block_img, block)

        for i in range(MAX_LIVES):
            screen.blit(heart_img if i < lives else broken_heart_img, (10 + i * 36, 10))

        screen.blit(font.render(f"Score: {catch_score}", True, BLACK), (W - 140, 10))

        if catch_game_over:
            screen.blit(font.render("GAME OVER", True, RED), (W // 2 - 70, H // 2 - 20))
            screen.blit(font.render("Press 'R' to Restart or ESC for Menu", True, BLACK), (W // 2 - 180, H // 2 + 20))

    elif state == FLAPPY_GAME:
        screen.blit(bg_skins[current_bg]["img"], (0, 0))
        for pipe in pipes:
            pipe.draw(screen)
        bird.draw(screen)

        # In-Game Live Score Display
        score_surface = font.render(f"Score: {flappy_score}", True, WHITE)
        screen.blit(score_surface, (W // 2 - score_surface.get_width() // 2, 20))

        # Flappy Bird Game Over Display
        if flappy_game_over:
            overlay = pygame.Surface((340, 230))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (W // 2 - 170, H // 2 - 115))

            over_txt = title_font.render("GAME OVER", True, RED)
            curr_score_txt = font.render(f"Score: {flappy_score}", True, WHITE)
            best_score_txt = font.render(f"Best Score: {flappy_high_score}", True, WHITE)
            coins_txt = font.render(f"+{flappy_score} Coins Earned!", True, (255, 215, 0))
            restart_txt = font.render("SPACE to Restart | ESC for Menu", True, GRAY)

            screen.blit(over_txt, over_txt.get_rect(center=(W // 2, H // 2 - 80)))
            screen.blit(curr_score_txt, curr_score_txt.get_rect(center=(W // 2, H // 2 - 30)))
            screen.blit(best_score_txt, best_score_txt.get_rect(center=(W // 2, H // 2 + 5)))
            screen.blit(coins_txt, coins_txt.get_rect(center=(W // 2, H // 2 + 40)))
            screen.blit(restart_txt, restart_txt.get_rect(center=(W // 2, H // 2 + 80)))

    pygame.display.update()

pygame.quit()
sys.exit()