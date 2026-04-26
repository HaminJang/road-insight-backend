import { useState, useEffect } from 'react'

interface Location {
  latitude: number | null
  longitude: number | null
  error: string | null
}

export const useGeolocation = () => {
  const [location, setLocation] = useState<Location>({
    latitude: null,
    longitude: null,
    error: null
  })

  useEffect(() => {
    if (!navigator.geolocation) {
      setLocation(prev => ({
        ...prev,
        error: 'GPS를 지원하지 않는 기기입니다'
      }))
      return
    }

    const watchId = navigator.geolocation.watchPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          error: null
        })
      },
      (error) => {
        setLocation(prev => ({
          ...prev,
          error: 'GPS 정보를 가져올 수 없습니다'
        }))
      },
      {
        enableHighAccuracy: true,
        maximumAge: 0
      }
    )

    return () => {
      navigator.geolocation.clearWatch(watchId)
    }
  }, [])

  return location
}
