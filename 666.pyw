import pygame
import random

pygame.init()
clock = pygame.time.Clock()

pygame.mixer.init()
sound = pygame.mixer.Sound("sounds/per3c - HiTom2.wav")

font = pygame.font.SysFont("Arial", 40)
score_test = font.render("game over",True,(0,0,0))

info = pygame.display.Info()
screen_WIDTH = info.current_w
screen_HEGIHT = info.current_h

ratio = int(screen_WIDTH/screen_HEGIHT)
WIDTH = screen_WIDTH*0.6
HEIGHT = screen_HEGIHT*0.6/ratio
win = pygame.display.set_mode((WIDTH,HEIGHT), pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("我的天哪死水大人")

tile_size = 40
jump_power = 25
play_speed = 5
max_speed = 10
gravity = 2
velocity_y = 0
on_ground = False
moving_left = False
moving_right = False
game_over = False
velocity_x = 0
friction = 2
camera_x = 0
MAP_WIDTH = 2500
camera_x = 0
restart_timer = 0
BOSS_ROOM_START = 1904
BOSS_ROOM_WIDTH  = 1000
BOSS_ROOM_END = BOSS_ROOM_START + BOSS_ROOM_WIDTH - 50
boss_fight =False

WHITE = (255,255,255)
BROWN = (150,75,0)
BLUE = (0,0,225)

grounds = [
    pygame.Rect(0,600,3000,40)
]
platforms = [
    pygame.Rect(200,500,100,20),
    pygame.Rect(600,400,150,20),
    pygame.Rect(900,530,150,20),
    pygame.Rect(1937,472,150,20),
    pygame.Rect(2037,372,150,20),
    pygame.Rect(2647,372,150,20),
    pygame.Rect(2727,472,150,20)
]

class Player:
    def __init__(self,x,y,width,height):
        self.rect = pygame.Rect(x,y,width,height)
        self.hp = 3
        self.invincible = 0
        self.knockback_x = 0
        self.attacking = False
        self.attack_cooldown = 0
        self.facing_right = True

    def draw_health(self):
        hearts = "♥" * self.hp
        heart_text = font.render(hearts,True,(0,0,0))
        win.blit(heart_text,(20,20))

    def update(self):
        if self.invincible > 0:
            self.invincible -= 1
        if self.knockback_x != 0:
            self.rect.x += self.knockback_x
            self.knockback_x *= 0.8
            if abs(self.knockback_x) < 0.5:
                self.knockback_x = 0

    def take_damage(self, damage,attack_direction,):
        global game_over,restart_timer
        if self.invincible == 0:
            self.hp -= damage
            self.invincible = 30
            self.knockback_x = 20 if attack_direction else -20
        if self.hp <= 0 and not game_over:
            game_over = True
            restart_timer = pygame.time.get_ticks()

    def attack(self):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_cookdown = 20
            attack_x = self.rect.right if self.facing_right else self.rect.left - 50
            attacks.append(Attack(attack_x,self.rect.y + 10))

    
    def draw(self,win):
        if game_over:
            return
        if self.invincible % 6 < 3:
            pygame.draw.rect(win,BLUE,(self.rect.x - camera_x,self.rect.y,self.rect.width,self.rect.height))

class Enemy:
    def __init__(self,x,y,hp,speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.rect = pygame.Rect(x, y, 20, 20)
        self.direction = 1
        self.width = 20
        self.height = 20
        self.hp = hp
        self.knockback_x = 0
        self.knockback_y = 0
        self.invincible =0
        self.velocity_y = 0
        self.on_ground = False

    def update(self,):
        if self.invincible > 0:
            self.invincible -= 1
        if self.knockback_x != 0:
            self.rect.x += self.knockback_x
            self.rect.y -= self.knockback_y
            self.knockback_x *= 0.5
            if abs(self.knockback_x) <= 0.5:
                self.knockback_x = 0
        if not self.on_ground:
            self.velocity_y += gravity
            self.rect.y +=self.velocity_y
        self.on_ground = False
        for ground in grounds:
            if self.rect.colliderect(ground) and self.velocity_y > 0:
                self.rect.y = ground.y - self.rect.height
                self.velocity_y = 0  
                self.on_ground = True
         
    def move(self): 
        self.rect.x += self.speed * self.direction
        if player.rect.x < 800:
            if self.rect.centerx > player.rect.centerx:
                self.direction = -1
            if self.rect.centerx < player.rect.centerx:
                self.direction = 1
        else:
            if self.rect.x + self.width > 800:
                self.direction = -1
            elif self.x <= 0:
                self.direction = 1

    def damage(self,attack_direction):
        if self.invincible == 0:
            self.invincible = 20
            self.hp -= 1
            self.knockback_x = 30 if attack_direction else -30
            self.knockback_y = 10
        if self.hp <= 0:
            enemies.remove(self)

    def draw(self,win):
        if self.invincible % 6 < 3:
            pygame.draw.rect(win,(255,0,0),(self.rect.x - camera_x,self.rect.y,self.rect.width,self.rect.height))

class Boss:
    def __init__(self,x,y,hp,width,height):
        self.rect = pygame.Rect(x,y,width,height)
        self.hp = hp
        self.speed = 2
        self.direction = 1
        self.knockback_x = 0
        self.knockback_y = 0
        self.attack_cooldown = 0
        self.hit_timer = 0
        self.velocity_y = 0
        self.on_ground = False
        self.state = 1
        self.vertical_dash = False
        self.dash_cooldown = 0
        self.dash_direction = False
        self.trigger_time = 0
        self.trigger_time1 = 0
        self.dash_speed = 0
        self.dash_speed1 = 0
        self.is_dashing = False

    def update_state(self):
        if self.state == 1 and self.hp <= 30: 
            self.state = 2
        if self.state == 2 and self.hp <= 15:  
            self.state = 3

    def move(self):
        self.update_state()
        if self.state == 1:
            self.rect.x += self.speed * self.direction
            if self.rect.x >= BOSS_ROOM_END:
                self.rect.x = BOSS_ROOM_END
                self.direction = -1 
            elif self.rect.x <= BOSS_ROOM_START:
                self.rect.x = BOSS_ROOM_START
                self.direction = 1
        elif self.state == 2:
            self.dash_attack(player)
        else:
            self.state == 3
            self.crazy_dash_attack(player)
        
    def dash_attack(self,player):
        if self.dash_cooldown <= 0 and abs(self.rect.centerx - player.rect.centerx) < 300:
            self.dash_cooldown=60
            self.dash_speed = 15
            if self.rect.centerx < player.rect.centerx:
                self.dash_direction = True
            else:
                self.dash_direction = False
            self.rect.x += self.dash_speed if self.dash_direction else -self.dash_speed
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        self.dash_speed *= 0.99
        if abs(self.dash_speed) <= 1:
            self.dash_speed = 0

    def crazy_dash_attack(self,player,vertical_dash_chance=0.2):
        self.dash_speed1 *= 0.95
        if abs(self.dash_speed1) <= 1:
            self.dash_speed = 0
        if self.dash_cooldown <= 0 and abs(self.rect.centerx - player.rect.centerx) < 300:
            self.vertical_dash = random.random() < vertical_dash_chance
            if self.vertical_dash:
                self.dash_cooldown = 120
                self.dash_speed1 = 30
            else:
                self.dash_speed1 = 15
                self.dash_cooldown = 120
            if self.rect.centerx < player.rect.centerx:
                self.dash_direction = True
            else:
                self.dash_direction = False
        self.rect.x += self.dash_speed1 if self.dash_direction else -self.dash_speed1
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1    
            
        
    def take_damage(self,damage,attack_direction):
        self.knockback_x = 30 if attack_direction else -30
        self.knockback_y = 10
        self.hp -= damage
        self.hit_timer = 15

    def die(self):
        
        
        boss_list.remove(self)
         
    def update(self):
        if self.hp > 0:
            self.move()
            if self.attack_cooldown > 0:
                self.attack_cooldown -= 1
            if self.hit_timer > 0:
                self.hit_timer -= 1
        if self.knockback_x != 0:
            self.rect.x += self.knockback_x
            self.rect.y -= self.knockback_y
            self.knockback_x *= 0.5
            if abs(self.knockback_x) <= 0.5:
                self.knockback_x = 0
        if abs(self.dash_speed) > 0:
            self.rect.x += self.dash_speed if self.dash_direction else -self.dash_speed
            self.dash_speed *= 0.9 
            if abs(self.dash_speed) <= 1:
                self.dash_speed = 0
        if not self.on_ground:
            self.velocity_y += gravity
            self.rect.y +=self.velocity_y
        self.on_ground = False
        for ground in grounds:
            if self.rect.colliderect(ground) and self.velocity_y > 0:
                self.rect.y = ground.y - self.rect.height
                self.velocity_y = 0  
                self.on_ground = True
        if self.hp <= 0:
            self.die()

    def draw(self,win):
        draw_health_bar(win,700,50,self.hp,40)
        if self.hp > 30:
            state_color = (255, 0, 0) 
        elif self.hp > 15:
            state_color = (255, 165, 0) 
        else:
            state_color = (0, 0, 255) 
        if self.hit_timer > 0:
            color = (150, 0, 255) if self.hit_timer % 4 < 2 else state_color
        else:
            color = state_color
        pygame.draw.rect(win,color,(self.rect.x - camera_x,self.rect.y,self.rect.width,self.rect.height))

class Attack:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x,y,50,20)
        self.timer = 5
        self.player = player
        self.update_position()

    def update_position(self):
        if self.player.facing_right:
            self.rect.x = self.player.rect.right
        else:
            self.rect.x = self.player.rect.left - self.rect.width
        self.rect.y = self.player.rect.y + 10

    def update(self):
        self.update_position()
        self.timer -= 1
        return self.timer > 1
    
    def draw(self,win):
        pygame.draw.rect(win,(192,192,192),(self.rect.x - camera_x,self.rect.y,self.rect.width,self.rect.height) )       

def check_colliderect(player,enemy):
    return player.rect.colliderect(enemy.rect)
def draw_health_bar(surface, x, y, hp, max_hp):
    bar_length = 200
    bar_height = 20
    fill = (hp / max_hp) * bar_length
    pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_length, bar_height))  
    pygame.draw.rect(surface, (0, 255, 0), (x, y, fill, bar_height))  

