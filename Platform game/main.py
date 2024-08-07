import io
import platform
import sys
import json
import base64
from pygame import gfxdraw, K_w, K_a, K_d, K_UP, K_LEFT, K_RIGHT, K_ESCAPE, K_F4, K_p, K_RALT, K_LALT, K_SPACE, \
    MOUSEBUTTONDOWN, QUIT, KEYUP, KEYDOWN, K_TAB, K_v, K_h, K_BACKSPACE, K_q, K_m, K_r
import pygame

WHITE = 255, 255, 255
BLACK = 0, 0, 0
MATTE_BLACK = 20, 20, 20
GREEN = 40, 175, 99
RED = 255, 0, 0
YELLOW = 250, 237, 39
DARK_GREEN = 0, 128, 0
LIGHT_BLUE = 0, 191, 255
GREY = 204, 204, 204
BLUE = 33, 150, 243
BACKGROUND = 205,255,221
WORLD_SHIFT_SPEED_PERCENT = 0.00135
FONT_BOLD = 'assets/fonts/OpenSans-SemiBold.ttf'
FONT_REG = 'assets/fonts/OpenSans-Regular.ttf'
FONT_LIGHT = 'assets/fonts/OpenSans-Light.ttf'
CONFIG_FILE = 'config.json'
config = {'DEBUG': False, 'show_score': True,
          'high_scores': [0, 0, 0, 0, 0, 0, 0, 0, 0]}
music_playing = False
delta_time = 0

def save_config():
    with open(CONFIG_FILE, 'w') as fp:
        json.dump(config, fp, indent=4)

try:
    with open(CONFIG_FILE) as f:
        _config = json.load(f)
except FileNotFoundError: _config = {}
save_file = False
for k, v in config.items():
    try: config[k] = _config[k]
    except KeyError: save_file = True
if save_file: save_config()
DEBUG = config['DEBUG']


def text_objects(text, font, colour=BLACK):
    text_surface = font.render(text, True, colour)
    return text_surface, text_surface.get_rect()


def create_hud_text(text, color):
    text_surf, text_rect = text_objects(text, HUD_TEXT, color)
    text_rect.topleft = -2, -5
    bg_w, text_bg_h = text_surf.get_size()
    bg_w += 10
    bg = pygame.Surface((bg_w, text_bg_h), pygame.SRCALPHA, 32)
    bg.fill((50, 50, 50, 160))
    bg.blit(text_surf, (5, 0))
    return bg, text_rect


def save_score(user_score: int) -> bool:
    scores = config['high_scores']
    placement = None
    for i, score in enumerate(scores):
        if user_score > score:
            placement = i
            break
    if placement is not None:
        scores.insert(placement, user_score)
        scores.pop()
        save_config()
        return True
    return False


def button(text, x, y, w, h, click, inactive_colour=BLUE, active_colour=LIGHT_BLUE, text_colour=WHITE):
    mouse = pygame.mouse.get_pos()
    return_value = False
    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        pygame.draw.rect(SCREEN, active_colour, (x, y, w, h))
        if click and pygame.time.get_ticks() > 100: return_value = True
    else: pygame.draw.rect(SCREEN, inactive_colour, (x, y, w, h))

    text_surf, text_rect = text_objects(text, SMALL_TEXT, colour=text_colour)
    text_rect.center = (int(x + w / 2), int(y + h / 2))
    SCREEN.blit(text_surf, text_rect)
    return return_value


def draw_circle(surface, x, y, radius, color):
    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.filled_circle(surface, x, y, radius, color)


def toggle_btn(text, x, y, w, h, click, text_colour=BLACK, enabled=True, draw_toggle=True, blit_text=True,
               enabled_color=LIGHT_BLUE, disabled_color=GREY):
    mouse = pygame.mouse.get_pos()
    rect_height = h // 2
    if rect_height % 2 == 0: 
        rect_height += 1
    if enabled and draw_toggle:
        pygame.draw.rect(SCREEN, WHITE, (x + TOGGLE_WIDTH - h // 4, y, TOGGLE_ADJ + h, rect_height))
        pygame.draw.rect(SCREEN, enabled_color, (x + TOGGLE_WIDTH, y, TOGGLE_ADJ, rect_height))
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH), y + h // 4, h // 4, enabled_color)
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH + TOGGLE_ADJ), y + h // 4, h // 4, enabled_color)
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH + TOGGLE_ADJ), y + h // 4, h // 5, WHITE) 
    elif draw_toggle:
        pygame.draw.rect(SCREEN, WHITE, (x + TOGGLE_WIDTH - h // 4, y, TOGGLE_ADJ + h, rect_height))
        pygame.draw.rect(SCREEN, disabled_color, (x + TOGGLE_WIDTH, y, TOGGLE_ADJ, rect_height))
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH), y + h // 4, h // 4, disabled_color)
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH + TOGGLE_ADJ), y + h // 4, h // 4, disabled_color)
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH), y + h // 4, h // 5, WHITE) 
    if blit_text:
        text_surf, text_rect = text_objects(text, MEDIUM_TEXT, colour=text_colour)
        text_rect.topleft = (x, y)
        SCREEN.blit(text_surf, text_rect)
    return x < mouse[0] < x + w and y < mouse[1] < y + h and click and pygame.time.get_ticks() > 100


