import type { Ratio } from '@/api/runs'

export type PromptTemplate = {
  id: string
  label: string
  prompt: string
  ratio: Ratio
}

/** 落地页与创作页共用的场景模板，点一下填入提示词。 */
export const PROMPT_TEMPLATES: PromptTemplate[] = [
  {
    id: 'hero',
    label: '白底主图',
    ratio: '1:1',
    prompt: '把这件商品放在纯白背景上，居中构图，柔和顶光，边缘干净，输出 1:1 主图。',
  },
  {
    id: 'scene',
    label: '场景氛围图',
    ratio: '4:5',
    prompt: '把商品放到温暖的木质桌面场景，侧逆光、浅景深，保留商品原有材质与颜色。',
  },
  {
    id: 'model',
    label: '模特上身',
    ratio: '4:5',
    prompt: '生成模特手持该商品的半身展示图，简洁室内背景、自然光，商品细节清晰可辨。',
  },
  {
    id: 'poster',
    label: '促销海报',
    ratio: '3:4',
    prompt: '做一张大促海报：主标题「新品首发」，副标题「限时 8 折」，突出商品，右侧留出文字区。',
  },
  {
    id: 'pack',
    label: '多尺寸物料',
    ratio: '1:1',
    prompt: '基于这张商品图输出一套投放物料，包含 1:1、4:5、9:16 三个尺寸，主体不被裁切。',
  },
]
