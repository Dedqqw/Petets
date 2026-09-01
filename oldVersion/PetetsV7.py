import pygame
import sys
import random
import json
import os

pygame.init()

# ---------------- SETTINGS ----------------
W, H = 550, 550
FPS = 60
MAX_LIVES = 3

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("PetetsV6")
clock = pygame.time.Clock()

# ---------------- SAVE SYSTEM ----------------
SAVE_FILE = "save.json"

if not os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "w") as f:
        json.dump({
            "money": 0,
            "owned_skins": ["Peters"],
            "owned_bg": ["Petets"],
            "current_skin": "Peters",
            "current_bg": "Petets",
            "leaderboard": []
        }, f)

with open(SAVE_FILE, "r") as f:
    save = json.load(f)

def save_game():
    with open(SAVE_FILE, "w") as f:
        json.dump(save, f, indent=4)

# ---------------- COLORS ----------------
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GRAY = (200,200,200)

# ---------------- FONTS ----------------
title_font = pygame.font.SysFont("arial", 48)
font = pygame.font.SysFont("arial", 26)

# ---------------- STATES ----------------
MENU = "menu"
GAME = "game"
SHOP = "shop"
LEADERBOARD = "leaderboard"
SKINS_BG = "skins_bg"
SKINS_PEDDLE = "skins_peddle"
state = MENU

# ---------------- MONEY ----------------
money = save["money"]

# ---------------- LEADERBOARD ----------------
leaderboard = save["leaderboard"]

# ---------------- LOAD IMAGES ----------------
#bg_skins = {
   # "default": pygame.transform.scale(pygame.image.load("fotos/Petersbg.png"), (W, H)),
   # "space": pygame.transform.scale(pygame.image.load("fotos/nick.png"), (W, H)),
    #"forest": pygame.transform.scale(pygame.image.load("bg_forest.png"), (W, H))
#}

#current_bg = save["current_bg"]

good_block_img = pygame.transform.scale(pygame.image.load("fotos/nota.png"), (100,100))
bad_block_img = pygame.transform.scale(pygame.image.load("fotos/penmakers.png"), (100,100))
rare_block_img = pygame.transform.scale(pygame.image.load("fotos/le-bon-bon-lebron-james.png"), (100,100))

heart_img = pygame.transform.scale(pygame.image.load("fotos/heart.png"), (32,32))
broken_heart_img = pygame.transform.scale(pygame.image.load("fotos/broken-heart.png"), (32,32))

# ---------------- SKINS ----------------
paddle_skins = {
    "Peters": {"img": pygame.transform.scale(pygame.image.load("fotos/peddle.png").convert_alpha(), (120,120)), "price": 0},
    "heil Nick": {"img": pygame.transform.scale(pygame.image.load("fotos/nick.png").convert_alpha(), (120,120)), "price": 50},
    "kian": {"img": pygame.transform.scale(pygame.image.load("fotos/kain.png").convert_alpha(), (120,120)), "price": 100},
    "anthony": {"img": pygame.transform.scale(pygame.image.load("fotos/anthony.png").convert_alpha(), (120,120)), "price": 150},
    "sam": {"img": pygame.transform.scale(pygame.image.load("fotos/sam.png").convert_alpha(), (120,120)), "price": 200},
    "nigel": {"img": pygame.transform.scale(pygame.image.load("fotos/nigel.png").convert_alpha(), (120,120)), "price": 250},
    "OG Emil": {"img": pygame.transform.scale(pygame.image.load("fotos/og emil.png").convert_alpha(), (120,120)), "price": 300}
}

owned_skins = save["owned_skins"]
current_skin = save["current_skin"]

bg_skins= {
        "Petets": {"img": pygame.transform.scale(pygame.image.load("fotos/Petersbg.png").convert_alpha(), (550,550)), "price": 0},
        "Nick": {"img": pygame.transform.scale(pygame.image.load("fotos/nick.png").convert_alpha(), (550,550)), "price":50},

}
owned_bg = save["owned_bg"]
current_bg = save["current_bg"]


# ---------------- BUTTON CLASS ----------------
class Button:
    def __init__(self, text, x, y, w, h):
        self.rect = pygame.Rect(x,y,w,h)
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)
        txt = font.render(self.text, True, BLACK)
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, e):
        return e.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos)
    
   


