import pygame
from pygame.locals import *
# 初始化 pygame
pygame.init()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

pygame.init()
# 字体
font = pygame.font.Font(None, 48)
title_font = pygame.font.Font("font/Portcullion.ttf", 100)  # 加载自定义字体，大小为72
font = pygame.font.Font(None, 48)  # 常规文字的字体和大小

# 加载开始界面图片
start_image = pygame.image.load("image/start1.png")
start_image = pygame.transform.scale(start_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# 加载并播放背景音乐
pygame.mixer.init()
# 加载背景音乐
pygame.mixer.music.load("music/backgroundmusic.mp3")

# 播放背景音乐
pygame.mixer.music.play(-1)  # 循环播放
def draw_text(text, font, color, surface, x, y, center=False):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


def draw_button(screen, rect, text, font, color_default, color_hover, mx, my, click):
    color = color_hover if rect.collidepoint((mx, my)) else color_default
    pygame.draw.rect(screen, color, rect)
    draw_text(text, font, BLACK, screen, rect.x + 10, rect.y + 10)
    return click and rect.collidepoint((mx, my))

def start_screen(screen, game_music_on):
    clock = pygame.time.Clock()
    click = False
    music_on = True

    while True:
        screen.blit(start_image, (0, 0))  # 显示开始界面图片
        draw_text("Catty Fishing", title_font, BLACK, screen, SCREEN_WIDTH // 2, 100, center=True)  # 添加标题

        mx, my = pygame.mouse.get_pos()
        button_1 = pygame.Rect(550, 250, 200, 50)
        button_2 = pygame.Rect(550, 350, 200, 50)
        button_3 = pygame.Rect(550, 450, 200, 50)

        if draw_button(screen, button_1, 'Start', font, WHITE, LIGHT_GRAY, mx, my, click):
            return music_on
        if draw_button(screen, button_2, 'Switch Bgm', font, WHITE, LIGHT_GRAY, mx, my, click):
            music_on = not music_on
            if music_on:
                pygame.mixer.music.unpause()  # 继续播放音乐
            else:
                pygame.mixer.music.pause()  # 暂停音乐
        if draw_button(screen, button_3, 'Exit', font, WHITE, LIGHT_GRAY, mx, my, click):
            pygame.quit()
            quit()

        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        clock.tick(60)
