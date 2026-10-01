# server/ — 本地 Agent 中枢

运行在家庭本地服务器上的 Agent 本体（Python）。承载感知 → 记忆 → 决策 → 表达四层，
以及 LiveKit 实时媒体接入与资源协调。

## 规划目录

```
server/
├── agent/          # 中枢四层编排 + 事件总线 + 资源协调
├── perception/     # 检测(YOLO) / VLM / 姿态 / 音频 分析器
├── memory/         # 事件时间线 / 作息画像 / 向量检索
├── media/          # MediaSource 抽象（本地文件 / go2rtc 流）
├── realtime/       # LiveKit agent worker / 房间 / token
└── config/         # 配置与模型清单
```

## 技术栈

- Python 3.11+
- LiveKit Agents（实时音视频）
- Ultralytics YOLO（常驻检测）
- 本地 VLM：MiniCPM-V 4.5 / Qwen2.5-VL（按硬件定）
- Whisper（音频转写）
- 事件总线：MQTT 或内存事件总线

> 当前为占位。实现见 [docs/roadmap/MVP.md](../docs/roadmap/MVP.md)。
