import { useEffect, useRef, useState } from 'react'
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

  useEffect(() => {
    const img = imgRef.current
    if (!img) return
    const update = () => {
      setDimensions({
        natural: { w: img.naturalWidth, h: img.naturalHeight },
        display: { w: img.clientWidth, h: img.clientHeight },
      })
    }
    if (img.complete) update()
    img.addEventListener('load', update)
    return () => img.removeEventListener('load', update)
  }, [imageUrl])

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
