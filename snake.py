import curses
from time import sleep
from random import randint


class Game:
    def __init__(self):
        # initialize curses
        self.win = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.win.keypad(True)
        self.win.timeout(10)

        # score board and back ground color
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        # snake color
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        # feed color
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        # get window width and height
        self.height, self.width = self.win.getmaxyx()

        self.move_vec = [
            [1, 0],
            [-1, 0],
            [0, 1],
            [0, -1]
        ]
        self.is_gameover = False

        # initalization
        self.init_player()
        self.init_feeds()

    def init_player(self):
        # initial position
        self.p_pos = [self.calc_random_pos()]
        self.p_length = 1
        self.p_dir = 0

    def init_feeds(self):
        self.max_feed = 3
        self.feeds = [self.calc_random_pos() for _ in range(self.max_feed)]

    def calc_random_pos(self):
        x = randint(1, self.width - 1)
        y = randint(2, self.height - 1)
        return x, y

    def run(self):
        self.win.clear()
        while not self.is_gameover:
            key = self.win.getch()
            if key == curses.KEY_UP:
                self.p_dir = 3
            elif key == curses.KEY_DOWN:
                self.p_dir = 2
            elif key == curses.KEY_RIGHT:
                self.p_dir = 0
            elif key == curses.KEY_LEFT:
                self.p_dir = 1
            elif key == curses.KEY_RESIZE:
                self.height, self.width = self.win.getmaxyx()
            self.win.erase()
            self.update()
            sleep(0.1 - self.p_length * 0.005)
            self.win.refresh()
        self.game_over()

    def update(self):
        # move
        px = self.p_pos[0][0] + self.move_vec[self.p_dir][0]
        py = self.p_pos[0][1] + self.move_vec[self.p_dir][1]
        self.p_pos.insert(0, [px, py])
        if len(self.p_pos) > self.p_length:
            self.p_pos.pop()
        # check game over
        if self.check_gameover(px, py):
            self.is_gameover = True
        else:
            # update
            self.check_collision_feed()
            self.draw_feeds()
            self.draw_player()
            self.draw_score()

    def draw_player(self):
        for index, pos in enumerate(self.p_pos):
            if index == 0:
                self.win.addch(pos[1], pos[0], '@', curses.color_pair(2))
            else:
                self.win.addch(pos[1], pos[0], 'o', curses.color_pair(2))

    def draw_feeds(self):
        for feed in self.feeds:
            self.win.addch(feed[1], feed[0], 'x', curses.color_pair(3))

    def draw_score(self):
        score_text = f"score: {self.p_length - 1}"
        self.win.addstr(
            0,
            (self.width - len(score_text)) // 2,
            score_text,
            curses.color_pair(1))

    def check_collision_feed(self):
        for index, feed in enumerate(self.feeds):
            if self.p_pos[0][0] == feed[0] \
                    and self.p_pos[0][1] == feed[1]:
                self.p_length += 1
                self.feeds[index] = self.calc_random_pos()

    def check_gameover(self, px, py):
        # is frameout
        if px < 0 or self.width <= px or py < 0 or self.height <= py:
            return True
        # collide body
        for index in range(1, self.p_length):
            if self.p_pos[index][0] == px and self.p_pos[index][1] == py:
                return True
        return False

    def game_over(self):
        game_over_text = 'G A M E  O V E R'
        x = (self.width - len(game_over_text)) // 2
        y = self.height // 2
        self.draw_score()
        self.win.addstr(y, x, game_over_text)
        self.win.timeout(-1)
        self.win.getch()

    def __del__(self):
        curses.nocbreak()
        self.win.keypad(False)
        curses.echo()
        curses.endwin()


if __name__ == "__main__":
    game = Game()
    game.run()
