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

## 3. 视频感知：级联漏斗（更优方案）

> **结论先行**：最初"YOLO → 通用 VLM"的两层思路方向正确，但有更成熟、更省算力的做法。
> 业界验证过的是一个**四级漏斗**：每升一级算力成本陡增，所以每一级只放行"真正需要上一级
> 回答不了的问题"的那一小部分数据。这不是我们拍脑袋，而是 Frigate（0.17，2026）这类成熟 NVR
> 已经固化下来的管线：`运动检测 → 目标检测 → GenAI 事件序列描述`。我们在它基础上为宠物场景
> 补上"行为/情绪专项分析"。

```
每级只放行少量数据上升，算力从左到右指数增长：

L0 运动门控      L1 目标检测/跟踪     L2 语义理解(VLM)        L3 专项分析
(几乎免费)   →   (轻量,可常驻)   →   (重,事件触发)    →    (最重,关键片段批处理)
像素级变化        宠物在不在/在哪      "它在啃沙发"           姿态/行为分类/情绪/健康
全天候常开        有宠物才跑          有意义事件才唤起        需要细节时才跑
```

### 3.0 第 0 级 — 运动门控（几乎免费，别跳过）

这是最容易被忽略、却最省钱的一级。先用**像素级运动检测**（OpenCV 背景差分，或直接解码器的运动矢量）
判断画面有没有变化，没变化就连目标检测都不跑。Frigate 的做法值得照搬：**运动掩码（motion mask）**
屏蔽时间戳、随风晃动的树枝等规律性噪声，避免把算力浪费在无意义运动上。宠物睡着不动的大段时间里，
整条流水线几乎零消耗。

