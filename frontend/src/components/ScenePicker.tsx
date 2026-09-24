import type { Scene } from '@/api/catalog'

export default function ScenePicker({
  scenes,
  selected,
  disabled,
  onSelect,
}: {
  scenes: Scene[]
  selected?: string | null
  disabled?: boolean
  onSelect: (sceneId: string) => void
}) {
  if (scenes.length === 0) return null
  return (
    <ul className="grid grid-cols-4 gap-2 sm:grid-cols-6">
      {scenes.map((scene) => {
        const active = scene.id === selected
        return (
          <li key={scene.id}>
            <button
              type="button"
              disabled={disabled}
              title={scene.hint}
              onClick={() => onSelect(scene.id)}
              className={`w-full overflow-hidden rounded-[12px] border text-left disabled:opacity-40 ${
                active ? 'border-brand shadow-control' : 'border-line hover:border-brand'
              }`}
            >
              <span
                className="block aspect-[4/3] w-full"
                style={{ background: scene.swatch }}
                aria-hidden
              />
              <span className="text-ink block truncate px-1.5 py-1 text-[11px]">{scene.label}</span>
            </button>
          </li>
        )
      })}
    </ul>
  )
}