player = Player(100, HEIGHT - tile_size - 40, 30, 40)
attacks  = []

enemies = [
        Enemy(500, HEIGHT - tile_size - 20, hp=5, speed=3),
        Enemy(900, HEIGHT - tile_size - 20, hp=5, speed=5) 
        ]
boss_list = [Boss(2404 - 40,HEIGHT - tile_size - 80,40,80,80)]

running = True
while running:
    win.fill(WHITE)

    on_ground = False

    for ground in grounds:
        if player.rect.colliderect(ground) and velocity_y > 0 and player.rect.y + player.rect.height - velocity_y <= ground.y:
            player.rect.y = ground.y - player.rect.height
            velocity_y = 0
            on_ground = True
    for platform in platforms:
        if player.rect.colliderect(platform) and velocity_y > 0 and player.rect.y + player.rect.height - velocity_y <= platform.y:
            player.rect.y = platform.y - player.rect.height
            velocity_y = 0
            on_ground = True

    if moving_left:
        velocity_x -= play_speed
        if velocity_x < -max_speed:
            velocity_x = -max_speed
    elif moving_right:
        velocity_x += play_speed  
        if velocity_x > max_speed:
            velocity_x = max_speed
    else:
        if velocity_x > 0:
            velocity_x -= friction
            if velocity_x < 0:
                velocity_x = 0
        elif velocity_x < 0:
            velocity_x += friction
            if velocity_x > 0:
                velocity_x = 0        
                     
    velocity_y += gravity  
    player.rect.y += velocity_y
    player.rect.x += velocity_x
    
    if player.rect.x < BOSS_ROOM_START - 20:
        camera_x = max(0, min(player.rect.x - WIDTH // 2, MAP_WIDTH - WIDTH))
    else:
        boss_fight = True
        target_camera_x = BOSS_ROOM_START
        camera_x += (target_camera_x - camera_x) * 0.1

    if boss_fight:
        player.rect.x  = max(BOSS_ROOM_START,min(player.rect.x,BOSS_ROOM_END + 40))
        for boss in boss_list[:]:
            boss.rect.x  = max(BOSS_ROOM_START,min(boss.rect.x,BOSS_ROOM_END))
            boss.draw(win)
            boss.move()
            boss.update()
            for attack in attacks:
                if attack.rect.colliderect(boss.rect):
                    attack_direction = player.facing_right
                    boss.take_damage(1,attack_direction)
                    sound.play()
            if boss.hp > 0 and player.rect.colliderect(boss):
                attack_direction = boss.rect.x < player.rect.x
                player.take_damage(1,attack_direction)

    
    for attack in attacks[:]:
        attack.update()
        attack.draw(win)
        if not attack.update():
            attacks.remove(attack)

    for enemy in enemies[:]:
        enemy.move()
        enemy.draw(win)
        enemy.update()
        for attack in attacks:
            if attack.rect.colliderect(enemy.rect):
                attack_direction = player.facing_right
                enemy.damage(attack_direction)
                
        if enemy.hp > 0 and player.rect.colliderect(enemy):
            attack_direction = enemy.rect.x < player.rect.x
            player.take_damage(1,attack_direction)

    enemies = [enemy for enemy in enemies if enemy.hp > 0]
    player.update()
    player.draw_health()
    player.draw(win)
    
    
    for platform in platforms:
        pygame.draw.rect(win,BROWN,(platform.x - camera_x, platform.y, platform.width, platform.height))
    for ground in grounds:
        pygame.draw.rect(win,BROWN,(ground.x - camera_x, ground.y, ground.width, ground.height))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
                player.facing_right = False
            elif event.key == pygame.K_d:
                moving_right = True
                player.facing_right = True
            elif event.key == pygame.K_SPACE and on_ground:
                velocity_y = -jump_power
        elif event.type == pygame.KEYUP:  
            if event.key == pygame.K_a:
                moving_left = False
            elif event.key == pygame.K_d:
                moving_right = False
        elif event.type == pygame.MOUSEBUTTONDOWN: 
            if event.button == 1: 
                player.attack()
    
    if game_over:
        death_angle = min((pygame.time.get_ticks() - restart_timer) // 10, 90)
        death_surface = pygame.Surface((player.rect.width,player.rect.height),pygame.SRCALPHA)
        death_surface.fill((0,0,255))
        if  not player.facing_right:
            death_angle = -death_angle
        death_surface = pygame.transform.rotate(death_surface,death_angle)
        death_rect = death_surface.get_rect(center=(player.rect.x - camera_x + player.rect.width // 2,player.rect.y + player.rect.height // 2))
        win.blit(death_surface,(player.rect.x - camera_x, player.rect.y + 10))

        fade_surface = pygame.Surface((WIDTH,HEIGHT))
        fade_surface.fill((0,0,0))
        fade_alpha = min((pygame.time.get_ticks() - restart_timer) // 10,255)
        fade_surface.set_alpha(fade_alpha)
        win.blit(fade_surface, (0,0))
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and pygame.time.get_ticks() - restart_timer > 3000:
                player = Player(100, HEIGHT - tile_size - 40, 30, 40)  
                enemies = [Enemy(500, HEIGHT - tile_size - 20, hp=5, speed=3),
                            Enemy(900, HEIGHT - tile_size - 20, hp=5, speed=5)]
                boss_list = [Boss(2404 - 40,HEIGHT - tile_size - 80,40,80,80)]
                game_over = False  
            pygame.display.update()
            continue

    pygame.display.update()
    clock.tick(30)
pygame.quit()



