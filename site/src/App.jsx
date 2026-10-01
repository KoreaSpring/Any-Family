import { useEffect, useRef, useState } from 'react'
import useReveal from './useReveal.js'
import * as img from './assets/index.js'

const NAV = [
  { href: '#product', label: '产品' },
  { href: '#features', label: '功能' },
  { href: '#how', label: '工作原理' },
  { href: '#privacy', label: '隐私' },
  { href: '#download', label: '下载' },
]

function Logo() {
  return (
    <a href="#top" className="flex items-center gap-2.5 cursor-pointer whitespace-nowrap">
      <span className="w-8 h-8 rounded-full bg-primary-500 text-background-50 flex items-center justify-center">
        <i className="ri-footprint-fill text-base" />
      </span>
      <span className="font-heading font-bold text-lg tracking-tight text-foreground-950">
        Any-Family
        <span className="ml-1.5 text-sm font-body font-normal text-foreground-500">伴宠</span>
      </span>
    </a>
  )
}

function Header() {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-background-50/90 backdrop-blur border-b border-background-200 shadow-sm' : 'bg-background-50/80 backdrop-blur border-b border-background-200/60'
      }`}
    >
      <nav className="w-full px-4 md:px-10 h-16 md:h-20 flex items-center justify-between">
        <Logo />
        <ul className="hidden md:flex items-center gap-9">
          {NAV.map((n) => (
            <li key={n.href}>
              <a
                href={n.href}
                className="text-sm text-foreground-700 hover:text-primary-600 transition-colors cursor-pointer whitespace-nowrap"
              >
                {n.label}
              </a>
            </li>
          ))}
        </ul>
        <div className="flex items-center gap-3">
          <a
            href="#download"
            className="hidden md:inline-flex items-center gap-2 bg-primary-500 hover:bg-primary-600 text-background-50 text-sm font-medium px-5 py-2.5 rounded-full transition-colors cursor-pointer whitespace-nowrap"
          >
            下载 App
          </a>
          <button
            type="button"
            aria-label="菜单"
            onClick={() => setMenuOpen((v) => !v)}
            className="md:hidden w-10 h-10 flex items-center justify-center rounded-full cursor-pointer"
          >
            <i className={`text-xl text-foreground-900 ${menuOpen ? 'ri-close-line' : 'ri-menu-line'}`} />
          </button>
        </div>
      </nav>
      {menuOpen && (
        <ul className="md:hidden bg-background-50 border-b border-background-200 px-4 pb-4 flex flex-col gap-1">
          {NAV.map((n) => (
            <li key={n.href}>
              <a
                href={n.href}
                onClick={() => setMenuOpen(false)}
                className="block py-2.5 text-sm text-foreground-700 hover:text-primary-600"
              >
                {n.label}
              </a>
            </li>
          ))}
          <li>
            <a
              href="#download"
              onClick={() => setMenuOpen(false)}
              className="mt-2 inline-flex items-center gap-2 bg-primary-500 text-background-50 text-sm font-medium px-5 py-2.5 rounded-full"
            >
              下载 App
            </a>
          </li>
        </ul>
      )}
    </header>
  )
}

function Hero() {
  return (
    <section id="top" className="relative bg-background-50 pt-16 md:pt-20">
      <div className="relative w-full h-[560px] md:h-[680px] overflow-hidden">
        <img
          alt="伴宠 AI 陪伴设备与狗狗在明亮客厅里"
          className="absolute inset-0 w-full h-full object-cover object-center"
          src={img.heroLivingRoom}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-background-50 via-background-50/90 to-background-50/5" />
        <div className="relative h-full max-w-7xl mx-auto px-4 md:px-10 flex items-center">
          <div className="w-full md:w-[62%] lg:w-[54%] reveal is-visible">
            <p className="text-sm font-medium text-foreground-500">全天候宠物陪伴 AI</p>
            <h1 className="mt-4 text-4xl md:text-6xl font-black tracking-tight leading-[1.08] text-foreground-950">
              让宠物不孤单，
              <br />
              让父母更懂它
            </h1>
            <p className="mt-6 text-base md:text-lg text-foreground-600 leading-relaxed max-w-lg">
              本地 AI Agent 加手机 App，全天候陪伴与读懂你的毛孩子。越用越懂它，也是贴心的健康管家。
            </p>
            <div className="mt-9 flex flex-col sm:flex-row gap-3">
              <a
                href="#download"
                className="inline-flex justify-center items-center gap-2 bg-primary-500 hover:bg-primary-600 text-background-50 font-medium px-7 py-3.5 rounded-full transition-all shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30 hover:-translate-y-0.5 cursor-pointer whitespace-nowrap"
              >
                <i className="ri-download-2-line" />
                下载 App
              </a>
              <a
                href="#how"
                className="inline-flex justify-center items-center gap-2 border border-foreground-300 hover:border-foreground-900 text-foreground-900 font-medium px-7 py-3.5 rounded-full transition-colors cursor-pointer whitespace-nowrap"
              >
                <i className="ri-play-circle-line" />
                了解原理
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function PainPoints() {
  return (
    <section className="bg-background-50 py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-4 md:px-10 flex flex-col md:flex-row items-center gap-10 md:gap-16">
        <div className="w-full md:w-1/2 h-[300px] md:h-[440px] rounded-2xl overflow-hidden reveal">
          <img alt="女孩与猫咪亲昵互动" className="w-full h-full object-cover object-top" src={img.introCat} />
        </div>
        <div className="w-full md:w-1/2 reveal">
          <span className="text-xs font-label font-semibold tracking-[0.22em] uppercase text-foreground-500">
            我们懂你的牵挂
          </span>
          <div className="mt-7 space-y-7">
            <div className="border-l-2 border-primary-200 pl-5">
              <h3 className="text-lg md:text-xl font-bold text-foreground-950">“不在家时，它过得好不好？”</h3>
              <p className="mt-2 text-sm text-foreground-600 leading-relaxed">
                关上门的那一刻，心就悬着了。它有没有好好吃饭、是不是一直在门口等你？
              </p>
            </div>
            <div className="border-l-2 border-primary-200 pl-5">
              <h3 className="text-lg md:text-xl font-bold text-foreground-950">“它不会说话，我读不懂它。”</h3>
              <p className="mt-2 text-sm text-foreground-600 leading-relaxed">
                一声叫、一次蹭、突然不爱动了……你想知道它到底想说什么。
              </p>
            </div>
          </div>
          <p className="mt-9 text-base text-foreground-800 leading-relaxed">
            伴宠想做的，是在你不在的时候，替你
            <strong className="font-semibold text-primary-600">陪着它</strong>
            ；在你想念的时候，帮你
            <strong className="font-semibold text-primary-600">读懂它</strong>。
          </p>
        </div>
      </div>
    </section>
  )
}

const PILLARS = [
  {
    img: img.pillarAgent,
    icon: 'ri-cpu-line',
    iconCls: 'bg-accent-50 text-accent-600',
    label: 'AI Agent',
    title: '本地 AI Agent',
    desc: '跑在家里的智能大脑。通过音视频持续感知、学习它的作息与习惯，并在本地完成解读与决策，隐私数据不出门。',
    tags: ['本地优先运行', '越用越懂它', '断网也能守护'],
    reverse: false,
  },
  {
    img: img.pillarApp,
    icon: 'ri-smartphone-line',
    iconCls: 'bg-primary-50 text-primary-600',
    label: 'App',
    title: '跨平台 App',
    desc: 'iOS / Android 双端可用。不论在通勤、开会还是出差，都能随时看看它、问问它今天怎么样、和它说说话。',
    tags: ['实时画面', '一句话提问', '远程互动'],
    reverse: true,
  },
  {
    img: img.pillarCare,
    icon: 'ri-heart-3-line',
    iconCls: 'bg-secondary-100 text-secondary-700',
    label: '陪伴',
    title: '全天候陪伴',
    desc: '不只是被动监控。察觉到它焦躁、无聊或等你回家时，会主动互动、轻声安抚，让独处的时光也有回应。',
    tags: ['主动互动', '情绪安抚', '异常提醒'],
    reverse: false,
  },
]

function Pillars() {
  return (
    <section id="product" className="bg-background-100 py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-4 md:px-10">
        <div className="reveal mb-12 md:mb-16 text-center max-w-2xl mx-auto">
          <span className="text-xs font-label font-semibold tracking-[0.22em] uppercase text-foreground-500">
            三位一体
          </span>
          <h2 className="mt-3 text-2xl md:text-4xl font-bold tracking-tight leading-tight text-foreground-950">
            一个大脑、一部手机、一份陪伴
          </h2>
          <p className="mt-4 text-sm md:text-base text-foreground-600 leading-relaxed">
            AI Agent 在家感知与思考，App 把它的心情带到你身边，陪伴让每一刻都有回应。
          </p>
        </div>
        <div className="flex flex-col gap-10 md:gap-14">
          {PILLARS.map((p, i) => (
            <div
              key={p.title}
              className={`reveal flex flex-col md:flex-row gap-6 md:gap-12 items-center ${
                p.reverse ? 'md:flex-row-reverse' : ''
              }`}
              style={{ transitionDelay: `${i * 70}ms` }}
            >
              <div className="w-full md:w-1/2">
                <div className="relative w-full aspect-[7/5] rounded-2xl overflow-hidden border border-background-200 bg-background-50">
                  <img alt={p.title} className="absolute inset-0 w-full h-full object-cover object-center" src={p.img} />
                </div>
              </div>
              <div className="w-full md:w-1/2">
                <div className="flex items-center gap-3">
                  <span className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl ${p.iconCls}`}>
                    <i className={p.icon} />
                  </span>
                  <span className="font-label text-xs font-semibold tracking-[0.22em] uppercase text-foreground-400">
                    {p.label}
                  </span>
                </div>
                <h3 className="mt-5 text-xl md:text-2xl font-bold text-foreground-950">{p.title}</h3>
                <p className="mt-3 text-sm md:text-base text-foreground-600 leading-relaxed max-w-xl">{p.desc}</p>
                <ul className="mt-6 flex flex-wrap gap-2.5">
                  {p.tags.map((t) => (
                    <li
                      key={t}
                      className="inline-flex items-center gap-1.5 text-xs font-medium text-foreground-700 bg-background-50 border border-background-200 rounded-full px-3.5 py-2 whitespace-nowrap"
                    >
                      <i className="ri-check-line text-accent-600" />
                      {t}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

const FEATURES = [
  {
    img: img.featKnow,
    icon: 'ri-search-eye-line',
    no: '01',
    title: '了解宠物',
    sub: 'AI 帮你汇总它的一天',
    desc: '今日概览、行为时间线、习惯画像一目了然；还能对比「品种普遍倾向 vs 你家这只」，看见它独一无二的小脾气。',
    tags: ['今日概览', '时间线', '习惯画像', '品种对比'],
    reverse: false,
  },
  {
    img: img.featHear,
    icon: 'ri-voiceprint-line',
    no: '02',
    title: '听懂我',
    sub: '叫声背后的情绪与需求',
    desc: '把叫声实时解读成「情绪 + 可能需求 + 置信度 + 依据」。结合画面与历史习惯综合判断，不是逐词翻译。',
    tags: ['情绪', '可能需求', '置信度 82%', '判断依据'],
    reverse: true,
  },
  {
    img: img.featSee,
    icon: 'ri-chat-smile-3-line',
    no: '03',
    title: '看到我',
    sub: '用熟悉的声音远程安抚',
    desc: '在 App 里输入文字，用它熟悉的指令词 + 你熟悉的声音说出来，远程安抚、打招呼或下达「坐下」「等等」。',
    tags: ['文字转语音', '主人声音', '常用指令词'],
    reverse: false,
  },
]

function Features() {
  return (
    <section id="features" className="bg-background-50 py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-4 md:px-10">
        <div className="reveal mb-12 md:mb-16 text-center max-w-2xl mx-auto">
          <span className="text-xs font-label font-semibold tracking-[0.22em] uppercase text-foreground-500">
            三大入口
          </span>
          <h2 className="mt-3 text-2xl md:text-4xl font-bold tracking-tight leading-tight text-foreground-950">
            了解它、听懂它、回应它
          </h2>
          <p className="mt-4 text-sm md:text-base text-foreground-600 leading-relaxed">
            打开 App，三个入口就是你和毛孩子之间的三座桥。
          </p>
        </div>
        <div className="space-y-14 md:space-y-24">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className={`reveal flex flex-col items-center gap-8 md:gap-16 ${
                f.reverse ? 'md:flex-row-reverse' : 'md:flex-row'
              }`}
            >
              <div className="w-full md:w-1/2 h-[280px] md:h-[420px] rounded-2xl overflow-hidden bg-background-100">
                <img alt={`伴宠 ${f.title} 功能`} className="w-full h-full object-cover object-top" src={f.img} />
              </div>
              <div className="w-full md:w-1/2">
                <div className="flex items-center gap-3 text-primary-600">
                  <span className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center text-xl">
                    <i className={f.icon} />
                  </span>
                  <span className="font-label font-semibold text-xs tracking-[0.2em] text-foreground-400">{f.no}</span>
                </div>
                <h3 className="mt-5 text-2xl md:text-3xl font-bold tracking-tight text-foreground-950">{f.title}</h3>
                <p className="mt-2 text-sm text-primary-600 font-medium">{f.sub}</p>
                <p className="mt-4 text-sm md:text-base text-foreground-600 leading-relaxed">{f.desc}</p>
                <div className="mt-6 flex flex-wrap gap-2">
                  {f.tags.map((t) => (
                    <span
                      key={t}
                      className="text-xs text-foreground-600 bg-background-100 border border-background-200 px-3 py-1.5 rounded-full whitespace-nowrap"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default function App() {
  useReveal()
  return (
    <div className="min-h-screen bg-background-50">
      <Header />
      <main>
        <Hero />
        <PainPoints />
        <Pillars />
        <Features />
        <Health3D />
        <HowItWorks />
        <Privacy />
        <Scenes />
        <Download />
      </main>
      <Footer />
    </div>
  )
}


// ---- 3D 健康形态图：拖动旋转 + 复位 ----
const HOTSPOTS = [
  { label: '左耳', left: '34%', top: '18%', color: 'bg-primary-500 ring-primary-100' },
  { label: '右后腿关节', left: '70%', top: '66%', color: 'bg-accent-500 ring-accent-100' },
  { label: '腹部', left: '52%', top: '52%', color: 'bg-accent-500 ring-accent-100' },
]

function Health3D() {
  const [angle, setAngle] = useState(0)
  const dragRef = useRef({ dragging: false, startX: 0, startAngle: 0 })

  const onDown = (e) => {
    const x = e.touches ? e.touches[0].clientX : e.clientX
    dragRef.current = { dragging: true, startX: x, startAngle: angle }
  }
  const onMove = (e) => {
    if (!dragRef.current.dragging) return
    const x = e.touches ? e.touches[0].clientX : e.clientX
    const delta = (x - dragRef.current.startX) * 0.5
    setAngle(dragRef.current.startAngle + delta)
  }
  const onUp = () => {
    dragRef.current.dragging = false
  }

  useEffect(() => {
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    window.addEventListener('touchmove', onMove, { passive: true })
    window.addEventListener('touchend', onUp)
    return () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
      window.removeEventListener('touchmove', onMove)
      window.removeEventListener('touchend', onUp)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const normalized = ((Math.round(angle) % 360) + 360) % 360

  return (
    <section className="bg-background-100 py-16 md:py-24 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 md:px-10 flex flex-col md:flex-row items-center gap-10 md:gap-16">
        <div className="w-full md:w-[45%] reveal">
          <span className="text-xs font-label font-semibold tracking-[0.22em] uppercase text-foreground-500">
            亮点 · 3D 健康形态图
          </span>
          <h2 className="mt-3 text-2xl md:text-4xl font-bold tracking-tight text-foreground-950 leading-tight">
            像看穴位图一样，
            <br />
            看见它可能不舒服的地方
          </h2>
          <p className="mt-4 text-sm md:text-base text-foreground-600 leading-relaxed">
            Agent 结合日常行为、步态、饮食与作息变化，在 3D 形象上高亮值得留意的部位。拖动可 360° 旋转，点击光点查看依据与建议。
          </p>
          <div className="mt-8 bg-background-50 border border-background-200 rounded-2xl p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-foreground-950">左耳</h3>
              <span className="text-xs bg-secondary-100 text-secondary-800 px-3 py-1 rounded-full whitespace-nowrap">
                建议观察
              </span>
            </div>
            <p className="mt-4 text-xs font-semibold text-foreground-500">判断依据</p>
            <p className="mt-1 text-sm text-foreground-700 leading-relaxed">
              近 3 天抓挠左耳频次较平时上升约 2.4 倍，并伴随甩头动作。
            </p>
            <p className="mt-4 text-xs font-semibold text-foreground-500">观察建议</p>
            <p className="mt-1 text-sm text-foreground-700 leading-relaxed">
              留意耳道是否有异味或分泌物；若持续或加重，请及时咨询兽医。
            </p>
          </div>
          <p className="mt-5 flex items-start gap-2 text-xs text-foreground-500 leading-relaxed">
            <i className="ri-information-line mt-0.5" />
            以上为健康提示，不是诊断。如有疑虑，建议就医，一切以兽医意见为准。
          </p>
        </div>
        <div className="w-full md:w-[55%] reveal">
          <div
            className="relative w-full h-[340px] md:h-[520px] rounded-2xl bg-background-50 border border-background-200 overflow-hidden cursor-grab active:cursor-grabbing select-none touch-none"
            style={{ perspective: '1200px' }}
            onMouseDown={onDown}
            onTouchStart={onDown}
          >
            <div className="absolute inset-0 flex items-center justify-center">
              <div
                className="relative w-[78%] h-[85%]"
                style={{ transform: `rotateY(${angle}deg)`, transformStyle: 'preserve-3d', transition: dragRef.current.dragging ? 'none' : 'transform 0.4s' }}
              >
                <img
                  alt="3D 宠物健康形态图"
                  draggable="false"
                  className="w-full h-full object-contain object-center"
                  src={img.model3dDog}
                />
                {HOTSPOTS.map((h) => (
                  <button
                    key={h.label}
                    type="button"
                    aria-label={h.label}
                    className="absolute -translate-x-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center cursor-pointer"
                    style={{ left: h.left, top: h.top }}
                  >
                    <span className={`w-3.5 h-3.5 rounded-full ring-4 ${h.color}`} />
                  </button>
                ))}
              </div>
            </div>
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-background-50 border border-background-200 text-xs text-foreground-600 px-4 py-2 rounded-full whitespace-nowrap">
              <i className="ri-drag-move-line" />
              拖动旋转 · {normalized}°
            </div>
            <button
              type="button"
              onClick={() => setAngle(0)}
              className="absolute top-4 right-4 w-9 h-9 rounded-full bg-background-50 border border-background-200 text-foreground-700 flex items-center justify-center cursor-pointer"
              aria-label="复位"
            >
              <i className="ri-refresh-line" />
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}

const STEPS = [
  { img: img.stepSense, icon: 'ri-eye-line', iconCls: 'bg-accent-50 text-accent-600', no: 'STEP 01', title: '感知', desc: '家中设备通过音视频持续感知它的动作、声音与环境。', tag: '本地设备', tagIcon: 'ri-home-wifi-line' },
  { img: img.stepMemory, icon: 'ri-brain-line', iconCls: 'bg-accent-50 text-accent-600', no: 'STEP 02', title: '学习记忆', desc: 'Agent 在本地服务器上记录作息、习惯，形成专属画像。', tag: '本地服务器', tagIcon: 'ri-home-wifi-line' },
  { img: img.stepDecide, icon: 'ri-lightbulb-flash-line', iconCls: 'bg-accent-50 text-accent-600', no: 'STEP 03', title: '解读决策', desc: '结合画面、声音与历史，给出情绪/需求解读和置信度，并决定是否主动陪伴。', tag: '本地服务器', tagIcon: 'ri-home-wifi-line' },
  { img: img.stepTell, icon: 'ri-smartphone-line', iconCls: 'bg-primary-50 text-primary-600', no: 'STEP 04', title: '父母端表达', desc: '把结论以概览、提醒、对话的方式送到你的手机 App。', tag: 'iOS / Android', tagIcon: 'ri-smartphone-line' },
]

function HowItWorks() {
  return (
    <section id="how" className="bg-background-50 py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-4 md:px-10">
        <div className="reveal mb-12 md:mb-16 text-center max-w-2xl mx-auto">
          <span className="text-xs font-label font-semibold tracking-[0.22em] uppercase text-foreground-500">
            工作原理
          </span>
          <h2 className="mt-3 text-2xl md:text-4xl font-bold tracking-tight leading-tight text-foreground-950">
            家里思考，手机表达
          </h2>
          <p className="mt-4 text-sm md:text-base text-foreground-600 leading-relaxed">
            感知、记忆与解读都在家庭本地服务器完成，手机 App 只负责把结论温柔地告诉你。
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 md:gap-6">
          {STEPS.map((s, i) => (
            <div
              key={s.title}
              className="reveal bg-background-100 rounded-2xl border border-background-200 overflow-hidden flex flex-col sm:flex-row hover:-translate-y-1 transition-transform duration-300"
              style={{ transitionDelay: `${i * 70}ms` }}
            >
              <div className="relative w-full h-48 sm:h-auto sm:w-2/5 shrink-0">
                <img alt={s.title} className="absolute inset-0 w-full h-full object-cover object-center" src={s.img} />
              </div>
              <div className="flex-1 p-6">
                <div className="flex items-center gap-3">
                  <span className={`w-11 h-11 rounded-xl flex items-center justify-center text-lg ${s.iconCls}`}>
                    <i className={s.icon} />
                  </span>
                  <p className="font-label font-semibold text-xs tracking-[0.2em] text-foreground-400">{s.no}</p>
                </div>
                <h3 className="mt-4 text-lg font-bold text-foreground-950">{s.title}</h3>
                <p className="mt-2 text-sm text-foreground-600 leading-relaxed">{s.desc}</p>
                <span className="mt-4 inline-flex items-center gap-1.5 text-xs text-foreground-500 whitespace-nowrap">
                  <i className={s.tagIcon} />
                  {s.tag}
                </span>
              </div>
            </div>
          ))}
        </div>
        <div className="reveal mt-10 flex flex-col md:flex-row items-center justify-center gap-4 text-sm text-foreground-600">
          <span className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-accent-500" />
            本地服务器（AI Agent）
          </span>
          <i className="ri-arrow-left-right-line text-foreground-300 hidden md:block" />
          <span className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-primary-500" />
            父母陪伴端（App，加密连接）
          </span>
        </div>
      </div>
    </section>
  )
}

const PRIVACY_CARDS = [
  { icon: 'ri-home-4-line', title: '本地优先', desc: '音视频处理与记忆存储默认在家庭本地服务器完成。' },
  { icon: 'ri-shield-keyhole-line', title: '数据不出门', desc: '原始画面不上传云端，App 只接收你授权的加密结果。' },
  { icon: 'ri-fingerprint-line', title: '生物特征可控', desc: '声纹、面部等特征数据需要你授权，可随时一键删除。' },
  { icon: 'ri-eye-off-line', title: '透明可查', desc: '每一条解读都附带依据，你始终知道它为什么这么判断。' },
]

function Privacy() {
  return (
    <section id="privacy" className="bg-background-100 py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-4 md:px-10 flex flex-col md:flex-row gap-10 md:gap-16 items-center">
        <div className="w-full md:w-1/2 reveal">
          <span className="text-xs font-label font-semibold tracking-[0.22em] uppercase text-foreground-500">
            隐私与信任
          </span>
          <h2 className="mt-3 text-2xl md:text-4xl font-bold tracking-tight text-foreground-950 leading-tight">
            它的一切，
            <br />
            都留在你们的家里
          </h2>
          <p className="mt-4 text-sm md:text-base text-foreground-600 leading-relaxed">
            我们相信，真正的陪伴从信任开始。伴宠采用本地优先架构，家是数据的边界。
          </p>
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {PRIVACY_CARDS.map((c) => (
              <div key={c.title} className="bg-background-50 rounded-2xl p-5 border border-background-200">
                <span className="w-10 h-10 rounded-xl bg-primary-50 text-primary-600 flex items-center justify-center text-lg">
                  <i className={c.icon} />
                </span>
                <h3 className="mt-4 text-base font-bold text-foreground-950">{c.title}</h3>
                <p className="mt-1.5 text-sm text-foreground-600 leading-relaxed">{c.desc}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="w-full md:w-1/2 reveal">
          <div className="relative w-full h-[300px] md:h-[480px] rounded-2xl overflow-hidden">
            <img alt="家庭本地部署示意图" className="w-full h-full object-cover object-center" src={img.privacyLocal} />
            <div className="absolute top-4 left-4 bg-background-50 rounded-xl border border-background-200 px-4 py-3 flex items-center gap-3">
              <span className="w-9 h-9 rounded-full bg-primary-50 text-primary-600 flex items-center justify-center">
                <i className="ri-server-line" />
              </span>
              <div>
                <p className="text-xs text-foreground-500">家庭本地服务器</p>
                <p className="text-sm font-bold text-foreground-950">运行中 · 数据 0 上传</p>
              </div>
            </div>
            <div className="absolute bottom-4 right-4 bg-background-50 rounded-xl border border-background-200 px-4 py-3 flex items-center gap-2 text-sm text-foreground-900">
              <i className="ri-lock-2-line text-primary-600" />
              端到端加密连接 App
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

const SCENES = [
  { img: img.sceneOffice, title: '朝九晚六的上班族', desc: '午休打开 App，看看它有没有好好睡午觉，顺便叫一声它的名字。' },
  { img: img.sceneTravel, title: '经常出差的旅人', desc: '在酒店里也能收到它今天的状态概览，异常时第一时间被提醒。' },
  { img: img.sceneMulti, title: '热闹的多宠家庭', desc: 'Agent 能分辨每一只毛孩子，分别记录它们的习惯与小情绪。' },
  { img: img.sceneSenior, title: '陪伴老年宠物', desc: '更细致地留意步态、饮食与作息变化，给出温和的观察建议。' },
]

function Scenes() {
  return (
    <section className="bg-background-50 py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-4 md:px-10">
        <div className="reveal mb-12 md:mb-16 text-center max-w-2xl mx-auto">
          <span className="text-xs font-label font-semibold tracking-[0.22em] uppercase text-foreground-500">
            适用场景
          </span>
          <h2 className="mt-3 text-2xl md:text-4xl font-bold tracking-tight leading-tight text-foreground-950">
            每一种生活，都值得被陪伴
          </h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {SCENES.map((s, i) => (
            <article
              key={s.title}
              className="reveal group bg-background-100 rounded-2xl overflow-hidden border border-background-200 hover:-translate-y-1 transition-transform duration-300"
              style={{ transitionDelay: `${i * 70}ms` }}
            >
              <div className="w-full h-60 overflow-hidden">
                <img
                  alt={s.title}
                  className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-700"
                  src={s.img}
                />
              </div>
              <div className="p-5">
                <h3 className="text-base font-bold text-foreground-950">{s.title}</h3>
                <p className="mt-2 text-sm text-foreground-600 leading-relaxed">{s.desc}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}

function Download() {
  return (
    <section id="download" className="bg-background-100 py-16 md:py-24">
      <div className="max-w-6xl mx-auto px-4 md:px-10">
        <div className="reveal flex flex-col md:flex-row items-center gap-10 md:gap-16">
          <div className="w-full md:w-3/5">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight leading-tight text-foreground-950">
              现在就更懂
              <br />
              你的毛孩子
            </h2>
            <p className="mt-4 text-sm md:text-base text-foreground-600 leading-relaxed max-w-md">
              下载伴宠 App，连接家中的 AI Agent，开启第一天的陪伴与了解。
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-3">
              <a
                href="#download"
                className="inline-flex items-center justify-center gap-3 bg-foreground-950 hover:bg-foreground-800 text-background-50 px-5 py-3 rounded-xl transition-colors cursor-pointer whitespace-nowrap"
              >
                <i className="ri-apple-fill text-2xl" />
                <span className="text-left leading-tight">
                  <span className="block text-[10px] opacity-70">Download on the</span>
                  <span className="text-sm font-semibold">App Store</span>
                </span>
              </a>
              <a
                href="#download"
                className="inline-flex items-center justify-center gap-3 bg-foreground-950 hover:bg-foreground-800 text-background-50 px-5 py-3 rounded-xl transition-colors cursor-pointer whitespace-nowrap"
              >
                <i className="ri-google-play-fill text-2xl" />
                <span className="text-left leading-tight">
                  <span className="block text-[10px] opacity-70">GET IT ON</span>
                  <span className="text-sm font-semibold">Google Play</span>
                </span>
              </a>
            </div>
          </div>
          <div className="w-full md:w-2/5 flex items-center justify-center gap-6">
            <div className="w-36 h-36 md:w-44 md:h-44 bg-background-50 rounded-2xl border border-background-200 p-3">
              <img alt="伴宠 AI 陪伴设备" className="w-full h-full object-contain" src={img.downloadDevice} />
            </div>
            <div className="bg-background-50 rounded-2xl border border-background-200 p-4 text-center">
              <div className="w-28 h-28 md:w-32 md:h-32 rounded-xl bg-background-100 border border-dashed border-background-300 flex flex-col items-center justify-center text-foreground-400">
                <i className="ri-qr-code-line text-4xl" />
                <span className="text-[10px] mt-1">二维码占位</span>
              </div>
              <p className="mt-2 text-xs text-foreground-600">扫码下载 App</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="bg-background-50 border-t border-background-200 pt-14 pb-8">
      <div className="max-w-7xl mx-auto px-4 md:px-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          <div>
            <Logo />
            <p className="mt-4 text-sm text-foreground-600 leading-relaxed max-w-xs">
              伴宠 Any-Family：全天候宠物陪伴 AI。让宠物不孤单，让父母更懂它。
            </p>
          </div>
          <div>
            <h4 className="text-sm font-bold text-foreground-950">
              <a href="#top">网站导航</a>
            </h4>
            <ul className="mt-4 grid grid-cols-2 gap-2">
              {NAV.map((n) => (
                <li key={n.href}>
                  <a href={n.href} className="text-sm text-foreground-600 hover:text-primary-600 cursor-pointer whitespace-nowrap">
                    {n.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-bold text-foreground-950">
              <a href="#privacy">我们的承诺</a>
            </h4>
            <p className="mt-4 text-xs text-foreground-600 leading-relaxed">
              <i className="ri-home-4-line text-primary-600 mr-1" />
              本地优先：音视频与记忆默认在家庭本地处理，隐私数据不出门。
            </p>
            <p className="mt-2 text-xs text-foreground-600 leading-relaxed">
              <i className="ri-stethoscope-line text-primary-600 mr-1" />
              伴宠提供的是情绪/状态解读与健康提示，不替代兽医诊断，如有不适请以兽医意见为准。
            </p>
          </div>
        </div>
        <div className="mt-12 pt-6 border-t border-background-200 flex flex-col sm:flex-row justify-between gap-2 text-xs text-foreground-500">
          <p>© 2026 Any-Family 伴宠. All rights reserved.</p>
          <p>用心陪伴每一个毛孩子</p>
        </div>
      </div>
    </footer>
  )
}