> 参考：[Frigate 运动检测](https://docs.frigate.video/configuration/motion_detection/)、
> [Frigate 目标检测器](https://github.com/blakeblackshear/frigate/blob/dev/docs/docs/configuration/object_detectors.md)。表述已重写。

### 3.1 第 1 级 — 目标检测/跟踪（轻量常驻）

判断"画面里有没有宠物、在哪、是不是进/出了某个区域（zone）、动没动"。有运动才跑，仍然是可全天候的一级。

**比默认 YOLOv8 更值得考虑的候选（2025–2026 现状）：**

| 模型 | 定位 | 相对优势 | 何时选它 |
| --- | --- | --- | --- |
| **YOLO11 / YOLO26** | CNN，边缘优化 | YOLO26（2025.09）主打低功耗边缘设备部署就绪、NMS-free 降延迟；是稳健默认 | 常驻检测的稳妥首选 |
| **RT-DETR / RT-DETRv2** | Transformer，端到端 | 无需 NMS，中大模型精度优于同级 YOLO，T4 上仍实时 | 本地服务器有像样 GPU、要更高精度 |
| **YOLOE（"实时万物检测"）** | 开放词汇，prompt-free | 内置大词汇 + 文本/视觉 prompt，零样本识别任意物体，不依赖外挂语言模型，推理高效 | 想免训练识别"狗/猫/玩具/食盆/呕吐物"等自定义目标 |
| **YOLO-World** | 开放词汇 | 零样本开放词汇检测，LVIS 上 52 FPS | YOLOE 的替代/对照 |
| **Grounding DINO** | 开放词汇，高精度 | 开放词汇精度常年领先 | 仅离线自动标注/难例，**不**用于实时（速度慢） |

**选型建议**：常驻检测用 **YOLO11/YOLO26**（有 GPU 可换 RT-DETRv2 提精度）；
如果希望"不重新训练就能识别宠物相关的任意自定义目标"（食盆、尿垫、特定玩具、呕吐物/排泄物），
用 **YOLOE** 做开放词汇检测会比固定类别的 YOLOv8 灵活得多，这是对你最初方案的一个实质升级。
Grounding DINO 太慢，只建议拿来离线给自有视频自动打标签、生成训练/评测集。

- 典型事件逻辑：检测 → 跟踪（给每只宠物稳定 ID）→ 连续多帧确认 → 事件（进/出画面、进出 zone、长时间静止、剧烈运动）。
- **zone（区域）** 概念直接借 Frigate：以 bbox 底边中点是否落入区域判定，可圈出"食盆区/门口/沙发/窝"，让事件带空间语义（"它去了食盆""它上了沙发"）。
- 事件总线用 **MQTT** 解耦（宠物监控开源项目的共同选择），感知层发事件、决策层订阅。

> 参考：[YOLOE: Real-Time Seeing Anything](https://arxiv.org/abs/2503.07465)、
> [YOLO-World](https://arxiv.org/html/2401.17270v3)、[RT-DETR](https://arxiv.org/abs/2304.08069)、
> [YOLO26 架构与基准](https://arxiv.org/abs/2509.25164)、
> [RT-DETRv2 vs YOLO11 对比](https://docs.ultralytics.com/compare/rtdetr-vs-yolo11/)。数据与结论已重新表述。

### 3.2 第 2 级 — 事件触发的语义理解（本地 VLM + 事件序列描述）

只有在第 1 级报了"有意义的事件"时，才唤起重型视觉语言模型做自然语言理解。
**这里有一个比"对单帧问 VLM"更好的成熟做法**：不要只喂一帧，而是喂**一段事件序列的若干关键帧**，
让模型输出一句**叙事（scene）描述**——"从头到尾发生了什么、在什么场景、宠物做了什么动作"。
这正是 Frigate 0.17 的 **Review Summaries / Object Descriptions** 的产物形态，用
`frigate/tracked_object_update` 这类 MQTT 主题把"检测事件"和"GenAI 描述"关联起来。
对我们而言，这种"一段事件 → 一句人话"的输出，天然就是喂给记忆层和"告诉父母"的理想素材。

本地 VLM 候选（2025 现状）：

| 模型 | 规模 | 特点 | 适用 |
| --- | --- | --- | --- |
| **MiniCPM-V 4.5** | 8B | 面向边缘设备高效推理，SigLIP 视觉编码 + 轻量 LLM；官方称同规模下性能领先，可跑手机 | 本地服务器显存有限时首选 |
| **Qwen2.5-VL** | 3B/7B/32B/72B | 强物体定位（bbox/point）、长视频理解、文档解析 | 需要精确定位 / 长片段理解时 |
| **MiniCPM-o** | — | 面向**实时端到端全模态**（流式视频+音频输入） | 若要做实时流式理解可评估 |
| **InternVL3** | 多规格 | 通用多模态 | 备选 |

- **采样节流**：复用 LiveKit vision-demo 的经验——按事件重要性调采样率（关注时 1 fps、平时更低），
  图片 JPEG、限 1024×1024，控制 VLM 输入 token。
- **省显存**：VLM 不常驻，用完释放；与第 3 级的专项模型互斥加载（见 ResourceCoordinator）。

> 参考：[Frigate Review Summaries](https://github.com/blakeblackshear/frigate/blob/dev/docs/docs/configuration/genai/review_summaries.md)、
> [Frigate Object Descriptions](https://docs.frigate.video/configuration/genai/genai_objects/)、
> [MiniCPM-V](https://github.com/openbmb/MiniCPM-V) 及[技术报告](https://arxiv.org/abs/2509.18154)、
> [Qwen2.5-VL 技术报告](https://arxiv.org/abs/2502.13923)。数据与结论已重新表述。

### 3.3 第 3 级 — 姿态与细粒度行为（最重，关键片段批处理）

想真正"学习宠物习惯"，需要比"检测到一只狗"更细的动作/姿态信息。这一级最重，所以只对
第 2 级标记出的关键片段做**离线/批处理**，不追求实时逐帧，产出结构化行为标签进记忆层：

- **姿态关键点**：[DeepLabCut](https://github.com/DeepLabCut/DeepLabCut)（无标记动物姿态估计的学术标杆，
  其 ModelZoo 对四足动物有零样本/少样本能力）；工程上可用 **YOLO-pose** 做更快的实时关键点，
  或 [MAX-DLC](https://github.com/farhanaugustine/max-dlc)（YOLO 找个体 + DLC 出高精度关键点）加速。
  多摄像头 3D 姿态可看 [anipose](https://github.com/lambdaloop/anipose)。
- **行为分类**：经典范式是 **CNN 抽帧特征 + RNN/时序模型**
  （如 [DeepAction](https://www.nature.com/articles/s41598-023-29574-0)、
  [个体级行为分析流水线](https://arxiv.org/abs/2509.12047) 报告时序模型可达 94% 准确率），
  现成宠物活动项目见 [PetActVision](https://github.com/Imannil/pet-act-vision)。
  **更现代的选择**是用自监督视频表征直接建模时序动作，避免逐任务重训：
  - **V-JEPA 2**（Meta）：联合时序建模，对"连续动作"比逐帧方法更强，适合区分"走/跑/刨/发抖"这类动态行为。
  - **VideoMAE / InternVideo / X-CLIP、EZ-CLIP**：高效视频动作识别，EZ-CLIP 仅约 520 万可训练参数、单卡可训，适合小数据微调出宠物专属动作类别。
  - 对比研究表明：逐帧（DINOv3 式）擅长静态姿态，联合时序（V-JEPA2 式）擅长动态动作——两者可按行为类型分工。

  > 参考：[V-JEPA2 vs DINOv3 视频动作对比](https://arxiv.org/html/2509.21595v1)、
  > [EZ-CLIP 高效零样本动作识别](https://arxiv.org/html/2312.08010v2)、
  > [TC-CLIP 时序上下文](https://arxiv.org/html/2404.09490v1)。结论已重新表述。
- **情绪 / 健康**：宠物面部表情识别（[Pet_Facial_Expression_Recognition](https://github.com/jeffeehsiung/Pet_Facial_Expression_Recognition)）、
  一体化动物行为/健康分析平台可参考 [animind](https://github.com/molka-mallek/animind) 与
  [AnimalCare](https://github.com/sandeepsalwan1/animalcare)（输入宠物视频输出健康/行为分析）。

### 3.4 工程落地：不要从零拼，优先复用 Frigate 做"感知底座"

最省事也最成熟的做法：**把 Frigate 当作第 0–2 级的现成底座**，而不是自己拼运动检测+跟踪+录制+zone+GenAI。
Frigate 已经把"RTSP 接入（go2rtc）+ 运动门控 + 目标检测/跟踪 + zone + 事件录制 + GenAI 事件描述 + MQTT 事件总线"
打包好了，还能换检测模型、接本地 Ollama 跑 GenAI 描述、全程本地不出网。

推荐分工：

- **Frigate 负责 L0–L2**：出"结构化事件 + 关键片段 + 一句话 scene 描述"，经 MQTT 抛给我们的 agent。
- **我们负责 L3 与"陪伴大脑"**：订阅 Frigate 的 MQTT 事件，叠加宠物专属的姿态/行为/情绪分析，
  做习惯画像、健康基线、主动陪伴与"讲给父母听"。阶段一本地文件也可先灌进 Frigate 或直接走我们自己的 L1/L2。

这样第一阶段就能快速跑通，把自研精力集中在真正差异化的"懂宠物 + 陪伴 + 对父母表达"上。

> 参考：[Frigate + 本地 AI 摄像头实践（2026）](https://localaimaster.com/blog/frigate-ollama-ai-cameras)、
> [Frigate 术语表（attribute/sub-label/zone）](https://docs.frigate.video/frigate/glossary)。表述已重写。

### 3.5 一句话总结：相比最初方案升级了什么

| 环节 | 最初方案 | 升级后 |
| --- | --- | --- |
| 触发 | YOLO 常驻 | **先加 L0 运动门控**（几乎免费），YOLO 只在有运动时跑 |
| 检测 | YOLOv8 固定类别 | **YOLO11/YOLO26**（或 RT-DETRv2 提精度）；需要自定义目标用 **YOLOE 开放词汇**免训练识别 |
| 语义理解 | 对单帧问 VLM | **对事件序列若干关键帧出 scene 叙事描述**（Frigate Review Summaries 范式），更契合"告诉父母" |
| 行为识别 | CNN+RNN | 保留经典范式，补 **V-JEPA2 / VideoMAE / EZ-CLIP** 自监督时序模型，静态姿态与动态动作分工 |
| 工程 | 自己拼管线 | **复用 Frigate 做 L0–L2 底座**，自研精力投在 L3 + 陪伴大脑 |

---

## 4. 音频感知

- **人声**：[Whisper](https://github.com/openai/whisper)（large-v3）本地转写，让父母语音可被 agent 理解，
  也能转写家中环境里对宠物说的话。
- **宠物叫声**：吠叫 / 喵叫的检测与情绪/状态分类（焦虑、求关注、警戒），可用音频分类模型
  （CNN on mel-spectrogram）。与视频情绪做 late-fusion，提升判断可靠性。
- **声学事件**：异响、长时间嚎叫等作为告警事件触发。

**叫声情绪的更优做法（2025）**：别只输出"开心/难过"这种生硬离散标签，用**连续的"效价-唤醒度（Valence-Arousal）"二维坐标**表达情绪强度，更适合长期趋势监测与异常发现。生物声学方向还出现了
**音频-语言基础模型 NatureLM-audio**，能对未见过的物种做零样本声音分类，是"听懂动物声音"方向最接近基础模型的东西，可作为长期技术储备。

> 参考：[宠物叫声 VA 连续情绪建模](https://arxiv.org/html/2510.12819v1)、
> [NatureLM-audio 生物声学基础模型](https://arxiv.org/abs/2411.07186)、
> [BEANS 动物声音基准](https://github.com/earthspecies/beans)。结论已重新表述。

---

## 5. 宠物情绪与状态解读（项目灵魂，不是监控）

> **这一章回答一个灵魂问题**：如果系统只会说"检测到一只狗在动"，那毫无价值。真正有价值的是"懂它"——
> 它现在开心、焦虑还是不舒服，想表达什么。本章给出诚实、可落地的做法。

### 5.1 先纠正一个认知：没有"宠物翻译机"，只有"状态解读器"

学术共识：动物没有人类意义上的词汇/语言，所以**不能做逐词翻译**。市面上"把狗叫翻译成人话"的宣传都是营销。
但**可以做情绪与状态的解读**，而且 2025 年已能落地。关键的范式转变：**不追求"它说了什么"，而是解读
"它现在是什么状态、可能有什么需求"**——"它焦虑了""它想要关注""它可能哪里不舒服"，这才是对父母有用的。

### 5.2 为什么单一模型不行：必须多模态融合

- [2025 Nature 研究](https://www.nature.com/articles/s41598-025-25199-7) 专门测了 GPT-4o/Gemini/LLaVA
  这类通用大视觉语言模型识别**狗情绪**的能力，结论是**有潜力但不够准，不能单独依赖**。
- [K9-Bench](https://arxiv.org/html/2607.02680)（2025）：专门评测多模态大模型在"狗为中心视频"（图像+视频+音频+文本）
  上的理解能力，说明业界已经在认真对待这个方向。
- [把猫狗行为翻译成人类可读信息的研究](https://www.mdpi.com/2813-0324/13/1/11/xml)：核心方法就是**融合肢体语言+声音+面部表情+动作**综合判断——这正是我们要的"解读"思路。

### 5.3 落地架构：硬信号 → 软解读 → 落记忆（两级）

直接问通用 VLM"这狗什么情绪"不够准。正确做法是两级分工：

```
  专用模型出"硬信号"（客观可量化）        VLM/LLM 做"软解读 + 落记忆"
┌───────────────────────────┐      ┌──────────────────────────────────┐
│ 叫声  → VA 情绪坐标(效价/唤醒)│      │ 读入这些结构化硬信号 + 看关键帧        │
│ 表情  → 情绪概率分布         │ ───▶ │ + 结合"这只宠物的历史画像/品种先验"    │
│ 姿态  → 动作标签             │      │ → 产出一句人话解读 + 置信度 + 证据链    │
│ 事件  → 场景/区域(zone)      │      │ → 写入记忆（结构化事件，非一句话）      │
└───────────────────────────┘      └──────────────────────────────────┘
```

- **专用模型**负责客观、可量化、可追溯的信号（不是黑箱猜测）。
- **VLM/LLM** 负责它真正擅长的：把多个信号 + 历史上下文揉成父母能懂的一句话，并解释依据
  （"它一直在门口徘徊 + 高唤醒度叫声 + 你以往出门时它也这样 → 它可能在焦虑地等你回家"）。
- **落到记忆**不是存一句话，而是存**结构化事件 + 证据 + 解读 + 置信度**，才能积累成"宠物画像"
  （焦虑触发点、黏人时段、叫声模式异常变化 = 健康预警基础）。

### 5.4 必须诚实承认的边界

- 不能"翻译"具体意图，只能给情绪/状态的概率解读。
- 冷启动解读很泛，必须靠**长期积累这只宠物的个性化基线**才会越来越准——这反而是护城河：
  别人没有你用户这只宠物的历史数据。
- **猫比狗难**：狗的行为研究成熟（见下章），猫的情绪表达更微妙、数据更稀缺，建议先做狗。

---

## 6. 品种先验 × 个体观测：让"懂它"从第一天就可用

> 不同品种、甚至同品种不同个体的猫狗，性格行为差异巨大。这是上一章"冷启动很泛"的解法：
> **用品种先验做冷启动，用个体观测逐步校准。**

### 6.1 两件事，成熟度完全不同

| 任务 | 成熟度 | 做法 |
| --- | --- | --- |
| **品种识别**（它是什么品种） | ✅ 完全成熟 | 直接微调现成模型，不自训 |
| **品种→性格/行为先验**（这品种通常什么脾气） | ⚠️ 无现成可推理模型 | **自建知识库**（这是护城河） |

- **品种识别**：狗用 [Stanford Dogs](https://github.com/ayushdabra/stanford-dogs-dataset-classification)（120 品种，
  EfficientNet/InceptionV3 迁移学习约 80% 验证准确率）；猫狗混合用 Oxford-IIIT Pet（37 品种）。
  手机拍一张照 → 模型给候选品种 → 用户点确认，完全可行。
- **品种行为先验**：有**数据**但无现成产品级模型。金矿是 **C-BARQ 数据集**（宾大犬类行为评估问卷，
  覆盖 **12000+ 只各品种狗**的标准化行为指标），是研究"品种×行为"的权威源；已有研究把狗性格归纳为
  **5 型**（易激动/过度依恋、焦虑/胆怯、疏离/捕食、反应/强势、冷静/随和），甚至有用可穿戴活动数据
  预测性格（AUC 0.63–0.90）。

> 参考：[C-BARQ 12000+ 狗行为数据集应用](https://link.springer.com/10.1007/978-981-96-4139-0_7)、
> [AI 预测狗性格类型（Nature 2024）](https://www.nature.com/articles/s41598-024-52920-9)、
> [可穿戴推断狗性格](https://arxiv.org/html/2301.06964v2)。结论已重新表述。

### 6.2 三层设计（对应产品的"录入 → 懂它"）

```
用户手机确认宠物信息（品种/年龄/性别/绝育/习惯/喜好/猫粮/作息）
        │
        ▼
 A. 品种知识层（公共先验，内置 + 联网补充）
    · 内置品种行为知识库（C-BARQ 等结构化为 YAML/JSON）
    · 确认品种后，可信源白名单检索补充该品种资料 → 结构化入库
    · 产出该品种"行为基线先验"：活跃度/吠叫倾向/焦虑易感/亲人度/典型健康风险
        │ 冷启动即可用
        ▼
 B. 个体观测层（这只宠物的真实数据 = 前面的感知链路）
    · 多模态硬信号持续积累 → 这只宠物的个性化画像
        │ 贝叶斯式动态加权
        ▼
 C. 融合解读层（品种先验 × 个体观测）
    · 第一天：主要靠品种先验（"金毛通常亲人，这叫声可能求玩"）
    · 积累后：个体数据覆盖先验（"但你家这只其实很独立，这叫声历史上都是饿了"）
```

**核心机制 — 先验与个体的动态权重**（直接回答"后续和特有宠物信息合并"）：
观测越多，自动降低品种先验权重、提高个体权重。最终形成"品种说法 A，但你家这只是例外 B"的
个性化反差——这是最打动用户、也最难被抄走的东西。

### 6.3 哪些该自训、哪些不该

| 任务 | 建议 | 理由 |
| --- | --- | --- |
| 品种识别 | 不训，微调现成 | 预训练已够好 |
| 品种行为先验 | **不训模型，建知识库** | 这是结构化知识（C-BARQ 整理成查表/规则）+ LLM 推理，比训模型更灵活可解释 |
| 叫声情绪 | 可微调小模型 | VA 情绪模型 + 自有数据微调 |
| 个体行为分类 | 用户数据持续微调 | 每只宠物"专属动作词典"，EZ-CLIP 等小参数模型单卡可训 |

**注意**：联网补充品种资料要做**可信源白名单 + 结构化抽取**，不能把网页原文直接塞给 LLM（引入错误与不可信内容）。
产品话术要强调"这是品种普遍倾向，你家宝贝可能不一样"。

---

## 7. Agent 中枢：事件驱动分层

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

## 8. 父母移动端（iOS / Android）

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

## 9. 分阶段落地建议

| 阶段 | 目标 | 关键交付 |
| --- | --- | --- |
| **MVP（阶段一）** | 本地文件数据源跑通"看懂→学习→陪伴→告诉父母"闭环 | 本地服务器：YOLO 检测 + 按需 VLM + Whisper；记忆画像；父母端 RN App 看报告 + 对话；LiveKit 打通一条实时音视频 |
| **阶段二** | 接入远程摄像头实时流 | go2rtc + FFmpeg 接入层；实时直播到父母端；常驻检测 + 事件触发分析上线 |
| **阶段三** | 细粒度习惯学习 + 健康预警 | 姿态/行为/情绪专项分析器；长期画像与异常基线；主动陪伴与预警 |
| **阶段四** | 多源融合 | 多摄像头 + 传感器（喂食器/项圈）融合，多宠物区分 |

---

## 10. 关键风险与注意

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
