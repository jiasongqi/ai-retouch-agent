import { Link } from 'react-router-dom'

import BrandMark from '@/components/BrandMark'

const NAV = [
  { href: '#demo', label: '编排' },
  { href: '#capabilities', label: '能力' },
  { href: '#delivery', label: '交付' },
]

export default function LandingHeader({
  account,
  entry,
}: {
  account: string | null
  entry: { label: string; to: string }
}) {
  return (
    <header className="border-line/70 bg-canvas/80 sticky top-0 z-10 border-b backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-3.5">
        <Link to="/" aria-label="AI 修图智能体首页">
          <BrandMark size="sm">
            <span className="text-ink text-sm font-semibold">AI 修图智能体</span>
          </BrandMark>
        </Link>

        <nav className="text-muted hidden items-center gap-6 text-sm sm:flex">
          {NAV.map((item) => (
            <a key={item.href} href={item.href} className="hover:text-ink transition-colors">
              {item.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          {account ? (
            <Link
              to={entry.to}
              className="bg-ink hover:bg-dark rounded-control px-3.5 py-1.5 text-sm font-medium text-white transition-colors"
            >
              {account} · {entry.label}
            </Link>
          ) : (
            <>
              <Link to="/auth" className="text-muted hover:text-ink hidden text-sm transition-colors sm:inline">
                登录
              </Link>
              <Link
                to={entry.to}
                className="bg-ink hover:bg-dark rounded-control px-3.5 py-1.5 text-sm font-medium text-white transition-colors"
              >
                {entry.label}
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
