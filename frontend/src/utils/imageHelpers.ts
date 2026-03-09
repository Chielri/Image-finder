export function formatConfidence(confidence: number): string {
  return `${(confidence * 100).toFixed(1)}%`
}
