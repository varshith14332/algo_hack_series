import { FileText, ExternalLink } from 'lucide-react'
import { MerkleProofBadge } from './MerkleProofBadge'
import { CacheHitBadge } from './CacheHitBadge'
import { StatusBadge } from '../shared/StatusBadge'
import { TxStatusTracker } from '../payment/TxStatusTracker'
import { shortenHash } from '../../utils/formatters'
import type { TaskResult } from '../../types/task'
import { LoadingSpinner } from '../shared/LoadingSpinner'

interface Props {
  taskId: string
  result: TaskResult | null
  isLoading: boolean
}

export function ResultCard({ taskId, result, isLoading }: Props) {
  if (isLoading && !result) {
    return (
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex flex-col items-center gap-4">
        <LoadingSpinner size="lg" />
        <p className="text-sm text-gray-500">Agent pipeline running...</p>
      </div>
    )
  }

  if (!result) return null

  const isProcessing = result.status === 'processing'

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-900">Result</span>
        </div>
        <div className="flex items-center gap-2">
          {result.from_cache && <CacheHitBadge score={result.similarity_score} />}
          <StatusBadge status={result.status} />
        </div>
      </div>

      <TxStatusTracker status={result.status} txId={taskId} />

      {isProcessing && (
        <div className="flex items-center gap-3 text-sm text-gray-500">
          <LoadingSpinner size="sm" />
          Agents are processing your task... This may take 30-60 seconds.
        </div>
      )}

      {result.result && (
        <div className="bg-gray-50 rounded-xl p-4">
          <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
            {result.result}
          </p>
        </div>
      )}

      {result.merkle_root && (
        <div className="space-y-2">
          <MerkleProofBadge merkleRoot={result.merkle_root} taskId={taskId} />
          <div className="flex items-center gap-4 text-xs text-gray-400">
            <span className="font-mono">Root: {shortenHash(result.merkle_root, 16)}</span>
            {result.ipfs_cid && (
              <a
                href={`https://w3s.link/ipfs/${result.ipfs_cid}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 hover:text-blue-600 transition"
              >
                IPFS <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        </div>
      )}

      {result.error && (
        <p className="text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2">{result.error}</p>
      )}
    </div>
  )
}
