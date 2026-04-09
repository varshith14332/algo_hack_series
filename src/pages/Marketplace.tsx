import { useState, useRef, useCallback } from 'react'
import { Brain, Zap, Bot, ChevronDown, ChevronUp, Loader2 } from 'lucide-react'
import { Layout } from '../components/shared/Layout'
import { TaskSubmitter } from '../components/marketplace/TaskSubmitter'
import { ResultCard } from '../components/marketplace/ResultCard'
import { PriceBreakdown } from '../components/marketplace/PriceBreakdown'
import { AgentActivityFeed } from '../components/agents/AgentActivityFeed'
import { AuditTrail } from '../components/agents/AuditTrail'
import type { AuditEntry } from '../components/agents/AuditTrail'
import { WalletGuard } from '../components/wallet/WalletGuard'
import { useTaskResult } from '../hooks/useTaskResult'
import { useAgentActivity } from '../hooks/useAgentActivity'
import { useWalletStore } from '../store/walletStore'
import { api } from '../services/api'
import toast from 'react-hot-toast'

// ─── Autonomous Mode ─────────────────────────────────────────────────────────

const COST_BREAKDOWN = [
  { label: 'Research', algo: 0.3 },
  { label: 'Analysis', algo: 0.4 },
  { label: 'Writing', algo: 0.2 },
]

interface AutonomousStatus {
  status: string
  current_step: string
  progress_percent: number
  audit_trail: AuditEntry[]
  result?: {
    final_output: string
    total_spent_algo: number
    subtasks_completed: number
    merkle_roots: string[]
    master_agent_address: string
  }
}

