from typing import Any, ClassVar
from shutil import get_terminal_size
import math
import curses
import random


BLOCK = "██"


class Paddle:
    def __init__(self, win: Any, side: str) -> None:
        self.win = win
        self.side = side
        self.y = 0
        if side == "LEFT":
            self.x = 4
        elif side == "RIGHT":
            self.x = Game.GAME_WIDTH - 6
        self.length = 5

    def move_up(self) -> None:
        self.y = max(0, self.y - 1)

    def move_down(self) -> None:
        self.y += 1
        if self.y + self.length >= Game.GAME_HEIGHT - 1:
            self.y = Game.GAME_HEIGHT - self.length - 1

    def render(self) -> None:
        for y in range(self.length):
            self.win.addstr(1 + y + self.y, self.x, BLOCK)


class Ball:
    SPPED_COUNT: ClassVar[int] = 100

    def __init__(self, win: Any) -> None:
        self.init()
        self.count = 0.0
        self.win = win

    def init(self) -> None:
        self.x = Game.GAME_WIDTH // 2
        self.y = Game.GAME_HEIGHT // 2
        self.vx = random.choice([1, -1])
        self.vy = random.choice([1, -1])
        self.speed = 1.5

    def update(self) -> None:
        if self.count >= Ball.SPPED_COUNT:
            self.move()
            self.count = 0
        self.count += self.speed

    def move(self) -> None:
        if self.vx > 0:
            self.x = min(self.x + self.vx, Game.GAME_WIDTH - 2)
        elif self.vx < 0:
            self.x = max(0, self.x + self.vx)

        self.y += self.vy
        self.bounce_y()

    def bounce_x(self) -> None:
        curses.beep()
        self.vx = -self.vx
        self.speed += 0.1

    def bounce_y(self) -> None:
        if self.y == 1:
            self.vy = -self.vy
            self.y = 1
        elif self.y == Game.GAME_HEIGHT - 1:
            self.vy = -self.vy
            self.y = Game.GAME_HEIGHT - 1

    @property
    def is_reach_left(self) -> bool:
        return self.x == 0

    @property
    def is_reach_right(self) -> bool:
        return self.x == Game.GAME_WIDTH - 2

    def render(self) -> None:
        self.win.addstr(self.y, self.x, BLOCK, curses.color_pair(1))


class NumberRender:
    def __init__(self, win: Any) -> None:
        self.win = win
        self.patterns = [
            [1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1],
            [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
            [1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
            [1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1],
            [1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1],
            [1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
            [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
        ]

    def render(self, x: int, y: int, num: int) -> None:
        digit_num = 2
        for digit in range(digit_num):
            for idx, p in enumerate(self.patterns[num % 10]):
                dx = x + idx % 3 * 2 + ((digit_num - 1) * 7) - digit * 7
                dy = y + idx // 3
                if dx < 0 or dx >= Game.GAME_WIDTH or dy < 0 or dy >= Game.GAME_HEIGHT:
                    continue
                if p:
                    self.win.addstr(dy, dx, BLOCK)
            num //= 10


class Game:
    GAME_WIDTH: ClassVar[int] = 80
    GAME_HEIGHT: ClassVar[int] = 20 + 2

    def __init__(self, win: Any, columns: int, lines: int) -> None:
        self.win = win.derwin(
            (lines - Game.GAME_HEIGHT) // 2,
            (columns - Game.GAME_WIDTH) // 2)
        self.win.timeout(1)
        self.ball = Ball(self.win)
        self.num_render = NumberRender(self.win)
        self.max_point = 9
        self.is_game_end = False
        self.points = {
            "LEFT": 0,
            "RIGHT": 0
        }
        self.paddles = [
            Paddle(self.win, "LEFT"),
            Paddle(self.win, "RIGHT")
        ]

    def draw(self) -> None:
        center_x = Game.GAME_WIDTH // 2
        # Draw lines
        for y in range(0, Game.GAME_HEIGHT, 2):
            self.win.addstr(1 + y, center_x, BLOCK)
        self.win.addstr(0, 0, BLOCK * (Game.GAME_WIDTH // 2))
        self.win.addstr(Game.GAME_HEIGHT, 0, BLOCK * (Game.GAME_WIDTH // 2))
        # Draw Points
        self.num_render.render(center_x - 18, 2, self.points["LEFT"])
        self.num_render.render(center_x + 7, 2, self.points["RIGHT"])

    def draw_result(self) -> None:
        winner = "Player 1" if self.points["LEFT"] > self.points["RIGHT"] else "Player 2"
        self.win.addstr(Game.GAME_HEIGHT // 2, Game.GAME_WIDTH //
                        2 - 6, f"Winner {winner}", curses.color_pair(2))

    def key_handle(self, key: int) -> None:
        # Player 1
        if key == ord('w'):
            self.paddles[0].move_up()
        elif key == ord('s'):
            self.paddles[0].move_down()
        # Player 2
        if key == ord('i'):
            self.paddles[1].move_up()
        elif key == ord('k'):
            self.paddles[1].move_down()

    def check_paddle(self, paddle: Paddle) -> None:
        by = self.ball.y
        if paddle.y <= by <= paddle.y + paddle.length:
            self.ball.bounce_x()

    def check_reach_edge(self) -> None:
        if self.ball.is_reach_left:
            self.points["RIGHT"] += 1
            curses.beep()
            self.ball.init()
        elif self.ball.is_reach_right:
            self.points["LEFT"] += 1
            curses.beep()
            self.ball.init()

        # Is game finished?
        if self.points["LEFT"] >= self.max_point \
                or self.points["RIGHT"] >= self.max_point:
            self.is_game_end = True

    def run(self) -> None:
        while not self.is_game_end:
            key = self.win.getch()
            self.win.erase()
            # Update objects
            self.ball.update()
            self.key_handle(key)
            # Judge if ball hit paddle
            if self.ball.x == self.paddles[0].x + 2 and self.ball.vx < 0:
                self.check_paddle(self.paddles[0])
            elif self.ball.x == self.paddles[1].x - 2 and self.ball.vx > 0:
                self.check_paddle(self.paddles[1])
            self.check_reach_edge()
            # Draw objects
            self.draw()
            self.paddles[0].render()
            self.paddles[1].render()
            self.ball.render()
            # Refresh window
            self.win.refresh()
        self.win.timeout(-1)
        self.draw()
        self.draw_result()
        self.win.getch()


def main(win: Any) -> None:
    terminal_size = get_terminal_size()
    if terminal_size.columns <= Game.GAME_WIDTH \
            or terminal_size.lines <= Game.GAME_HEIGHT:
        return
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, 9, 0)
    curses.init_pair(2, 0, 15)
    curses.curs_set(0)
    game = Game(win, terminal_size.columns, terminal_size.lines)
    game.run()


if __name__ == "__main__":
    curses.wrapper(main)
