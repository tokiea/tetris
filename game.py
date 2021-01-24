import math
import random
import sys
from copy import deepcopy
import pygame as pg
from pygame.locals import *


pg.init()
pg.display.set_caption('俄罗斯方块')
fclock = pg.time.Clock()

FPS = 20
FONT = pg.font.SysFont('simhei', 30)
WindowX = 18
WindowY = 20
award = 10  # 奖励倍数
BLOCK_SIZE = 30
LINE_SPACE = 2
MAIN_X, MAIN_Y = MAIN_WINDOW = [18, 20]
GAME_X, GAME_Y = GAME_WINDOW = [11, MAIN_Y]
NEXT_X = MAIN_X - GAME_X

RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class BaseBlock:
    def __init__(self):
        self.turn_times = 0
        self.x_move = 0
        self.y_move = 0
        self.location = []


class IBlock(BaseBlock):
    def __init__(self):
        super().__init__()
        self.dot = {
            0: [(0, 1), (0, 0), (0, -1), (0, -2)],
            1: [(-1, 0), (0, 0), (1, 0), (2, 0)],
        }


class OBlock(BaseBlock):
    def __init__(self):
        super().__init__()
        self.dot = {
            0: [(0, 0), (1, 0), (1, 1), (0, 1)],
        }


class LBlock(BaseBlock):
    def __init__(self):
        super().__init__()
        self.dot = {
            0: [(0, 0), (0, 1), (0, -1), (-1, 1)],
            1: [(0, 0), (-1, 0), (1, 0), (1, 1)],
            2: [(0, 0), (0, 1), (0, -1), (1, -1)],
            3: [(0, 0), (1, 0), (-1, 0), (-1, -1)],
        }


class ULBlock(BaseBlock):
    def __init__(self):
        super().__init__()
        self.dot = {
            0: [(0, 0), (0, 1), (0, -1), (1, 1)],
            1: [(0, 0), (-1, 0), (1, 0), (1, -1)],
            2: [(0, 0), (0, 1), (0, -1), (-1, -1)],
            3: [(0, 0), (1, 0), (-1, 0), (-1, 1)],
        }


class TBlock(BaseBlock):
    def __init__(self):
        super().__init__()
        self.dot = {
            0: [(0, 0), (1, 0), (0, 1), (-1, 0)],
            1: [(0, 0), (1, 0), (0, 1), (0, -1)],
            2: [(0, 0), (1, 0), (0, -1), (-1, 0)],
            3: [(0, 0), (0, -1), (0, 1), (-1, 0)],
        }


class SBlock(BaseBlock):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.dot = {
            0: [(0, 0), (0, 1), (-1, 0), (-1, -1)],
            1: [(0, 0), (1, 0), (0, 1), (-1, 1)],
        }


class ZBlock(BaseBlock):
    def __init__(self):
        super().__init__()
        self.dot = {
            0: [(0, 0), (0, 1), (-1, 0), (-1, -1)],
            1: [(0, 0), (1, 0), (0, 1), (-1, 1)],
        }