function AutonomousMode() {
  const { address } = useWalletStore()
  const [goal, setGoal] = useState('')
  const [budget, setBudget] = useState(1)
  const [running, setRunning] = useState(false)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [status, setStatus] = useState<AutonomousStatus | null>(null)
  const [showFullResult, setShowFullResult] = useState(false)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopPoll = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
  }, [])

  const pollStatus = useCallback(async (id: string) => {
    try {
      const res = await api.get<{ success: boolean; data: AutonomousStatus }>(`/api/autonomous/status/${id}`)
      if (res.data.success) {
        setStatus(res.data.data)
        if (res.data.data.status === 'complete' || res.data.data.status === 'failed') {
          stopPoll()
          setRunning(false)
        }
      }
    } catch {
      // ignore transient errors
    }
  }, [stopPoll])

  const launch = async () => {
    if (!address) { toast.error('Connect your wallet first'); return }
    if (!goal.trim()) { toast.error('Please enter a goal'); return }

    setRunning(true)
    setStatus(null)
    setTaskId(null)

    try {
      const res = await api.post<{ success: boolean; data: { task_id: string; master_agent_address: string; estimated_cost_algo: number } }>(
        '/api/autonomous/run',
        { goal: goal.trim(), budget_algo: budget, owner_address: address }
      )
      if (!res.data.success) throw new Error('Launch failed')
      const id = res.data.data.task_id
      setTaskId(id)
      toast.success(`Pipeline launched — est. cost ${res.data.data.estimated_cost_algo} ALGO`)

      pollRef.current = setInterval(() => pollStatus(id), 2000)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Launch failed'
      toast.error(msg)
      setRunning(false)
    }
  }

  const scaledBreakdown = COST_BREAKDOWN.map((item) => ({
    ...item,
    algo: +(item.algo * (budget / 0.9)).toFixed(4),
  }))

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left: goal input */}
      <div className="lg:col-span-2 space-y-4">
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Bot className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-semibold text-gray-900">Autonomous Agent Pipeline</h2>
            <span className="ml-auto bg-purple-50 text-purple-700 border border-purple-200 rounded-full px-2.5 py-0.5 text-xs font-medium">
              No wallet popup
            </span>
          </div>

          <p className="text-xs text-gray-500 mb-4">
            Describe your research goal. The master agent will break it into subtasks, hire
            specialist agents, verify results on-chain, and return a full report — no manual signing
            required.
          </p>

          <textarea
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={4}
            placeholder="e.g. Research the top 3 Algorand DeFi protocols and summarize their risks"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            disabled={running}
          />

          {/* Budget slider */}
          <div className="mt-4 space-y-2">
            <div className="flex justify-between text-xs text-gray-600">
              <span>Agent budget</span>
              <span className="font-semibold">{budget} ALGO</span>
            </div>
            <input
              type="range"
              min={0.5}
              max={10}
              step={0.5}
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              disabled={running}
              className="w-full accent-blue-600"
            />
            <div className="flex justify-between text-xs text-gray-400">
              <span>0.5 ALGO</span>
              <span>10 ALGO</span>
            </div>
          </div>

          {/* Cost breakdown */}
          <div className="mt-4 grid grid-cols-3 gap-2">
            {scaledBreakdown.map((item) => (
              <div key={item.label} className="bg-gray-50 rounded-xl p-3 text-center">
                <p className="text-xs text-gray-400">{item.label}</p>
                <p className="text-sm font-semibold text-gray-800">~{item.algo} ALGO</p>
              </div>
            ))}
          </div>

          <button
            onClick={launch}
            disabled={running || !goal.trim()}
            className="mt-4 w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl px-4 py-2.5 text-sm font-medium transition flex items-center justify-center gap-2"
          >
            {running ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Running pipeline…
              </>
            ) : (
              <>
                <Bot className="w-4 h-4" />
                Launch Agent Pipeline
              </>
            )}
          </button>
        </div>

        {/* Progress bar */}
        {status && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm font-semibold text-gray-900">Pipeline Progress</p>
              <span className="text-xs text-gray-500">{status.progress_percent}%</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden mb-2">
              <div
                className="h-full bg-blue-600 rounded-full transition-all duration-500"
                style={{ width: `${status.progress_percent}%` }}
              />
            </div>
            <p className="text-xs text-gray-500">{status.current_step}</p>

            {/* Final result */}
            {status.status === 'complete' && status.result && (
              <div className="mt-4 border-t pt-4 space-y-3">
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="bg-green-50 text-green-700 border border-green-200 rounded-full px-2.5 py-0.5 text-xs font-medium">
                    Complete
                  </span>
                  <span className="text-xs text-gray-500">
                    {status.result.subtasks_completed} subtasks · {status.result.total_spent_algo.toFixed(4)} ALGO spent
                  </span>
                  {status.result.merkle_roots.length > 0 && (
                    <span className="bg-purple-50 text-purple-700 border border-purple-200 rounded-full px-2.5 py-0.5 text-xs font-medium">
                      {status.result.merkle_roots.length} Merkle commitments
                    </span>
                  )}
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs font-semibold text-gray-700">Final Report</p>
                    <button
                      onClick={() => setShowFullResult((v) => !v)}
                      className="text-xs text-blue-600 flex items-center gap-1"
                    >
                      {showFullResult ? <><ChevronUp className="w-3 h-3" /> Collapse</> : <><ChevronDown className="w-3 h-3" /> Expand</>}
                    </button>
                  </div>
                  <div className={`text-xs text-gray-700 whitespace-pre-wrap leading-relaxed ${!showFullResult ? 'line-clamp-6' : ''}`}>
                    {status.result.final_output}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right: live audit trail */}
      <div className="space-y-4">
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-4 h-4 text-gray-400" />
            <h3 className="text-sm font-semibold text-gray-900">Live Audit Trail</h3>
            {status && (
              <span className="ml-auto bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-2 py-0.5 text-xs font-medium">
                {status.audit_trail.length} events
              </span>
            )}
          </div>
          <AuditTrail entries={status?.audit_trail ?? []} />
          {taskId && status?.status === 'complete' && (
            <a
              href={`/api/autonomous/audit/${taskId}`}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-3 block text-center text-xs text-blue-600 hover:underline"
            >
              View full audit trail →
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────

type Tab = 'manual' | 'autonomous'

export function Marketplace() {
  const [tab, setTab] = useState<Tab>('manual')
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null)
  const { data: result, isLoading } = useTaskResult(activeTaskId)

  useAgentActivity()

  return (
    <Layout>
      {/* Hero */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-4 py-1.5 text-sm font-medium mb-4">
          <Zap className="w-3.5 h-3.5" />
          x402 Micro-Payment Protocol · Algorand Testnet
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">AI Computation Marketplace</h1>
        <p className="text-gray-500 max-w-xl mx-auto text-sm leading-relaxed">
          Submit AI tasks with micro-payments. Results are Merkle-committed on-chain and resold at
          discount — eliminating redundant computation forever.
        </p>
      </div>

      {/* Tab switcher */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 mb-6 w-fit mx-auto">
        <button
          onClick={() => setTab('manual')}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition ${tab === 'manual' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
        >
          Manual Task
        </button>
        <button
          onClick={() => setTab('autonomous')}
          className={`flex items-center gap-1.5 px-5 py-2 rounded-lg text-sm font-medium transition ${tab === 'autonomous' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
        >
          <Bot className="w-3.5 h-3.5" />
          Autonomous Mode
        </button>
      </div>

      <WalletGuard>
        {tab === 'manual' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <TaskSubmitter onResult={(id) => setActiveTaskId(id)} />
              {(activeTaskId || result) && (
                <ResultCard
                  taskId={activeTaskId ?? ''}
                  result={result ?? null}
                  isLoading={isLoading}
                />
              )}
            </div>
            <div className="space-y-6">
              <PriceBreakdown />
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Brain className="w-4 h-4 text-gray-400" />
                  <h3 className="text-sm font-semibold text-gray-900">Live Agent Feed</h3>
                </div>
                <AgentActivityFeed />
              </div>
            </div>
          </div>
        ) : (
          <AutonomousMode />
        )}
      </WalletGuard>
    </Layout>
  )
}
