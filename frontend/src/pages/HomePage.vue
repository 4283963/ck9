<script setup lang="ts">
import { ref } from 'vue'
import WaferScene from '@/components/WaferScene.vue'
import LayerPanel from '@/components/LayerPanel.vue'
import DefectInfo from '@/components/DefectInfo.vue'
import StatsBar from '@/components/StatsBar.vue'
import { useWaferData } from '@/composables/useWaferData'
import type { Defect } from '@/types/wafer'

const { waferData, loading } = useWaferData()

const hiddenLayers = ref<number[]>([])
const highlightLayer = ref<number | null>(null)
const selectedDefect = ref<Defect | null>(null)
const exploded = ref(false)

function onToggleLayer(layerId: number) {
  const idx = hiddenLayers.value.indexOf(layerId)
  if (idx >= 0) {
    hiddenLayers.value.splice(idx, 1)
  } else {
    hiddenLayers.value.push(layerId)
  }
}

function onHighlightLayer(layerId: number | null) {
  highlightLayer.value = layerId
}

function onDefectClick(defect: Defect) {
  selectedDefect.value = defect
  highlightLayer.value = defect.layer_id
}

function onDefectClose() {
  selectedDefect.value = null
}

function onResetLayers() {
  hiddenLayers.value = []
  highlightLayer.value = null
}

function onToggleExploded() {
  exploded.value = !exploded.value
}
</script>

<template>
  <div class="w-screen h-screen bg-[#0a1628] overflow-hidden relative">
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center z-[100]">
      <div class="text-cyan-400 text-lg font-mono animate-pulse">加载晶圆数据...</div>
    </div>

    <template v-if="waferData">
      <StatsBar :waferData="waferData" />

      <div class="flex h-[calc(100vh-48px)]">
        <LayerPanel
          :layers="waferData.layers"
          :defects="waferData.defects"
          :hiddenLayers="hiddenLayers"
          :highlightLayer="highlightLayer"
          :exploded="exploded"
          @toggle-layer="onToggleLayer"
          @highlight-layer="onHighlightLayer"
          @reset-layers="onResetLayers"
          @toggle-exploded="onToggleExploded"
        />

        <div class="flex-1 h-full">
          <WaferScene
            :waferData="waferData"
            :hiddenLayers="hiddenLayers"
            :highlightLayer="highlightLayer"
            :exploded="exploded"
            @defect-click="onDefectClick"
          />
        </div>
      </div>

      <DefectInfo
        :defect="selectedDefect"
        @close="onDefectClose"
      />
    </template>
  </div>
</template>
