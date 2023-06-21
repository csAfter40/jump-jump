# Jump Jump Game

import pygame
import sys
import random
import os
from pygame.locals import *
from settings import *
from sprites import *
from os import path

class Game:

    def __init__(self):
        # initialize game settings
        pygame.mixer.init(22050, -16, 2, 512)  # initializing mixer before pygame solved sound lag problem
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "600,40"  # locate game window on desktop
        self.screen = pygame.display.set_mode((screen_w, screen_h), 0, 32)
        pygame.display.set_caption(game_title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_name = pygame.font.match_font('freesansbold')
        self.score = 0
        self.floor = []
        self.load_data()
        self.draw_trophy = False
        self.trophy_pos = (0, 0)

    def load_data(self):
        # define paths
        self.dir = path.dirname(__file__)
        # set image directory
        self.img_dir = path.join(self.dir, 'img')
        self.snd_dir = path.join(self.dir, 'snd')
        # load images
        self.spritesheet = Spritesheet(path.join(self.img_dir, SPRITESHEET_IMG))
        self.logo = pygame.image.load(path.join(self.img_dir, LOGO_IMG)).convert_alpha()
        self.go_img = pygame.image.load(path.join(self.img_dir, GO_IMG)).convert_alpha()
        # load background images
        self.bg_img1 = pygame.image.load(path.join(self.img_dir, BG_IMG1)).convert()
        self.bg_img2 = pygame.image.load(path.join(self.img_dir, BG_IMG2)).convert_alpha()
        self.bg_img3 = pygame.image.load(path.join(self.img_dir, BG_IMG3)).convert_alpha()
        self.bg_img4 = pygame.image.load(path.join(self.img_dir, BG_IMG4)).convert_alpha()

        # get background image surfaces
        self.bg_img2, self.rect_bg_img2 = self.get_transformed_surface(self.bg_img2)
        self.bg_img3, self.rect_bg_img3 = self.get_transformed_surface(self.bg_img3)
        self.bg_img4, self.rect_bg_img4 = self.get_transformed_surface(self.bg_img4)

        # load booster picture
        self.booster_img = self.spritesheet.get_image(820, 1805, 71, 70)
        self.booster_img.set_colorkey((0, 0, 0))

        # load bullet picture
        self.bullet_img = self.spritesheet.get_image(820, 1733, 78, 70)
        self.bullet_img.set_colorkey((0, 0, 0))

        # load bomb picture
        self.bomb_img = pygame.image.load(path.join(self.img_dir, BOMB_IMG)).convert_alpha()
        self.bomb_img = pygame.transform.scale(self.bomb_img, (16, 16))

        # load trophy picture
        self.trophy_img = pygame.image.load(path.join(self.img_dir, TROPHY)).convert_alpha()
        self.trophy_img = pygame.transform.scale(self.trophy_img, (50, 50))

        # load cloud pictures
        self.cloud_img1 = pygame.image.load(path.join(self.img_dir, CLOUD1)).convert_alpha()
        self.cloud_img2 = pygame.image.load(path.join(self.img_dir, CLOUD2)).convert_alpha()
        self.cloud_img3 = pygame.image.load(path.join(self.img_dir, CLOUD3)).convert_alpha()
        # self.cloud_img1.set_colorkey((0, 0, 0))
        # self.cloud_img2.set_colorkey()
        # self.cloud_img3.set_colorkey()

        # load explosion spritesheet
        self.exp_spritesheet = Spritesheet(path.join(self.img_dir, SPRITESHEET_EXP))

        # load highscore file
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

        # load sound files

        self.jump_snd = pygame.mixer.Sound(path.join(self.snd_dir, JUMP_SOUND))
        self.jump_snd.set_volume(0.2)
        self.fall_snd = pygame.mixer.Sound(path.join(self.snd_dir, FALL_SOUND))
        self.fall_snd.set_volume(0.2)
        self.powerup_snd = pygame.mixer.Sound(path.join(self.snd_dir, POWERUP_SOUND))
        self.powerup_snd.set_volume(0.2)
        self.shoot_snd = pygame.mixer.Sound(path.join(self.snd_dir, SHOOT_SOUND))
        self.shoot_snd.set_volume(0.2)
        self.explosion_snd = pygame.mixer.Sound(path.join(self.snd_dir, EXPLOSION_SOUND))
        self.explosion_snd.set_volume(0.2)
        self.coin_snd = pygame.mixer.Sound(path.join(self.snd_dir, COIN_SOUND))
        self.coin_snd.set_volume(0.2)

    @staticmethod
    def get_transformed_surface(image):
        rect_image = image.get_rect()
        image = pygame.transform.scale(image, (screen_w, int(rect_image.h * screen_w / rect_image.w)))
        rect_image = image.get_rect()
        rect_image.bottomleft = (0, screen_h)
        return image, rect_image

    def new(self):
        # starts a new game

        # create sprite groups
        self.all_sprites = pygame.sprite.LayeredUpdates() # groups with layers
        self.platforms = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.weapons = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()

        self.player = Player(self)
        self.floor = [[0, 0]]
        self.score = 0
        self.bullet = 5
        self.draw_trophy = False
        self.play_fall_sound = True

        i = 0

        # initialize background music
        pygame.mixer.music.load(path.join(self.snd_dir, BG_MUSIC))
        pygame.mixer.music.set_volume(0.4)


        for plat in platform_list:
            p = Platform(self, *plat, self.floor[-1][1])  # '*plat' explodes plat. It stands for plat[0], plat[1]...plat[-1]
            self.floor.append([id(p), i])
            i += 1

        self.run()

    def run(self):
        # Game Loop - run
        pygame.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(fps)
            self.events()
            self.update()
            self.draw()
        pygame.mixer.music.fadeout(200)

    def update(self):
        # Game Loop - update elements
        self.all_sprites.update()

        # Collision mechanics player and platforms:
        hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        if hits and (abs(self.player.rect.right - hits[0].rect.left) < 12 and
                     not(abs(self.player.rect.bottom - hits[0].rect.top) < 5 or
                      abs(self.player.rect.top - hits[0].rect.bottom) < 5)):
            self.player.pos.x = hits[0].rect.left - 15
            self.player.vel.x = 0
        elif hits and (abs(self.player.rect.left - hits[0].rect.right) < 12 and
                     not(abs(self.player.rect.bottom - hits[0].rect.top) < 5 or
                      abs(self.player.rect.top - hits[0].rect.bottom) < 5)):

            self.player.pos.x = hits[0].rect.right + 15
            self.player.vel.x = 0
        elif self.player.vel.y >= 0 and hits and abs(self.player.rect.bottom - hits[0].rect.top) < 20:
            self.player.pos.y = hits[0].rect.top + 1
            self.player.vel.y = 0
            if hits[0].moving:
                self.player.pos.x += hits[0].vel_x  # player moves with the moving platform
        elif self.player.vel.y < 0 and hits and abs(self.player.rect.top - hits[0].rect.bottom) < 20:
            self.player.pos.y = hits[0].rect.bottom + self.player.rect.h
            self.player.vel.y = 0
            self.player.pos.y += 1

        # powerup collision
        hits_pow = pygame.sprite.spritecollide(self.player, self.powerups, True)
        if hits_pow:
            self.powerup_snd.play()
            if hits_pow[0].type == 'booster':
                self.player.booster_timer = pygame.time.get_ticks()
                self.player.booster_active = True
            elif hits_pow[0].type == 'weapon':
                self.player.weapon_timer = pygame.time.get_ticks()
                self.player.weapon_active = True
                self.bullet += 5

        # coin collision
        hits_coins = pygame.sprite.spritecollide(self.player, self.coins, False)
        if hits_coins:
            self.coin_snd.play()
            hits_coins[0].kill()
            self.score += 1

        # mobs collision
        hits_mobs = pygame.sprite.spritecollide(self.player, self.mobs, False)
        if hits_mobs:
            hits_mask = pygame.sprite.spritecollide(self.player, self.mobs, False, pygame.sprite.collide_mask)
            if hits_mask:
                self.fall_snd.play()
                self.player_kill_animation()
                self.playing = False

        # bombs collision
        hits_bombs = pygame.sprite.spritecollide(self.player, self.bombs, False)
        if hits_bombs:
            hits_bombs_mask = pygame.sprite.spritecollide(self.player, self.bombs, False, pygame.sprite.collide_mask)
            if hits_bombs_mask:
                Explosion(self, hits_bombs[0])
                hits_bombs[0].kill()
                self.fall_snd.play()
                self.player_kill_animation()
                self.playing = False

        # scoring
        if hits:
            floor_no = self.get_floor(id(hits[0]))
            if self.score < floor_no:
                self.score = floor_no

        # screen scrolling
        if self.player.rect.top <= screen_h/4 and self.player.vel.y < 0:  # velocity added for bug fix
            self.player.pos.y += abs(self.player.vel.y)
            if self.draw_trophy:
                self.trophy_rect.y += abs(self.player.vel.y)
                if self.trophy_rect.top > screen_h:
                    self.draw_trophy = False
            # scroll clouds down
            for cloud in self.clouds:
                cloud.rect.y += abs(self.player.vel.y)

            # scroll platforms down
            for plat in self.platforms:
                plat.rect.y += abs(self.player.vel.y)

                if plat.rect.top > screen_h:
                    plat.kill()
                    self.floor.pop(0) # fix bug for get_floor func.

        # spawn new platforms
        while 0 < len(self.platforms) < 9:
            if self.score < 150:
                min_width = 100 - int(self.score/3)
            else:
                min_width = 25
            rand_width = random.randrange(min_width, min_width + 25)
            height = 20
            
            p = Platform(self, random.randrange(0, screen_w - rand_width),
                         self.platforms.sprites()[-1].rect.top + random.randrange(-130, -100),
                         rand_width,
                         height, self.floor[-1][1])
            a = self.floor[-1][1]
            self.floor.append([id(p), a+1])

            # spawn clouds
            if random.randrange(100) < cloud_freq:
                Clouds(self)

            # put highscore trophy on the highscore platform
            if self.highscore > 4:
                hs_var = self.highscore
            else:
                hs_var = 5
            if a+1 == hs_var:
                self.draw_trophy = True
                self.trophy_rect = self.trophy_img.get_rect()
                self.trophy_rect.midbottom = (p.rect.midtop[0], p.rect.midtop[1])

            # background layers movement
            if self.player.rect.bottom < screen_h:
                self.rect_bg_img4.y += 1
                self.rect_bg_img3.y += 0.6
                self.rect_bg_img2.y += 0.3

        # game over
        if self.player.rect.bottom > screen_h:
            if self.play_fall_sound:
                self.fall_snd.play()
                self.play_fall_sound = False
            if self.player.rect.top > screen_h:
                self.player.kill()

            if self.draw_trophy:
                self.trophy_rect.y -= self.player.vel.y
            for sprite in self.all_sprites:
                sprite.rect.y -= self.player.vel.y
                if sprite.rect.bottom < -130:
                    sprite.kill()
            if len(self.all_sprites) == 0:
                self.playing = False

    def draw(self):
        # Game Loop _ draw elements
        self.screen.blit(self.bg_img1, (0, 0))
        self.screen.blit(self.bg_img2, self.rect_bg_img2)
        self.screen.blit(self.bg_img3, self.rect_bg_img3)
        self.screen.blit(self.bg_img4, self.rect_bg_img4)
        if self.player.booster_active:
            self.screen.blit(self.booster_img, (10, 10))
        if self.draw_trophy:
            self.screen.blit(self.trophy_img, self.trophy_rect)

        self.all_sprites.draw(self.screen)
         # draw score and bullets
        self.draw_text(f'score: {self.score}', 30, red, (screen_w - 100, 10))
        self.screen.blit(self.bullet_img, (screen_w/2 - 40, 10))
        self.draw_text(f'= {self.bullet}', 30, red, (screen_w/2 - 15, 10), 'left')
        pygame.display.update()

    def events(self):
        # Game Loop - events management
        for event in pygame.event.get():
            if event.type == QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.playing:
                        self.playing = False
                    self.running = False
                if event.key == jump_key:
                    self.player.jump()
                if event.key == shoot_key:
                    if self.bullet > 0:
                        self.player.fire()
                        self.bullet -= 1

            if event.type == KEYUP:
                if event.key == jump_key:
                    self.player.jump_cut()

    def show_start_screen(self):
        # Opens game start screen
        self.screen.fill(white)
        logo_rect = self.logo.get_rect()
        logo_rect.midtop = (screen_w/2, 70)
        self.screen.blit(self.logo, logo_rect)
        self.draw_text('Instructions:', 35, black, (30, screen_h/2 + 25))
        self.draw_text('Use arrow keys to move left and right.', 25, black,
                       (30, screen_h / 2 + 60))
        self.draw_text('Use space to jump.', 25, black, (30, screen_h/2 + 80))
        self.draw_text('Press any key to start', 30, black,
                       (screen_w/2, screen_h - 100), 'center')
        self.draw_text(f'High Score: {str(self.highscore)}', 30, red,
                       (screen_w/2, 10), allign='center')
        pygame.display.update()
        self.wait_for_key()

    def show_go_screen(self):
        # Opens game over screen
        pygame.event.clear()
        if not self.running:
            return None
        self.screen.fill(white)
        go_img_rect = self.go_img.get_rect()
        go_img_rect.midtop = (screen_w/2, 100)
        self.screen.blit(self.go_img, go_img_rect)
        self.draw_text(f'Score: {str(self.score)}', 40, black, (screen_w/2, 200),
                       allign='center')
        self.draw_text('Press any key to start again.', 30, black,
                       (screen_w/2, 500), allign='center')
        if self.score > self.highscore:
            self.highscore = self.score
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.highscore))
            self.draw_text('NEW HIGH SCORE!', 40, red, (screen_w/2, 250),
                           allign='center')
        else:
            self.draw_text(f'High Score: {str(self.highscore)}', 40, red,
                           (screen_w/2, 250), allign='center')
        pygame.display.update()
        self.wait_for_key()

    def draw_text(self, text, size, color, position, allign='left'):
        font = pygame.font.Font(self.font_name, size)
        font_surface = font.render(text, True, color)
        font_rect = font_surface.get_rect()
        if allign == 'left':
            font_rect.topleft = position
        elif allign == 'right':
            font_rect.topright = position
        elif allign == 'center':
            font_rect.midtop = position
        else:
            font_rect.topleft = position
        self.screen.blit(font_surface, font_rect)

    def get_floor(self, id):
        for floor in self.floor:
            if id == floor[0]:
                return floor[1]

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(fps)
            for event in pygame.event.get():
                if event.type == QUIT:
                    waiting = False
                    self.running = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        waiting = False
                        self.running = False
                if event.type == KEYUP:
                    waiting = False

    def player_kill_animation(self, time=2000):
        init_time = pygame.time.get_ticks()
        waiting = True
        once = True
        if self.player.pos.x > screen_w/2:
            direction = -1
        else:
            direction = 1
        while waiting:
            self.clock.tick(fps)
            current_time = pygame.time.get_ticks()
            if current_time - init_time > time:
                waiting = False
            elif current_time - init_time > time/3:
                self.player.vel.x = 2*direction
                if once:
                    self.player.vel.y = -8
                    once = False
                self.player.update()
            self.explosions.update()
            self.draw()

game = Game()
game.show_start_screen()
while game.running:
    game.new()
    game.show_go_screen()

pygame.quit()
sys.exit()