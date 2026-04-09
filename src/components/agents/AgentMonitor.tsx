import { ShoppingCart, Store, ShieldCheck, Star } from 'lucide-react'
import { useAgentStore } from '../../store/agentStore'
import { AGENT_COLORS } from '../../utils/constants'
import { formatReputationScore } from '../../utils/formatters'

const AGENTS = [
  { key: 'buyer', label: 'Buyer Agent', icon: ShoppingCart, role: 'Routes tasks & checks cache' },
  { key: 'seller', label: 'Seller Agent', icon: Store, role: 'Executes AI computation' },
  { key: 'verifier', label: 'Verifier Agent', icon: ShieldCheck, role: 'Validates result quality' },
  { key: 'reputation', label: 'Reputation Agent', icon: Star, role: 'Updates agent scores' },
]

export function AgentMonitor() {
  const { reputations, activities } = useAgentStore()

  function getAgentScore(key: string): number {
    const rep = reputations.find((r) => r.agent_type === key)
    return rep?.score ?? 500
  }

  function getLastEvent(key: string) {
    return activities.find((a) => a.agent === key)
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {AGENTS.map(({ key, label, icon: Icon, role }) => {
        const score = getAgentScore(key)
        const lastEvent = getLastEvent(key)
        const color = AGENT_COLORS[key]

        return (
          <div
            key={key}
            className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5"
          >
            <div className="flex items-center gap-3 mb-4">
              <div
                className="p-2 rounded-xl"
                style={{ backgroundColor: `${color}18` }}
              >
                <Icon className="w-5 h-5" style={{ color }} />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-900">{label}</p>
                <p className="text-xs text-gray-400">{role}</p>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Reputation</span>
                <span className="font-medium text-gray-900">{formatReputationScore(score)}</span>
              </div>

              {/* Score bar */}
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{ width: `${(score / 1000) * 100}%`, backgroundColor: color }}
                />
              </div>

              {lastEvent && (
                <p className="text-xs text-gray-400 mt-1">
                  Last: {lastEvent.event.replace(/_/g, ' ')}
                </p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
