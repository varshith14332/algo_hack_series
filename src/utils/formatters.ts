import { ALGO_USD_ESTIMATE } from './constants'

export function shortenAddress(address: string, chars = 6): string {
  if (!address) return ''
  return `${address.slice(0, chars)}...${address.slice(-4)}`
}

export function shortenHash(hash: string, chars = 8): string {
  if (!hash) return ''
  return `${hash.slice(0, chars)}...`
}

export function algoToUsd(algo: number): string {
  return (algo * ALGO_USD_ESTIMATE).toFixed(4)
}

export function formatAlgo(algo: number): string {
  return algo.toFixed(6)
}

export function formatScore(score: number): string {
  return `${(score * 100).toFixed(1)}%`
}

export function formatReputationScore(score: number): string {
  return `${score.toFixed(0)} / 1000`
}

export function timeAgo(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime()
  const seconds = Math.floor(diff / 1000)
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  return `${hours}h ago`
}
