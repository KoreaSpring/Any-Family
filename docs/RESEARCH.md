# Any-Family 实现方案调研

> 目标系统：本地优先的宠物陪伴 AI。Agent 跑在家庭本地服务器，持续用音视频感知/陪伴宠物、
> 学习其习惯，并通过跨平台（iOS/Android）App 让父母随时了解与互动。数据源从"本地已有音视频文件"
> 起步，后续接入"远程摄像头实时流"。
>
> 本文给出各子系统的业界成熟方案对比与选型建议，所有结论来自 GitHub 开源项目与公开技术资料，
> 并针对本项目场景做了取舍。内容为重新整理表述，非原文照搬。

---

## 0. 总体架构主张

一句话：**检测驱动、分层上模型、本地优先、实时通道用成熟框架**。

```
       家庭本地服务器（Agent 本体）                              远端父母
┌───────────────────────────────────────────┐          ┌─────────────────────┐
│  数据源层                                    │          │  父母端 App          │
│   本地视频/图片/音频  →（后续）RTSP 摄像头流    │          │  (iOS / Android)     │
│         │                                   │          │  实时看 + 对话 + 逗玩 │
│         ▼                                   │          └──────────▲──────────┘
│  感知层（分层，省算力）                        │                     │ WebRTC / 推送
│   常驻: YOLO 检测(宠物在不在/位置/运动)         │          ┌──────────┴──────────┐
│   触发: 本地 VLM 语义理解 / 姿态 / 行为分类      │◀────────▶│  LiveKit 实时媒体层   │
│   音频: Whisper + 叫声情绪分类                 │  媒体/信令 │  (自托管 server)      │
│         │ 结构化事件                          │          └─────────────────────┘
│         ▼                                   │
│  记忆层: 向量检索 + 作息画像 + 异常时间线        │
│         ▼                                   │
│  决策层: 对话大脑 + 主动陪伴 + 健康预警          │
│         ▼                                   │
│  表达层: 语音/文字/远程逗玩动作                 │
└───────────────────────────────────────────┘
```

核心原则：

1. **本地优先**：感知模型（检测/VLM/姿态/音频）与记忆全部跑在本地服务器，隐私数据不出家门。
   仅对话大模型可选走线上 API（也可全本地）。
2. **分层上模型**：不要对每一帧都跑重型 VLM。常驻一个轻量检测器判断"有没有事发生"，
   只有在有意义的事件（宠物进画面、长时间不动、剧烈活动、异常叫声）时才唤起重模型做语义理解。
   这是 Frigate 等成熟项目验证过的省算力范式。
3. **实时通道不要自己造**：用 LiveKit 这类成熟 WebRTC 框架承载"父母端 ↔ 本地 agent"的实时音视频，
   省掉自建信令/打洞/移动端 SDK 的巨大工作量。

---

## 1. 实时音视频通道（父母端 ↔ 本地 Agent）

### 选型结论：**LiveKit（自托管）+ LiveKit Agents**

父母要在手机上实时看宠物、和它"对话"（经由 agent）、远程逗玩，本质是一条双向低延迟音视频通道，
穿越家庭 NAT。自建 WebRTC 信令、TURN、移动端采集与各端 SDK 工作量极大且坑多。

