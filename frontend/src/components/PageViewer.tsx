import { useCallback, useEffect, useRef, useState } from 'react'
import { MatchResult } from '../types'
import { BoundingBoxOverlay } from './BoundingBoxOverlay'

interface Props {
  imageUrl: string
  matches: MatchResult[]
  minConfidence: number
}

export function PageViewer({ imageUrl, matches, minConfidence }: Props) {
  const imgRef = useRef<HTMLImageElement>(null)
  const [dimensions, setDimensions] = useState({ natural: { w: 0, h: 0 }, display: { w: 0, h: 0 } })

  const updateDimensions = useCallback(() => {
    const img = imgRef.current
    if (!img || img.naturalWidth === 0) return
    setDimensions({
      natural: { w: img.naturalWidth, h: img.naturalHeight },
      display: { w: img.clientWidth, h: img.clientHeight },
    })
  }, [])

  useEffect(() => {
    const img = imgRef.current
    if (!img) return

    if (img.complete && img.naturalWidth > 0) updateDimensions()

    img.addEventListener('load', updateDimensions)
    return () => img.removeEventListener('load', updateDimensions)
  }, [imageUrl, updateDimensions])

  useEffect(() => {
    const img = imgRef.current
    if (!img) return
    const observer = new ResizeObserver(updateDimensions)
    observer.observe(img)
    return () => observer.disconnect()
  }, [updateDimensions])

  return (
    <div className="relative inline-block w-full">
      <img
        ref={imgRef}
        src={imageUrl}
        alt="Document page"
        className="w-full h-auto rounded border border-gray-200"
      />
      {dimensions.natural.w > 0 && dimensions.display.w > 0 && (
        <BoundingBoxOverlay
          matches={matches}
          imageWidth={dimensions.natural.w}
          imageHeight={dimensions.natural.h}
          displayWidth={dimensions.display.w}
          displayHeight={dimensions.display.h}
          minConfidence={minConfidence}
        />
      )}
    </div>
  )
}
