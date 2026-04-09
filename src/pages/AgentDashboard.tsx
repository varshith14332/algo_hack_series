import { useEffect, useState } from 'react'
import { LayoutDashboard, Users, Activity, Shield, Database } from 'lucide-react'
import { Layout } from '../components/shared/Layout'
import { AgentMonitor } from '../components/agents/AgentMonitor'
import { AgentActivityFeed } from '../components/agents/AgentActivityFeed'
import { AgentGraph } from '../components/agents/AgentGraph'
import { ReputationCard } from '../components/agents/ReputationCard'
import { AgentCredential } from '../components/agents/AgentCredential'
import type { AgentCredentialData } from '../components/agents/AgentCredential'
import { useAgentActivity } from '../hooks/useAgentActivity'
import { useAgentStore } from '../store/agentStore'
import { api } from '../services/api'
import type { AgentReputation } from '../types/agent'

interface ApiEnvelope<T> { success: boolean; data: T }
interface ReputationListResponse { agents: AgentReputation[] }

interface ServiceEntry {
  service_id: string
  service_name: string
  category: string
  price_microalgo: number
  reputation_threshold: number
  is_active: boolean
  total_calls: number
  agent_address: string
}

// Derive mock credential data from reputation list for display purposes
function reputationToCredential(rep: AgentReputation): AgentCredentialData {
  return {
    agent_address: rep.agent_address,
    owner_address: rep.agent_address.slice(0, 58).padEnd(58, 'A'),
    spending_limit_algo: 2.0,
    spent_algo: rep.total_tasks * 0.001,
    allowed_categories: ['research', 'data', 'analysis', 'writing'],
    reputation_score: Math.round(rep.score),
    is_active: true,
  }
}

export function AgentDashboard() {
  const { reputations, setReputations, activities } = useAgentStore()
  const [services, setServices] = useState<ServiceEntry[]>([])
  const [loadingServices, setLoadingServices] = useState(false)

  useAgentActivity()

  useEffect(() => {
    api
      .get<ApiEnvelope<ReputationListResponse>>('/api/agents/reputation')
      .then((res) => {
        if (res.data.success) setReputations(res.data.data.agents)
      })
      .catch(() => {})
  }, [setReputations])

  useEffect(() => {
    setLoadingServices(true)
    api
      .get<ApiEnvelope<{ services: ServiceEntry[] }>>('/api/agents/services')
      .then((res) => {
        if (res.data.success && res.data.data.services) {
          setServices(res.data.data.services)
        }
      })
      .catch(() => {})
      .finally(() => setLoadingServices(false))
  }, [])

  return (
    <Layout>
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-1">
          <LayoutDashboard className="w-5 h-5 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Agent Dashboard</h1>
        </div>
        <p className="text-sm text-gray-500">
          Monitor LangGraph agent pipeline, on-chain identities, service registry, and real-time activity.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Agent status cards */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Users className="w-4 h-4 text-gray-400" />
              <h2 className="text-sm font-semibold text-gray-900">Agent Status</h2>
            </div>
            <AgentMonitor />
          </div>

          {/* Reputation chart */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">Reputation History</h2>
            <AgentGraph />
          </div>

          {/* Reputation cards */}
          {reputations.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-gray-900 mb-3">Registered Agents</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {reputations.map((rep) => (
                  <ReputationCard key={rep.agent_address} reputation={rep} />
                ))}
              </div>
            </div>
          )}

          {/* ── NEW: Active Agent Credentials ── */}
          {reputations.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Shield className="w-4 h-4 text-gray-400" />
                <h2 className="text-sm font-semibold text-gray-900">Active Agent Credentials</h2>
                <span className="ml-auto bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-2 py-0.5 text-xs font-medium">
                  On-chain Identity Registry
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {reputations.map((rep) => (
                  <AgentCredential
                    key={rep.agent_address}
                    credential={reputationToCredential(rep)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* ── NEW: Service Registry ── */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Database className="w-4 h-4 text-gray-400" />
              <h2 className="text-sm font-semibold text-gray-900">Service Registry</h2>
              <span className="ml-auto bg-green-50 text-green-700 border border-green-200 rounded-full px-2 py-0.5 text-xs font-medium">
                {services.length} services
              </span>
            </div>
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
              {loadingServices ? (
                <div className="p-8 text-center text-sm text-gray-400">Loading services…</div>
              ) : services.length === 0 ? (
                <div className="p-8 text-center text-sm text-gray-400">
                  No services registered yet. Services appear after the first autonomous run.
                </div>
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100 bg-gray-50">
                      <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500">Service</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500">Category</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500">Price</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500">Min Rep</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500">Calls</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500">Provider</th>
                    </tr>
                  </thead>
                  <tbody>
                    {services.map((svc) => (
                      <tr key={svc.service_id} className="border-b border-gray-50 hover:bg-gray-50 transition">
                        <td className="px-4 py-3">
                          <div>
                            <p className="font-medium text-gray-900 text-xs">{svc.service_name}</p>
                            <p className="font-mono text-xs text-gray-400">{svc.service_id}</p>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-2 py-0.5 text-xs font-medium">
                            {svc.category}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right text-xs text-gray-600">
                          {(svc.price_microalgo / 1_000_000).toFixed(4)} ALGO
                        </td>
                        <td className="px-4 py-3 text-right text-xs text-gray-600">
                          {svc.reputation_threshold}
                        </td>
                        <td className="px-4 py-3 text-right text-xs text-gray-600">
                          {svc.total_calls}
                        </td>
                        <td className="px-4 py-3">
                          <span className="font-mono text-xs text-gray-400">
                            {svc.agent_address ? `${svc.agent_address.slice(0, 8)}…` : '—'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>

        {/* Activity feed sidebar */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 h-fit">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-4 h-4 text-gray-400" />
            <h2 className="text-sm font-semibold text-gray-900">Activity Feed</h2>
            <span className="ml-auto bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-2 py-0.5 text-xs font-medium">
              {activities.length}
            </span>
          </div>
          <AgentActivityFeed />
        </div>
      </div>
    </Layout>
  )
}
