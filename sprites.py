# Classes for sprites
import pygame
import random
from settings import *
from pygame.locals import *
import pygame.math

vec = pygame.math.Vector2


class Spritesheet():
    # utility class for spritesheets
    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height):
        imgSurf = pygame.Surface((width, height), SRCALPHA)
        imgSurf.blit(self.spritesheet, (0, 0), (x, y, width, height))
        imgSurf = pygame.transform.scale(imgSurf, (width * 2 // 8, height * 2 // 8))
        return imgSurf


class Player(pygame.sprite.Sprite):

    def __init__(self, game):
        self.groups = game.all_sprites
        self._layer = player_layer
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.strength = 5
        self.mass = 10
        self.friction = 0.8
        self.jump_speed = -15
        self.pos = vec(screen_w / 2, screen_h / 2)
        self.vel = vec(0, 0)
        self.run_acc = vec(0, 0)
        self.acc = vec(0, gravity)
        self.fric_acc = vec(0, 0)
        self.acc_x_threshold = 0.3
        self.vel_x_threshold = 5
        # powerup runners
        self.booster_timer = 0
        self.booster_active = False
        self.weapon_timer = 0
        self.weapon_active = False

    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(690, 406, 120, 201),
                                self.game.spritesheet.get_image(614, 1063, 120, 191)]
        for frame in self.standing_frames:
            frame.set_colorkey((0, 0, 0))
        self.walking_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
                                 self.game.spritesheet.get_image(692, 1458, 120, 207)]
        self.walking_frames_l = []
        for frame in self.walking_frames_r:
            frame.set_colorkey((0, 0, 0))
            self.walking_frames_l.append(pygame.transform.flip(frame, True, False))
        self.jump_frame = self.game.spritesheet.get_image(382, 763, 150, 181)
        self.jump_frame.set_colorkey((0, 0, 0))

    def animate(self):
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        if abs(self.vel.y) >= 2:
            self.walking = False
            self.jumping = True

        elif keys[K_LEFT] or keys[K_RIGHT] and abs(self.vel.y) < 2:

            self.jumping = False
            self.walking = True

        else:
            self.walking = False
            self.jumping = False
        # if abs(self.vel.x) > 1 and abs(self.vel.y) < 2:

        if self.walking:
            if now - self.last_update > 100:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames_r)
                if keys[K_RIGHT]:
                    self.image = self.walking_frames_r[self.current_frame]
                if keys[K_LEFT]:
                    self.image = self.walking_frames_l[self.current_frame]
        if self.jumping:
            self.image = self.jump_frame
        if not self.walking and not self.jumping:
            if now - self.last_update > 300:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # create mask for player. Should be done after deciding what self.image
        # will be displayed on the screen
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.animate()
        self.run_acc = vec(0, 0)

        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.run_acc.x = -self.strength / self.mass  # F = m.a(Newton)
        if keys[K_RIGHT]:
            self.run_acc.x = self.strength / self.mass  # F = m.a(Newton)

        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)

        if abs(self.vel.y) > 2:  # effect of friction when jumping
            self.friction = 0.8
            self.strength = 5
            self.vel_x_threshold = 5

        elif hits and (hits[0].rect.collidepoint(self.rect.midbottom) or
                       hits[0].rect.collidepoint(self.rect.bottomleft) or
                       hits[0].rect.collidepoint(self.rect.bottomright)):
            self.friction = hits[0].friction[hits[0].level]
            self.strength = hits[0].strength[hits[0].level]
            self.vel_x_threshold = hits[0].vel_x_threshold[hits[0].level]

        # if not self.vel == vec(0, 0):
        self.fric_acc.x = gravity * self.friction
        # else:
        #     self.fric_acc = vec(0, 0)

        if keys[K_RIGHT]: #and self.vel.x > 0:
            self.acc.x = min(self.fric_acc.x,
                           self.run_acc.x * (1 - self.vel.x/self.vel_x_threshold))
        elif keys[K_LEFT]: # and self.vel.x < 0:
            self.acc.x = max(-self.fric_acc.x,
                           self.run_acc.x * (1 + self.vel.x / self.vel_x_threshold))
        elif self.vel.x > 0.1:
            self.acc.x =  -self.fric_acc.x
        elif self.vel.x < -0.1:
            self.acc.x = self.fric_acc.x
        else:
            self.acc.x = 0

        #   Below code is for bug fix. It prevents friction deceleration causes
        # a negative direction velocity around vel = 0.
        if keys[K_RIGHT] or keys[K_LEFT]:
            self.vel += self.acc
        elif self.vel.x > 0:
            self.vel.x = max(self.vel.x + self.acc.x, 0)
            self.vel.y += self.acc.y
        elif self.vel.x < 0:
            self.vel.x = min(self.vel.x + self.acc.x, 0)
            self.vel.y += self.acc.y
        else:
            self.vel += self.acc


        if abs(self.vel.x) <= 0.1:
            self.vel.x = 0
        self.pos += self.vel

        if self.pos.x > screen_w + 12:
            self.pos.x = -12
        if self.pos.x < - 12:
            self.pos.x = screen_w + 12
        if self.vel.y > 15:  # limits falling speed to avoid collision problems
            self.vel.y = 15

        self.rect.midbottom = self.pos

        # booster
        if self.booster_active:
            self.jump_speed = -20
            if pygame.time.get_ticks() - self.booster_timer > 10000:
                self.jump_speed = -15
                self.booster_active = False

    def jump(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 1
        if hits and (hits[0].rect.collidepoint(self.rect.midbottom) or
                     hits[0].rect.collidepoint(self.rect.bottomleft) or
                     hits[0].rect.collidepoint(self.rect.bottomright)):
            self.game.jump_snd.play()
            if hits[0].level == 1:  # if on a sand platform
                self.vel.y = self.jump_speed * sand_jump_factor
            else:
                self.vel.y = self.jump_speed

    def jump_cut(self):
        if self.vel.y < -5:
            self.vel.y *= 0.5

    def fire(self):
        self.game.shoot_snd.play()
        Weapon(self.game)

    def kill_animation(self, once=True):
        if once:
            self.vel = vec(2, -2)
            once = False
        self.update()


class Platform(pygame.sprite.Sprite):

    def __init__(self, game, x, y, w, h, floor):
        self.groups = game.all_sprites, game.platforms
        self._layer = platform_layer
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.img_w = 200
        self.img_h = 94
        self.floor = floor
        self.moving = False
        if self.floor > 20:
            if random.randrange(100) < moving_plat_freq:
                self.moving = True
        self.vel_x = 1
        self.friction = [0.9, 1, 0.3]
        self.strength = [5, 1.8, 5]
        self.vel_x_threshold = [5, 2, 5]
        if floor < 70:
            self.level = 0
        elif floor < 120:
            self.level = 1
        else:
            self.level = 2
        #  load platform images. 0 = grass, 1 = sand, 2 = snow
        plat_image = [self.game.spritesheet.get_image(55, 288, self.img_w, self.img_h),
                      self.game.spritesheet.get_image(55, 672, self.img_w, self.img_h),
                      self.game.spritesheet.get_image(55, 768, self.img_w, self.img_h)]
        transformed_img_w = int(self.img_w * h / self.img_h)
        self.image = pygame.Surface((w, h))

        for i in range(w // transformed_img_w + 1):
            self.image.blit(plat_image[self.level], (i * transformed_img_w, 0))

        self.rect = self.image.get_rect().move(0, -5)
        self.rect.x = x
        self.rect.y = y

        # spawn a powerup
        if random.randrange(100) < powerup_freq:
            Pow(self.game, self)
        elif random.randrange(100) < coin_freq:
            Coin(self.game, self)

        # spawn a mob
        if random.randrange(100) < mob_freq:
            Mob(self.game, self)

    def update(self):
        if self.moving:
            self.rect.x += self.vel_x
            if self.rect.right > screen_w:
                self.rect.right = screen_w
                self.vel_x *= -1
            if self.rect.left < 0:
                self.rect.left = 0
                self.vel_x *= -1


class Pow(pygame.sprite.Sprite):

    def __init__(self, game, plat):
        self.groups = game.all_sprites, game.powerups
        self._layer = powerup_layer
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = random.choice(['booster', 'weapon'])
        self.image_booster = self.game.spritesheet.get_image(820, 1805, 71, 70)
        self.image_weapon = self.game.spritesheet.get_image(820, 1733, 78, 70)
        if self.type == 'booster':
            self.image = self.image_booster
        else:
            self.image = self.image_weapon
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        self.rect.centerx = self.plat.rect.centerx
        if not self.game.platforms.has(self.plat):
            self.kill()


class Mob(pygame.sprite.Sprite):

    def __init__(self, game, plat, bombing=True):
        self.groups = game.all_sprites, game.mobs
        self._layer = mob_layer
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey((0, 0, 0))
        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey((0, 0, 0))
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centery = self.plat.rect.top + 60
        self.rect.centerx = -50
        self.vel_x = 2
        self.vel_y = 0
        self.acc_y = 0.2
        self.oscillation_y = 0
        self.bombing = bombing
        self.has_bomb = True

    def update(self):
        self.rect.centerx += self.vel_x
        if self.rect.centerx > screen_w + 100 or self.rect.centerx < -100:
            self.vel_x *= -1
            self.has_bomb = True
        self.vel_y += self.acc_y
        if self.vel_y > 3 or self.vel_y < -3:
            self.acc_y *= -1
        self.oscillation_y += self.vel_y
        self.rect.centery = self.plat.rect.top + 60 + self.oscillation_y

        center = self.rect.centery  # get image position
        if self.vel_y < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect.centery = center  # position new image on the old image

        if self.bombing:
            self.drop_bomb()

        # create mask for collision
        self.mask = pygame.mask.from_surface(self.image)  # mask should be created after image self.image decision

        # kill the mob if not used
        if not self.game.platforms.has(self.plat):
            self.kill()

    def drop_bomb(self):
        if self.rect.y > 0 and self.has_bomb and \
                self.rect.bottom < (self.game.player.rect.top - 50) and \
                self.game.player.rect.left < self.rect.centerx < self.game.player.rect.right:
            Bomb(self.game, self)
            self.has_bomb = False


class Clouds(pygame.sprite.Sprite):

    def __init__(self, game):
        self._layer = clouds_layer
        self.groups = game.all_sprites, game.clouds
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = random.choice([self.game.cloud_img1, self.game.cloud_img2,
                                    self.game.cloud_img3])
        self.scale = random.randrange(2, 5)
        self.image = pygame.transform.scale(self.image,
                                            (int(self.image.get_width() / self.scale),
                                             int(self.image.get_height() / self.scale)))
        self.image.set_alpha(200)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(screen_w)
        self.rect.bottom = random.randrange(-200, 0)
        self.vel_x = random.choice([0.2, 0.4, 0.6, 0.8])
        self.x = self.rect.right

    def update(self):
        self.x += self.vel_x
        self.rect.right = self.x
        if self.rect.left > screen_w:
            self.x = -10
        if self.rect.top > screen_h:
            self.kill()


class Weapon(pygame.sprite.Sprite):

    def __init__(self, game):
        self._layer = weapon_layer
        self.groups = game.all_sprites, game.weapons
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.spritesheet.get_image(820, 1733, 78, 70)
        self.image = pygame.transform.rotate(self.image, 135)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.bottom = self.game.player.rect.top
        self.rect.centerx = self.game.player.rect.centerx
        self.vel_y = -10

    def update(self):
        self.rect.centery += self.vel_y
        if self.rect.bottom < 0:
            self.kill()

        # collision with platforms and mobs
        hits_plat = pygame.sprite.spritecollide(self, self.game.platforms, False)
        hits_mob = pygame.sprite.spritecollide(self, self.game.mobs, False)
        if hits_plat and abs(self.rect.left - hits_plat[0].rect.right) > 5 \
                and abs(self.rect.right - hits_plat[0].rect.left) > 5:
            self.kill()
        if hits_mob and abs(self.rect.left - hits_mob[0].rect.right) > 15 \
                and abs(self.rect.right - hits_mob[0].rect.left) > 15:
            self.kill()
            hits_mob[0].kill()


class Bomb(pygame.sprite.Sprite):

    def __init__(self, game, mob):
        self._layer = bomb_layer
        self.groups = game.all_sprites, game.bombs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.mob = mob
        self.image = self.game.bomb_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)  # create mask for collision
        self.rect.centerx = self.mob.rect.centerx
        self.rect.centery = self.mob.rect.midbottom[1]
        self.acc_y = gravity
        self.vel_y = 0

    def update(self):
        self.vel_y += self.acc_y
        if self.vel_y > bomb_vel_y_threshold:
            self.vel_y = bomb_vel_y_threshold
        self.rect.centery += self.vel_y
        hits_plat = pygame.sprite.spritecollide(self, self.game.platforms, False)
        if hits_plat:
            Explosion(self.game, self)
            self.kill()
        if self.rect.top > screen_h:
            self.kill()


class Explosion(pygame.sprite.Sprite):

    def __init__(self, game, bomb):
        self._layer = explosion_layer
        self.groups = game.all_sprites, game.explosions
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.bomb = bomb
        self.frames = []
        self.load_images()
        self.image = self.frames[0]#.convert_alpha()
        # self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.bomb.rect.midbottom
        self.frame = 0
        self.game.explosion_snd.play()

    def load_images(self):
        for i in range(12):
            x = i*96
            self.frames.append(self.game.exp_spritesheet.get_image(x, 0, 96, 96))

    def update(self):
        self.image = self.frames[self.frame]#.convert_alpha()
        # self.image.set_colorkey((0, 0, 0))
        self.frame += 1
        if self.frame == 12:
            self.kill()


class Coin(pygame.sprite.Sprite):

    def __init__(self, game, plat):
        self._layer = coin_layer
        self.groups = game.all_sprites, game.coins
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.load_images()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5
        self.frame = 0
        self.fps = 10
        self.screen_frame = 0

    def load_images(self):
        self.frames = [self.game.spritesheet.get_image(698, 1931, 84, 84),
                       self.game.spritesheet.get_image(829, 0, 66, 84),
                       self.game.spritesheet.get_image(897, 1574, 50, 84),
                       self.game.spritesheet.get_image(645, 651, 15, 84)]
        self.frames.append(pygame.transform.flip(self.frames[2], True, False))
        self.frames.append(pygame.transform.flip(self.frames[1], True, False))

    def update(self):
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5
        if self.screen_frame == fps//self.fps:
            self.animate()
            self.screen_frame = 0
        else:
            self.screen_frame += 1
        if not self.game.platforms.has(self.plat):
            self.kill()

    def animate(self):
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5
        self.frame += 1
        if self.frame == 6:
            self.frame = 0