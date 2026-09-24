import { api } from '@/api/client'

export type BrandKit = {
  primary_color: string
  accent_color: string
  logo_asset_id: string | null
  safe_margin: number
  default_scene_id: string | null
  show_logo: boolean
}

export type Scene = {
  id: string
  label: string
  hint: string
  swatch: string
  prompt: string
}

export type Platform = {
  id: 'taobao_main' | 'amazon_main' | 'douyin_cover'
  label: string
  hint: string
  width: number
  height: number
  fill_ratio: number
}

export const catalogApi = {
  scenes: () => api.get<Scene[]>('/scenes'),
  platforms: () => api.get<Platform[]>('/platforms'),
  brandKit: () => api.get<BrandKit>('/brand-kit'),
  saveBrandKit: (body: BrandKit) => api.put<BrandKit>('/brand-kit', body),
}
