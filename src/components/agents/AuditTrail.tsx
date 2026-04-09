import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, XCircle, Clock, ExternalLink, DollarSign } from 'lucide-react'

export interface AuditEntry {
  agent: 'master' | 'buyer' | 'seller' | 'verifier' | 'reputation'
  action: string
  detail: string
  payment_algo: number | null
  tx_id: string | null
  timestamp?: string
}

interface Props {
  entries: AuditEntry[]
  className?: string
}

const AGENT_COLORS: Record<string, string> = {
  master: 'bg-blue-100 text-blue-700 border-blue-200',
  buyer: 'bg-purple-100 text-purple-700 border-purple-200',
  seller: 'bg-teal-100 text-teal-700 border-teal-200',
  verifier: 'bg-amber-100 text-amber-700 border-amber-200',
  reputation: 'bg-green-100 text-green-700 border-green-200',
}

const AGENT_DOT: Record<string, string> = {
  master: 'bg-blue-500',
  buyer: 'bg-purple-500',
  seller: 'bg-teal-500',
  verifier: 'bg-amber-500',
  reputation: 'bg-green-500',
}

const SUCCESS_ACTIONS = new Set([
  'verified', 'cache_hit', 'result_produced', 'reward', 'service_selected',
  'payment_recorded', 'subtask_complete', 'pipeline_complete', 'identity_registered',
  'goal_parsed', 'writing_report',
])
const FAILURE_ACTIONS = new Set([
  'rejected', 'execution_failed', 'slash', 'budget_exceeded', 'budget_guard',
])

function StatusIcon({ action }: { action: string }) {
  if (SUCCESS_ACTIONS.has(action)) return <CheckCircle className="w-3.5 h-3.5 text-green-500 shrink-0" />
  if (FAILURE_ACTIONS.has(action)) return <XCircle className="w-3.5 h-3.5 text-red-500 shrink-0" />
  return <Clock className="w-3.5 h-3.5 text-gray-400 shrink-0 animate-pulse" />
}

function timeLabel(ts?: string): string {
  if (!ts) return ''
  try {
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ''
  }
}

const EXPLORER_BASE = 'https://testnet.algoexplorer.io/tx/'

export function AuditTrail({ entries, className = '' }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [entries.length])

  if (entries.length === 0) {
    return (
      <div className={`flex items-center justify-center h-32 text-sm text-gray-400 ${className}`}>
        Waiting for agent activity…
      </div>
    )
  }

  return (
    <div className={`space-y-2 overflow-y-auto max-h-96 pr-1 ${className}`}>
      <AnimatePresence initial={false}>
        {entries.map((entry, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="flex gap-3 items-start"
          >
            {/* Timeline dot */}
            <div className="flex flex-col items-center mt-1">
              <div className={`w-2 h-2 rounded-full ${AGENT_DOT[entry.agent] ?? 'bg-gray-400'}`} />
              {i < entries.length - 1 && <div className="w-px flex-1 bg-gray-200 mt-1" style={{ minHeight: 12 }} />}
            </div>

            {/* Card */}
            <div className="flex-1 bg-white border border-gray-100 rounded-xl p-3 shadow-sm min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                {/* Agent badge */}
                <span className={`inline-flex items-center gap-1 border rounded-full px-2 py-0.5 text-xs font-medium ${AGENT_COLORS[entry.agent] ?? 'bg-gray-100 text-gray-600 border-gray-200'}`}>
                  {entry.agent.charAt(0).toUpperCase() + entry.agent.slice(1)}
                </span>
                {/* Action */}
                <span className="text-xs font-mono text-gray-500">{entry.action}</span>
                {/* Status icon */}
                <StatusIcon action={entry.action} />
                {/* Timestamp */}
                {entry.timestamp && (
                  <span className="ml-auto text-xs text-gray-400">{timeLabel(entry.timestamp)}</span>
                )}
              </div>

              {/* Detail */}
              <p className="text-xs text-gray-600 leading-relaxed">{entry.detail}</p>

              {/* Payment + tx */}
              {(entry.payment_algo != null || entry.tx_id) && (
                <div className="flex items-center gap-3 mt-2 flex-wrap">
                  {entry.payment_algo != null && (
                    <span className="inline-flex items-center gap-1 text-xs text-green-700 bg-green-50 border border-green-200 rounded-full px-2 py-0.5">
                      <DollarSign className="w-3 h-3" />
                      {entry.payment_algo.toFixed(4)} ALGO
                    </span>
                  )}
                  {entry.tx_id && !entry.tx_id.startsWith('dev-') && !entry.tx_id.startsWith('agent-mode') && (
                    <a
                      href={`${EXPLORER_BASE}${entry.tx_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline"
                    >
                      <ExternalLink className="w-3 h-3" />
                      {entry.tx_id.slice(0, 10)}…
                    </a>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
      <div ref={bottomRef} />
    </div>
  )
}
