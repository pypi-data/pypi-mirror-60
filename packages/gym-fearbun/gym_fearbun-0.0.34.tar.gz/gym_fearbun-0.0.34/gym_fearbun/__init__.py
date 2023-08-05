from gym.envs.registration import register

register(
    id='raceboard-v0',
    entry_point='gym_fearbun.envs.raceboard:RaceboardEnv',
)

register(
    id='raceboard-v1',
    entry_point='gym_fearbun.envs.raceboard:CRaceboardEnv',
)

