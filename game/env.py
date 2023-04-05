"""
Content: Gym wrapper for world001.
Author : Lu Yudong
"""

import os
import types
from typing import Tuple, Dict, Any
import gym
import numpy as np

from engine import close, init, step, reset


def _defaultDone(self):
    '''Check whether the game is done. 
    Because it is checked internally already, we directly retrieve it from game context, unless we have different ending conditions.
    '''
    
    world_id = entity_get_with_name(self.ctx, 'world')
    globals_comp = component_get_with_type(self.ctx,world_id,"GlobalsComp")
    
    if globals_comp.result is not None:
        return True
    
    return False


def _defaultObs(self):
    obs = []
    ctx = self.ctx
    # 玩家和宝宝信息
    EntityList = ['player', 'baby']
    for entity in EntityList:
        eid = entity_get_with_name(ctx, entity)
        if eid == None:
            obs += [0] * 10
        else:
            poscomp = component_get_with_type(ctx, eid, 'TransformComp')
            obs.append(poscomp.pos[0])
            obs.append(poscomp.pos[1])
            dmgcomp = component_get_with_type(ctx, eid, 'DamageComp')
            obs.append(dmgcomp.hp)
            obs.append(dmgcomp.ht)
            obs.append(dmgcomp.atk)
            obs.append(dmgcomp.def_)
            obs.append(dmgcomp.rng)
            obs.append(dmgcomp.ct)
            obs.append(dmgcomp.cd)
            bufcomp = component_get_with_type(ctx, eid, 'BuffComp')
            if 'CollisionFreeBuff' not in bufcomp.passive_buffs.keys():
                obs.append(0)
            else:
                obs.append(bufcomp.passive_buffs['CollisionFreeBuff'].remaining_steps)
    # 怪物信息
    EnemyNumb = 0
    for i in range(20):
        eid = entity_get_with_name(ctx, 'enemy_{}'.format(i))
        if eid == None:
            obs += [0] * 5
        else:
            EnemyNumb += 1
            poscomp = component_get_with_type(ctx, eid, 'TransformComp')
            obs.append(poscomp.pos[0])
            obs.append(poscomp.pos[1])
            dmgcomp = component_get_with_type(ctx, eid, 'DamageComp')
            obs.append(dmgcomp.hp)
            obs.append(dmgcomp.atk)
            rewardcomp = component_get_with_type(ctx, eid, 'RewardComp')
            obs.append(rewardcomp.score)
    obs.append(EnemyNumb)
    # 剩余时间信息
    world_id = entity_get_with_name(self.ctx, 'world')
    globals_comp = component_get_with_type(self.ctx,world_id,"GlobalsComp")
    obs.append(ctx.config["max_steps"] - (globals_comp.tick - globals_comp.last_result_tick))

    obs = np.array(obs)
    return [obs, obs]


def _defaultStep(self, action):
    ctx = self.ctx
    eid = entity_get_with_name(ctx, 'player')
    if not self.HumanCtl:
        if not self.Render:
            behavior_comp = component_get_with_type(ctx, eid, 'BehaviorComp')
            behavior_comp.behavior.action = action[0]
            # 如需在训练中令player使用默认规则，就将上两行注释，并将下面内容释放注释
            # if self.target_idx == len(self.path):
            #     self.target_idx = 1
            # else:
            #     target_pos = self.path[self.target_idx]
            #     if move_to(eid, ctx, target_pos) is not False:
            #         action_h = move_to(eid, ctx, target_pos)
            #         behavior_comp = component_get_with_type(ctx, eid, 'BehaviorComp')
            #         behavior_comp.behavior.action = [action_h,1]
            #     else:
            #         self.target_idx += 1
        else:
            if self.target_idx == len(self.path):
                self.target_idx = 1
            else:
                target_pos = self.path[self.target_idx]
                if move_to(eid, ctx, target_pos) is not False:
                    action_h = move_to(eid, ctx, target_pos)
                    behavior_comp = component_get_with_type(ctx, eid, 'BehaviorComp')
                    behavior_comp.behavior.action = [action_h,1]
                else:
                    self.target_idx += 1
    eid = entity_get_with_name(ctx, 'baby')
    behavior_comp = component_get_with_type(ctx, eid, 'BehaviorComp')
    behavior_comp.behavior.action = action[1]
    step(ctx)


def move_to(eid: int, ctx: Context, target_pos: np.ndarray, precision=0.2) -> bool: # TODO:改一版简单版本
    move_dir_map = [[0, 0], [0, -1], [0, 1], [-1, 0], [1, 0], [-1, -1], [1, -1], [-1, 1], [1, 1]]
    transform_comp = component_get_with_type(ctx, eid, "TransformComp")
    dynamic_comp = component_get_with_type(ctx, eid, "DynamicsComp")
    dynamic_comp.move_dir = None
    dynamic_comp.speed = dynamic_comp.max_speed
    pos = transform_comp.pos
    dist = np.linalg.norm(target_pos - pos)
    if dist > precision:
        estimated_frames = dist / (dynamic_comp.max_speed / ctx.config["fps"])
        expected_frames = int(np.ceil(estimated_frames))
        if expected_frames == 0:
            dynamic_comp.move_dir = np.zeros(2, dtype=np.float32)
            dynamic_comp.speed = dynamic_comp.max_speed
            return False
        expected_speed = dist / expected_frames * ctx.config["fps"]
        dynamic_comp.move_dir = target_pos - pos
        if not np.all(dynamic_comp.move_dir == 0):
            dynamic_comp.move_dir = dynamic_comp.move_dir / np.linalg.norm(dynamic_comp.move_dir)
            dynamic_comp.speed = expected_speed
            return move_dir_map.index([int(dynamic_comp.move_dir[0]+0.5 if dynamic_comp.move_dir[0]>0 else dynamic_comp.move_dir[0]-0.5), int(dynamic_comp.move_dir[1]+0.5 if dynamic_comp.move_dir[1]>0 else dynamic_comp.move_dir[1]-0.5)])
    return False


class Env():
    def __init__(self) -> None:
        '''
        环境封装初始化
        '''
        ctx = Context()
        init(ctx)
        self.ctx = ctx
        self.NumOfObs = len(self.obs_fn()[0])
        self.sActionSpace = gym.spaces.Tuple([gym.spaces.MultiDiscrete([9, 2]), gym.spaces.MultiDiscrete([9, 3])])
        self.sObservationSpace = [
            gym.spaces.Box(np.ones(self.NumOfObs) * -np.Inf,
                           np.ones(self.NumOfObs) * np.Inf) for _ in range(2)
        ]
        self.sShareObservationSpace = [
            gym.spaces.Box(np.ones(self.NumOfObs) * -np.Inf,
                           np.ones(self.NumOfObs) * np.Inf) for _ in range(2)
        ]

    def legalAction(self):
        '''
        给出当前obs下合法的动作
        output: 一维numpy
        '''
        legalAction = np.ones(self.NumOfObs)
        return [legalAction, legalAction]

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
