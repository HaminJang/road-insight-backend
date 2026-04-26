'use client'

import { useRef, useState, useCallback } from 'react'

interface CameraCaptureProps {
  onCapture: (file: File) => void
}

export default function CameraCapture({ onCapture }: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [streaming, setStreaming] = useState(false)
  const [captured, setCaptured] = useState(false)

  const startCamera = useCallback(async () => {
    console.log('버튼 클릭됨')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true
      })
      console.log('스트림 성공', stream)
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
        setStreaming(true)
        console.log('streaming true 설정됨')
      }
    } catch (err) {
      console.log('카메라 오류', err)
      alert('카메라 오류: ' + err)
    }
  }, [])

  const capture = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return
    const canvas = canvasRef.current
    const video = videoRef.current
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    ctx.drawImage(video, 0, 0)
    canvas.toBlob((blob) => {
      if (!blob) return
      const file = new File([blob], 'pothole.jpg', { type: 'image/jpeg' })
      onCapture(file)
      setCaptured(true)
      const stream = video.srcObject as MediaStream
      stream?.getTracks().forEach(track => track.stop())
      setStreaming(false)
    }, 'image/jpeg', 0.9)
  }, [onCapture])

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      {!streaming && !captured && (
        <button
          onClick={startCamera}
          style={{
            width: '100%',
            padding: '16px',
            background: '#1D9E75',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            cursor: 'pointer'
          }}
        >
          카메라 시작
        </button>
      )}

      <div style={{ position: 'relative', display: streaming ? 'block' : 'none' }}>
        <video
          ref={videoRef}
          style={{ width: '100%', borderRadius: '8px' }}
          playsInline
          autoPlay
          muted
        />
        <div style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <div style={{
            width: '60%',
            height: '40%',
            border: '2px solid #00ff00',
            borderRadius: '8px'
          }} />
        </div>
        <p style={{
          position: 'absolute',
          bottom: '70px',
          width: '100%',
          textAlign: 'center',
          color: 'white',
          fontSize: '14px',
          margin: 0
        }}>
          파손 부위를 녹색 박스 안에 맞춰주세요
        </p>
        <button
          onClick={capture}
          style={{
            position: 'absolute',
            bottom: '16px',
            left: '50%',
            transform: 'translateX(-50%)',
            padding: '12px 32px',
            background: '#1D9E75',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            cursor: 'pointer'
          }}
        >
          촬영
        </button>
      </div>

      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {captured && (
        <p style={{ textAlign: 'center', color: '#1D9E75', fontWeight: 500 }}>
          촬영 완료! 분석 중...
        </p>
      )}
    </div>
  )
}
