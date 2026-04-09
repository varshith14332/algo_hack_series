import { Zap } from 'lucide-react'
import { formatScore } from '../../utils/formatters'

interface Props {
  score?: number
}

export function CacheHitBadge({ score }: Props) {
  return (
    <span className="inline-flex items-center gap-1 bg-purple-50 text-purple-700 border border-purple-200 rounded-full px-2.5 py-0.5 text-xs font-medium">
      <Zap className="w-3 h-3" />
      Cache Hit {score !== undefined && `· ${formatScore(score)}`}
    </span>
  )
}
