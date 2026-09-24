import { useEffect, useState } from 'react'

const JOBS = [
  { tool: '抠图', detail: '主体已分离' },
  { tool: '换背景', detail: '白底棚拍光' },
  { tool: '导出', detail: '1:1 · 4:5 · 9:16' },
]

/**
 * 首屏右侧的「正在修这一张」：同一件商品的真实原图 vs 可上架白底。
 * 分割线按修图工作台的前后对比滑杆来做，步骤条同步往前走。
 */
export default function StudioStage() {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)')
    if (media.matches) {
      setStep(JOBS.length)
      return
    }

    const id = window.setInterval(() => {
      setStep((current) => (current + 1) % (JOBS.length + 1))
    }, 2200)
    return () => window.clearInterval(id)
  }, [])

  const doneCount = step >= JOBS.length ? JOBS.length : step

  return (
    <figure className="group relative mx-auto w-full max-w-[380px]">
      <div className="border-line bg-paper shadow-panel rounded-[28px] border p-3" aria-hidden>
        <div className="relative overflow-hidden rounded-[20px]">
          <div className="relative aspect-[4/5] overflow-hidden">
            <img
              src="/landing/product-after.png"
              alt=""
              className="absolute inset-0 size-full object-cover"
            />
            <span className="bg-accent text-ink absolute top-3 right-3 z-[1] rounded-full px-2.5 py-1 text-[10px] font-medium">
              可上架
            </span>
            <div className="animate-studio-wipe group-hover:[animation-play-state:paused] motion-reduce:animate-none motion-reduce:[clip-path:inset(0_42%_0_0)] absolute inset-0">
              <img
                src="/landing/product-before.png"
                alt=""
                className="absolute inset-0 size-full object-cover"
              />
              <span className="bg-ink/70 absolute top-3 left-3 rounded-full px-2.5 py-1 text-[10px] text-white">
                修前
              </span>
            </div>
            <div className="animate-studio-divider group-hover:[animation-play-state:paused] motion-reduce:left-[58%] motion-reduce:animate-none pointer-events-none absolute inset-y-0 left-[78%] z-10 w-px bg-white">
              <span className="border-line bg-paper shadow-control absolute top-1/2 left-1/2 grid size-7 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full border">
                <SplitGlyph />
              </span>
            </div>
          </div>

          <ol className="bg-paper/92 border-line absolute inset-x-3 bottom-3 z-20 space-y-1 rounded-[14px] border px-3 py-2.5 backdrop-blur-sm">
            {JOBS.map((job, index) => {
              const done = index < doneCount
              const active = index === step && step < JOBS.length
              return (
                <li
                  key={job.tool}
                  className={`flex items-center gap-2 text-[11px] ${
                    done || active ? 'text-ink' : 'text-faint'
                  }`}
                >
                  <span
                    className={`grid size-4 shrink-0 place-items-center rounded-full ${
                      done ? 'bg-accent text-ink' : active ? 'bg-brand text-white' : 'bg-line'
                    }`}
                  >
                    {done ? <CheckGlyph /> : null}
                  </span>
                  <span className="font-medium">{job.tool}</span>
                  <span className="text-muted ml-auto">{job.detail}</span>
                </li>
              )
            })}
          </ol>
        </div>
      </div>

      <figcaption className="text-faint mt-3 text-center text-xs">
        智能体正在把一张原图编排成可投放主图
      </figcaption>
    </figure>
  )
}

function SplitGlyph() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="text-ink size-3.5">
      <path d="M9 8L5 12l4 4M15 8l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  )
}

function CheckGlyph() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="size-2.5">
      <path d="M5 13l4.5 4.5L19 7" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" />
    </svg>
  )
}
