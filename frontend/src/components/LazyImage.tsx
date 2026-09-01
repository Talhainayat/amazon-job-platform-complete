import { useState, useEffect, useRef } from 'react'

interface LazyImageProps {
  src?: string
  alt: string
  className?: string
  width?: number
  height?: number
  fallback?: string
}

/**
 * LazyImage component with Intersection Observer API support
 * Loads images only when they enter the viewport for optimal performance
 */
export default function LazyImage({ src, alt, className = '', width, height, fallback }: LazyImageProps) {
  const [imageSrc, setImageSrc] = useState<string | undefined>(undefined)
  const [isLoaded, setIsLoaded] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    if (!src) {
      setImageSrc(fallback)
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setImageSrc(src)
            if (imgRef.current) {
              observer.unobserve(imgRef.current)
            }
          }
        })
      },
      { rootMargin: '50px' }
    )

    if (imgRef.current) {
      observer.observe(imgRef.current)
    }

    return () => {
      if (imgRef.current) {
        observer.unobserve(imgRef.current)
      }
    }
  }, [src, fallback])

  const handleLoad = () => {
    setIsLoaded(true)
  }

  return (
    <img
      ref={imgRef}
      src={imageSrc || fallback || 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 300%22%3E%3Crect fill=%22%23e2e8f0%22 width=%22400%22 height=%22300%22/%3E%3C/svg%3E'}
      alt={alt}
      width={width}
      height={height}
      className={`lazy-image ${isLoaded ? 'loaded' : ''} ${className}`}
      onLoad={handleLoad}
      loading="lazy"
    />
  )
}
