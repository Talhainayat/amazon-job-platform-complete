function formatMatchScore(score) {
  return `${Math.round(score)}% Match`
}

function matchTone(score) {
  if (score >= 80) return 'strong'
  if (score >= 60) return 'good'
  return 'fair'
}

if (formatMatchScore(91.6) !== '92% Match') throw new Error('formatMatchScore failed')
if (matchTone(90) !== 'strong' || matchTone(61) !== 'good' || matchTone(20) !== 'fair') {
  throw new Error('matchTone failed')
}
console.log('frontend match helpers ok')
