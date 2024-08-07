import random
from math import ceil
import pygame
from extracter import extract_images, extract_platforms, scale_image
import time
from functools import wraps

JUMP_SOUND = pygame.mixer.Sound('assets/audio/jump.ogg')
JUMP_SOUND.set_volume(0.15)
CURRENT_W, CURRENT_H = pygame.display.Info().current_w, pygame.display.Info().current_h

class Player(pygame.sprite.Sprite):
    PERCENT_OF_SCREEN_HEIGHT = 0.1296296296296296
    ANIMATION_SPEED = 4 
    change_animation = 2  

    facing_right = True
    on_ground = True
    idle_index = 1
    running_index = 0
    speed = [0, 0]

    animation_frame = 'idle'
    IDLE_PATH = 'assets/sprites/idle1.png'
    JUMP_PATH = 'assets/sprites/jump.png'
    LANDING_PATH = 'assets/sprites/landing.png'
    MID_AIR_PATH = 'assets/sprites/mid air.png'
    RUN_PATH = 'assets/sprites/run.png'

    RUNNING_SPEED = round(CURRENT_W / 200)  
    JUMP_SPEED = round(CURRENT_H / -30)   
    GRAVITY_CONSTANT = -0.05 * JUMP_SPEED
    scale_factor = CURRENT_H * PERCENT_OF_SCREEN_HEIGHT / 34
    idle_images = [[], []] 
    for image in extract_images(IDLE_PATH, 19, scale_factor):  
        idle_images[0].append(pygame.transform.flip(image, True, False))
        idle_images[1].append(image)

    jump_image = pygame.image.load(JUMP_PATH).convert_alpha()
    jump_image = scale_image(jump_image, scale_factor)
    jump_images = [pygame.transform.flip(jump_image, True, False), jump_image]


    mid_air_images = [[], []] 
    for image in extract_images(MID_AIR_PATH, 20, scale_factor):
        mid_air_images[0].append(pygame.transform.flip(image, True, False))
        mid_air_images[1].append(image)

    run_images = [[], []] 
    for image in extract_images(RUN_PATH, 21, scale_factor):
        run_images[0].append(pygame.transform.flip(image, True, False))
        run_images[1].append(image)

    GROUND_ADJUSTMENT = ceil(0.1111111111111111 * 0.07901234567901234 * CURRENT_H)

    def __init__(self, world):
        super(Player, self).__init__()

        self.world = world
        self.image: pygame.Surface = self.idle_images[1][0]
        self.rect: pygame.Rect = self.image.get_rect()
        collide_width = self.rect.width - 80 * self.scale_factor
        self.collide_rect: pygame.Rect = pygame.rect.Rect((0, 0), (collide_width, self.rect.height))
        self.rect.left = 0.05 * CURRENT_W

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def reset_change_animation(self):
        self.change_animation = self.ANIMATION_SPEED

    def get_image(self, images: list, index: int = None) -> pygame.image:
        if index is None: return images[self.facing_right]
        return images[self.facing_right][index]

    def update_idle(self):
        if self.change_animation <= 0:
            self.image = self.get_image(self.idle_images, self.idle_index)
            self.idle_index += 1
            if self.idle_index >= len(self.idle_images[0]): self.idle_index = 0
            self.reset_change_animation()
        else: self.change_animation -= 1

    def update_running(self):
        if self.change_animation <= 0:
            self.image = self.get_image(self.run_images, self.running_index)
            self.running_index += 1
            if self.running_index >= len(self.run_images[0]): self.running_index = 0
            self.reset_change_animation()
        else: self.change_animation -= 1

    def gravity(self):
        self.on_ground = False
        for platform in pygame.sprite.spritecollide(self, self.world.platform_list, False):
            if self.rect.bottom == platform.rect.top + self.GROUND_ADJUSTMENT:
                self.on_ground = True
                break
        if not self.on_ground:
            self.speed[1] += self.GRAVITY_CONSTANT
            if self.speed[1] > 0 and self.animation_frame != f'mid-air down {self.facing_right}':
                self.image = self.get_image(self.mid_air_images, 1)
                self.animation_frame = f'mid-air down {self.facing_right}'
            elif 0 > self.speed[1] >= -12 and self.animation_frame != f'mid-air up {self.facing_right}':
                self.image = self.get_image(self.mid_air_images, 0)
                self.animation_frame = f'mid-air up {self.facing_right}'

    def update(self, seconds_passed=1/60):
        self.gravity()
        self.rect.y += self.speed[1]

        platform_hit_list = pygame.sprite.spritecollide(self, self.world.platform_list, False) 

        for platform in platform_hit_list:
            if self.speed[1] > 0 and self.rect.bottom > platform.rect.top + self.GROUND_ADJUSTMENT:
                self.rect.bottom = platform.rect.top + self.GROUND_ADJUSTMENT
                self.speed[1] = 0
            elif self.speed[1] < 0 and platform.rect.top < self.rect.top < platform.rect.bottom: 
                self.rect.top = platform.rect.bottom
                self.speed[1] = 0

        self.rect.x += self.speed[0]
        platform_hit_list = pygame.sprite.spritecollide(self, self.world.platform_list, False)
        for platform in platform_hit_list:
            if (self.speed[0] > 0 and
                    platform.rect.left < self.rect.right and
                    platform.rect.top + self.GROUND_ADJUSTMENT < self.rect.bottom):
                self.rect.right = platform.rect.left 
            elif (self.speed[0] < 0 and
                  platform.rect.right > self.rect.left and
                  platform.rect.top + self.GROUND_ADJUSTMENT < self.rect.bottom):
                self.rect.left = platform.rect.right 
        if self.speed == [0, 0]: 
            self.update_idle()
            self.animation_frame = 'idle'
        elif self.speed[0] != 0 and self.on_ground:
            self.update_running()
            self.animation_frame = 'running'
        return self.rect

    def stop(self, pressed_keys):

        if self.speed[0] == 0:
            if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]: 
                self.speed[0] += self.RUNNING_SPEED
            if pressed_keys[pygame.K_LEFT]  or pressed_keys[pygame.K_a]: 
                self.speed[0] -= self.RUNNING_SPEED
            if self.speed[0] > 0: 
                self.facing_right = True
            if self.speed[0] < 0: 
                self.facing_right = False

        elif not(pressed_keys[pygame.K_LEFT] and pressed_keys[pygame.K_a] and pressed_keys[pygame.K_RIGHT] and pressed_keys[pygame.K_d]):
            if self.on_ground: 
                self.image = self.get_image(self.idle_images, True)
            self.speed[0] = 0

    def force_stop(self):
        self.speed = [0, 0]

    def go_left(self):
        if self.speed[0] > -self.RUNNING_SPEED: 
            self.speed[0] -= self.RUNNING_SPEED
        self.facing_right = False


    def go_right(self):
        if self.speed[0] < self.RUNNING_SPEED: 
            self.speed[0] += self.RUNNING_SPEED
        self.facing_right = True
    def jump(self):
        if self.on_ground:
            pygame.mixer.Channel(0).play(JUMP_SOUND)
            self.image = self.get_image(self.jump_images)
            self.speed[1] = self.JUMP_SPEED
            self.on_ground = False
            self.animation_frame = 'jump'

    def update_rect(self):
        pos = self.rect.bottomleft
        self.rect: pygame.Rect = self.image.get_rect()
        collide_width = self.rect.width - 8 * self.scale_factor
        self.rect.bottomleft = pos
        self.collide_rect: pygame.Rect = pygame.rect.Rect((0, 0), (collide_width, self.rect.height))
        self.collide_rect.midbottom = self.rect.midbottom


