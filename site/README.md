# 伴宠 Any-Family 品牌官网

全天候宠物陪伴 AI 的品牌官网。基于 Vite + React + Tailwind CSS，复刻自 readdy.ai 生成的设计稿，图片素材已全部本地化，可直接部署到 GitHub Pages。

## 技术栈

- **Vite 5** + **React 18**：构建与组件
- **Tailwind CSS 3**：样式，颜色用 oklch 色板（暖奶橘主色 + 青蓝科技辅色）
- **Remixicon**：图标（CDN）
- **Inter / Noto Sans SC**：字体（Google Fonts CDN）

## 本地开发

```bash
cd site
npm install
npm run dev      # 本地开发服务器
npm run build    # 生产构建，输出到 dist/
npm run preview  # 预览构建产物
```

## 目录结构

```
site/
├── index.html              # Vite 入口（含 SEO meta、字体与图标 CDN）
├── vite.config.js          # base 由 DEPLOY_BASE 环境变量控制
├── tailwind.config.js      # oklch 色板映射为 Tailwind 工具类
├── postcss.config.js
├── src/
│   ├── main.jsx            # React 入口
│   ├── App.jsx             # 全部页面区块（Header/Hero/三支柱/三入口/3D健康图/原理/隐私/场景/下载/Footer）
│   ├── useReveal.js        # 滚动淡入显现 hook
│   ├── index.css           # :root oklch 变量 + reveal 动画 + Tailwind 指令
│   └── assets/             # 页面所用图片（本地化，参与构建打包）
├── images/                 # 早期抓取的参考素材存档（不参与构建）
└── readdy-prompt.md        # readdy.ai 建站提示词存档
```

## 部署到 GitHub Pages

仓库已含 `.github/workflows/deploy-site.yml`，推送到 `main` 且改动涉及 `site/**` 时自动构建并发布。

一次性设置：在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。

部署后访问地址：`https://koreaspring.github.io/any-family/`

> workflow 构建时注入 `DEPLOY_BASE=/any-family/`，使资源路径匹配仓库子路径。
> 若改用自定义域名或部署到根路径，把该值改为 `/` 即可。

## 内容说明（诚实边界）

页面文案遵循产品红线：伴宠做的是宠物**情绪/状态/需求的解读**与**健康提示**，
不是逐词翻译宠物语言，也不替代兽医诊断。健康相关表述均带「建议观察 / 请以兽医为准」。

图片素材部分抓取自参考网站，仅用于原型。正式上线建议替换为自有或授权素材。
