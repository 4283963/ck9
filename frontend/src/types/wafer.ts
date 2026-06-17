export interface WaferLayer {
  layer_id: number
  layer_name: string
  thickness: number
  material: string
  color: string
}

export type DefectType = 'scratch' | 'particle' | 'crack' | 'void' | 'contamination'
export type Severity = 'low' | 'medium' | 'high'

export interface Defect {
  defect_id: number
  layer_id: number
  x: number
  y: number
  z: number
  defect_type: DefectType
  severity: Severity
  description: string
}

export interface WaferData {
  wafer_id: string
  wafer_diameter: number
  total_layers: number
  layers: WaferLayer[]
  defects: Defect[]
}
