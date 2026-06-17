<template>
  <div ref="containerRef" style="width: 100%; height: 100%;"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import type { WaferData, WaferLayer, Defect } from '@/types/wafer'

const props = defineProps<{
  waferData: WaferData
  hiddenLayers: number[]
  highlightLayer: number | null
}>()

const emit = defineEmits<{
  'defect-click': [defect: Defect]
}>()

const containerRef = ref<HTMLDivElement | null>(null)

let renderer: THREE.WebGLRenderer | null = null
let camera: THREE.PerspectiveCamera | null = null
let scene: THREE.Scene | null = null
let controls: OrbitControls | null = null
let animationFrameId = 0
let layerMeshes: THREE.Mesh[] = []
let ringMeshes: THREE.Mesh[] = []
let defectInstances: THREE.InstancedMesh | null = null
let defectList: Defect[] = []
let basePositions: THREE.Vector3[] = []
let selectionIndicator: THREE.Mesh | null = null
let selectedInstanceId = -1
let mouseDownPos = { x: 0, y: 0 }
const raycaster = new THREE.Raycaster()
const pointer = new THREE.Vector2()
const clock = new THREE.Clock()
const dummy = new THREE.Object3D()
const defaultColor = new THREE.Color(0xff3d3d)
const selectedColor = new THREE.Color(0xff9999)

function getLayerVisualHeight(layerId: number): number {
  return layerId === 1 ? 1.5 : 0.4
}

function buildLayerYMap(layers: WaferLayer[]): Map<number, number> {
  const map = new Map<number, number>()
  const sorted = [...layers].sort((a, b) => a.layer_id - b.layer_id)
  let y = 0
  for (const layer of sorted) {
    const vh = getLayerVisualHeight(layer.layer_id)
    map.set(layer.layer_id, y + vh / 2)
    y += vh + 1.2
  }
  return map
}

function buildWafer() {
  if (!scene) return

  layerMeshes.forEach((m) => {
    scene!.remove(m)
    m.geometry.dispose()
    ;(m.material as THREE.Material).dispose()
  })
  ringMeshes.forEach((m) => {
    scene!.remove(m)
    m.geometry.dispose()
    ;(m.material as THREE.Material).dispose()
  })
  if (defectInstances) {
    scene.remove(defectInstances)
    defectInstances.geometry.dispose()
    ;(defectInstances.material as THREE.Material).dispose()
  }
  if (selectionIndicator) {
    scene.remove(selectionIndicator)
    selectionIndicator.geometry.dispose()
    ;(selectionIndicator.material as THREE.Material).dispose()
  }

  layerMeshes = []
  ringMeshes = []
  defectInstances = null
  defectList = []
  basePositions = []
  selectedInstanceId = -1
  selectionIndicator = null

  const radius = props.waferData.wafer_diameter / 10 / 2
  const sorted = [...props.waferData.layers].sort((a, b) => a.layer_id - b.layer_id)
  const layerYMap = buildLayerYMap(props.waferData.layers)

  let y = 0
  for (const layer of sorted) {
    const visualHeight = getLayerVisualHeight(layer.layer_id)
    const geometry = new THREE.CylinderGeometry(radius, radius, visualHeight, 64)
    const material = new THREE.MeshPhysicalMaterial({
      color: new THREE.Color(layer.color),
      transparent: true,
      opacity: 0.35,
      side: THREE.DoubleSide,
      metalness: 0.3,
      roughness: 0.4,
    })
    const mesh = new THREE.Mesh(geometry, material)
    mesh.position.y = y + visualHeight / 2
    mesh.userData.layerId = layer.layer_id
    scene.add(mesh)
    layerMeshes.push(mesh)

    const ringGeometry = new THREE.TorusGeometry(radius, 0.05, 8, 64)
    const ringMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color(layer.color),
      emissive: new THREE.Color(layer.color),
      emissiveIntensity: 0.3,
    })
    const ring = new THREE.Mesh(ringGeometry, ringMaterial)
    ring.rotation.x = Math.PI / 2
    ring.position.y = y + visualHeight
    ring.userData.layerId = layer.layer_id
    scene.add(ring)
    ringMeshes.push(ring)

    y += visualHeight + 1.2
  }

  const defects = props.waferData.defects
  const count = defects.length

  if (count > 0) {
    const sphereGeo = new THREE.SphereGeometry(0.3, 8, 6)
    const sphereMat = new THREE.MeshStandardMaterial({
      color: 0xff3d3d,
      emissive: 0xff0000,
      emissiveIntensity: 0.8,
    })
    defectInstances = new THREE.InstancedMesh(sphereGeo, sphereMat, count)

    for (let i = 0; i < count; i++) {
      const defect = defects[i]
      defectList.push(defect)

      const px = defect.x / 10
      const pz = -(defect.y / 10)
      const py = layerYMap.get(defect.layer_id) ?? 0

      const pos = new THREE.Vector3(px, py, pz)
      basePositions.push(pos)

      dummy.position.copy(pos)
      dummy.scale.set(1, 1, 1)
      dummy.updateMatrix()
      defectInstances.setMatrixAt(i, dummy.matrix)
      defectInstances.setColorAt(i, defaultColor)
    }

    defectInstances.instanceMatrix.needsUpdate = true
    if (defectInstances.instanceColor) {
      defectInstances.instanceColor.needsUpdate = true
    }
    scene.add(defectInstances)
  }

  const indicatorGeo = new THREE.IcosahedronGeometry(0.55, 1)
  const indicatorMat = new THREE.MeshBasicMaterial({
    color: 0x00e5ff,
    wireframe: true,
    transparent: true,
    opacity: 0.7,
  })
  selectionIndicator = new THREE.Mesh(indicatorGeo, indicatorMat)
  selectionIndicator.visible = false
  scene.add(selectionIndicator)

  updateLayerVisibility()
  updateHighlight()
}

