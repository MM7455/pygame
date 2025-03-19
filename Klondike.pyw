import random
import pygame
import copy

pygame.init()
clock = pygame.time.Clock()

font = pygame.font.SysFont("Segoeuisymbol", 20)

info = pygame.display.Info()
screen_WIDTH = info.current_w
screen_HEGIHT = info.current_h

ratio = int(screen_WIDTH/screen_HEGIHT)
WIDTH = screen_WIDTH*0.6
HEIGHT = screen_HEGIHT*0.6/ratio
win = pygame.display.set_mode((WIDTH,HEIGHT), pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("Klondike Solitaire")

CARD_WIDTH = 70
CARD_HEIGHT = 100

GREEN = (0, 128, 0)  
WHITE = (255, 255, 255)  
BLACK = (0, 0, 0)
RED = (255,0,0)

COLOR_DICT = {"♠": BLACK, "♣": BLACK, "♥": RED, "♦": RED}

class Card:
    def __init__(self,suit,rank):
        self.suit = suit
        self.rank = rank
        self.face_up = False
        self.is_red = suit in ["♥", "♦"]
        
    def __repr__(self):
        return f"{self.suit}{self.rank}"
    
class KlondikeGame:
    def __init__(self):
        self.suit = ['♠', '♥', '♦', '♣']
        self.rank = list(range(1,14))
        self.deck = [Card(suit,rank) for suit in self.suit for rank in self.rank]
        self.waste_plie = [[]]
        self.foundation = [[] for _ in range(4)]
        self.selected_card = None
        self.selected_offset = (0, 0)
        self.dragging_pos = None
        random.shuffle(self.deck)
        self.columns = [[] for _ in range(7)]
        for i in range(7):
            for j in range(i + 1):
                card = self.deck.pop()
                if i == j:  
                    card.face_up = True
                self.columns[i].append(card)
        self.draw_plie = self.deck[:]

def check_victory(game):
    total_cards = 52
    foundation_count = sum(len(f) for f in game.foundation)
    if foundation_count == total_cards:
        text = font.render("YOU WIN!", True, (255, 215, 0))  # 金色字体
        win.blit(text, (200, 300))

def licensing(game,mouse_pos):
        licensing_rect = pygame.Rect(50, 50, CARD_WIDTH, CARD_HEIGHT)
        if len(game.draw_plie) == 0:
            licensing1_rect = pygame.Rect(50, 50, CARD_WIDTH, CARD_HEIGHT)
            if licensing1_rect.collidepoint(mouse_pos):
                    game.draw_plie = copy.deepcopy(game.waste_plie[0])
                    game.waste_plie[0] = []
                    random.shuffle(game.draw_plie)
        elif licensing_rect.collidepoint(mouse_pos) and len(game.draw_plie) != 0: #elif与if独立进行
            for _ in range(3):
                if len(game.draw_plie) > 0:
                    card = game.draw_plie.pop()
                    card.face_up = True
                    game.waste_plie[0].append(card) 
            

def handle_mouse_up(game,mouse_pos):
    moved = False
    if game.selected_card:
        col_idx,card_idx,moved_cards = game.selected_card
        if col_idx == "waste_plie": #废牌区交互
            waste_plie_idx = card_idx #1
            original_waste_plie = game.waste_plie[waste_plie_idx] #[♥A, ♥2, ♥3]
            moved_card = moved_cards[0] #也就是 ♥3
            if original_waste_plie and id(original_waste_plie[-1]) == id(moved_card): #original_waste_plie and original_waste_plie[-1] == moved_card: 
                original_waste_plie.pop()
            for target_col_idx, target_column in enumerate(game.columns):
                x = 70 + target_col_idx * (CARD_WIDTH + 65)
                if target_column:
                    y = 200 + (len(target_column) - 1) * 25
                else:    
                    y = 200
                target_rect = pygame.Rect(x,y,CARD_WIDTH,CARD_HEIGHT)
                if target_rect.collidepoint(mouse_pos):
                    if can_place_cards(target_column, moved_cards):
                        target_column.extend(moved_cards)
                        moved = True
                        break
                
                    
            for idx, foundation in enumerate(game.foundation):
                x = 500 + idx * (CARD_WIDTH + 35)  # 回收区坐标
                y = 50
                foundation_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
                if foundation_rect.collidepoint(mouse_pos):
                    if can_place_in_foundation(foundation, moved_cards[0]):  
                        foundation.append(moved_cards[0])  # 只允许放一张牌
                        moved = True
                        break
            # 位置问题位置问题位置问题位置问题位置问题位置问题位置问题
            if not moved:
                if col_idx == "waste_plie":
                    # 确保 foundation 也是合法的
                    if card_idx < len(game.waste_plie):
                        
                            game.waste_plie[card_idx].append(moved_card)
           
        if isinstance(col_idx, int):
            original_column = game.columns[col_idx] #读取索引
            moved_cards = game.selected_card[2] #从card_idx:开始取出牌 
            
            for target_col_idx, target_column in enumerate(game.columns):
                x = 70 + target_col_idx * (CARD_WIDTH + 65)
                if target_column:
                    y = 200 + (len(target_column) - 1) * 25
                else:    
                    y = 200
                target_rect = pygame.Rect(x,y,CARD_WIDTH,CARD_HEIGHT)
                if target_rect.collidepoint(mouse_pos):
                    if can_place_cards(target_column, moved_cards):
                        target_column.extend(moved_cards)
                        del original_column[card_idx:]
                        if original_column:
                            original_column[-1].face_up = True
                        break
            for idx, foundation in enumerate(game.foundation):
                x = 500 + idx * (CARD_WIDTH + 35)  # 回收区坐标
                y = 50
                foundation_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

                if foundation_rect.collidepoint(mouse_pos):
                    if can_place_in_foundation(foundation, moved_cards[0]):  
                        foundation.append(moved_cards[0])  # 只允许放一张牌
                        del original_column[card_idx:]
                        if original_column:
                            original_column[-1].face_up = True
                        break
        
        if col_idx == "foundation": #game.selected_card = ("foundation", 1, [♥3])
            foundation_idx = card_idx #1
            original_foundation = game.foundation[foundation_idx] #[♥A, ♥2, ♥3]
            moved_card = moved_cards[0] #也就是 ♥3
            if original_foundation and original_foundation[-1] == moved_card:  
                original_foundation.pop()
            for idx, foundation in enumerate(game.foundation):
                    x = 500 + idx * (CARD_WIDTH + 35)  # 回收区坐标
                    y = 50
                    foundation_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
                    if foundation_rect.collidepoint(mouse_pos):
                        if can_place_in_foundation(foundation, moved_cards[0]):  
                            foundation.append(moved_cards[0])
                            moved = True
                            break
     
            for target_col_idx, target_column in enumerate(game.columns):
                    x = 70 + target_col_idx * (CARD_WIDTH + 65)
                    if target_column:
                        y = 200 + (len(target_column) - 1) * 25
                    else:
                        y = 200
                    target_rect = pygame.Rect(x,y,CARD_WIDTH,CARD_HEIGHT)
                    if target_rect.collidepoint(mouse_pos):
                        if can_place_cards(target_column, moved_cards):
                            target_column.append(moved_card)
                            moved = True
                            break
            if not moved:
                if col_idx == "foundation":
                    # 确保 foundation 也是合法的
                    if card_idx < len(game.foundation):
                        game.foundation[card_idx].append(moved_card)

        game.selected_card = None
        game.dragging_pos = None
        check_victory(game)

def handle_mouse_down(game,mouse_pos):
    for col_idx,column in enumerate(game.columns):
        x = 70 + col_idx * (CARD_WIDTH + 65)
        y = 200 + (len(column) - 1) * 25
        for card_idx in range(len(column) -1, -1 ,-1):
            card = column[card_idx]
            if card.face_up:
                if card_idx < len(column) - 1:
                    card.height = 40
                else:
                    card.height = CARD_HEIGHT
                card_rect = pygame.Rect(x,y,CARD_WIDTH,CARD_HEIGHT)
                if card_rect.collidepoint(mouse_pos):
                    game.selected_card = (col_idx, card_idx, column[card_idx:]) #添加列索引，牌索引进入selected_card同步改变column[card_idx:]
                    game.selected_offset = (mouse_pos[0] - x, mouse_pos[1] - y)
                    moved_cards = column[card_idx:]
                    game.selected_card = (col_idx, card_idx, moved_cards)
                    return
            y -= 25
    for idx, foundation in enumerate(game.foundation):
        if not foundation:
            continue
        x = 500 + idx * (CARD_WIDTH + 35)
        y = 50
        foundation_rect = pygame.Rect(x,y,CARD_WIDTH,CARD_HEIGHT)
        if foundation_rect.collidepoint(mouse_pos):
            game.selected_card = ("foundation", idx, [foundation[-1]])
            game.selected_offset = (mouse_pos[0] - x,mouse_pos[1] - y)
            moved_cards = [foundation[-1]]
            game.selected_card = ("foundation", idx, moved_cards)
            foundation.pop() 
            return
        
    for idx, waste_plie in enumerate(game.waste_plie):
        if not waste_plie:
            continue
        x = 150
        y = 50
        waste_plie_rect = pygame.Rect(x,y,CARD_WIDTH,CARD_HEIGHT)
        if waste_plie_rect.collidepoint(mouse_pos):
            game.selected_card = ("waste_plie", idx, [waste_plie[-1]])
            game.selected_offset = (mouse_pos[0] - x,mouse_pos[1] - y)
            moved_cards = [waste_plie[-1]]
            game.selected_card = ("waste_plie", idx, moved_cards)
            waste_plie.pop() 
            return

def handle_mouse_motion(game,mouse_pos):
    if game.selected_card:
        game.dragging_pos = (mouse_pos[0] - game.selected_offset[0],
                             mouse_pos[1] - game.selected_offset[1])
    
def can_place_cards(target_column,moved_cards):
        if not target_column:
            return moved_cards[0].rank == 13 #return表只有
        game.top_card = target_column[-1]
        game.new_card = moved_cards[0]
        return (game.top_card.is_red != game.new_card.is_red) and (game.top_card.rank == game.new_card.rank + 1)

def can_place_in_foundation(foundation, card):
    if not foundation:
        return card.rank == 1 
    top_card = foundation[-1]
    return (top_card.suit == card.suit) and (top_card.rank + 1 == card.rank)

def draw_card(win,card,x,y):
    pygame.draw.rect(win,(225,225,225),(x - 2,y - 2,CARD_WIDTH + 4,CARD_HEIGHT + 4),border_radius = 10)
    pygame.draw.rect(win,WHITE,(x ,y ,CARD_WIDTH ,CARD_HEIGHT ),border_radius = 10)
    text = font.render(card.__repr__(),True,COLOR_DICT[card.suit])
    win.blit(text,(x + 5,y + 5))

def draw_plie(win):
    win.fill(GREEN)
    
    dragging_cards = game.selected_card[2] if game.selected_card else []

    if game.draw_plie:
        pygame.draw.rect(win,WHITE, (48,48,CARD_WIDTH + 4,CARD_HEIGHT + 4),border_radius = 10)
        pygame.draw.rect(win,WHITE, (50,50,CARD_WIDTH,CARD_HEIGHT),border_radius = 10)
        if len(game.draw_plie) > 0:
            text = font.render(f"{len(game.draw_plie)}",True,BLACK)
            win.blit(text,(70,80))
    for col_idx, column in enumerate(game.waste_plie):
        if column:
            draw_card(win,column[-1],150,50)
    for idx, plie in enumerate(game.foundation):
        x = 500 + idx * (CARD_WIDTH + 35)
        y = 50
        if plie:
        
            draw_card(win,plie[-1],x,y)
        else:
            pygame.draw.rect(win, (225,225,225),(x,y,CARD_WIDTH + 5,CARD_HEIGHT + 5),border_radius = 10)
        if game.selected_card and game.dragging_pos:
            x, y = game.dragging_pos
            for moved_card in dragging_cards:
                draw_card(win, moved_card, x, y)
    for col_idx, column in enumerate(game.columns): #列索引
        x = 70 + col_idx * (CARD_WIDTH + 65)
        y = 200
        for card in column: #牌索引
            if game.selected_card and card in dragging_cards:
                continue
            if card.face_up:
                draw_card(win, card, x, y)
            else:
                pygame.draw.rect(win,WHITE,(x-2,y-2,CARD_WIDTH + 4,CARD_HEIGHT + 4),border_radius = 12)
                pygame.draw.rect(win,BLACK,(x,y,CARD_WIDTH,CARD_HEIGHT), border_radius = 10)
            y += 25
        if game.selected_card and game.dragging_pos:
            x, y = game.dragging_pos
            for moved_card in dragging_cards:
                draw_card(win, moved_card, x, y)
                y += 25
    
    pygame.display.update()

game = KlondikeGame()

running = True
while running:
    win.fill(GREEN)
    draw_plie(win)
    pygame.display.flip()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP:
            handle_mouse_up(game, pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONDOWN:
            licensing(game, pygame.mouse.get_pos())
            handle_mouse_down(game,pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEMOTION:
            handle_mouse_motion(game,pygame.mouse.get_pos())
        if event.type == pygame.QUIT:
            running = False
            
clock.tick(240)
pygame.quit()

        