def view_high_scores():
    SCREEN.fill(WHITE)
    text_surf, text_rect = text_objects('High Scores', MENU_TEXT)
    text_rect.center = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 6))
    SCREEN.blit(text_surf, text_rect)
    for i, score in enumerate(config['high_scores']):
        text_surf, text_rect = text_objects(str(score), LARGE_TEXT)
        text_rect.center = (SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * (i / 1.5 + 3) // 11))
        SCREEN.blit(text_surf, text_rect)
    on_high_scores = True
    pygame.display.update()
    back_button_rect = ((SCREEN_WIDTH - BUTTON_WIDTH) // 2, SCREEN_HEIGHT * 4 // 5, BUTTON_WIDTH, BUTTON_HEIGHT)
    while on_high_scores:
        click = False
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and event.key == pygame.K_F4
                      and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]))
            if event.type == QUIT or alt_f4: sys.exit()
            elif event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_BACKSPACE): on_high_scores = False
            elif event.type == MOUSEBUTTONDOWN: click = True
        if button('B A C K', *back_button_rect, click): break
        pygame.display.update([back_button_rect])
        clock.tick(60)


def main_menu_setup():
    SCREEN.fill(WHITE)
    text_surf, text_rect = text_objects('Pltaform game', MENU_TEXT)
    text_rect.center = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 4))
    SCREEN.blit(text_surf, text_rect)
    pygame.display.update()


def main_menu():
    global ticks
    main_menu_setup()
    start_game = view_hs = False
    while True:
        click = False
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and (event.key == K_F4
                      and (pressed_keys[K_LALT] or pressed_keys[K_RALT])
                      or event.key == K_q or event.key == K_ESCAPE))
            if event.type == QUIT or alt_f4: sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE: start_game = True
            elif event.type == KEYDOWN and (event.key == K_v or event.key == K_h): view_hs = True
            elif event.type == MOUSEBUTTONDOWN: click = True

        if button('S T A R T  G A M E', *button_layout_4[0], click): start_game = True
        elif button('H I G H S C O R E S', *button_layout_4[1], click) or view_hs:
            view_high_scores()
            view_hs = False
            main_menu_setup()
        elif button('Q U I T  G A M E', *button_layout_4[2], click): 
            sys.exit()
        if start_game:
            while start_game: 
                start_game = game() == 'Restart'
            main_menu_setup()
        pygame.display.update(button_layout_4)
        clock.tick(60)


def settings_menu():
    SCREEN.fill(WHITE)
    text_surf, text_rect = text_objects('Settings', MENU_TEXT)
    text_rect.center = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 4))
    SCREEN.blit(text_surf, text_rect)
    pygame.display.update()
    first_run = draw_bg_toggle = draw_jump_toggle = True
    while True:
        click = False
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and (event.key == K_F4 and (pressed_keys[K_LALT] or pressed_keys[K_RALT]) or event.key == K_q))
            if event.type == QUIT or alt_f4: 
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE: 
                return
            elif event.type == MOUSEBUTTONDOWN: 
                click = True
        if toggle_btn('Background Music', *button_layout_4[0], click, enabled=config['background_music'], draw_toggle=draw_bg_toggle, blit_text=first_run):
            config['background_music'] = not config['background_music']
            save_config()
            draw_bg_toggle = True
        elif toggle_btn('Jump Sound', *button_layout_4[1], click, enabled=config['jump_sound'], draw_toggle=draw_jump_toggle, blit_text=first_run):
            config['jump_sound'] = not config['jump_sound']
            save_config()
            draw_jump_toggle = True
        elif button('B A C K', *button_layout_4[2], click): 
            return
        else:
            draw_bg_toggle = draw_jump_toggle = False
        first_run = False
        pygame.display.update(button_layout_4)
        clock.tick(60)


