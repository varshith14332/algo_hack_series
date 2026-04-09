import { Copy, ExternalLink, CheckCircle, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export interface AgentCredentialData {
  agent_address: string
  owner_address: string
  spending_limit_algo: number
  spent_algo: number
  allowed_categories: string[]
  reputation_score: number
  is_active: boolean
  registered_at?: string
}

interface Props {
  credential: AgentCredentialData
}

const EXPLORER_BASE = 'https://testnet.algoexplorer.io/address/'

function shortenAddr(addr: string, chars = 6): string {
  if (!addr || addr.length < chars * 2) return addr
  return `${addr.slice(0, chars)}…${addr.slice(-chars)}`
}

function ReputationGauge({ score }: { score: number }) {
  const pct = Math.min(100, (score / 1000) * 100)
  const color = pct >= 70 ? 'bg-green-500' : pct >= 40 ? 'bg-amber-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-gray-600 w-16 text-right">{score} / 1000</span>
    </div>
  )
}

function SpendBar({ spent, limit }: { spent: number; limit: number }) {
  const pct = limit > 0 ? Math.min(100, (spent / limit) * 100) : 0
  const color = pct >= 90 ? 'bg-red-500' : pct >= 70 ? 'bg-amber-500' : 'bg-blue-500'
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-500">
        <span>{spent.toFixed(4)} ALGO spent</span>
        <span>{limit.toFixed(4)} ALGO limit</span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

function CopyButton({ value }: { value: string }) {
  const copy = () => {
    navigator.clipboard.writeText(value).then(() => toast.success('Copied!')).catch(() => {})
  }
  return (
    <button onClick={copy} className="p-1 hover:bg-gray-100 rounded transition">
      <Copy className="w-3 h-3 text-gray-400" />
    </button>
  )
}

export function AgentCredential({ credential }: Props) {
  const {
    agent_address,
    owner_address,
    spending_limit_algo,
    spent_algo,
    allowed_categories,
    reputation_score,
    is_active,
  } = credential

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-xs text-gray-400 mb-0.5">Agent Address</p>
          <div className="flex items-center gap-1">
            <span className="font-mono text-sm text-gray-800">{shortenAddr(agent_address)}</span>
            <CopyButton value={agent_address} />
            <a
              href={`${EXPLORER_BASE}${agent_address}`}
              target="_blank"
              rel="noopener noreferrer"
              className="p-1 hover:bg-gray-100 rounded transition"
            >
              <ExternalLink className="w-3 h-3 text-gray-400" />
            </a>
          </div>
        </div>
        <span className={`inline-flex items-center gap-1 text-xs font-medium rounded-full px-2.5 py-0.5 border ${is_active ? 'bg-green-50 text-green-700 border-green-200' : 'bg-gray-100 text-gray-500 border-gray-200'}`}>
          {is_active ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
          {is_active ? 'Active' : 'Inactive'}
        </span>
      </div>

      {/* Owner */}
      <div>
        <p className="text-xs text-gray-400 mb-0.5">Owner</p>
        <div className="flex items-center gap-1">
          <span className="font-mono text-xs text-gray-600">{shortenAddr(owner_address)}</span>
          <CopyButton value={owner_address} />
        </div>
      </div>

      {/* Spend bar */}
      <div>
        <p className="text-xs text-gray-400 mb-1.5">Budget</p>
        <SpendBar spent={spent_algo} limit={spending_limit_algo} />
      </div>

      {/* Reputation gauge */}
      <div>
        <p className="text-xs text-gray-400 mb-1.5">Reputation Score</p>
        <ReputationGauge score={reputation_score} />
      </div>

      {/* Allowed categories */}
      <div>
        <p className="text-xs text-gray-400 mb-1.5">Allowed Categories</p>
        <div className="flex flex-wrap gap-1.5">
          {allowed_categories.map((cat) => (
            <span
              key={cat}
              className="bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-2.5 py-0.5 text-xs font-medium"
            >
              {cat}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
