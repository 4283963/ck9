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
let defectGroup: THREE.Group | null = null
let selectedSphere: THREE.Mesh | null = null
let mouseDownPos = { x: 0, y: 0 }
const raycaster = new THREE.Raycaster()
const pointer = new THREE.Vector2()
const clock = new THREE.Clock()

function getLayerVisualHeight(layerId: number): number {
  return layerId === 1 ? 1.5 : 0.4
}

function getLayerCenterY(layerId: number, layers: WaferLayer[]): number {
  const sorted = [...layers].sort((a, b) => a.layer_id - b.layer_id)
  let y = 0
  for (const layer of sorted) {
    const vh = getLayerVisualHeight(layer.layer_id)
    if (layer.layer_id === layerId) {
      return y
    }
    y += vh + 1.2
  }
  return y
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
  if (defectGroup) {
    scene.remove(defectGroup)
    defectGroup.traverse((child) => {
      if ((child as THREE.Mesh).geometry) {
        ;(child as THREE.Mesh).geometry.dispose()
      }
      if ((child as THREE.Mesh).material) {
        ;((child as THREE.Mesh).material as THREE.Material).dispose()
      }
    })
  }

  layerMeshes = []
  ringMeshes = []
  defectGroup = new THREE.Group()
  selectedSphere = null

  const radius = props.waferData.wafer_diameter / 10 / 2
  const sorted = [...props.waferData.layers].sort((a, b) => a.layer_id - b.layer_id)

  let y = 0
  const layerYMap = new Map<number, number>()

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
    layerYMap.set(layer.layer_id, y + visualHeight / 2)

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

  for (const defect of props.waferData.defects) {
    const sphereGeo = new THREE.SphereGeometry(0.3, 16, 16)
    const sphereMat = new THREE.MeshStandardMaterial({
      color: 0xff3d3d,
      emissive: 0xff0000,
      emissiveIntensity: 0.8,
    })
    const sphere = new THREE.Mesh(sphereGeo, sphereMat)
    const defectX = defect.x / 10
    const defectY = -(defect.y / 10)
    const layerY = layerYMap.get(defect.layer_id) ?? 0
    sphere.position.set(defectX, layerY, defectY)
    sphere.userData.defectId = defect.defect_id
    sphere.userData.defect = defect
    defectGroup.add(sphere)
  }

  scene.add(defectGroup)
  updateLayerVisibility()
  updateHighlight()
}

function updateLayerVisibility() {
  for (const mesh of layerMeshes) {
    mesh.visible = !props.hiddenLayers.includes(mesh.userData.layerId)
  }
  for (const ring of ringMeshes) {
    ring.visible = !props.hiddenLayers.includes(ring.userData.layerId)
  }
  if (defectGroup) {
    defectGroup.traverse((child) => {
      if ((child as THREE.Mesh).userData.defect) {
        const defect = child.userData.defect as Defect
        ;(child as THREE.Mesh).visible = !props.hiddenLayers.includes(defect.layer_id)
      }
    })
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

  const defectSpheres: THREE.Mesh[] = []
  if (defectGroup) {
    defectGroup.traverse((child) => {
      if ((child as THREE.Mesh).isMesh && (child as THREE.Mesh).userData.defectId !== undefined) {
        defectSpheres.push(child as THREE.Mesh)
      }
    })
  }

  const intersects = raycaster.intersectObjects(defectSpheres, false)
  if (intersects.length > 0) {
    const hit = intersects[0].object as THREE.Mesh
    const defect = hit.userData.defect as Defect

    if (selectedSphere && selectedSphere !== hit) {
      const prevMat = selectedSphere.material as THREE.MeshStandardMaterial
      prevMat.emissiveIntensity = 0.8
    }

    selectedSphere = hit
    const mat = hit.material as THREE.MeshStandardMaterial
    mat.emissiveIntensity = 2.0

    emit('defect-click', defect)
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

  if (defectGroup) {
    defectGroup.traverse((child) => {
      if ((child as THREE.Mesh).isMesh && (child as THREE.Mesh).userData.defectId !== undefined) {
        const baseY = (child as THREE.Mesh).userData.baseY ?? (child as THREE.Mesh).position.y
        if (!(child as THREE.Mesh).userData.baseY) {
          ;(child as THREE.Mesh).userData.baseY = (child as THREE.Mesh).position.y
        }
        ;(child as THREE.Mesh).position.y = baseY + Math.sin(elapsed * 2 + (child as THREE.Mesh).userData.defectId) * 0.1
      }
    })
  }

  if (selectedSphere) {
    const mat = selectedSphere.material as THREE.MeshStandardMaterial
    mat.emissiveIntensity = 2.0 + Math.sin(elapsed * 5) * 0.5
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
