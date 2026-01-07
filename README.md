# Guandan - 掼蛋游戏 Python 实现

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

一个完整的掼蛋（Guandan）游戏实现，包含游戏引擎和随机策略。

## 项目简介

掼蛋是一种在中国流行的四人扑克牌游戏，结合了斗地主和跑得快的玩法特点。本项目提供了一个完整的掼蛋游戏实现，包括：

- **游戏引擎**：完整的掼蛋规则实现，包括发牌、出牌、进贡、还贡、升级等所有规则
- **随机策略**：提供随机出牌的策略实现

## 项目结构

```
Guandan/
├── game/                    # 游戏核心引擎
│   ├── __init__.py
│   ├── engine.py           # 游戏引擎主逻辑
│   ├── env.py              # 游戏环境接口
│   ├── utils.py            # 工具函数
│   └── comps/              # 游戏组件
│       ├── __init__.py
│       ├── card_deck.py    # 牌堆管理
│       ├── context.py      # 游戏上下文
│       ├── player.py       # 玩家类
│       └── table.py        # 牌桌管理
├── agent/                  # agent 系统
│   ├── __init__.py
│   ├── agents.py           # agent 注册表
│   └── random_agent.py     # 随机策略
├── LICENSE
└── README.md
```

## 功能特性

### 游戏规则完整实现
- 四人两两搭档对战模式
- 完整的牌型识别：单张、对子、三张、顺子、连对、三连对、钢板、同花顺等
- 炸弹和特殊牌型处理
- 进贡和还贡机制
- 升级系统（从2到A）
- 接风规则

### 随机策略
- **随机 agent**：完全随机出牌，用于基础游戏测试和模拟

## 快速开始

### 环境要求
- Python 3.8+

### 运行游戏

运行完整游戏（默认使用随机策略）：

```bash
python env.py
```

这将启动一个完整的掼蛋游戏，使用4个随机策略进行对战。


## 开发指南

### 游戏引擎使用

游戏引擎位于 `game/` 目录下，提供了完整的掼蛋游戏逻辑。主要组件包括：

- **engine.py**: 游戏引擎主逻辑，管理游戏状态和流程
- **env.py**: 游戏环境接口，用于与智能体交互
- **comps/**: 游戏组件，包括牌堆、玩家、牌桌等

### 运行自定义游戏

您可以通过修改 `game/env.py` 来运行自定义的游戏配置：

```python
# 创建游戏环境
env = Env()

# 运行单局游戏
env.run_episode()

# 运行多局游戏
env.multiple_episodes(10)  # 运行10局游戏
```


### AI agent 开发

如果您需要开发自定义的 AI agent，可以参考以下步骤：

#### agent 接口规范

每个 agent 必须实现以下接口：

```python
class MyAgent:
    def __init__(self, id=0):
        self.id = id
    
    def received_message(self, message):
        """
        处理游戏消息，返回动作索引
        
        Args:
            message: JSON格式的游戏状态信息
            
        Returns:
            int: 动作列表中的索引
        """
        # 解析消息，决策逻辑
        return action_index
```

#### 游戏消息格式

游戏环境通过 JSON 消息与 agent 通信，包含以下阶段：
- `beginning`：游戏开始，发送手牌信息
- `tribute`：进贡阶段
- `play`：出牌阶段
- `back`：还贡阶段
- `episodeOver`：一局结束

#### 开发步骤

1. 在 `agent/` 目录下创建新的 agent 文件
2. 实现 agent 类，包含 `__init__` 和 `received_message` 方法
3. 在 `agent/agents.py` 中注册新 agent 
4. 在 `game/env.py` 中使用新 agent 进行测试

#### 示例：随机 agent

可以参考 `agent/random_agent.py` 中的 `RandomAgent` 类实现：

```python
class RandomAgent:
    def __init__(self, id=0):
        self.id = id
    
    def received_message(self, message):
        # 随机选择合法动作
        return random.choice(message['actionList'])
```

## 游戏规则参考

### 基本规则
- 4人游戏，2人一队，对家为队友
- 使用两副扑克牌（共108张）
- 从2开始升级，先升级到A的队伍获胜

### 牌型大小
1. 单张、对子、三张、顺子（5张）、连对（3连对）、钢板（2个连续三张）、同花顺
2. 炸弹：4张及以上相同点数的牌
3. 四大天王：4张王牌（最大牌型）
4. 同花顺大于普通炸弹

### 特殊规则
- **进贡**：上一局下游玩家向上游玩家进贡最大牌
- **还贡**：上游玩家向进贡玩家还贡任意牌
- **抗贡**：下游玩家有两张大王可抗贡
- **接风**：玩家出完牌后，下家接风出牌

## 性能优化

游戏引擎经过优化，支持：
- 快速牌型识别和合法性检查
- 高效的状态空间搜索
- 内存友好的对象管理
- 支持大规模模拟对战

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 致谢

- 感谢所有掼蛋游戏爱好者的规则整理
- 感谢贡献者的代码和测试

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 参与项目讨论

---

**Happy Guandan Playing!** 🃏
