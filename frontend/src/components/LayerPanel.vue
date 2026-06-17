<script setup lang="ts">
import { computed } from 'vue'
import { Eye, EyeOff, Scissors, Layers } from 'lucide-vue-next'
import type { WaferLayer, Defect } from '../types/wafer'

const props = defineProps<{
  layers: WaferLayer[]
  defects: Defect[]
  hiddenLayers: number[]
  highlightLayer: number | null
  exploded: boolean
}>()

const emit = defineEmits<{
  'toggle-layer': [layerId: number]
  'highlight-layer': [layerId: number | null]
  'reset-layers': []
  'toggle-exploded': []
}>()

const layerDefectCounts = computed(() => {
  const counts: Record<number, number> = {}
  for (const defect of props.defects) {
    counts[defect.layer_id] = (counts[defect.layer_id] ?? 0) + 1
  }
  return counts
})
</script>

<template>
  <div class="h-full w-[260px] bg-gray-900/90 border-r border-cyan-500/20 flex flex-col">
    <div class="px-4 py-5 border-b border-cyan-500/20">
      <h2 class="text-cyan-400 text-lg font-bold tracking-wide">层级控制</h2>
    </div>

    <ul class="flex-1 overflow-y-auto py-2">
      <li
        v-for="layer in layers"
        :key="layer.layer_id"
        class="flex items-center gap-2 px-4 py-3 cursor-pointer transition-all duration-200"
        :class="[
          highlightLayer === layer.layer_id
            ? 'border-l-2 border-cyan-400 bg-cyan-500/10 text-cyan-300'
            : 'border-l-2 border-transparent text-gray-300 hover:bg-gray-800/50',
          hiddenLayers.includes(layer.layer_id) ? 'opacity-40' : ''
        ]"
        @click="emit('highlight-layer', highlightLayer === layer.layer_id ? null : layer.layer_id)"
      >
        <span
          class="w-3 h-3 rounded-full shrink-0"
          :style="{ backgroundColor: layer.color }"
        />
        <span
          class="flex-1 text-sm truncate"
          :class="hiddenLayers.includes(layer.layer_id) ? 'line-through' : ''"
        >
          {{ layer.layer_name }}
        </span>
        <span class="text-xs bg-gray-700/80 text-gray-400 px-1.5 py-0.5 rounded-full">
          {{ layerDefectCounts[layer.layer_id] ?? 0 }}
        </span>
        <button
          class="p-1 hover:text-cyan-400 transition-colors"
          @click.stop="emit('toggle-layer', layer.layer_id)"
        >
          <EyeOff v-if="hiddenLayers.includes(layer.layer_id)" class="w-4 h-4" />
          <Eye v-else class="w-4 h-4" />
        </button>
      </li>
    </ul>

    <div class="px-4 py-3 border-t border-cyan-500/20 space-y-2">
      <button
        class="w-full py-2.5 text-sm font-medium rounded transition-all duration-200 flex items-center justify-center gap-2"
        :class="[
          exploded
            ? 'bg-[#ff3d3d]/80 text-white border border-[#ff3d3d] shadow-lg shadow-[#ff3d3d]/30 hover:bg-[#ff3d3d]'
            : 'text-[#00e5ff] border border-[#00e5ff]/40 hover:bg-[#00e5ff]/10 shadow-lg shadow-[#00e5ff]/10'
        ]"
        @click="emit('toggle-exploded')"
      >
        <Layers v-if="exploded" class="w-4 h-4" />
        <Scissors v-else class="w-4 h-4" />
        <span>{{ exploded ? '合拢还原' : '一键炸开解体' }}</span>
      </button>

      <button
        class="w-full py-2 text-sm text-cyan-400 border border-cyan-500/30 rounded hover:bg-cyan-500/10 transition-colors"
        @click="emit('reset-layers')"
      >
        全部显示
      </button>
    </div>
  </div>
</template>
