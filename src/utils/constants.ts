export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000'
export const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'
export const ALGORAND_NODE_URL =
  import.meta.env.VITE_ALGORAND_NODE_URL ?? 'https://testnet-api.algonode.cloud'

export const NEW_TASK_PRICE_ALGO = 0.005
export const CACHED_TASK_PRICE_ALGO = 0.001
export const ALGO_USD_ESTIMATE = 0.15

export const TASK_TYPES = [
  { value: 'summarize', label: 'Summarize', description: 'Concise summary of the document' },
  { value: 'extract', label: 'Extract', description: 'Extract key data and entities' },
  { value: 'analyze', label: 'Analyze', description: 'Deep analysis and insights' },
] as const

export const AGENT_COLORS: Record<string, string> = {
  buyer: '#2563EB',
  seller: '#16A34A',
  verifier: '#D97706',
  reputation: '#7C3AED',
}

export const AGENT_LABELS: Record<string, string> = {
  buyer: 'Buyer Agent',
  seller: 'Seller Agent',
  verifier: 'Verifier Agent',
  reputation: 'Reputation Agent',
}
