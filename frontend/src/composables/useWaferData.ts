import { ref, onMounted } from 'vue'
import type { WaferData } from '@/types/wafer'

export function useWaferData() {
  const waferData = ref<WaferData | null>(null)
  const loading = ref(false)

  const fetchWaferData = async () => {
    loading.value = true
    try {
      const response = await fetch('/api/wafer/data')
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      waferData.value = await response.json()
    } catch (error) {
      console.error('Failed to fetch wafer data:', error)
      waferData.value = null
    } finally {
      loading.value = false
    }
  }

  onMounted(fetchWaferData)

  return { waferData, loading, fetchWaferData }
}
