import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { useAgentStore } from '../../store/agentStore'
import { AGENT_COLORS, AGENT_LABELS } from '../../utils/constants'
import { timeAgo } from '../../utils/formatters'

export function AgentGraph() {
  const { activities } = useAgentStore()

  // Build chart data from activity feed
  const data = activities
    .filter((a) => a.event === 'reputation_updated')
    .slice(0, 20)
    .reverse()
    .map((a, idx) => ({
      idx: idx + 1,
      time: timeAgo(a.timestamp),
      [a.agent]: (a.details.score as number) ?? 500,
    }))

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-400">
        Reputation history will appear here as tasks are processed.
      </div>
    )
  }

  const agents = ['buyer', 'seller', 'verifier', 'reputation']

  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
        <XAxis dataKey="idx" tick={{ fontSize: 11, fill: '#9CA3AF' }} />
        <YAxis domain={[0, 1000]} tick={{ fontSize: 11, fill: '#9CA3AF' }} />
        <Tooltip
          contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} formatter={(v: string) => AGENT_LABELS[v] ?? v} />
        {agents.map((key) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            stroke={AGENT_COLORS[key]}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
