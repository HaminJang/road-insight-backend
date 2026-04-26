'use client'

import { useState } from 'react'
import CameraCapture from '@/components/CameraCapture'
import { useGeolocation } from '@/hooks/useGeolocation'
import { analyzeRoad, downloadPDF } from '@/lib/api'

export default function Home() {
  const location = useGeolocation()
  const [result, setResult] = useState<any>(null)
  const [capturedFile, setCapturedFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [pdfLoading, setPdfLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCapture = async (file: File) => {
    setCapturedFile(file)
    setLoading(true)
    setError(null)
    try {
      const data = await analyzeRoad(file, location.latitude, location.longitude)
      setResult(data)
    } catch (err) {
      setError('분석 중 오류가 발생했습니다')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPDF = async () => {
    if (!capturedFile) return
    setPdfLoading(true)
    try {
      await downloadPDF(capturedFile, location.latitude, location.longitude)
    } catch (err) {
      setError('PDF 생성 중 오류가 발생했습니다')
    } finally {
      setPdfLoading(false)
    }
  }

  return (
    <main style={{
      maxWidth: '480px',
      margin: '0 auto',
      padding: '24px 16px',
      fontFamily: 'sans-serif'
    }}>
      <h1 style={{
        fontSize: '24px',
        fontWeight: 500,
        color: '#1D9E75',
        marginBottom: '8px'
      }}>
        Road-Insight
      </h1>
      <p style={{
        fontSize: '14px',
        color: '#888',
        marginBottom: '24px'
      }}>
        AI 도로 파손 증거 생성 서비스
      </p>

      <CameraCapture onCapture={handleCapture} />

      {loading && (
        <div style={{ textAlign: 'center', padding: '24px', color: '#888' }}>
          AI 분석 중...
        </div>
      )}

      {error && (
        <div style={{
          padding: '12px',
          background: '#FCEBEB',
          borderRadius: '8px',
          color: '#A32D2D',
          marginTop: '16px'
        }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{
          marginTop: '24px',
          padding: '16px',
          border: '0.5px solid #e0e0e0',
          borderRadius: '12px'
        }}>
          <h2 style={{ fontSize: '16px', fontWeight: 500, marginBottom: '12px' }}>
            분석 결과
          </h2>

          <div style={{
            padding: '12px',
            background: result.detection.detected ? '#FCEBEB' : '#E1F5EE',
            borderRadius: '8px',
            marginBottom: '12px',
            textAlign: 'center',
            fontWeight: 500,
            color: result.detection.detected ? '#A32D2D' : '#085041'
          }}>
            {result.message}
          </div>

          {result.detection.detected && (
            <div style={{ fontSize: '14px', color: '#444' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                padding: '8px 0',
                borderBottom: '0.5px solid #f0f0f0'
              }}>
                <span style={{ color: '#888' }}>AI 신뢰도</span>
                <span style={{ fontWeight: 500 }}>
                  {(result.detection.confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                padding: '8px 0',
                borderBottom: '0.5px solid #f0f0f0'
              }}>
                <span style={{ color: '#888' }}>위험도 점수</span>
                <span style={{ fontWeight: 500, color: '#D85A30' }}>
                  {result.detection.damage_score.toFixed(1)} / 100
                </span>
              </div>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                padding: '8px 0',
                borderBottom: '0.5px solid #f0f0f0'
              }}>
                <span style={{ color: '#888' }}>GPS</span>
                <span style={{ fontWeight: 500, fontSize: '12px' }}>
                  {result.latitude?.toFixed(4)}, {result.longitude?.toFixed(4)}
                </span>
              </div>
              <div style={{
                padding: '8px 0',
                fontSize: '11px',
                color: '#aaa',
                wordBreak: 'break-all'
              }}>
                <span>SHA-256: </span>
                {result.hash.substring(0, 20)}...
              </div>
            </div>
          )}

          <button
            onClick={handleDownloadPDF}
            disabled={pdfLoading}
            style={{
              width: '100%',
              padding: '12px',
              marginTop: '16px',
              background: pdfLoading ? '#888' : '#1D9E75',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '15px',
              fontWeight: 500,
              cursor: pdfLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {pdfLoading ? 'PDF 생성 중...' : '증거 PDF 다운로드'}
          </button>
        </div>
      )}
    </main>
  )
}
