import { CheckCircle, Clock, XCircle, Loader2 } from 'lucide-react'
import type { TaskStatus } from '../../types/task'

interface Props {
  status: TaskStatus
  txId?: string
}

const STATUS_CONFIG: Record<string, { icon: typeof Clock; color: string; label: string }> = {
  processing: { icon: Loader2, color: 'text-blue-600', label: 'Processing...' },
  verified: { icon: CheckCircle, color: 'text-green-600', label: 'Verified' },
  cache_hit: { icon: CheckCircle, color: 'text-purple-600', label: 'Cache Hit' },
  failed: { icon: XCircle, color: 'text-red-600', label: 'Failed' },
  pending: { icon: Clock, color: 'text-gray-400', label: 'Pending' },
}

export function TxStatusTracker({ status, txId }: Props) {
  const { icon: Icon, color, label } = STATUS_CONFIG[status] ?? STATUS_CONFIG.pending

  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
      <Icon
        className={`w-5 h-5 ${color} ${status === 'processing' ? 'animate-spin' : ''}`}
      />
      <div>
        <p className="text-sm font-medium text-gray-900">{label}</p>
        {txId && (
          <p className="text-xs text-gray-400 font-mono">{txId.slice(0, 20)}...</p>
        )}
      </div>
    </div>
  )
}
