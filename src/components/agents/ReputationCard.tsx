import { TrendingUp } from 'lucide-react'
import type { AgentReputation } from '../../types/agent'
import { formatReputationScore } from '../../utils/formatters'
import { AGENT_COLORS } from '../../utils/constants'

interface Props {
  reputation: AgentReputation
}

export function ReputationCard({ reputation }: Props) {
  const color = AGENT_COLORS[reputation.agent_type ?? ''] ?? '#6B7280'
  const successRate =
    reputation.total_tasks > 0
      ? ((reputation.successful_tasks / reputation.total_tasks) * 100).toFixed(1)
      : '—'

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-center gap-2 mb-3">
        <TrendingUp className="w-4 h-4 text-gray-400" />
        <p className="text-sm font-medium text-gray-500 font-mono">
          {reputation.agent_address.slice(0, 8)}...
        </p>
      </div>

      <p className="text-2xl font-bold text-gray-900 mb-1">
        {formatReputationScore(reputation.score)}
      </p>

      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden mb-3">
        <div
          className="h-full rounded-full"
          style={{ width: `${(reputation.score / 1000) * 100}%`, backgroundColor: color }}
        />
      </div>

      <div className="flex justify-between text-xs text-gray-400">
        <span>{reputation.total_tasks} tasks</span>
        <span>{successRate}% success</span>
      </div>
    </div>
  )
}
