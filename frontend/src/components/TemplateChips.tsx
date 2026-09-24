import type { PromptTemplate } from '@/lib/templates'

export default function TemplateChips({
  templates,
  onPick,
  align = 'center',
}: {
  templates: PromptTemplate[]
  onPick: (template: PromptTemplate) => void
  align?: 'center' | 'start'
}) {
  return (
    <div className={`flex flex-wrap gap-2 ${align === 'start' ? 'justify-start' : 'justify-center lg:justify-start'}`}>
      {templates.map((template) => (
        <button
          key={template.id}
          type="button"
          onClick={() => onPick(template)}
          className="border-line bg-paper/70 text-muted hover:border-brand hover:text-brand-strong rounded-full border px-3.5 py-1.5 text-xs transition-colors"
        >
          {template.label}
        </button>
      ))}
    </div>
  )
}
