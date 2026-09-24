import { Link } from 'react-router-dom'

export default function StartBanner({ label, to }: { label: string; to: string }) {
  return (
    <section id="start" className="mx-auto max-w-5xl scroll-mt-20 px-6 pb-20">
      <div className="bg-ink rounded-panel relative isolate overflow-hidden px-8 py-12 text-center sm:py-14">
        <div
          className="absolute inset-0 bg-[radial-gradient(52%_60%_at_50%_-10%,rgb(217_255_110/0.18),transparent_70%)]"
          aria-hidden
        />

        <div className="relative">
          <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
            第一句话，出四张可上架候选
          </h2>
          <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-white/65">
            登录即可开始。描述需求，或上传现有商品图。
          </p>

          <Link
            to={to}
            className="bg-accent text-ink rounded-control mt-7 inline-flex px-6 py-3 text-sm font-medium transition-opacity hover:opacity-90"
          >
            {label}
          </Link>

          <p className="mt-4 text-xs text-white/45">无需设计经验 · 支持 JPG / PNG / WebP</p>
        </div>
      </div>
    </section>
  )
}
