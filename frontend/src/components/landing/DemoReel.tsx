import { useEffect, useState } from 'react'

const FRAMES = [
  { src: '/landing/product-before.png', caption: '修前原图' },
  { src: '/landing/product-after.png', caption: '白底主图' },
  { src: '/landing/product-scene.png', caption: '场景氛围' },
  { src: '/landing/product-story.png', caption: '9:16 竖版' },
  { src: '/landing/product-poster.png', caption: '促销海报' },
]

/**
 * 中段演示：同一件商品从杂乱原图切到各投放画幅，步骤条跟着走。
 */
export default function DemoReel() {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)')
    if (media.matches) return
    const id = window.setInterval(() => {
      setIndex((current) => (current + 1) % FRAMES.length)
    }, 1800)
    return () => window.clearInterval(id)
  }, [])

  return (
    <section className="mx-auto max-w-5xl scroll-mt-20 px-6 py-16" id="demo">
      <header className="max-w-xl">
        <p className="text-brand-strong text-sm font-medium">编排</p>
        <h2 className="text-ink mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">
          一张原图，五步变成投放物料
        </h2>
        <p className="text-muted mt-3 leading-relaxed">
          抠图、换白底、出场景、切竖版、做海报。智能体按依赖自动跑完，你只确认结果。
        </p>
      </header>

      <figure className="border-line bg-paper shadow-card mt-8 overflow-hidden rounded-[22px] border">
        <div className="bg-canvas relative aspect-[4/5] sm:aspect-[16/10]">
          {FRAMES.map((frame, frameIndex) => (
            <img
              key={frame.src}
              src={frame.src}
              alt={frame.caption}
              className={`absolute inset-0 size-full object-cover transition-opacity duration-500 ${
                frameIndex === index ? 'opacity-100' : 'opacity-0'
              }`}
            />
          ))}
          <span className="bg-ink/75 absolute top-4 left-4 rounded-full px-3 py-1 text-xs text-white">
            {FRAMES[index].caption}
          </span>
        </div>
        <ol className="flex flex-wrap gap-2 px-5 py-3">
          {FRAMES.map((frame, frameIndex) => (
            <li key={frame.caption}>
              <button
                type="button"
                onClick={() => setIndex(frameIndex)}
                className={`rounded-full px-3 py-1 text-xs transition-colors ${
                  frameIndex === index
                    ? 'bg-ink text-white'
                    : 'bg-soft text-muted hover:text-ink'
                }`}
              >
                {frameIndex + 1}. {frame.caption}
              </button>
            </li>
          ))}
        </ol>
      </figure>
    </section>
  )
}
