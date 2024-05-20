import pygame
import random
import math
from pygame.locals import *
from enum import Enum
import start_screen

# 初始化 pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("小猫钓鱼")
start_image = pygame.image.load("image/start1.png")
failure_image=pygame.image.load("image/fail3.png")
win_image=pygame.image.load("image/happy2.png")
start_image = pygame.transform.scale(start_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# 字体
font = pygame.font.Font(None, 48)
title_font = pygame.font.Font("font/Portcullion.ttf", 100)  # 加载自定义字体，大小为72
font = pygame.font.Font(None, 48)  # 常规文字的字体和大小

# 游戏音乐变量
game_music_on = True

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GOLD_COLOR = (255, 215, 0)
GREEN = (0, 255, 0)
# 游戏变量
gold_num=10#普通金币鱼数量
diamond_num=5#珍贵矿石鱼数量
super_mineral_num=1#会说话的鱼数量
HOOK_SPEED = 2#鱼钩速度
HOOK_ANGLE_SPEED = 0.02#鱼钩摇摆速度
MAX_HOOK_LENGTH = 600#最大长度
MIN_HOOK_LENGTH = 80#最小长度
MAX_HOOK_ANGLE = -math.pi  # -180度（上限）
MIN_HOOK_ANGLE = -math.pi * 2  # -270度（下限）
TARGET_SCORE_BASE = 800  # 基础目标分数
clock = pygame.time.Clock()
time_limit_base = 45 # 倒计时时间（秒）
game_over = False
win = False
score = 0
special_message = ''  # 寄语
# 加载图像
bg = pygame.image.load('image/background_1.png') if pygame.image.get_extended() else pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
hook_image = pygame.image.load('image/hook.png') if pygame.image.get_extended() else pygame.Surface((20, 20))
gold_image = pygame.image.load('image/fish1.png') if pygame.image.get_extended() else pygame.Surface((20, 20))
diamond_image = pygame.image.load('image/fish2.png') if pygame.image.get_extended() else pygame.Surface((20, 20))
super_mineral_image = pygame.image.load('image/book_fish.png') if pygame.image.get_extended() else pygame.Surface((40, 40))
book_image = pygame.image.load('image/book_gosh.png') if pygame.image.get_extended() else pygame.Surface((40, 40))
dialog_image = pygame.image.load('image/dialog.png') if pygame.image.get_extended() else pygame.Surface((150, 50))

bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
hook_image = pygame.transform.scale(hook_image, (20, 20))
gold_image = pygame.transform.scale(gold_image, (40, 40))
diamond_image = pygame.transform.scale(diamond_image, (80, 60))
super_mineral_image = pygame.transform.scale(super_mineral_image, (100, 80))
book_image = pygame.transform.scale(book_image, (150, 90))
dialog_image = pygame.transform.scale(dialog_image, (400, 100))

# 游戏字体
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

sound_played_victory = False
sound_played_failure = False
# 游戏音乐文件
go_sound = pygame.mixer.Sound("music/fishingsteel_go.mp3")
back_sound = pygame.mixer.Sound("music/fishingsteel_back.mp3")
yeah_sound = pygame.mixer.Sound('music/fishing_Yeah.mp3')
success_sound = pygame.mixer.Sound("music/success.mp3")
failed_sound = pygame.mixer.Sound("music/fail.mp3")
def return_to_start_screen(screen, game_music_on):
    # 调用 start_screen 并更新音乐状态
    game_music_on = start_screen.start_screen(screen, game_music_on)
    return game_music_on  # 可以选择返回更新后的音乐状态
def play_sound(sound):
    sound.play()

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    VICTORY = 3
    FAILURE = 4


class Button:
    def __init__(self, text, x, y, width, height, color, font, action=None, border_radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = (int(color[0] * 0.8), int(color[1] * 0.8), int(color[2] * 0.8))  # 暗色版本
        self.text = text
        self.font = font
        self.action = action
        self.border_radius = border_radius
        self.is_hovered = False

    def draw(self, screen):
        # 如果鼠标悬浮则使用hover_color，否则使用正常颜色
        fill_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, fill_color, self.rect, border_radius=self.border_radius)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def check_hover(self, mouse_pos):
        # 检测鼠标位置是否在按钮范围内
        if self.rect.collidepoint(mouse_pos):
            self.is_hovered = True
        else:
            self.is_hovered = False

#鱼钩
class Hook:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2-82
        self.y = 35
        self.angle = -5 * math.pi / 4  # 从 -225 度开始
        self.length = MIN_HOOK_LENGTH
        self.state = 'swing'
        self.angle_speed = HOOK_ANGLE_SPEED
        self.target = None

    def update(self):
        global score
        if self.state == 'swing':
            self.angle += self.angle_speed
            if self.angle >= MAX_HOOK_ANGLE or self.angle <= MIN_HOOK_ANGLE:
                self.angle_speed *= -1

        elif self.state == 'extend':
            self.length += HOOK_SPEED
            if self.length >= MAX_HOOK_LENGTH:
                self.state = 'retract'
                play_sound(back_sound)

        elif self.state == 'retract':
            self.length -= HOOK_SPEED
            if self.length <= MIN_HOOK_LENGTH:
                if self.target:
                    play_sound(yeah_sound)
                    score += self.target.value
                    self.target = None
                self.state = 'swing'

        if self.target:
            self.target.update_position(self.x + self.length * math.cos(self.angle),
                                        self.y + self.length * math.sin(self.angle))

    def draw(self):
        end_x = self.x + self.length * math.cos(self.angle)
        end_y = self.y + self.length * math.sin(self.angle)
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 2)
        screen.blit(hook_image, (end_x - 10, end_y - 10))

