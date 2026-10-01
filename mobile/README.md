# mobile/ — 父母端跨平台 App

iOS / Android 跨平台 App，让父母随时了解宠物、与 agent 对话、远程互动。

## 技术栈

- React Native（New Architecture：Fabric + JSI + TurboModules）
- LiveKit React Native SDK（实时音视频）
- 3D 渲染：react-native-filament / three.js(GL)（首页 360° 可旋转宠物形态图）
- 推送：APNs（iOS）/ FCM（Android）

## 核心界面（规划）

- **引导录入**：拍照/录视频 → 品种确认 → 习惯/喜好/作息
- **首页 3D 形态图**：360° 可旋转宠物形象 + 穴位图式健康标注
- **🔍 了解宠物**：今日概览 / 时间线 / 习惯画像 / 品种 vs 个体
- **👂 听懂我**：宠物音频 → 情绪与需求的文字解读（带依据/置信度）
- **💬 看到我**：文字 → 熟悉指令词 + 主人声音远程回放
- 习惯 / 健康报告与提醒

> 完整功能设计见 [docs/PRODUCT.md](../docs/PRODUCT.md)，选型理由见 [docs/RESEARCH.md 第 8 节](../docs/RESEARCH.md)。当前为占位。
