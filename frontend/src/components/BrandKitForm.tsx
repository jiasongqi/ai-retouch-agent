import { useState } from 'react'

import type { Asset } from '@/api/assets'
import type { BrandKit, Scene } from '@/api/catalog'

const EMPTY: BrandKit = {
  primary_color: '#171917',
  accent_color: '#C4B5A0',
  logo_asset_id: null,
  safe_margin: 0.08,
  default_scene_id: 'marble',
  show_logo: true,
}

export default function BrandKitForm({
  value,
  scenes,
  assets,
  disabled,
  saving,
  onSave,
}: {
  value?: BrandKit
  scenes: Scene[]
  assets: Asset[]
  disabled?: boolean
  saving?: boolean
  onSave: (kit: BrandKit) => void
}) {
  const kit = value ?? EMPTY
  const [draft, setDraft] = useState<BrandKit>(kit)
  const [synced, setSynced] = useState(kit)
  if (kit !== synced) {
    setSynced(kit)
    setDraft(kit)
  }

  const logos = assets.filter((asset) => asset.kind !== 'mask')

  return (
    <div className="border-line bg-paper rounded-[16px] border p-4">
      <div className="mb-3 grid gap-3 sm:grid-cols-2">
        <label className="text-muted block text-xs">
          主色
          <span className="mt-1 flex items-center gap-2">
            <input
              type="color"
              value={draft.primary_color.toLowerCase()}
              disabled={disabled}
              onChange={(event) => setDraft({ ...draft, primary_color: event.target.value })}
            />
            <span className="text-faint tabular-nums">{draft.primary_color}</span>
          </span>
        </label>
        <label className="text-muted block text-xs">
          辅色
          <span className="mt-1 flex items-center gap-2">
            <input
              type="color"
              value={draft.accent_color.toLowerCase()}
              disabled={disabled}
              onChange={(event) => setDraft({ ...draft, accent_color: event.target.value })}
            />
            <span className="text-faint tabular-nums">{draft.accent_color}</span>
          </span>
        </label>
      </div>

      <label className="text-muted mb-3 block text-xs">
        安全边距 {Math.round(draft.safe_margin * 100)}%
        <input
          type="range"
          min={0.04}
          max={0.18}
          step={0.01}
          value={draft.safe_margin}
          disabled={disabled}
          onChange={(event) => setDraft({ ...draft, safe_margin: Number(event.target.value) })}
          className="mt-1 w-full"
        />
      </label>

      <label className="text-muted mb-3 block text-xs">
        默认场景
        <select
          value={draft.default_scene_id ?? ''}
          disabled={disabled}
          onChange={(event) =>
            setDraft({ ...draft, default_scene_id: event.target.value || null })
          }
          className="border-line text-ink mt-1 w-full rounded-[10px] border bg-transparent px-2 py-1.5 text-xs"
        >
          {scenes.map((scene) => (
            <option key={scene.id} value={scene.id}>
              {scene.label}
            </option>
          ))}
        </select>
      </label>

      {logos.length > 0 && (
        <div className="mb-3">
          <p className="text-muted mb-1.5 text-xs">角标 Logo</p>
          <ul className="flex flex-wrap gap-1.5">
            <li>
              <button
                type="button"
                disabled={disabled}
                onClick={() => setDraft({ ...draft, logo_asset_id: null })}
                className={`rounded-control border px-2 py-1 text-[11px] ${
                  !draft.logo_asset_id ? 'border-brand text-brand-strong' : 'border-line text-muted'
                }`}
              >
                不用
              </button>
            </li>
            {logos.slice(0, 8).map((asset) => (
              <li key={asset.id}>
                <button
                  type="button"
                  disabled={disabled}
                  onClick={() => setDraft({ ...draft, logo_asset_id: asset.id })}
                  className={`block overflow-hidden rounded-[8px] border ${
                    draft.logo_asset_id === asset.id ? 'border-brand' : 'border-line'
                  }`}
                >
                  <img src={asset.url} alt="" className="size-9 object-cover" />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <button
        type="button"
        disabled={disabled || saving}
        onClick={() => onSave(draft)}
        className="bg-ink hover:bg-dark rounded-control px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
      >
        {saving ? '保存中…' : '保存品牌设置'}
      </button>
    </div>
  )
}
