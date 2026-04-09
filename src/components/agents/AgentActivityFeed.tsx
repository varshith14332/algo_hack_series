import { useAgentStore } from '../../store/agentStore'
import { AGENT_COLORS, AGENT_LABELS } from '../../utils/constants'
import { timeAgo } from '../../utils/formatters'

export function AgentActivityFeed() {
  const { activities } = useAgentStore()

  if (activities.length === 0) {
    return (
      <div className="text-center py-8 text-sm text-gray-400">
        No activity yet. Submit a task to see the agent pipeline in action.
      </div>
    )
  }

  return (
    <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
      {activities.map((activity, idx) => {
        const color = AGENT_COLORS[activity.agent] ?? '#6B7280'
        const label = AGENT_LABELS[activity.agent] ?? activity.agent

        return (
          <div key={idx} className="flex items-start gap-3 p-3 bg-white rounded-xl border border-gray-100">
            <div
              className="w-2 h-2 rounded-full mt-1.5 shrink-0"
              style={{ backgroundColor: color }}
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold" style={{ color }}>
                  {label}
                </span>
                <span className="text-xs text-gray-400">{timeAgo(activity.timestamp)}</span>
              </div>
              <p className="text-sm text-gray-700 mt-0.5">
                {activity.event.replace(/_/g, ' ')}
              </p>
              {activity.details.task_id && (
                <p className="text-xs text-gray-400 font-mono mt-0.5">
                  {String(activity.details.task_id).slice(0, 16)}...
                </p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
