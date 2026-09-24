import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { catalogApi, type BrandKit } from '@/api/catalog'
import { errorMessage } from '@/hooks/useAuth'
import { toast } from '@/stores/toasts'

const KIT_KEY = ['brand-kit']
const SCENES_KEY = ['scenes']
const PLATFORMS_KEY = ['platforms']

export function useBrandKit() {
  return useQuery({ queryKey: KIT_KEY, queryFn: catalogApi.brandKit })
}

export function useSaveBrandKit() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: BrandKit) => catalogApi.saveBrandKit(body),
    onSuccess: (kit) => {
      queryClient.setQueryData(KIT_KEY, kit)
      toast('品牌设置已保存')
    },
    onError: (error) => toast(errorMessage(error), 'danger'),
  })
}

export function useScenes() {
  return useQuery({ queryKey: SCENES_KEY, queryFn: catalogApi.scenes })
}

export function usePlatforms() {
  return useQuery({ queryKey: PLATFORMS_KEY, queryFn: catalogApi.platforms })
}