class Platform(pygame.sprite.Sprite):
    PERCENT_OF_SCREEN_HEIGHT = 0.07901234567901234
    GROUND_ADJUSTMENT = ceil(0.1111111111111111 * 0.07901234567901234 * CURRENT_H)
    TILESET_SIDELENGTH = 27
    scale_factor = PERCENT_OF_SCREEN_HEIGHT * CURRENT_H / TILESET_SIDELENGTH
    images = extract_platforms(scale_factor=scale_factor)
    images = {'left': images[0], 'centre': images[1], 'right': images[2]}

    def __init__(self, x, y, platform_type='centre'):
        super(Platform, self).__init__()
        self.image = self.images[platform_type.lower()]
        self.rect = self.image.get_rect()
        w, h = self.image.get_size()
        w -= self.GROUND_ADJUSTMENT * 2
        h -= self.GROUND_ADJUSTMENT
        self.collide_rect = pygame.rect.Rect((0, 0), (w, h))
        self.rect.topleft = (x, y)
        self.collide_rect.midbottom = self.rect.midbottom


class World:

    def __init__(self):
        TILESET_SIDELENGTH = Platform.TILESET_SIDELENGTH
        self.platform_list = pygame.sprite.Group()
        self.player = None
        self.screen_width, self.screen_height = CURRENT_W, CURRENT_H
        self.scale_factor = 0.07901234567901234 * CURRENT_H / TILESET_SIDELENGTH
        self.tileset_new_sidelength = int(TILESET_SIDELENGTH * self.scale_factor)
        self.number_of_spots = self.screen_width // self.tileset_new_sidelength
        pos_y = self.screen_height - self.tileset_new_sidelength
        for pos_x in range(0, self.screen_width, self.tileset_new_sidelength):
            platform = Platform(pos_x, pos_y)
            self.platform_list.add(platform)
        for x in range(3, ceil(self.screen_height / self.tileset_new_sidelength), 4):
            self.create_platforms(self.screen_height - self.tileset_new_sidelength * (x + 1))

    def draw(self, screen):
        self.platform_list.draw(screen)

    def set_player(self, player: Player):
        player.rect.bottom = CURRENT_H - self.tileset_new_sidelength + player.GROUND_ADJUSTMENT
        player.collide_rect.midbottom = player.rect.midbottom
        self.player = player

    def create_platforms(self, pos_y):
        safe_spaces = 1.75, 2, 2.5, 3, 3.5, 4
        starting_pos = int(random.choice([-1, 0, 1, 1.5]) * self.tileset_new_sidelength)
        safety = starting_pos - 1
        for x in range(starting_pos, self.screen_width, int(self.tileset_new_sidelength * 0.25)):
            if x > safety:
                max_tiles = max(((self.screen_width - x) // self.tileset_new_sidelength), 2)
                num_of_tiles = min(random.randint(3, 10), max_tiles)
                safety = x + num_of_tiles * self.tileset_new_sidelength + random.choice(
                    safe_spaces) * self.tileset_new_sidelength
                for tile_number in range(num_of_tiles):
                    if tile_number == 0: platform_type = 'left'
                    elif tile_number == num_of_tiles - 1:  platform_type = 'right'
                    else: platform_type = 'centre'
                    platform = Platform(x + tile_number * self.tileset_new_sidelength, pos_y, platform_type)
                    self.platform_list.add(platform)

    def shift_world(self, shift_y=0, shift_x=0):
        platforms_to_remove = []
        highest_y = self.screen_height
        self.player.rect.y += shift_y
        self.player.rect.x += shift_x
        self.player.collide_rect.y += shift_y
        self.player.collide_rect.x += shift_x

        for platform in self.platform_list:
            platform.rect.y += shift_y
            platform.collide_rect.y += shift_y
            platform.rect.x += shift_x
            platform.collide_rect.x += shift_x
            if platform.rect.y < highest_y:
                highest_y = platform.rect.y
            if platform.rect.top > self.screen_height + self.player.rect.height:
                platforms_to_remove.append(platform)
        if platforms_to_remove:
            self.platform_list.remove(platforms_to_remove)
            platforms_to_remove.clear()
        if highest_y > -self.tileset_new_sidelength * 3:
            self.create_platforms(highest_y - self.tileset_new_sidelength * 4)

    def update(self):
        self.platform_list.update()