class Game:
    def __init__(self):
        self.fps = FPS
        self.screen = pg.display.set_mode([MAIN_X * BLOCK_SIZE, MAIN_Y * BLOCK_SIZE])
        self.screen.fill(WHITE)
        self.stop_block = {k: [] for k in range(MAIN_Y)}
        self.level_list = ['简单', '一般', '困难', '地狱']
        self.level = 1
        self.score = 0
        self.next_block = self.create_next()
        self.now_block = None
        self.gaming = False
        self.click_box = []
        self.click_color = RED

    def draw_text(self):
        score_obj = FONT.render('分数: %s' % self.score, True, (0, 0, 0), )
        level_obj = FONT.render('等级: %s' % self.level_list[self.level - 1], True, (0, 0, 0), )
        x, y = self.three.topleft

        self.screen.blit(score_obj, [x + BLOCK_SIZE * 1.5, y + BLOCK_SIZE * 5])
        self.screen.blit(level_obj, [x + BLOCK_SIZE * 1.5, y + BLOCK_SIZE * 7.5])

    @property
    def speed(self):
        # print(round(self.level / 10, 1))
        return round(self.level / 10, 1)

    def start(self):
        if self.gaming:
            if not self.now_block:
                self.change_next()
            self.draw_next_block()
            self.draw_now_block()
            self.draw_stop()
            self.draw_wall()
            self.move()
            remove_line = self.check_full_block()
            if remove_line:
                self.score += award * remove_line
            self.draw_text()
        else:
            self.choice_level()

    def level_add(self):
        if self.level + 1 <= len(self.level_list):
            self.level += 1
        else:
            self.level = 1

    def level_pop(self):
        if self.level - 1 >= 1:
            self.level -= 1
        else:
            self.level = len(self.level_list)

    def to_gaming(self):
        self.gaming = not self.gaming

    def choice_level(self):
        self.screen.fill(WHITE)
        self.click_box = []
        # self.rect = pg.draw.rect(self.screen, BLACK, (0, 0, MAIN_X*BLOCK_SIZE, MAIN_Y*BLOCK_SIZE), LINE_SPACE)

        font1 = FONT.render('排行榜', True, BLACK)

        self.rect1 = pg.draw.rect(self.screen, BLACK, (MAIN_X * BLOCK_SIZE // 2 - 150 // 2, 80, 150, 60), 10)
        # self.click_box.append([self.rect1, self.show_order])

        self.screen.blit(font1,
                         [self.rect1.centerx - font1.get_width() // 2,
                          self.rect1.centery - font1.get_height() // 2])

        self.rect2 = pg.draw.rect(self.screen, BLACK, (MAIN_X * BLOCK_SIZE // 2 - 150 // 2, 200, 150, 60), 10)

        font2 = FONT.render(self.level_list[self.level - 1], True, (0, 0, 0), )
        self.screen.blit(font2,
                         [self.rect2.centerx - font2.get_width() // 2,
                          self.rect2.centery - font2.get_height() // 2])

        self.rect2_left = pg.draw.circle(self.screen, BLACK,
                                         (MAIN_X * BLOCK_SIZE // 2 - 120, self.rect2.y + self.rect2.height // 2), 15, 5)
        self.click_box.append([self.rect2_left, self.level_pop])

        self.rect2_right = pg.draw.circle(self.screen, BLACK,
                                          (MAIN_X * BLOCK_SIZE // 2 + 120, self.rect2.y + self.rect2.height // 2), 15,
                                          5)
        self.click_box.append([self.rect2_right, self.level_add])

        font3 = FONT.render('开始游戏', True, BLACK)
        self.rect3 = pg.draw.rect(self.screen, BLACK, (MAIN_X * BLOCK_SIZE // 2 - 200 // 2, 350, 200, 60), 10)
        self.click_box.append([self.rect3, self.to_gaming])
        self.screen.blit(font3,
                         [self.rect3.centerx - font3.get_width() // 2,
                          self.rect3.centery - font3.get_height() // 2])

    def click_check(self, axis):
        if not self.gaming:
            x, y = axis
            for i in self.click_box:
                if i[0].left <= x <= i[0].right:
                    if i[0].top <= y < i[0].bottom:
                        pg.draw.rect(self.screen,RED,i[0],10)
                        i[1]()

    def change_next(self):
        for i in self.next_block.dot[0]:
            self.now_block = self.next_block
            if not self.stop_check(i):
                print('game over')

                self.now_block.location = []
                # break
                self.__init__()
        self.now_block = self.next_block
        self.now_block.location = [list(i) for i in self.next_block.dot[0]]
        self.next_block = self.create_next()

    def now_block_to_stop(self):
        for x, y in self.now_block.location:
            if math.ceil(y) == -1:
                return
            else:
                y_stop_block = self.stop_block[int(y)]
                # print(5 in y_stop_block)
                if (x + GAME_X // 2) not in y_stop_block:
                    y_stop_block.append(x + GAME_X // 2)
        self.change_next()

    def stop_check(self, axis):

        x, y = axis
        y_stop_block = self.stop_block.get(y)
        if y == int(y):
            if y_stop_block:
                if (x + GAME_X // 2) in y_stop_block:
                    # print(x + GAME_X // 2, y_stop_block, y)
                    return False
            return True
        else:
            y1 = int(y)
            y2 = math.ceil(y)
            check1 = self.stop_check((x, y1))
            check2 = self.stop_check((x, y2))
            if check1 and check2:
                return True
            return False

    def wall_check(self, location):
        wrong = 0
        for x, y in location:
            if x + GAME_X // 2 < 0:
                wrong = 1
            elif x + GAME_X // 2 > 10:
                wrong = -1
        if wrong:
            for i in location:
                i[0] += wrong
            self.wall_check(location)
        return location

    def move_check(self):
        for x, y in self.now_block.location:
            z = round(y + self.speed, 1)
            if self.stop_check((x, y)):
                pass
            else:
                return False

            if z <= MAIN_Y - 1:  # (0-19)
                # 到达底部墙体
                pass
            else:
                return False
        return True

    def move(self, ):
        if self.move_check():
            for i in self.now_block.location:
                i[1] = round(self.speed + i[1], 1)
            self.now_block.y_move = round(self.speed + self.now_block.y_move, 1)
        else:
            self.now_block_to_stop()

    def change_block(self):
        new_location = []
        dot = self.now_block.dot
        index = self.now_block.turn_times % len(dot.keys())
        for x, y in self.now_block.dot[index]:
            new_location.append([x + self.now_block.x_move, y + self.now_block.y_move])

        return new_location

    def turn(self, direction):

        location_copy = deepcopy(self.now_block.location)
        turn_switch = 0
        if direction == 'LEFT':
            for i in location_copy:
                i[0] -= 1

        elif direction == 'RIGHT':
            for i in location_copy:
                i[0] += 1
        elif direction == 'UP':
            self.now_block.turn_times += 1
            location_copy = self.change_block()
        # elif direction == 'DOWN':
        #     pass

        location_copy = self.wall_check(location_copy)

        for i in location_copy:
            check_result = self.stop_check(i)

            if not check_result:
                turn_switch += 1

        if turn_switch == 0:
            self.now_block.location = location_copy
            if direction == 'LEFT':
                self.now_block.x_move -= 1
            elif direction == 'RIGHT':
                self.now_block.x_move += 1
            # elif direction == 'UP':

    def draw_now_block(self):
        for x, y in self.now_block.location:
            pg.draw.rect(self.screen, GREEN, (
                (x + GAME_X // 2) * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X // 2) * BLOCK_SIZE, y * BLOCK_SIZE, LINE_SPACE, BLOCK_SIZE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X // 2) * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, LINE_SPACE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X // 2 + 1) * BLOCK_SIZE, y * BLOCK_SIZE, LINE_SPACE, BLOCK_SIZE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X // 2) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE, BLOCK_SIZE, LINE_SPACE), 0)

    def draw_next_block(self):
        self.screen.fill(WHITE)
        for x, y in self.next_block.dot[0]:
            # print(x, y)
            pg.draw.rect(self.screen, RED, (
                (x + GAME_X + NEXT_X // 2) * BLOCK_SIZE, (y + NEXT_X // 2) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X + NEXT_X // 2) * BLOCK_SIZE, (y + NEXT_X // 2) * BLOCK_SIZE, LINE_SPACE, BLOCK_SIZE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X + NEXT_X // 2) * BLOCK_SIZE, (y + NEXT_X // 2) * BLOCK_SIZE, BLOCK_SIZE, LINE_SPACE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X + NEXT_X // 2 + 1) * BLOCK_SIZE, (y + NEXT_X // 2) * BLOCK_SIZE, LINE_SPACE, BLOCK_SIZE), 0)
            pg.draw.rect(self.screen, WHITE, (
                (x + GAME_X + NEXT_X // 2) * BLOCK_SIZE, (y + NEXT_X // 2 + 1) * BLOCK_SIZE, BLOCK_SIZE, LINE_SPACE), 0)

    @staticmethod
    def create_next():
        return random.choice([IBlock, OBlock, LBlock, SBlock, ZBlock, TBlock, ULBlock])()

    # 画静止方块
    def draw_stop(self):

        for k, v in self.stop_block.items():
            if v:
                for i in v:
                    pg.draw.rect(self.screen, BLUE, (i * BLOCK_SIZE, k * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                    pg.draw.rect(self.screen, BLACK, (i * BLOCK_SIZE, k * BLOCK_SIZE, LINE_SPACE, BLOCK_SIZE), 0)
                    pg.draw.rect(self.screen, BLACK, (i * BLOCK_SIZE, k * BLOCK_SIZE, BLOCK_SIZE, LINE_SPACE), 0)
                    pg.draw.rect(self.screen, BLACK, ((i + 1) * BLOCK_SIZE, k * BLOCK_SIZE, LINE_SPACE, BLOCK_SIZE), 0)
                    pg.draw.rect(self.screen, BLACK, (i * BLOCK_SIZE, (k + 1) * BLOCK_SIZE, BLOCK_SIZE, LINE_SPACE), 0)

    def draw_wall(self):
        pg.draw.rect(self.screen, BLACK, (0, 0, MAIN_X * BLOCK_SIZE, MAIN_Y * BLOCK_SIZE), LINE_SPACE)
        pg.draw.rect(self.screen, BLACK, (0, 0, GAME_X * BLOCK_SIZE, GAME_Y * BLOCK_SIZE), LINE_SPACE)
        pg.draw.rect(self.screen, BLACK, (GAME_X * BLOCK_SIZE, 0, NEXT_X * BLOCK_SIZE, NEXT_X * BLOCK_SIZE), LINE_SPACE)
        self.three = pg.draw.rect(self.screen, BLACK, (
            GAME_X * BLOCK_SIZE, NEXT_X * BLOCK_SIZE, (MAIN_X - GAME_X) * BLOCK_SIZE, (MAIN_Y - NEXT_X) * BLOCK_SIZE),
                                  LINE_SPACE)

    def check_full_block(self):
        new_values = []
        block_keys = list(self.stop_block.keys())
        block_values = list(self.stop_block.values())
        remove_line = 0
        for i in block_values:
            if len(i) < GAME_X:
                new_values.append(i)
            else:
                remove_line += 1
        while len(new_values) < len(block_keys):
            new_values.insert(0, [])
        self.stop_block = dict(zip(block_keys, new_values))
        return remove_line


if __name__ == '__main__':
    game = Game()
    while True:
        fclock.tick(game.fps)
        game.start()
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if game.gaming:
                    if event.key == K_LEFT:
                        game.turn('LEFT')
                    elif event.key == K_RIGHT:
                        game.turn('RIGHT')
                    elif event.key == K_UP:
                        game.turn('UP')
                    elif event.key == K_DOWN:
                        game.fps = FPS * 10
                else:
                    if event.key == K_LEFT:
                        game.level_pop()
                    elif event.key == K_RIGHT:
                        game.level_add()
                    elif event.key == 13:
                        game.to_gaming()
                    else:
                        print(event.key)

            elif event.type == KEYUP:
                if event.key == K_DOWN:
                    game.fps = FPS
            elif event.type == MOUSEBUTTONDOWN:
                axis = pg.mouse.get_pos()
                game.click_check(axis)
        pg.display.update()