[LiveKit](https://github.com/livekit/agents) 是目前这类"实时 AI agent"场景最成熟的开源方案：

- **Agents 框架**（Python，2025 年 1.0，后续到 1.5.x）：面向"能看、能听、能说"的实时服务端 agent，
  采用 **worker 池 + 任务分发**模型，LiveKit server 自动做负载均衡，可自托管到容器 / K8s。
- 原生 WebRTC，天然处理 NAT 穿透；官方提供 iOS / Android / React Native / Web 全套 SDK。
- 原生支持 MCP 工具调用，便于 agent 接外部能力。
- 官方 [vision-demo](https://github.com/livekit-examples/vision-demo) 展示了成熟的视频喂 VLM 节流做法：
  **用户说话时 1 fps 采样，否则 0.3 fps**，图片按 JPEG、限制到 1024×1024 —— 直接可借鉴到我们"按需看"。

> 参考：[LiveKit 自托管部署](https://docs.livekit.io/agents/ops/deployment/custom/)、
> [LiveKit-Template（自托管 server+agent+web 全栈样例）](https://github.com/yuting1214/LiveKit-Template)。
> 内容已重述以符合引用规范。

### 备选

- **Pipecat**（[pipecat](https://github.com/joachimchauvet/pipecat-livekit)）：语音/多模态对话编排框架，
  擅长"语音 agent 流水线"，常与 LiveKit 搭配。若后续对话链路复杂（打断、多轮、工具）可引入。
- 纯自建 WebRTC / WebSocket：仅在对依赖极度敏感时考虑，不推荐作为起步方案。

---

## 2. 摄像头实时流接入（阶段二）

### 选型结论：**go2rtc + FFmpeg（Frigate 范式）**

接入远程 IP 摄像头时，直接用业界验证过的 NVR 数据管线做法，而不是自己撸 RTSP 解码：

- [Frigate](https://github.com/blakeblackshear/frigate) 的视频管线很有参考价值：简单情况 FFmpeg 直接
  连 RTSP（TCP），复杂来源（HomeKit / Nest 等）用 **go2rtc** 统一接入。
- **restream 复用**：同一路摄像头，一份高清主流给录制 / 父母直播看，一份低清子流喂检测模型，
  视频流直接 copy 不重编码，省 CPU。[Frigate restream 文档](https://docs.frigate.video/configuration/restream)。
- go2rtc 支持 RTSP / WebRTC / HomeKit 等多种流类型，可把摄像头流转成 WebRTC 直接给父母端低延迟直播。

落地建议：阶段二把 go2rtc 作为"摄像头接入适配层"，对上游 agent 暴露统一的
"低清流（给感知）+ 高清流（给直播/录制）"，与阶段一的本地文件数据源共用同一套感知接口。

> 参考：[Frigate video_pipeline](https://github.com/blakeblackshear/frigate/blob/dev/docs/docs/frigate/video_pipeline.md)、
> [go2rtc 配置](https://github.com/blakeblackshear/frigate/blob/dev/docs/docs/configuration/go2rtc.md)。表述已重写。

---

## 3. 视频感知：检测 → 语义理解分层

宠物陪伴的视频理解不是"每帧都问大模型它在干嘛"，而是分层：

### 3.1 第一层 — 常驻轻量检测（YOLO）

判断"画面里有没有宠物、在哪、动没动、是不是出现了值得关注的事"。这是最省算力、可全天候常开的一层。

- **YOLOv8 / Ultralytics** 是宠物监控开源项目的事实标准，大量项目用它做猫狗检测 + IP 摄像头实时流 +
  MQTT 告警（如 [katzenschreck](https://github.com/andremotz/katzenschreck)、
  [Animal_Detection_and_Warning_System](https://github.com/srthkaggrwl/Animal_Detection_and_Warning_System)、
  [Real-Time-Animal-Detection](https://github.com/KajalBhammar/Real-Time-Animal-Detection-Using-CCTV-Camera-OpenVision)）。
- 典型做法：检测到宠物 → 连续多帧确认 → 触发事件（进/出画面、长时间静止、剧烈运动）。
- 事件总线用 **MQTT** 解耦（多个监控项目的共同选择），感知层发事件、决策层订阅。

### 3.2 第二层 — 事件触发的语义理解（本地 VLM）

只有在第一层报了"有意义的事件"时，才唤起重型视觉语言模型，对关键帧/短片段做自然语言理解
（"它在啃沙发""它趴在门口看起来没精神"），喂给记忆与决策层。

本地 VLM 候选（2025 现状）：

| 模型 | 规模 | 特点 | 适用 |
| --- | --- | --- | --- |
| **MiniCPM-V 4.5** | 8B | 面向边缘设备高效推理，SigLIP 视觉编码 + 轻量 LLM；官方称同规模下性能领先，可跑手机 | 本地服务器显存有限时首选 |
| **Qwen2.5-VL** | 3B/7B/32B/72B | 强物体定位（bbox/point）、长视频理解、文档解析 | 需要精确定位 / 长片段理解时 |
| **InternVL3** | 多规格 | 通用多模态 | 备选 |
| **MiniCPM-o** | — | 面向**实时端到端全模态**（流式视频+音频输入） | 若要做实时流式理解可评估 |

> 参考：[MiniCPM-V](https://github.com/openbmb/MiniCPM-V) 及其
> [技术报告](https://arxiv.org/abs/2509.18154)、[Qwen2.5-VL 技术报告](https://arxiv.org/abs/2502.13923)、
> [本地 VLM+Whisper 流水线实践](https://localaimaster.com/blog/local-ai-video-analysis)。数据与结论已重新表述。

显存协调：VLM 与姿态模型按需加载、互斥共存（参考资源协调思路），不常驻。

### 3.3 第三层 — 姿态与细粒度行为

想真正"学习宠物习惯"，需要比"检测到一只狗"更细的动作/姿态信息：

- **姿态关键点**：[DeepLabCut](https://github.com/DeepLabCut/DeepLabCut)（无标记动物姿态估计的学术标杆，
  其 ModelZoo 对四足动物有零样本/少样本能力）；工程上可用 **YOLO-pose** 做更快的实时关键点，
  或 [MAX-DLC](https://github.com/farhanaugustine/max-dlc)（YOLO 找个体 + DLC 出高精度关键点）加速。
  多摄像头 3D 姿态可看 [anipose](https://github.com/lambdaloop/anipose)。
- **行为分类**：成熟范式是 **CNN 抽帧特征 + RNN/时序模型分类行为**
  （如 [DeepAction](https://www.nature.com/articles/s41598-023-29574-0)、
  [个体级行为分析流水线](https://arxiv.org/abs/2509.12047) 报告时序模型可达 94% 准确率）。
  宠物活动识别也有现成项目（[PetActVision](https://github.com/Imannil/pet-act-vision)）。
- **情绪 / 健康**：宠物面部表情识别（[Pet_Facial_Expression_Recognition](https://github.com/jeffeehsiung/Pet_Facial_Expression_Recognition)）、
  一体化动物行为/健康分析平台可参考 [animind](https://github.com/molka-mallek/animind) 与
  [AnimalCare](https://github.com/sandeepsalwan1/animalcare)（输入宠物视频输出健康/行为分析）。

落地建议：姿态/行为/情绪模型作为"第二层之后的专项分析器"，同样按事件触发、按需加载，
不追求实时逐帧，而是对关键片段做批处理，产出结构化行为标签进记忆层。

---

## 4. 音频感知

- **人声**：[Whisper](https://github.com/openai/whisper)（large-v3）本地转写，让父母语音可被 agent 理解，
  也能转写家中环境里对宠物说的话。
- **宠物叫声**：吠叫 / 喵叫的检测与情绪/状态分类（焦虑、求关注、警戒），可用音频分类模型
  （CNN on mel-spectrogram）。与视频情绪做 late-fusion，提升判断可靠性。
- **声学事件**：异响、长时间嚎叫等作为告警事件触发。

---

## 5. Agent 中枢：事件驱动分层

借鉴成熟 AI 陪伴架构（事件总线 + 分层），针对宠物场景裁剪为四层：

- **感知层 Perception**：上述检测/VLM/姿态/音频，统一产出结构化 `perception.*` 事件。
- **记忆层 Memory**：
  - 短期：当日时间线（在吃/睡/玩/闹的事件流）。
  - 长期：作息画像（活跃时段、饮食规律、焦虑触发点）、异常时间线。
  - 技术：向量检索（语义相似事件召回）+ 结构化画像。可评估开源记忆层
    [mem0](https://github.com/mem0ai/mem0) 等，但宠物场景结构化画像占比高，可自建轻量方案。
- **决策层 Decision**：
  - 被动：父母提问 → 组织上下文（画像+近期事件+相关记忆）→ 对话大模型回答。
  - 主动：主动陪伴（宠物焦虑时放音/逗玩）、健康预警（行为偏离画像基线时提醒父母）。
- **表达层 Expression**：语音播放（陪宠物）、推送/对话（给父母）、远程逗玩动作指令。

> 记忆与"长期对话个性化"可参考 [LD-Agent](https://github.com/leolee99/LD-Agent)（NAACL 2025，
> LLM 驱动的长期对话个性化 agent），"安全的主动行为"框架可参考
> [proactive agent 行为框架](https://github.com/nitinjain999/platform-skills/blob/main/references/agent-self-improve.md)。

---

## 6. 父母移动端（iOS / Android）

### 选型结论：**React Native + LiveKit RN SDK**

- **为什么 RN**：实时音视频的核心已由 LiveKit 承载，父母端主要是"实时看 + 对话 + 看报告 + 推送"
  这类偏信息展示 + 实时流的应用，RN 完全胜任；RN 的 New Architecture（Fabric + JSI + TurboModules，
  0.82 起生产就绪）已消除旧桥接性能问题，且 LiveKit / Agora / Stream 等都有一流 RN 绑定。
- **一致性**：团队既有项目是 TS/React 栈，RN 复用技术栈与人力，长期维护成本更低。
- **推送**：APNs（iOS）/ FCM（Android），用于健康预警与主动提醒。

### 何时考虑 Flutter

若后续父母端演进为**重实时监控 / 多路视频墙 / 复杂自绘 UI**，Flutter（Impeller 引擎）在高帧率自绘上更稳。
但起步阶段 RN 的生态与团队契合度更优。

> 参考：[跨平台视频 App 框架对比](https://www.forasoft.com/blog/article/cross-platform-video-app)、
> [RN 视频通话架构](https://www.forasoft.com/blog/article/react-native-video-chat)。结论已重新表述。
> 合规说明：以上第三方资料内容均经改写与归纳，用于技术选型论证。

---

## 7. 分阶段落地建议

| 阶段 | 目标 | 关键交付 |
| --- | --- | --- |
| **MVP（阶段一）** | 本地文件数据源跑通"看懂→学习→陪伴→告诉父母"闭环 | 本地服务器：YOLO 检测 + 按需 VLM + Whisper；记忆画像；父母端 RN App 看报告 + 对话；LiveKit 打通一条实时音视频 |
| **阶段二** | 接入远程摄像头实时流 | go2rtc + FFmpeg 接入层；实时直播到父母端；常驻检测 + 事件触发分析上线 |
| **阶段三** | 细粒度习惯学习 + 健康预警 | 姿态/行为/情绪专项分析器；长期画像与异常基线；主动陪伴与预警 |
| **阶段四** | 多源融合 | 多摄像头 + 传感器（喂食器/项圈）融合，多宠物区分 |

---

## 8. 关键风险与注意

- **算力**：本地服务器显存是主约束。严格执行"检测驱动 + 按需加载 + 模型互斥"，避免多重模型常驻。
- **隐私**：家庭音视频高度敏感，默认全本地处理、父母端访问需鉴权、数据不上第三方。
- **误报**：健康预警宁可"先观察趋势再提醒"，避免频繁惊扰父母。
- **多宠物 / 遮挡**：检测+重识别（ReID）区分多只宠物是后期难点，MVP 先假设单宠物或人工指定。
- **冷启动**：习惯画像需要时间积累，MVP 阶段先给"原始事件时间线"，画像随数据增长逐步可靠。

---

## 参考项目与资料（均为公开来源，内容已重述）

- 实时 agent 媒体层：[livekit/agents](https://github.com/livekit/agents)、[vision-demo](https://github.com/livekit-examples/vision-demo)
- 摄像头管线：[Frigate](https://github.com/blakeblackshear/frigate)
- 本地 VLM：[MiniCPM-V](https://github.com/openbmb/MiniCPM-V)、[Qwen2.5-VL](https://arxiv.org/abs/2502.13923)
- 动物姿态/行为：[DeepLabCut](https://github.com/DeepLabCut/DeepLabCut)、[anipose](https://github.com/lambdaloop/anipose)、[PetActVision](https://github.com/Imannil/pet-act-vision)
- 宠物监控样例：[animind](https://github.com/molka-mallek/animind)、[AnimalCare](https://github.com/sandeepsalwan1/animalcare)、[dog-monitoring-local](https://github.com/ShionGT/dog-monitoring-local)
- 对话编排：[Pipecat](https://github.com/joachimchauvet/pipecat-livekit)
- 长期记忆/个性化：[LD-Agent](https://github.com/leolee99/LD-Agent)、[mem0](https://github.com/mem0ai/mem0)

> 以上第三方内容均经改写与归纳，用于技术选型论证，遵循来源的署名与引用要求。
