from pygame.locals import *

# game settings
screen_w = 480
screen_h = 600
fps = 60
game_title = 'Jump Jump'
gravity = 0.5

# key configuration
jump_key = K_SPACE
shoot_key = K_LALT
# jump_key = K_UP
# shoot_key = K_SPACE

# powerup properties
powerup_freq = 5 # per cent

# mob properties
mob_freq = 8 # per cent
bomb_vel_y_threshold = 3

# cloud properties
cloud_freq = 20 # per cent

# coin properties
coin_freq = 20

# draw layers
player_layer = 3
mob_layer = 3
platform_layer = 2
powerup_layer = 2
clouds_layer = 1
weapon_layer = 3
bomb_layer = 3
explosion_layer = 3
coin_layer = 2

#platfom settings
platform_list = [(-10, screen_h - 20, screen_w + 10, 20),
                 (screen_w/2 - 50, screen_h*3/4, 120, 20),
                 (0, screen_h/2 + 40, 120, 20),
                 (screen_w/2 - 50, screen_h/2 - 110, 120, 20),
                 (screen_w - 100, 50, 120, 20)]
sand_jump_factor = 0.9
moving_plat_freq = 8  # per cent

# default colors
white = (255, 255, 255)
black = (20, 20, 10)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (10, 210, 60)
yellow = (225, 225, 10)
brown = (105, 60, 40)
sky_blue = (241, 250, 255)

# filenames
HS_FILE = 'highscore.txt'
SPRITESHEET_IMG = 'spritesheet_jumper.png'
SPRITESHEET_EXP = 'spritesheet_explosion.png'
GO_IMG = 'gameover.png'
LOGO_IMG = 'logo.png'
BG_IMG1 = 'bg_layer1.png'
BG_IMG2 = 'bg_layer2.png'
BG_IMG3 = 'bg_layer3.png'
BG_IMG4 = 'bg_layer4.png'
TROPHY = 'trophy.png'
CLOUD1 = 'cloud1.png'
CLOUD2 = 'cloud2.png'
CLOUD3 = 'cloud3.png'
BOMB_IMG = 'bomb.png'

BG_MUSIC = 'bg_music.ogg'
JUMP_SOUND = 'jump.wav'
FALL_SOUND = 'fall.wav'
POWERUP_SOUND = 'powerup.wav'
SHOOT_SOUND = 'shoot.wav'
EXPLOSION_SOUND = 'explosion.wav'
COIN_SOUND = 'coin.wav'