function updateLayerVisibility() {
  const hiddenSet = new Set(props.hiddenLayers)

  for (const mesh of layerMeshes) {
    mesh.visible = !hiddenSet.has(mesh.userData.layerId)
  }
  for (const ring of ringMeshes) {
    ring.visible = !hiddenSet.has(ring.userData.layerId)
  }

  if (defectInstances) {
    for (let i = 0; i < defectList.length; i++) {
      const isHidden = hiddenSet.has(defectList[i].layer_id)
      dummy.position.copy(basePositions[i])
      dummy.scale.setScalar(isHidden ? 0 : 1)
      dummy.updateMatrix()
      defectInstances.setMatrixAt(i, dummy.matrix)
    }
    defectInstances.instanceMatrix.needsUpdate = true
  }

  if (selectedInstanceId >= 0 && selectionIndicator) {
    const defect = defectList[selectedInstanceId]
    if (defect && hiddenSet.has(defect.layer_id)) {
      selectionIndicator.visible = false
    }
  }
}

function updateHighlight() {
  for (const mesh of layerMeshes) {
    const mat = mesh.material as THREE.MeshPhysicalMaterial
    if (props.highlightLayer === null) {
      mat.opacity = 0.35
    } else if (mesh.userData.layerId === props.highlightLayer) {
      mat.opacity = 0.7
    } else {
      mat.opacity = 0.15
    }
  }
}

function onPointerDown(event: PointerEvent) {
  mouseDownPos.x = event.clientX
  mouseDownPos.y = event.clientY
}

function onPointerUp(event: PointerEvent) {
  const dx = event.clientX - mouseDownPos.x
  const dy = event.clientY - mouseDownPos.y
  if (Math.sqrt(dx * dx + dy * dy) > 5) return

  if (!containerRef.value || !camera || !scene) return

  const rect = containerRef.value.getBoundingClientRect()
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  raycaster.setFromCamera(pointer, camera)

  if (selectedInstanceId >= 0 && defectInstances?.instanceColor) {
    defectInstances.setColorAt(selectedInstanceId, defaultColor)
    defectInstances.instanceColor.needsUpdate = true
  }

  if (defectInstances) {
    const intersects = raycaster.intersectObject(defectInstances, false)
    if (intersects.length > 0 && intersects[0].instanceId !== undefined) {
      const instanceId = intersects[0].instanceId
      const defect = defectList[instanceId]

      const hiddenSet = new Set(props.hiddenLayers)
      if (hiddenSet.has(defect.layer_id)) {
        selectedInstanceId = -1
        if (selectionIndicator) selectionIndicator.visible = false
        return
      }

      selectedInstanceId = instanceId

      if (defectInstances.instanceColor) {
        defectInstances.setColorAt(instanceId, selectedColor)
        defectInstances.instanceColor.needsUpdate = true
      }

      if (selectionIndicator) {
        selectionIndicator.position.copy(basePositions[instanceId])
        selectionIndicator.visible = true
      }

      emit('defect-click', defect)
    } else {
      selectedInstanceId = -1
      if (selectionIndicator) selectionIndicator.visible = false
    }
  }
}

function onResize() {
  if (!containerRef.value || !renderer || !camera) return
  const w = containerRef.value.clientWidth
  const h = containerRef.value.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
}

function animate() {
  animationFrameId = requestAnimationFrame(animate)
  const elapsed = clock.getElapsedTime()

  if (selectionIndicator && selectionIndicator.visible) {
    const pulse = 1.0 + Math.sin(elapsed * 4) * 0.15
    selectionIndicator.scale.set(pulse, pulse, pulse)
    const mat = selectionIndicator.material as THREE.MeshBasicMaterial
    mat.opacity = 0.4 + Math.sin(elapsed * 4) * 0.3
    selectionIndicator.rotation.y = elapsed * 0.8
  }

  controls?.update()
  renderer?.render(scene!, camera!)
}

onMounted(() => {
  if (!containerRef.value) return

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.setSize(containerRef.value.clientWidth, containerRef.value.clientHeight)
  containerRef.value.appendChild(renderer.domElement)

  camera = new THREE.PerspectiveCamera(45, containerRef.value.clientWidth / containerRef.value.clientHeight, 0.1, 1000)
  camera.position.set(0, 25, 30)
  camera.lookAt(0, 0, 0)

  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0a1628)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05

  const ambientLight = new THREE.AmbientLight(0x334455, 0.6)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0)
  directionalLight.position.set(10, 20, 15)
  scene.add(directionalLight)

  const gridHelper = new THREE.GridHelper(60, 60, 0x1a2a4a, 0x0f1f3a)
  scene.add(gridHelper)

  const axesHelper = new THREE.AxesHelper(3)
  scene.add(axesHelper)

  buildWafer()

  containerRef.value.addEventListener('pointerdown', onPointerDown)
  containerRef.value.addEventListener('pointerup', onPointerUp)
  window.addEventListener('resize', onResize)

  animate()
})

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  if (containerRef.value) {
    containerRef.value.removeEventListener('pointerdown', onPointerDown)
    containerRef.value.removeEventListener('pointerup', onPointerUp)
  }
  window.removeEventListener('resize', onResize)
  controls?.dispose()
  renderer?.dispose()
  if (containerRef.value && renderer?.domElement) {
    containerRef.value.removeChild(renderer.domElement)
  }
  renderer = null
  camera = null
  scene = null
  controls = null
})

watch(() => props.waferData, buildWafer, { deep: true })

watch(() => props.hiddenLayers, updateLayerVisibility, { deep: true })

watch(() => props.highlightLayer, updateHighlight)
</script>
