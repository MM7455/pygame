import random
import pygame

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
        self.draw_plie = self.deck[:]
        self.waste_plie = []
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
            
    def reset_draw_plie(self):
        if len(self.draw_plie) == 0:
            self.draw_plie = self.waste_plie[:]
            self.waste_plie = []
            random.shuffle(self.draw_plie)

    def licensing(self):
        for _ in range(3):
            if len(self.draw_plie) > 0:
                crad = self.draw_plie.pop()
                crad.face_up = False
                self.waste_plie.append(crad)

    def print_game_state(self):
        print(f"Draw:{len(self.draw_plie)}张")
        print(f"Waste:{[str(card) for card in self.waste_plie[-3]]}")

def handle_mouse_up(game,mouse_pos):
    if game.selected_card:
        col_idx,card_idx,moved_cards = game.selected_card
        original_column = game.columns[col_idx] #读取索引
        moved_cards = game.selected_card[2] #从card_idx:开始取出牌
        del original_column[card_idx:]
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
                    if original_column:
                        original_column[-1].face_up = True
                    break
        else:
            original_column.extend(moved_cards)
        game.selected_card = None
        game.dragging_pos = None

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
                    game.selected_card = (col_idx, card_idx, column[card_idx:]) #添加列索引，牌索引进入selected_card
                    game.selected_offset = (mouse_pos[0] - x, mouse_pos[1] - y)
                    moved_cards = column[card_idx:]
                    game.selected_card = (col_idx, card_idx, moved_cards)
                    return
            y -= 25

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

def draw_card(win,card,x,y):
    pygame.draw.rect(win,(225,225,225),(x - 2,y - 2,CARD_WIDTH + 4,CARD_HEIGHT + 4),border_radius = 10)
    pygame.draw.rect(win,WHITE,(x ,y ,CARD_WIDTH ,CARD_HEIGHT ),border_radius = 10)
    text = font.render(card.__repr__(),True,COLOR_DICT[card.suit])
    win.blit(text,(x + 5,y + 5))

def draw_plie(win):
    win.fill(GREEN)
    
    dragging_cards = game.selected_card[2] if game.selected_card else []
         
    if game.draw_plie:
        pygame.draw.rect(win,WHITE, (50,50,CARD_WIDTH,CARD_HEIGHT),border_radius = 10)
        text = font.render(f"{len(game.draw_plie)}",True,BLACK)
        win.blit(text,(70,80))
    if game.waste_plie:
        draw_card(win,game.waste_plie[-1],150,50)
    for idx, plie in enumerate(game.foundation):
        x = 500 + idx * (CARD_WIDTH + 35)
        y = 50
        if plie:
            draw_card(win,plie[-1],x,y)
        else:
            pygame.draw.rect(win, (225,225,225),(x,y,CARD_WIDTH + 5,CARD_HEIGHT + 5),border_radius = 10)
        
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
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP:
            handle_mouse_up(game, pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mouse_down(game,pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEMOTION:
            handle_mouse_motion(game,pygame.mouse.get_pos())
        if event.type == pygame.QUIT:
            running = False

pygame.quit()

        