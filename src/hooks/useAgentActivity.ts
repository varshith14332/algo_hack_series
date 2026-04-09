import { useEffect, useRef } from 'react'
import { useAgentStore } from '../store/agentStore'
import type { AgentActivity } from '../types/agent'

const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'

export function useAgentActivity() {
  const wsRef = useRef<WebSocket | null>(null)
  const { addActivity } = useAgentStore()

  useEffect(() => {
    let reconnectTimer: ReturnType<typeof setTimeout>

    function connect() {
      const ws = new WebSocket(`${WS_URL}/api/agents/ws/activity`)

      ws.onopen = () => {
        console.info('[AgentFeed] Connected')
      }

      ws.onmessage = (e: MessageEvent<string>) => {
        try {
          const msg = JSON.parse(e.data) as AgentActivity
          if (msg.type === 'activity') {
            addActivity(msg)
          }
        } catch {
          // Malformed message — ignore
        }
      }

      ws.onclose = () => {
        console.warn('[AgentFeed] Disconnected — reconnecting in 3s')
        reconnectTimer = setTimeout(connect, 3000)
      }

      ws.onerror = () => ws.close()

      wsRef.current = ws
    }

    connect()

    return () => {
      clearTimeout(reconnectTimer)
      wsRef.current?.close()
    }
  }, [addActivity])
}
