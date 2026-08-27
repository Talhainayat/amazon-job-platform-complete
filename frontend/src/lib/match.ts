export function formatMatchScore(score: number): string {
  return `${Math.round(score)}% Match`
}

export function matchTone(score: number): 'strong' | 'good' | 'fair' {
  if (score >= 80) return 'strong'
  if (score >= 60) return 'good'
  return 'fair'
}
