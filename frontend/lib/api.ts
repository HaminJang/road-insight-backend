const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

export interface AnalysisResponse {
  success: boolean
  hash: string
  timestamp: string
  latitude: number | null
  longitude: number | null
  detection: {
    detected: boolean
    confidence: number
    area_ratio: number
    damage_score: number
    bbox: number[] | null
  }
  message: string
}

export async function analyzeRoad(
  file: File,
  latitude: number | null,
  longitude: number | null
): Promise<AnalysisResponse> {
  const formData = new FormData()
  formData.append('file', file)
  if (latitude !== null) formData.append('latitude', latitude.toString())
  if (longitude !== null) formData.append('longitude', longitude.toString())

  const response = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error('분석 요청 실패')
  }

  return response.json()
}

export async function downloadPDF(
  file: File,
  latitude: number | null,
  longitude: number | null
) {
  const formData = new FormData()
  formData.append('file', file)
  if (latitude !== null) formData.append('latitude', latitude.toString())
  if (longitude !== null) formData.append('longitude', longitude.toString())

  const response = await fetch(`${API_URL}/generate-pdf`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error('PDF 생성 실패')
  }

  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `road_insight_${new Date().toISOString().slice(0, 10)}.pdf`
  a.click()
  window.URL.revokeObjectURL(url)
}
