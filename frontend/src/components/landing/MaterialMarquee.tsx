const BOARDS = [
  { label: '1:1 白底主图', ratio: '1:1', width: 'w-[158px]', src: '/landing/product-after.png' },
  { label: '4:5 场景图', ratio: '4:5', width: 'w-[136px]', src: '/landing/product-scene.png' },
  { label: '9:16 竖版', ratio: '9:16', width: 'w-[108px]', src: '/landing/product-story.png' },
  { label: '促销海报', ratio: '海报', width: 'w-[148px]', src: '/landing/product-poster.png' },
  { label: '修前原图', ratio: '原图', width: 'w-[136px]', src: '/landing/product-before.png' },
] as const

/**
 * 投放物料的灯箱：真实商品画板横向缓慢滚过。
 */
export default function MaterialMarquee() {
  return (
    <section className="border-line bg-soft overflow-hidden border-y py-10" aria-label="可导出的投放尺寸">
      <p className="text-muted mx-auto mb-6 max-w-5xl px-6 text-sm">一次导出，覆盖常用投放画幅</p>

      <div className="relative">
        <div className="from-soft pointer-events-none absolute inset-y-0 left-0 z-10 w-16 bg-gradient-to-r to-transparent" />
        <div className="from-soft pointer-events-none absolute inset-y-0 right-0 z-10 w-16 bg-gradient-to-l to-transparent" />

        <div className="animate-marquee hover:[animation-play-state:paused] motion-reduce:animate-none flex w-max">
          <BoardRow boards={BOARDS} />
          <BoardRow boards={BOARDS} decorative />
        </div>
      </div>
    </section>
  )
}

function BoardRow({
  boards,
  decorative = false,
}: {
  boards: typeof BOARDS
  decorative?: boolean
}) {
  return (
    <ul className="flex shrink-0 gap-5 pr-5" aria-hidden={decorative || undefined}>
      {boards.map((board) => (
        <li key={board.label} className="shrink-0">
          <Artboard label={board.label} ratio={board.ratio} width={board.width} src={board.src} />
        </li>
      ))}
    </ul>
  )
}

function Artboard({
  label,
  ratio,
  width,
  src,
}: {
  label: string
  ratio: string
  width: string
  src: string
}) {
  return (
    <figure className="w-[188px]">
      <div className="flex h-[228px] items-end justify-center">
        <div className={`relative ${width}`}>
          <CropMarks />
          <div className="border-line bg-paper relative overflow-hidden rounded-[4px] border shadow-[0_10px_28px_rgb(25_31_26/0.08)]">
            <div className="aspect-[4/5]">
              <img src={src} alt="" className="size-full object-cover" />
            </div>
            <span className="text-faint absolute bottom-1.5 left-1.5 rounded-[3px] bg-white/80 px-1.5 py-0.5 text-[9px] tabular-nums">
              {ratio}
            </span>
          </div>
        </div>
      </div>
      <figcaption className="text-muted mt-3 text-center text-xs">{label}</figcaption>
    </figure>
  )
}

function CropMarks() {
  return (
    <>
      <span className="border-faint/70 absolute -top-2 -left-2 size-3 border-t border-l" />
      <span className="border-faint/70 absolute -top-2 -right-2 size-3 border-t border-r" />
      <span className="border-faint/70 absolute -bottom-2 -left-2 size-3 border-b border-l" />
      <span className="border-faint/70 absolute -bottom-2 -right-2 size-3 border-b border-r" />
    </>
  )
}
