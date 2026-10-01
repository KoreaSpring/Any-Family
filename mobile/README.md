# mobile/ — 父母端 App（Expo / React Native）

iOS / Android 跨平台 App。当前为可运行的 MVP：引导录入 + 首页（含三个入口）。

## 技术栈

- Expo (SDK 51) + Expo Router（文件路由）
- React Native 0.74（New Architecture 开启）
- TypeScript（`npm run typecheck` 通过）

## 已实现

```
mobile/
├── app/
│   ├── _layout.tsx    # 根布局（导航）
│   ├── index.tsx      # 引导录入：名字/物种/品种/年龄/指令/喜好 → POST /pet
│   └── home.tsx       # 首页：3D形象占位 + 今日概览 + 三入口 + 健康
├── lib/
│   ├── api.ts         # 服务端 REST 封装（/pet /overview /interpretations /ask /speak /play /feed ...）
│   └── theme.ts       # 配色
└── app.json           # extra.apiBaseUrl 指向本地服务端
```

首页三入口：
- 🔍 **了解宠物**：输入问题 → `/ask`（有 LLM 更自然，否则规则版）。
- 👂 **听懂我**：展示情绪/需求解读（带依据与置信度）。
- 💬 **看到我**：用主人熟悉的话远程播放 + 逗玩 + 投食。

## 跑起来

```bash
npm install
# 真机：把 app.json 的 extra.apiBaseUrl 改成电脑局域网 IP（如 http://192.168.1.10:8080）
npm start      # Expo Go 扫码，或 npm run android / npm run ios
npm run typecheck   # TS 校验
```

> 需先启动服务端（见 [../server/README.md](../server/README.md)）。
> 完整产品设计见 [../docs/PRODUCT.md](../docs/PRODUCT.md)。
