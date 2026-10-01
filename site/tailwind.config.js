/** @type {import('tailwindcss').Config} */

// 把 readdy 的 oklch 色板映射为 Tailwind 颜色工具类。
// readdy CSS 里形如：oklch(var(--primary-500) / <alpha>)，
// 这里用 CSS 变量驱动，变量定义在 src/index.css 的 :root。
const shade = (name) => {
  const steps = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
  return steps.reduce((acc, s) => {
    acc[s] = `oklch(var(--${name}-${s}) / <alpha-value>)`
    return acc
  }, {})
}

export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        background: shade('background'),
        primary: shade('primary'),
        accent: shade('accent'),
        secondary: shade('secondary'),
        foreground: shade('foreground'),
      },
      fontFamily: {
        heading: ['var(--font-heading)'],
        body: ['var(--font-body)'],
        label: ['var(--font-label)'],
      },
      keyframes: {
        floaty: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      animation: {
        floaty: 'floaty 7s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
