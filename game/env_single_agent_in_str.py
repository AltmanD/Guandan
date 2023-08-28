"""
Content: Single agent gym wrapper for Guandan.
Author : Lu Yudong
"""
__author__ = 'Lu Yudong'

import os
import types
from typing import Tuple, Dict, Any
import gym
import numpy as np

from engine import close, init, step, reset
from game import Context


class Env():
    def __init__(self) -> None:
        '''
        环境封装初始化
        '''
        ctx = Context()
        # 初始化掼蛋引擎
        init(ctx)
        self.ctx = ctx
        self.global_step = 0
        self.each_step = [0, 0, 0, 0]
        self.action_type = 'str'
        self.observation_type = 'str'
        self.ActionSpace = None
        self.ObservationSpace = None

    def legalAction(self):
        '''
        给出当前obs下合法的动作
        output: 一维numpy
        '''
        legalAction = np.ones(self.NumOfObs)
        return legalAction

    def info(self):
        '''
        返回当前步的score
        output: 包含键为“score”的字典
        '''
        return [{}, {}]
    
    def obs(self):
        return 0
    
    def done(self):
        return 0

    def step(self, action: Any) -> Tuple[Any, float, bool, Dict[str, Any]]:
        '''
        返回当前步执行结束后算法需要的信息
        inpu: 动作序号
        output: 状态，奖励，结束标志，额外信息，合法动作
        '''
        self.step_fn(action)
        done = self.done_fn()
        obs = self.obs_fn()
        reward = self.reward()
        info = self.info()
        legalAction = self.legalAction()
        return obs, reward, done, info, legalAction

    def reward(self):
        '''
        返回当前步执行结束后相应的奖励（若无则为0）
        output: 奖励值
        '''
        # info['kill']表示杀敌数
        # info['score']表示当前得分，白色怪物1分，红色5分
        # 这两个信息每一帧都可以获取
        episode_id = entity_get_with_name(self.ctx, 'episode')
        data_comp = component_get_with_type(self.ctx, episode_id, "EpisodeComp")
        if data_comp is not None:
            mix = data_comp.kill + data_comp.score
            return mix
        return 0

    def reset(self):
        '''
        重置游戏状态
        output: 初始状态
        '''
        ctx = self.ctx
        for _ in range(3):
            player_id = entity_get_with_name(ctx, 'player')
            baby_id = entity_get_with_name(ctx, 'baby')
            if player_id is not None and baby_id is not None:
                break
            step(ctx)

    def close(self):
        '''
        关闭游戏环境
        '''
        close(self.ctx)


if __name__ == '__main__':
    # 调试用
    env = Env()
    for i in range(100):
        frame = 0
        score = 0
        obs = env.reset()
        import time
        stime = time.time()
        while 1:
            a = env.sActionSpace.sample()
            obs, r, done, info, legalacgion = env.step(a)
            # print(obs, r, done, info, legalacgion)
            score += r
            frame += 1
            if done:
                print("score=%0.2f in %i frames" % (score, frame))
                break
        print(time.time()-stime)
    env.close()