#金币鱼
class Gold:
    def __init__(self):
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = random.randint(180, SCREEN_HEIGHT - 50)
        self.caught = False
        self.speed = random.choice([-2, -1, 1, 2])  # 随机速度：向左或向右
        self.value = 100
        self.flipped = (self.speed > 0)  # 如果速度为负，则翻转图像
        self.image = gold_image

    def update(self):
        if not self.caught:
            self.x += self.speed

            # 在屏幕边缘反弹
            if self.x <= 20 or self.x >= SCREEN_WIDTH - 20:
                self.speed *= -1
                self.flipped = not self.flipped  # 更新翻转状态

    def draw(self, hook):
        if not self.caught or hook.target == self:
            current_image = self.image
            if self.flipped:
                current_image = pygame.transform.flip(self.image, True, False)
            screen.blit(current_image, (self.x - current_image.get_width() // 2, self.y - current_image.get_height() // 2))

    def update_position(self, x, y):
        self.x = x
        self.y = y


#钻石鱼
class Diamond:
    def __init__(self):
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = random.randint(180, SCREEN_HEIGHT - 50)
        self.caught = False
        self.speed = random.choice([-3, -2, 2, 3])  # 更快的速度
        self.value = 300  # 更高的得分
        self.flipped=False
        self.image=diamond_image
        self.flipped = (self.speed > 0)  # 如果速度为负，则翻转图像

    def update(self):
        if not self.caught:
            self.x += self.speed

            if self.x <= 20 or self.x >= SCREEN_WIDTH - 20:
                self.speed *= -1
                self.flipped=not self.flipped

    def draw(self, hook):
        if not self.caught or hook.target == self:
            if self.flipped:
                flipped_image = pygame.transform.flip(self.image, True, False)
                screen.blit(flipped_image,
                            (self.x - self.image.get_width() // 2, self.y - self.image.get_height() // 2))
            else:
                screen.blit(self.image, (self.x - self.image.get_width() // 2, self.y - self.image.get_height() // 2))

    def update_position(self, x, y):
        self.x = x
        self.y = y

#会说话的鱼
class SuperMineral:
    def __init__(self):
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = random.randint(180, SCREEN_HEIGHT - 50)
        self.caught = False
        self.speed = random.choice([-2, -1, 1, 2])  # 随机速度：向左或向右
        self.value = 0  # 更高的得分
        self.flipped=False
        self.image=super_mineral_image
        self.flipped = (self.speed > 0)  # 如果速度为负，则翻转图像

    def update(self):
        if not self.caught:
            self.x += self.speed

            # 在屏幕边缘反弹
            if self.x <= 20 or self.x >= SCREEN_WIDTH - 20:
                self.speed *= -1
                self.flipped=not self.flipped


    def draw(self, hook):
        if not self.caught or hook.target == self:
            if self.flipped:
                flipped_image = pygame.transform.flip(self.image, True, False)
                screen.blit(flipped_image,
                            (self.x - self.image.get_width() // 2, self.y - self.image.get_height() // 2))
            else:
                screen.blit(self.image, (self.x - self.image.get_width() // 2, self.y - self.image.get_height() // 2))

    def update_position(self, x, y):
        self.x = x
        self.y = y


# 初始化与 SuperMineral 捕获相关的全局变量
show_book = False
book_display_time = 0


def draw_dialog_with_book():
    """绘制对话框和会说话的书籍/鱼"""
    screen.blit(dialog_image, (SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT // 2 - 150))
    screen.blit(book_image, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 100))
    message_text = font.render('I wish you add your time', True, BLACK)
    screen.blit(message_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 130))


# 定义不同游戏状态对应的界面绘制函数
def draw_menu():
    screen.blit(start_image, (0, 0))
    draw_text("Catty Fishing", title_font, BLACK, screen, SCREEN_WIDTH // 2, 100, center=True)  # 添加标题
    start_button.draw(screen)
    return_button.draw(screen)  # 绘制返回按钮
    pygame.display.flip()
def draw_text(text, font, color, surface, x, y, center=False):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

def draw_playing(hook, golds, diamonds, super_minerals, time_left):
    screen.blit(bg, (0, 0))

    hook.draw()

    for gold in golds:
        gold.draw(hook)

    for diamond in diamonds:
        diamond.draw(hook)

    for super_mineral in super_minerals:
        super_mineral.draw(hook)



    score_text = font.render(f' {score}', True, BLACK)
    screen.blit(score_text, (150, 25))
    target_score_text = font.render(f' {TARGET_SCORE}', True, BLACK)
    screen.blit(target_score_text, (150, 80))
    time_text = font.render(f'   {int(time_left)}', True, BLACK)
    screen.blit(time_text, (700, 25))
    level_text=font.render(f"{current_level}", True, BLACK)
    screen.blit(level_text, (710, 80))
    tip_text = font.render("press [Space] to fish ", True, WHITE)  # 添加游戏提示
    screen.blit(tip_text, (280, 560))
    # screen.blit(score_text, (20, 20))
    # screen.blit(target_score_text, (20, 50))
    # screen.blit(time_text, (20, 80))

    if show_book:
        draw_dialog_with_book()

    pygame.display.flip()

#胜利界面
def draw_victory():
    global sound_played_victory
    screen.blit(win_image, (0, 0))
    # draw_text("Catty Fishing", title_font, BLACK, screen, SCREEN_WIDTH // 2, 100, center=True)  # 添加标题
    victory_text = large_font.render("You Got The Target!", True, BLACK)
    screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 4))
    next_level_button.draw(screen)
    main_menu_button.draw(screen)
    pygame.display.flip()

#失败界面
def draw_failure():
    global sound_played_failure
    screen.blit(failure_image, (0, 0))
    # draw_text("Catty Fishing", title_font, BLACK, screen, SCREEN_WIDTH // 2, 100, center=True)  # 添加标题
    failure_text = large_font.render("OH NO Failure Fishing", True, BLACK)
    screen.blit(failure_text, (SCREEN_WIDTH // 2 - failure_text.get_width() // 2, SCREEN_HEIGHT // 4))
    retry_button.draw(screen)
    main_menu_button.draw(screen)
    pygame.display.flip()



# 按钮实例
def start_game():

    global state,start_ticks
    state = GameState.PLAYING
    start_ticks=pygame.time.get_ticks()
    # print("start_game更新的时间：",start_ticks)
    initialize_targets()  # 初始化目标物品


#下一关卡
def next_level():
    global state, current_level, TARGET_SCORE, score, start_ticks, time_limit, game_over, win, show_book, book_display_time
    current_level += 1
    TARGET_SCORE = TARGET_SCORE_BASE + current_level*100
    score = 0
    time_limit = time_limit_base
    start_ticks = pygame.time.get_ticks()
    game_over = False
    win = False
    show_book = False
    book_display_time = 0
    state = GameState.PLAYING
    play_sound(success_sound)
    # print("Next level started: ", state)  # Debug: Print new game state
    initialize_targets()  # 重新生成目标物品

#重玩当前关卡
def retry_level():
    global state, score, start_ticks, time_limit, game_over, win, show_book, book_display_time, time_left, golds, diamonds, super_minerals
    score = 0
    start_ticks = pygame.time.get_ticks()  # 获取当前的时间戳
    time_limit = time_limit_base
    game_over = False
    win = False
    show_book = False
    book_display_time = 0
    state = GameState.PLAYING
    # play_sound(failed_sound)
    initialize_targets()  # 重新生成目标物品


def main_menu():
    global state, score, current_level
    score = 0
    current_level = 1
    state = GameState.MENU



start_button = Button(
    "enter", SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 25, 150, 50, WHITE, font,
    action=start_game, border_radius=15
)
# 在游戏胜利界面的按钮
next_level_button = Button(
    "Next", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 25, 150, 50, WHITE, font,
    action=next_level, border_radius=15
)

retry_button = Button(
    "retry", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 25, 150, 50, WHITE, font,
    action=retry_level, border_radius=15
)

main_menu_button = Button(
    "back", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 50, 150, 50, WHITE, font,
    action=main_menu, border_radius=15
)
return_button = Button(
    "back", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 100, 150, 50, WHITE, font,
    action=return_to_start_screen, border_radius=15
)

# 全局游戏状态变量
state = GameState.MENU
current_level = 1
TARGET_SCORE = TARGET_SCORE_BASE * current_level
score = 0
time_limit = time_limit_base + (current_level - 1) * 10
start_ticks = 0
game_over = False
win = False
def initialize_targets():
    global golds, diamonds, super_minerals
    golds = [Gold() for _ in range(gold_num)]
    diamonds = [Diamond() for _ in range(diamond_num)]
    super_minerals = [SuperMineral() for _ in range(super_mineral_num)]

def main():
    pygame.init()
    global state,score, time_limit, game_over, win, special_message, show_book, book_display_time, game_music_on,start_ticks

    # 调用开始界面
    game_music_on = start_screen.start_screen(screen, game_music_on)

    hook = Hook()
    # golds = [Gold() for _ in range(gold_num)]
    # diamonds = [Diamond() for _ in range(diamond_num)]
    # super_minerals = [SuperMineral() for _ in range(super_mineral_num)]

    running = True
    start_ticks = pygame.time.get_ticks()

    while running:
        mouse_pos = pygame.mouse.get_pos()
        start_button.check_hover(mouse_pos)  # 更新开始按钮的悬浮状态
        next_level_button.check_hover(mouse_pos)  # 更新下一关按钮的悬浮状态
        retry_button.check_hover(mouse_pos)  # 更新重试按钮的悬浮状态
        main_menu_button.check_hover(mouse_pos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if state == GameState.MENU:
                    if start_button.is_clicked(pos):
                        start_button.action()
                    elif return_button.is_clicked(pos):
                        return_button.action(screen,game_music_on)  # 处理返回按钮的点击事件
                elif state == GameState.VICTORY:
                    if next_level_button.is_clicked(pos):
                        next_level_button.action()
                    elif main_menu_button.is_clicked(pos):
                        main_menu_button.action()
                elif state == GameState.FAILURE:
                    if retry_button.is_clicked(pos):
                        print("retry button clicked")
                        retry_button.action()
                    elif main_menu_button.is_clicked(pos):
                        main_menu_button.action()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and hook.state == 'swing':
                    play_sound(go_sound)
                    hook.state = 'extend'


        if state == GameState.MENU:
            draw_menu()
        elif state == GameState.PLAYING:
            seconds = (pygame.time.get_ticks() - start_ticks) / 1000  # 从开始到现在过了多少秒

            time_left = max(0, time_limit - seconds)  # 更新剩余时间
            # print("main的秒数时间戳",seconds)
            # print("剩余时间",time_left)
            # 更新钩子和小鱼对象
            hook.update()
            for gold in golds:
                gold.update()
                if not gold.caught and math.hypot(hook.x + hook.length * math.cos(hook.angle) - gold.x,
                                                  hook.y + hook.length * math.sin(hook.angle) - gold.y) < 20 and hook.state == 'extend':
                    hook.state = 'retract'
                    hook.target = gold
                    gold.caught = True

            for diamond in diamonds:
                diamond.update()
                if not diamond.caught and math.hypot(hook.x + hook.length * math.cos(hook.angle) - diamond.x,
                                                     hook.y + hook.length * math.sin(hook.angle) - diamond.y) < 20 and hook.state == 'extend':
                    hook.state = 'retract'
                    hook.target = diamond
                    diamond.caught = True

            for super_mineral in super_minerals:
                super_mineral.update()
                if not super_mineral.caught and math.hypot(hook.x + hook.length * math.cos(hook.angle) - super_mineral.x,
                                                          hook.y + hook.length * math.sin(hook.angle) - super_mineral.y) < 20 and hook.state == 'extend':
                    hook.state = 'retract'
                    hook.target = super_mineral
                    super_mineral.caught = True
                    time_limit += 25
                    show_book = True
                    book_display_time = pygame.time.get_ticks()
            if show_book:
                draw_dialog_with_book()
                # 如果显示时间超过3秒，则隐藏
                if pygame.time.get_ticks() - book_display_time > 3000:
                    show_book = False
            # 判断是否超时
            if time_left == 0:
                game_over = True
                win = score >= TARGET_SCORE
                if win:
                    state = GameState.VICTORY
                    play_sound(success_sound)
                else:
                    state = GameState.FAILURE
                    play_sound(failed_sound)
                print(f"Game Over: {'WIN' if win else 'LOSS'} - State set to {'VICTORY' if win else 'FAILURE'}")

            draw_playing(hook, golds, diamonds, super_minerals, time_left)
        elif state == GameState.VICTORY:
            draw_victory()
            # play_sound(success_sound)
        elif state == GameState.FAILURE:
            draw_failure()
            # play_sound(failed_sound)
        else:
            seconds = 0
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()



