import { useState } from 'react'
import { FileText, Filter } from 'lucide-react'
import { Layout } from '../components/shared/Layout'
import { WalletGuard } from '../components/wallet/WalletGuard'
import { useTaskStore } from '../store/taskStore'
import { StatusBadge } from '../components/shared/StatusBadge'
import { MerkleProofBadge } from '../components/marketplace/MerkleProofBadge'
import { CacheHitBadge } from '../components/marketplace/CacheHitBadge'
import { shortenHash, timeAgo } from '../utils/formatters'
import type { TaskStatus } from '../types/task'

type Filter = 'all' | 'cached' | 'fresh'

const FILTER_LABELS: Record<Filter, string> = {
  all: 'All',
  cached: 'Cached',
  fresh: 'Fresh',
}

export function MyResults() {
  const { tasks } = useTaskStore()
  const [filter, setFilter] = useState<Filter>('all')
  const [expanded, setExpanded] = useState<string | null>(null)

  const filtered = tasks.filter((t) => {
    if (filter === 'cached') return t.from_cache
    if (filter === 'fresh') return !t.from_cache
    return true
  })

  const doneStatuses: TaskStatus[] = ['verified', 'cache_hit', 'failed']
  const completed = filtered.filter((t) => doneStatuses.includes(t.status))

  return (
    <Layout>
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-1">
          <FileText className="w-5 h-5 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">My Results</h1>
        </div>
        <p className="text-sm text-gray-500">All AI computation results you've purchased.</p>
      </div>

      <WalletGuard>
        {/* Filter */}
        <div className="flex items-center gap-2 mb-6">
          <Filter className="w-4 h-4 text-gray-400" />
          {(Object.keys(FILTER_LABELS) as Filter[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'border border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {FILTER_LABELS[f]}
            </button>
          ))}
        </div>

        {completed.length === 0 ? (
          <div className="text-center py-16 text-sm text-gray-400">
            No results yet. Submit tasks on the Marketplace.
          </div>
        ) : (
          <div className="space-y-4">
            {completed.map((task) => (
              <div
                key={task.task_id}
                className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden"
              >
                {/* Header */}
                <button
                  className="w-full text-left p-5 hover:bg-gray-50 transition"
                  onClick={() =>
                    setExpanded(expanded === task.task_id ? null : task.task_id)
                  }
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {task.prompt}
                      </p>
                      <div className="flex items-center gap-2 mt-1 flex-wrap">
                        <span className="text-xs text-gray-400 font-mono">
                          {shortenHash(task.task_hash)}
                        </span>
                        <span className="text-xs text-gray-400">·</span>
                        <span className="text-xs text-gray-400">{timeAgo(task.created_at)}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {task.from_cache && <CacheHitBadge />}
                      <StatusBadge status={task.status} />
                    </div>
                  </div>
                </button>

                {/* Expanded result */}
                {expanded === task.task_id && task.result && (
                  <div className="border-t border-gray-100 p-5 space-y-4">
                    <div className="bg-gray-50 rounded-xl p-4">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                        {task.result}
                      </p>
                    </div>

                    {task.merkle_root && (
                      <MerkleProofBadge
                        merkleRoot={task.merkle_root}
                        taskId={task.task_id}
                      />
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </WalletGuard>
    </Layout>
  )
}
