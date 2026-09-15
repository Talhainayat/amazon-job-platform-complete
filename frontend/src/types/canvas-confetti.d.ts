declare module 'canvas-confetti' {
  interface ConfettiOptions {
    particleCount?: number
    spread?: number
    origin?: { x?: number; y?: number }
    colors?: string[]
    disableForReducedMotion?: boolean
  }

  const confetti: (options?: ConfettiOptions) => Promise<null> | null
  export default confetti
}