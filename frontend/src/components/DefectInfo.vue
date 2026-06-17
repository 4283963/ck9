<script setup lang="ts">
import { computed } from 'vue'
import { X } from 'lucide-vue-next'
import type { Defect, DefectType, Severity } from '../types/wafer'

const props = defineProps<{
  defect: Defect | null
}>()

const emit = defineEmits<{
  close: []
}>()

const defectTypeColors: Record<DefectType, string> = {
  scratch: 'bg-cyan-500/20 text-cyan-400',
  particle: 'bg-amber-500/20 text-amber-400',
  crack: 'bg-red-500/20 text-red-400',
  void: 'bg-purple-500/20 text-purple-400',
  contamination: 'bg-green-500/20 text-green-400'
}

const severityColors: Record<Severity, string> = {
  low: 'text-green-400',
  medium: 'text-amber-400',
  high: 'text-red-400'
}

const visible = computed(() => props.defect !== null)
</script>

<template>
  <Transition name="defect-info">
    <div
      v-if="visible && defect"
      class="fixed bottom-6 right-6 w-[320px] bg-gray-900/90 border border-cyan-500/30 rounded-lg shadow-lg shadow-cyan-500/10 z-50"
    >
      <div class="flex items-center justify-between px-4 py-3 border-b border-cyan-500/20">
        <h3 class="text-cyan-400 font-bold tracking-wide">缺陷详情</h3>
        <button
          class="p-1 text-gray-400 hover:text-cyan-400 transition-colors"
          @click="emit('close')"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <div class="px-4 py-3 space-y-2 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-500">缺陷编号</span>
          <span class="text-gray-200">{{ defect.defect_id }}</span>
        </div>

        <div class="flex justify-between items-center">
          <span class="text-gray-500">缺陷类型</span>
          <span
            class="px-2 py-0.5 rounded text-xs font-medium"
            :class="defectTypeColors[defect.defect_type]"
          >
            {{ defect.defect_type }}
          </span>
        </div>

        <div class="flex justify-between items-center">
          <span class="text-gray-500">严重程度</span>
          <span :class="severityColors[defect.severity]" class="font-medium">
            {{ defect.severity }}
          </span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">所在层级</span>
          <span class="text-gray-200">{{ defect.layer_id }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">坐标</span>
          <span class="text-gray-200 font-mono text-xs">
            ({{ defect.x.toFixed(2) }}, {{ defect.y.toFixed(2) }}, {{ defect.z.toFixed(2) }})
          </span>
        </div>

        <div class="pt-1">
          <span class="text-gray-500">描述</span>
          <p class="text-gray-300 mt-1 text-xs leading-relaxed">{{ defect.description }}</p>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.defect-info-enter-active {
  transition: all 0.3s ease-out;
}
.defect-info-leave-active {
  transition: all 0.2s ease-in;
}
.defect-info-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.defect-info-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
