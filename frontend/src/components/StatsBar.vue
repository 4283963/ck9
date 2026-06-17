<script setup lang="ts">
import { computed } from 'vue'
import { AlertTriangle, Layers, Activity } from 'lucide-vue-next'
import type { WaferData, DefectType } from '@/types/wafer'

const props = defineProps<{ waferData: WaferData }>()

const defectTypeColors: Record<DefectType, string> = {
  scratch: 'bg-cyan-500/80',
  particle: 'bg-amber-500/80',
  crack: 'bg-red-500/80',
  void: 'bg-purple-500/80',
  contamination: 'bg-green-500/80',
}

const totalDefects = computed(() => props.waferData.defects.length)

const defectsByType = computed(() => {
  const counts: Partial<Record<DefectType, number>> = {}
  for (const d of props.waferData.defects) {
    counts[d.defect_type] = (counts[d.defect_type] || 0) + 1
  }
  return counts
})

const defectsByLayer = computed(() => {
  const counts: Record<number, number> = {}
  for (const d of props.waferData.defects) {
    counts[d.layer_id] = (counts[d.layer_id] || 0) + 1
  }
  return counts
})
</script>

<template>
  <div class="flex items-center gap-6 px-5 py-3 bg-gray-900/80 border-b border-cyan-500/20 backdrop-blur-sm text-sm">
    <div class="flex items-center gap-2">
      <AlertTriangle :size="16" class="text-cyan-400" />
      <span class="text-gray-400">总缺陷</span>
      <span class="text-[#00e5ff] font-mono font-bold text-base">{{ totalDefects }}</span>
    </div>

    <div class="h-4 w-px bg-gray-700" />

    <div class="flex items-center gap-2">
      <Activity :size="16" class="text-cyan-400" />
      <span class="text-gray-400">按类型</span>
      <div class="flex items-center gap-1.5">
        <span
          v-for="(count, type) in defectsByType"
          :key="type"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium text-white"
          :class="defectTypeColors[type as DefectType]"
        >
          {{ type }} <span class="font-mono">{{ count }}</span>
        </span>
      </div>
    </div>

    <div class="h-4 w-px bg-gray-700" />

    <div class="flex items-center gap-2">
      <Layers :size="16" class="text-cyan-400" />
      <span class="text-gray-400">按层</span>
      <div class="flex items-center gap-1.5">
        <span
          v-for="layer in waferData.layers"
          :key="layer.layer_id"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-gray-700/80 text-gray-200"
        >
          {{ layer.layer_name }} <span class="font-mono text-cyan-300">{{ defectsByLayer[layer.layer_id] || 0 }}</span>
        </span>
      </div>
    </div>
  </div>
</template>
