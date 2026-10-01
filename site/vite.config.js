import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages 部署在 https://<user>.github.io/<repo>/ 下时，
// base 需设置为 '/<repo>/'。此处 any-family 仓库的 site 子目录单独部署，
// 若用 gh-pages 发布到 any-family 仓库，base 用 '/any-family/'。
// 本地 dev / 自定义域名可用 '/'，通过环境变量切换。
export default defineConfig({
  base: process.env.DEPLOY_BASE || '/',
  plugins: [react()],
})