# ---------------- BUTTONS ----------------
play_btn = Button("PLAY", 175, 200, 200, 50)
shop_btn = Button("SHOP", 175, 260, 200, 50)
leader_btn = Button("LEADERBOARD", 175, 320, 200, 50)
back_btn = Button("BACK", 20, 20, 120, 40)
skin_btn = Button("SKINS PEDDLE", 40, 260, 200, 40)
bg_btn = Button("BG SKINS", 320, 260, 140, 40 )

# ---------------- GAME OBJECTS ----------------
paddle = paddle_skins[current_skin]["img"].get_rect(midbottom=(W//2, H-10))
#bg = bg_skins[current_skin]["img"].get_rect(midbottom=(W//2, H-10))
block = good_block_img.get_rect()

score = 0
lives = MAX_LIVES
fall_speed = 5
block_type = "good"
game_over = False

# ---------------- FUNCTIONS ----------------
def spawn_block():
    global block_type
    r = random.random()
    block_type = "rare" if r < 0.01 else "bad" if r < 0.25 else "good"
    block.x = random.randint(0, W-block.width)
    block.y = 0

def reset_game():
    global score, lives, fall_speed, game_over
    score = 0
    lives = MAX_LIVES
    fall_speed = 5
    game_over = False
    paddle.midbottom = (W//2, H-10)
    spawn_block()

def skin_button(x, y, w, h, text, selected=False):
    color = (150, 255, 150) if selected else GRAY
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, rect)
    txt = font.render(text, True, BLACK)
    screen.blit(txt, txt.get_rect(center=rect.center))
    return rect
reset_game()

# ---------------- MAIN LOOP ----------------
run = True
while run:
    clock.tick(FPS)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            save_game()
            run = False
        if state == LEADERBOARD:
            if back_btn.clicked(e) or e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                state = MENU
                save_game()
        if state == MENU:
            if play_btn.clicked(e):
                reset_game()
                state = GAME
            if shop_btn.clicked(e):
                state = SHOP
            if leader_btn.clicked(e):
                state = LEADERBOARD
            if skin_btn.clicked(e):
                state = SKINS_PEDDLE
            if bg_btn.clicked(e):
                state = SKINS_BG

        elif state == SHOP:
            if skin_btn.clicked(e) or e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                state = SKINS_PEDDLE
                save_game()
            if back_btn.clicked(e) or e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                state = MENU
                save_game()
            if bg_btn.clicked(e):
                state = SKINS_BG
                save_game()

        if state == SKINS_BG:
            if back_btn.clicked(e) or e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                state = SHOP
                save_game()
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                y = 200
                for name, bg  in bg_skins.items():
                    rect = pygame.Rect(120, y, 300, 30)
                    if rect.collidepoint(e.pos):
                        if name in owned_bg:
                            current_bg = name
                        elif money >= bg["price"]:
                            money -= bg["price"]
                            owned_bg.append(name)
                            current_bg = name
                        save.update({
                            "money": money,
                            "owned_bg": owned_bg,
                            "current_bg": current_bg})
                        save_game()
                    y += 40
        
        if state == SKINS_PEDDLE:
            if back_btn.clicked(e) or e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                state = SHOP
                save_game()
            if e.type == pygame.MOUSEBUTTONDOWN:
                y = 200
                for name, skin in paddle_skins.items():
                    rect = pygame.Rect(120, y, 300, 30)
                    if rect.collidepoint(e.pos):
                        if name in owned_skins:
                            current_skin = name
                        elif money >= skin["price"]:
                            money -= skin["price"]
                            owned_skins.append(name)
                            current_skin = name
                        save.update({
                            "money": money,
                            "owned_skins": owned_skins,
                            "current_skin": current_skin
                        })
                        save_game()
                    y += 40
                
           
        
        

            #if e.type == pygame.MOUSEBUTTONDOWN:
             #   y = 200
              #  for name, skin in paddle_skins.items():
               #     rect = pygame.Rect(120, y, 300, 30)
                #    if rect.collidepoint(e.pos):
                 #       if name in owned_skins:
                  #          current_skin = name
                   #     elif money >= skin["price"]:
                    #        money -= skin["price"]
                     #       owned_skins.append(name)
                      #      current_skin = name
                       # save.update({
                        #    "money": money,
                         #   "owned_skins": owned_skins,
                          #  "current_skin": current_skin
                        #})
                        #save_game()
                    #y += 40
            #if e.type == pygame.MOUSEBUTTONDOWN:
             #   
              #  y += 20
               # for name, bg  in bg_skins.items():
                #    rect = pygame.Rect(120, y, 300, 30)
                 #   if rect.collidepoint(e.pos):
                  #      if name in owned_bg:
                   #         current_bg = name
                    #    elif money >= bg["price"]:
                     #       money -= bg["price"]
                      #      owned_bg.append(name)
                       #     current_bg = name
                        #save.update({
                         #   "money": money,
                          #  "owned_bg": owned_bg,
                           # "current_bg": current_bg})
                        #save_game()
                    #y += 40
                       # current_bg = bg
                        #save["current_bg"] = current_bg
                        #save_game()
                    #y += 40
       # elif state == GAME:
        #    if game_over and e.type == pygame.KEYDOWN:
         #       if e.key == pygame.K_r:
          #          save["money"] = money
           #         save_game()
            #        reset_game()

        elif state == GAME:
           if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
               if game_over and e.type == pygame.KEYDOWN:
                   if e.key == pygame.K_r:
                       
                        save["money"] = money
                        save_game()
                        reset_game()
                        
                    
              
               state = MENU

    # ---------------- GAME LOGIC ----------------
    if state == GAME and not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: paddle.x -= 8
        if keys[pygame.K_d]: paddle.x += 8
        paddle.x = max(0, min(W-paddle.width, paddle.x))

        block.y += fall_speed

        if block.colliderect(paddle):
            if block_type == "good":
                score += 1
                fall_speed += 0.3
                spawn_block()
            elif block_type == "rare":
                score += 10
                spawn_block()
            elif block_type == "bad":
                lives -= 1
                fall_speed -= 1
                spawn_block()

        if block.y > H:
            if block_type !="bad":
                lives-=1
                fall_speed -=1
            spawn_block()

        if lives <= 0:
            game_over = True
            money += score
            leaderboard.append(score)
            leaderboard.sort(reverse=True)
            leaderboard[:] = leaderboard[:5]
            save.update({"money": money, "leaderboard": leaderboard})
            save_game()

    # ---------------- DRAW ----------------
    screen.fill(WHITE)

    if state == MENU:
        screen.blit(title_font.render("     Petets", True, BLACK), (W//2-110, 120))
        play_btn.draw()
        shop_btn.draw()
        leader_btn.draw()
        screen.blit(font.render(f"Money: {money}", True, BLACK), (10,10))

    elif state == SHOP:
        screen.blit(title_font.render("SHOP", True, BLACK), (W//2-60, 120))
        
        skin_btn.draw()
        back_btn.draw()
        bg_btn.draw()

    elif state == SKINS_PEDDLE:
        screen.blit(title_font.render("SKINS", True, BLACK), (W//2-60, 120))

        y = 200
        for name, skin in paddle_skins.items():
            if name == current_skin:
                status = "SELECTED"
            elif name in owned_skins:
                status = "OWNED"
            else:
                status = f"{skin['price']} coins"
            text = f"{name.upper()} - {status}"
            #owned = "OWNED" if name in owned_skins else f"{skin['price']} coins"
            screen.blit(font.render(text, True, BLACK), (120,y))
            y += 40
            back_btn.draw()

    elif state == SKINS_BG:
        screen.blit(title_font.render("SKINS", True ,BLACK),(W//2-60, 120))
        y = 200
        for name, bg in bg_skins.items():
            if name == current_bg:
                status = "SELECTED"
            elif name in owned_bg:
                status = "OWNED"
            else:
                status = f"{bg['price']} coins"
            
            text = f"{name.upper()} - {status}"
            #owned = "OWNED" if name in owned_bg else f"{bg['price']} coins"
            screen.blit(
                    font.render(text,  True, BLACK), (120,y))
            y += 40
    
            back_btn.draw()

    elif state == LEADERBOARD:
        screen.blit(title_font.render("TOP SCORES", True, BLACK), (W//2-120, 120))
        y = 200
        for i, s in enumerate(leaderboard):
            screen.blit(font.render(f"{i+1}. {s}", True, BLACK), (240,y))
            y += 40
        back_btn.draw()

    elif state == GAME:
        screen.blit(bg_skins[current_bg]["img"], (0,0))
        screen.blit(paddle_skins[current_skin]["img"], paddle)
        screen.blit(good_block_img if block_type=="good" else bad_block_img if block_type=="bad" else rare_block_img, block)

        for i in range(MAX_LIVES):
            screen.blit(heart_img if i < lives else broken_heart_img, (10+i*36,10))

        screen.blit(font.render(f"Score: {score}", True, BLACK), (W-140,10))

        if game_over:
            screen.blit(font.render("GAME OVER", True, RED), (W//2-90, H//2))

    pygame.display.update()

pygame.quit()
sys.exit()

