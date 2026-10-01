# server/ — 本地 Agent 中枢（能动 Agent）

运行在家庭本地服务器上的 Agent 本体（Python）。不是被动监控，而是一个**能理解宠物需求、
自主规划并驱动陪伴硬件执行**的能动 Agent：

```
感知(Perception) → 记忆(Memory) → 规划(Planning) → 执行器(Actuator) → 反馈闭环
                         事件总线 EventBus 解耦各层
```

硬件（你已有的陪伴机器人：语音/摄像头/逗玩/投食）被抽象成 **Device + 四类能力工具**，
Agent 通过"调用能力"驱动硬件，接新硬件只需实现 `Device` 接口，上层不改。

## 当前已实现（MVP 骨架，可运行）

```
server/src/anyfamily/
├── config.py        # 运行时配置（本地优先，数据不出门）
├── models.py        # PetProfile / EmotionVA / Interpretation / HealthAlert
├── events.py        # 类型化事件：perception.* / decision.* / action.* / health.*
├── bus.py           # 异步事件总线（观察者模式）
├── devices/         # 设备抽象层
│   ├── base.py      #   Capability(speak/camera/play/feed) + Device 接口
│   ├── mock.py      #   MockCompanionDevice（模拟你的硬件，含投食安全上限）
│   └── registry.py  #   ActuatorRegistry（action.request → 硬件执行 → 反馈）
├── perception.py    # Detector 接口 + StubDetector（真实接入换 YOLO/VLM/叫声情绪）
├── memory.py        # 事件时间线(JSONL) + 今日概览 + 解读/健康提示存储
├── planning.py      # Interpreter(解读) + Planner(规划) + DecisionEngine(闭环)
├── agent.py         # Agent 门面：把各层接到同一条总线
├── api.py           # FastAPI 接口（供父母端调用）
└── app.py           # 入口：组装 + 后台感知循环 + 起服务
```

## 跑起来

```bash
# 安装依赖（uv）
uv sync

# 方式一：冒烟测试闭环（不起 HTTP）
uv run python scripts/smoke.py

# 方式二：起 HTTP 服务（含后台自主感知循环）
uv run anyfamily
# 然后访问 http://127.0.0.1:8080/docs 看接口

# 方式三：接口冒烟（进程内 TestClient）
uv run --extra dev python scripts/api_smoke.py
```

## 主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/overview` | 今日概览（活动分布 + 发声 + 动作 + 一句话总结） |
| GET | `/timeline` | 事件时间线 |
| GET | `/interpretations` | 近期解读（"听懂我"） |
| GET | `/health-alerts` | 健康提示（3D 形态图标注来源） |
| POST | `/speak` | "看到我"：用熟悉的话 + 主人声音远程播放 |
| POST | `/play` | 远程逗玩 |
| POST | `/feed` | 远程投食（有每日上限保护） |
| POST | `/perceive-once` | 演示：手动驱动一次感知，走完解读→规划→执行闭环 |

## 从 MVP 到真实

- `StubDetector` → 真实感知：按 RESEARCH.md 第 3 章级联漏斗（运动门控 → YOLO → 事件触发 VLM）。
- `MockCompanionDevice` → 真实硬件适配器：在 `execute()` 里发 BLE/REST/MQTT 指令。
- 规则版 `Planner`/`Interpreter` → 接 LLM（`settings.use_llm_planner`）。
- 事件总线进程内 → 需要跨进程时换 MQTT，上层不动。

> 技术选型见 [../docs/RESEARCH.md](../docs/RESEARCH.md)，架构见 [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)。