def pause_menu_setup(background):
    SCREEN.blit(background, (0, 0))
    background = SCREEN.copy()
    text_surf, text_rect = text_objects('Paused', MENU_TEXT, colour=WHITE)
    text_rect.center = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 4))
    SCREEN.blit(text_surf, text_rect)
    pygame.display.update()
    return background


def pause_menu(player):
    paused = True
    facing_left = player.facing_right  
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
    background.fill((*MATTE_BLACK, 160))
    background = pause_menu_setup(background)
    while paused:
        click = False
        pks = pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and event.key == K_F4
                      and (pressed_keys[K_LALT] or pressed_keys[K_RALT]))
            if event.type == pygame.QUIT or alt_f4: 
                sys.exit()
            elif event.type == KEYDOWN:
                right_key = event.key == K_RIGHT and not pks[K_d] or event.key == K_d and not pks[K_RIGHT]
                left_key = event.key == K_LEFT and not pks[K_a] or event.key == K_a and not pks[K_LEFT]
                if right_key: 
                    player.go_right()
                elif left_key: 
                    player.go_left()
                elif event.key in (pygame.K_ESCAPE, pygame.K_p): paused = False
                elif event.key == K_m: 
                    return 'Main Menu'
                elif event.key == K_SPACE: 
                    return 'Resume'
                elif event.key == K_q: 
                    sys.exit()
            elif event.type == MOUSEBUTTONDOWN: click = True
            elif event.type == KEYUP:
                if event.key in (K_d, K_RIGHT, K_a, K_LEFT):
                    player.stop(pygame.key.get_pressed())
                    player.facing_right = facing_left
        if button('R E S U M E', *button_layout_4[0], click): return 'Resume'
        if button('M A I N  M E N U', *button_layout_4[1], click): return 'Main Menu'
        elif button('Q U I T  G A M E', *button_layout_4[2], click): sys.exit()
        pygame.display.update(button_layout_4)
        clock.tick(60)
    return 'Resume'


def end_game_setup(score, surface_copy=None):
    if surface_copy is not None:
        SCREEN.blit(surface_copy, (0, 0))
    else:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
        background.fill((255, 255, 255, 160))
        SCREEN.blit(background, (0, 0))
        text_surf, text_rect = text_objects('Game Over', MENU_TEXT)
        text_rect.center = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 4))
        SCREEN.blit(text_surf, text_rect)
        text_surf, text_rect = text_objects(f'You scored {score}', LARGE_TEXT)
        text_rect.center = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT * 8 // 21))
        SCREEN.blit(text_surf, text_rect)
        surface_copy = pygame.display.get_surface().copy()
    pygame.display.update()
    return surface_copy


def end_game(score):
    view_hs = False
    end_screen_copy = end_game_setup(score)
    if save_score(score): pass
    button_layout_3 = [(button_x_start, SCREEN_HEIGHT * 6 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                       (button_x_start, SCREEN_HEIGHT * 7 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                       (button_x_start, SCREEN_HEIGHT * 8 // 13, BUTTON_WIDTH, BUTTON_HEIGHT)]
    while True:
        click, pressed_keys = False, pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and event.key == pygame.K_F4
                      and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]))
            if event.type == QUIT or alt_f4: 
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_m): 
                return 'Main Menu'
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_r): 
                return 'Restart'
            elif event.type == KEYDOWN and (event.key == K_v or event.key == K_h): view_hs = True
            elif event.type == MOUSEBUTTONDOWN: click = True
        if button('R E S T A R T', *button_layout_3[0], click): 
            return 'Restart'
        if button('M A I N  M E N U', *button_layout_3[2], click): 
            return 'Main Menu'
        elif button('V I E W  H I G H S C O R E S', *button_layout_3[1], click) or view_hs:
            view_high_scores()
            view_hs = False
            end_game_setup(score, end_screen_copy)
        pygame.display.update(button_layout_3)
        clock.tick(60)


