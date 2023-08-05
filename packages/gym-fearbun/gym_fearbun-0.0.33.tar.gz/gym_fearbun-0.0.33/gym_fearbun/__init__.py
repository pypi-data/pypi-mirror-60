from gym.envs.registration import register
from gym_fearbun.envs.raceboard.c_raceboard import CRaceboardEnv
from gym_fearbun.envs.raceboard.raceboard import RaceboardEnv

register(
    id='raceboard-v0',
    entry_point='gym_fearbun.envs:RaceboardEnv',
)

register(
    id='raceboard-v1',
    entry_point='gym_fearbun.envs:CRaceboardEnv',
)

