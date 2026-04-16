import { useEffect, useRef, useCallback } from 'react'
import { useAgentStore } from '../store/agentStore'
import type { AgentActivity } from '../types/agent'

const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'

export function useAgentActivity() {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const mountedRef = useRef(true)
  const { addActivity } = useAgentStore()

  const connect = useCallback(() => {
    // Don't connect if already open or component unmounted
    if (!mountedRef.current) return
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(`${WS_URL}/api/agents/ws/activity`)

    ws.onopen = () => {
      console.log('[AgentFeed] Connected')
    }

    ws.onmessage = (e: MessageEvent<string>) => {
      try {
        const msg = JSON.parse(e.data) as AgentActivity
        if (msg.type === 'activity') {
          addActivity(msg)
        }
      } catch {
        // ignore malformed messages
      }
    }

    ws.onclose = () => {
      if (!mountedRef.current) return
      console.log('[AgentFeed] Disconnected — reconnecting in 3s')
      reconnectRef.current = setTimeout(connect, 3000)
    }

    ws.onerror = () => {
      ws.close() // triggers onclose which handles reconnect
    }

    wsRef.current = ws
  }, [addActivity])

  useEffect(() => {
    mountedRef.current = true

    // Small delay prevents StrictMode double-invoke race
    const timer = setTimeout(connect, 100)

    return () => {
      mountedRef.current = false
      clearTimeout(timer)
      if (reconnectRef.current) clearTimeout(reconnectRef.current)
      wsRef.current?.close()
    }
  }, [connect])
}
