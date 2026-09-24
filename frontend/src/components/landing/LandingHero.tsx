import { useRef, useState } from 'react'

import TemplateChips from '@/components/TemplateChips'
import { PROMPT_TEMPLATES } from '@/lib/templates'

import PromptComposer from './PromptComposer'
import StudioStage from './StudioStage'

const FACTS = ['无需设计经验', '支持 JPG / PNG / WebP', '1:1 / 4:5 / 9:16 一次导出']

export default function LandingHero({
  initialPrompt,
  submitLabel,
  onStart,
}: {
  initialPrompt: string
  submitLabel: string
  onStart: (prompt: string) => void
}) {
  const [prompt, setPrompt] = useState(initialPrompt)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const pick = (text: string) => {
    setPrompt(text)
    inputRef.current?.focus()
  }

  return (
    <section className="relative isolate overflow-hidden">
      <div className="bg-glow absolute inset-x-0 -top-24 h-[560px]" aria-hidden />
      <div className="bg-grid absolute inset-x-0 -top-24 h-[560px]" aria-hidden />

      <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-6 pt-14 pb-16 lg:grid-cols-[minmax(0,1fr)_380px] lg:gap-16 lg:pt-20 lg:pb-20">
        <div className="text-center lg:text-left">
          <p className="border-line bg-paper/80 text-muted animate-rise inline-flex items-center gap-2 rounded-full border px-3.5 py-1.5 text-xs backdrop-blur">
            <span className="bg-accent size-1.5 rounded-full" aria-hidden />
            面向电商运营与内容创作者
          </p>

          <h1 className="text-ink animate-rise mt-6 text-[2rem] leading-[1.2] font-semibold tracking-tight text-balance sm:text-[2.55rem] lg:text-[2.85rem]">
            一句话，交付
            <span className="relative mx-1 whitespace-nowrap">
              <span
                className="bg-accent/55 absolute inset-x-[-7px] top-[14%] bottom-[8%] -skew-x-6 rounded-[3px]"
                aria-hidden
              />
              <span className="relative">可上架</span>
            </span>
            的商品物料
          </h1>

          <p className="text-muted animate-rise mx-auto mt-5 max-w-xl leading-relaxed lg:mx-0">
            描述需求即可从零生成，也可上传商品图继续编辑。抠图、换背景、局部精修、扩图、图层拆分与多尺寸导出，全部由智能体自动编排。
          </p>

          <div className="animate-rise mx-auto mt-8 max-w-2xl lg:mx-0" style={{ animationDelay: '120ms' }}>
            <PromptComposer
              value={prompt}
              onChange={setPrompt}
              onSubmit={() => onStart(prompt)}
              onAttach={() => onStart(prompt)}
              submitLabel={submitLabel}
              placeholder="描述你想要的商品图，例：把这双跑鞋放到清晨的城市街道，侧逆光，输出 1:1 主图与 9:16 竖版…"
              inputRef={inputRef}
            />
          </div>

          <div className="animate-rise mt-4" style={{ animationDelay: '180ms' }}>
            <TemplateChips templates={PROMPT_TEMPLATES} onPick={(template) => pick(template.prompt)} />
          </div>

          <ul className="text-faint animate-rise mt-8 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-xs lg:justify-start">
            {FACTS.map((fact) => (
              <li key={fact} className="flex items-center gap-1.5">
                <span className="bg-line-strong size-1 rounded-full" aria-hidden />
                {fact}
              </li>
            ))}
          </ul>
        </div>

        <div className="animate-rise mx-auto w-full lg:mx-0" style={{ animationDelay: '160ms' }}>
          <StudioStage />
        </div>
      </div>
    </section>
  )
}
