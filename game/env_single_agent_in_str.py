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
from legalaction import legalaction


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

    def step(self, action: Any) -> Tuple[Any, float, bool, Dict[str, Any]]:
        '''
        返回当前步执行结束后算法需要的信息
        inpu: 动作序号
        output: 状态，奖励，结束标志，额外信息，合法动作
        '''
        step(action)
        done = self.done()
        obs = self.obs()
        reward = self.reward()
        info = self.info()
        legalAction = self.legalAction(obs)
        return obs, reward, done, info, legalAction

    def reset(self):
        reset()
        self.global_step = 0
        self.each_step = [0, 0, 0, 0]

    def close(self):
        close(self.ctx)

    def legalAction(self, obs):
        legalAction = legalaction(obs)
        return legalAction

    def info(self):
        return self.ctx.info
    
    def obs(self):
        return self.ctx.obs
    
    def done(self):
        return self.ctx.done

    def reward(self):
        return self.ctx.reward


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
