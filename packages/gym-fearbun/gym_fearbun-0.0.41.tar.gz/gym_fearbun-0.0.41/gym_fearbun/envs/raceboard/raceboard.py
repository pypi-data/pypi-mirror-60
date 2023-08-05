import gym
from gym import spaces
from gym.utils import seeding, colorize
from enum import Enum
from six import StringIO
import sys
from operator import methodcaller
from pathlib import Path


def action_to_space(action):
    return action[0] + 1, action[1] + 1


def space_to_action(space):
    return space[0] - 1, space[1] - 1


# board  x ->
#       y
#       |
#       V
# action for y +1 = up -1 = down
class RaceboardEnv(gym.Env):
    FINISHED = 'F'
    START = 'S'
    BEFORE = 'B'
    CURRENT = 'A'
    BOARD = ' '
    EDGE = '_'
    CRASHED = 'X'

    metadata = {'render.modes': ['human', 'ansi']}

    class MoveResult(Enum):
        OKAY = 0
        FINISHED = 1
        CRASHED = 2

    action_space = spaces.MultiDiscrete([3, 3])
    reward_range = (-1, 0)

    def __init__(self, map_name, is_noise=False, invalid_reward=-1):
        self.s = None
        self.crashed_pos = None
        self.last = None
        self.invalid_reward = None
        self.invalid = None
        self.observation_space = None
        self.map = None
        self.start_pos = None
        self.start_pos_size = None
        self.np_random = None
        self.is_noise = None
        self.action_result = None

        self.configure(map_name, is_noise, invalid_reward)
        self.seed()

    def step(self, action):
        action = space_to_action(action)
        self.crashed_pos = None

        delta_y, delta_x = action
        y, x, vel_y, vel_x = self.s
        self.last = (y, x)
        self.invalid = False

        # y = 25
        # x = 4

        if self.is_noise and self.np_random.random() <= 0.1:
            delta_y = 0
            delta_x = 0

        vel_y += delta_y
        vel_x += delta_x

        if vel_y < 0 or vel_x < 0 or (vel_y == 0 and vel_x == 0) or vel_x >= 5 or vel_y >= 5:
            self.invalid = True
            return self.s, self.invalid_reward, False, {}

        finished = False
        result_code, y, x = self.move(y, x, vel_y, vel_x)

        if result_code == RaceboardEnv.MoveResult.CRASHED:
            self.crashed_pos = (y, x)
            self.last = None
            self.s = self.get_random_start_state()
        elif result_code == RaceboardEnv.MoveResult.FINISHED:
            self.s = (y, x, vel_y, vel_x)
            finished = True
        elif result_code == RaceboardEnv.MoveResult.OKAY:
            self.s = (y, x, vel_y, vel_x)

        self.action_result = result_code

        return self.s, -1, finished, {}

    def reset(self):
        self.s = self.get_random_start_state()
        self.action_result = RaceboardEnv.MoveResult.OKAY
        self.crashed_pos = None
        self.last = None
        self.invalid = False

        return self.s

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return seed

    def render(self, mode='human', close=False):
        if close:
            return

        outfile = StringIO() if mode == 'ansi' else sys.stdout

        y, x, vel_y, vel_x = self.s
        outfile.write('\n')
        outfile.write(
            f'(y,x) = ({y},{x}) Speed(y,x) = ({vel_x},{vel_y})  Action Result: {self.action_result.name} + Invalid: {self.invalid}\n')

        tmp = self.map[y][x]
        self.map[y][x] = colorize(self.CURRENT, 'blue', bold=True)

        if self.crashed_pos:
            crashed_tmp = self.map[self.crashed_pos[0]][self.crashed_pos[1]]
            self.map[self.crashed_pos[0]][self.crashed_pos[1]] = colorize(self.CRASHED, 'red')

        if self.last:
            last_y, last_x = self.last
            is_last_set = last_y != y or last_x != x
            if is_last_set:
                last_tmp = self.map[last_y][last_x]
                self.map[last_y][last_x] = self.BEFORE

        text = '\n'.join([''.join(row) for row in self.map])
        outfile.write(text)
        outfile.write('\n')
        self.map[y][x] = tmp

        if self.crashed_pos:
            self.map[self.crashed_pos[0]][self.crashed_pos[1]] = crashed_tmp

        if self.last and is_last_set:
            self.map[last_y][last_x] = last_tmp

        return outfile

    def configure(self, file_name, is_noise, invalid_reward):
        self.is_noise = is_noise
        self.action_space = spaces.MultiDiscrete([3, 3])
        self.invalid_reward = invalid_reward

        file = Path(file_name)
        if file.is_file():
            with file.open() as fp:
                tmp = fp.readlines()
        else:
            file = Path(__file__).parent.parent.joinpath('maps', file_name)
            if file.is_file():
                with file.open() as fp:
                    tmp = fp.readlines()
            else:
                raise FileNotFoundError(file_name)

        tmp = map(methodcaller('rstrip', '\n'), tmp)
        self.map = list(map(list, tmp))

        self.observation_space = spaces.MultiDiscrete([len(self.map), len(self.map[0]), 5, 5])

        self.start_pos = []
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                if cell == self.START:
                    self.start_pos.append((y, x))
        self.start_pos_size = len(self.start_pos)

    def get_random_start_state(self):
        return self.start_pos[self.np_random.choice(self.start_pos_size)] + (0, 0)

    def check_collision(self, y, x):
        if self.map[y][x] == self.EDGE:
            return RaceboardEnv.MoveResult.CRASHED, y, x
        elif self.map[y][x] == self.FINISHED:
            return RaceboardEnv.MoveResult.FINISHED, y, x
        else:
            return None

    def move(self, y, x, vel_y, vel_x):
        dest_y = y - vel_y
        dest_x = x + vel_x

        if vel_y == 0 or vel_x == 0:
            while y != dest_y or x != dest_x:
                y -= vel_y > 0
                x += vel_x > 0

                ret = self.check_collision(y, x)
                if ret:
                    return ret
            return RaceboardEnv.MoveResult.OKAY, y, x

        real_y = y
        real_x = x
        while y != dest_y or x != dest_x:
            ret_y = self.check_collision(y - 1, x)
            if ret_y:
                return ret_y

            ret_x = self.check_collision(y, x + 1)
            if ret_x:
                return ret_x

            diff_y = -(y - 1 - real_y) / vel_y
            diff_x = (x + 1 - real_x) / vel_x
            if diff_x > diff_y:
                delta = diff_y
                y -= 1
            elif diff_x < diff_y:
                delta = diff_x
                x += 1
            else:
                delta = diff_y
                y -= 1
                x += 1

            real_y -= delta
            real_x += delta

        return RaceboardEnv.MoveResult.OKAY, y, x
