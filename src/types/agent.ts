export type AgentType = 'buyer' | 'seller' | 'verifier' | 'reputation'

export type AgentEvent =
  | 'task_received'
  | 'task_executing'
  | 'verifying'
  | 'reputation_updated'
  | 'cache_hit'

export interface AgentActivity {
  type: 'activity' | 'ping'
  event: AgentEvent
  agent: AgentType
  details: Record<string, unknown>
  timestamp: string
}

export interface AgentReputation {
  agent_address: string
  agent_type?: string
  score: number
  total_tasks: number
  successful_tasks: number
}

export interface AgentStatus {
  agents: AgentType[]
  active_connections: number
  status: string
}