def game():
    global delta_time
    world = World()
    player = Player(world)
    player.force_stop()
    world.set_player(player)
    world_shift_speed = 0
    speed_increment = round(WORLD_SHIFT_SPEED_PERCENT * SCREEN_HEIGHT)
    MAX_SPEED = speed_increment * 4
    speed_level, score = 1, 0
    shift_threshold = 0.75 * SCREEN_HEIGHT
    while True:
        '''if not pygame.mouse.get_focused():
            if pause_menu(player) == 'Main Menu': 
                return 'Main Menu'''
        for event in pygame.event.get():
            pressed_keys = pygame.key.get_pressed()
            alt_f4 = (event.type == KEYDOWN and event.key == K_F4 and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]))
            if event.type == QUIT or alt_f4: 
                sys.exit()
            if event.type == KEYDOWN:
                if event.key in (K_UP, K_w, K_SPACE):
                    player.jump()
        pressed_keys = pygame.key.get_pressed()
        right_key = (pressed_keys[pygame.K_RIGHT] and not pressed_keys[pygame.K_d] or pressed_keys[pygame.K_d] and not pressed_keys[pygame.K_RIGHT])
        left_key = (pressed_keys[pygame.K_LEFT] and not pressed_keys[pygame.K_a] or pressed_keys[pygame.K_a] and not pressed_keys[pygame.K_LEFT])
        if right_key and not left_key: 
            player.go_right()
        if left_key and not right_key: 
            player.go_left()
        if pressed_keys[pygame.K_ESCAPE] and not pressed_keys[pygame.K_p] or pressed_keys[pygame.K_p] and not pressed_keys[pygame.K_ESCAPE]:
            if pause_menu(player) == 'Main Menu': 
                return 'Main Menu'
        if not left_key and not right_key:
            player.stop(pressed_keys)
        if left_key and right_key:
            player.stop(pressed_keys)
        player.update(delta_time)
        if world_shift_speed:
            for _ in range(world_shift_speed):
                world.shift_world(1)
                SCREEN.fill(BACKGROUND)
                player.draw(SCREEN)
                world.draw(SCREEN)  
            score += 1
            if score > 1000 * world_shift_speed + (world_shift_speed - 1) * 1000:
                world_shift_speed = min(world_shift_speed + speed_increment, MAX_SPEED)
        else:
            SCREEN.fill(BACKGROUND)
            player.draw(SCREEN)
            world.draw(SCREEN) 
            if player.rect.top < shift_threshold: 
                world_shift_speed = speed_increment
        if DEBUG:
            custom_text = f'Platform Sprites: {len(world.platform_list)}'
            custom_bg, custom_rect = create_hud_text(custom_text, RED)
            custom_rect.topleft = 50, -5
            SCREEN.blit(custom_bg, custom_rect)
        if config['show_score']:
            score_bg, score_rect = create_hud_text(str(score), WHITE)
            score_rect.topright = SCORE_ANCHOR
            SCREEN.blit(score_bg, score_rect)
        pygame.display.update()
        if player.rect.top > SCREEN_HEIGHT + player.rect.height // 2:
            return end_game(score)
        delta_time = clock.tick(60) / 1000  

pygame.mixer.init(frequency=44100, buffer=512)
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = int(pygame.display.Info().current_w), int(pygame.display.Info().current_h)
FULLSCREEN = True
if FULLSCREEN:
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
else:
    SCREEN_WIDTH, SCREEN_HEIGHT = int(0.75 * SCREEN_WIDTH), int(0.75 * SCREEN_HEIGHT)
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
BUTTON_WIDTH = int(SCREEN_WIDTH * 0.625 // 3)
BUTTON_HEIGHT = int(SCREEN_HEIGHT * 5 // 72)
button_x_start = (SCREEN_WIDTH - BUTTON_WIDTH) // 2
button_layout_4 = [(button_x_start, SCREEN_HEIGHT * 2 // 5, BUTTON_WIDTH, BUTTON_HEIGHT),
                   (button_x_start, SCREEN_HEIGHT * 2.38 // 5, BUTTON_WIDTH, BUTTON_HEIGHT),
                   (button_x_start, SCREEN_HEIGHT * 2.76 // 5, BUTTON_WIDTH, BUTTON_HEIGHT)]
TOGGLE_WIDTH = int(BUTTON_WIDTH * 0.875)
TOGGLE_ADJ = int(BUTTON_WIDTH * 0.075)
SCORE_ANCHOR = SCREEN_WIDTH - 8, -5
MENU_TEXT = pygame.font.Font(FONT_LIGHT, int(110 / 1080 * SCREEN_HEIGHT))
LARGE_TEXT = pygame.font.Font(FONT_REG, int(40 / 1080 * SCREEN_HEIGHT))
MEDIUM_TEXT = pygame.font.Font(FONT_LIGHT, int(35 / 1440 * SCREEN_HEIGHT))
SMALL_TEXT = pygame.font.Font(FONT_BOLD, int(25 / 1440 * SCREEN_HEIGHT))
HUD_TEXT = pygame.font.Font(FONT_REG, int(40 / 1440 * SCREEN_HEIGHT))

pygame.display.set_caption('Platform game')
clock = pygame.time.Clock()
ticks = 0
from objects import *
main_menu()
