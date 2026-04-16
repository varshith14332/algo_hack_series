// Singleton WebSocket manager for agent activity feed
// Prevents multiple connections from being created

type MessageHandler = (data: unknown) => void

class WebSocketManager {
  private ws: WebSocket | null = null
  private handlers: Set<MessageHandler> = new Set()
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private isConnecting = false
  private shouldReconnect = true

  private readonly url = `${import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'}/api/agents/ws/activity`

  connect() {
    // Prevent multiple simultaneous connection attempts
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      console.log('[WebSocket] Already connected or connecting')
      return
    }

    this.isConnecting = true
    console.log('[WebSocket] Connecting...')

    try {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        this.isConnecting = false
        console.log('[WebSocket] Connected')
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          // Notify all registered handlers
          this.handlers.forEach(handler => handler(data))
        } catch (error) {
          console.warn('[WebSocket] Failed to parse message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error)
        this.isConnecting = false
      }

      this.ws.onclose = () => {
        console.log('[WebSocket] Disconnected')
        this.isConnecting = false
        this.ws = null

        // Auto-reconnect if we should
        if (this.shouldReconnect && this.handlers.size > 0) {
          console.log('[WebSocket] Reconnecting in 3s...')
          this.reconnectTimer = setTimeout(() => this.connect(), 3000)
        }
      }
    } catch (error) {
      console.error('[WebSocket] Connection failed:', error)
      this.isConnecting = false
    }
  }

  disconnect() {
    this.shouldReconnect = false
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    console.log('[WebSocket] Disconnected')
  }

  subscribe(handler: MessageHandler): () => void {
    this.handlers.add(handler)
    
    // Connect if this is the first subscriber
    if (this.handlers.size === 1) {
      this.shouldReconnect = true
      this.connect()
    }

    // Return unsubscribe function
    return () => {
      this.handlers.delete(handler)
      
      // Disconnect if no more subscribers
      if (this.handlers.size === 0) {
        this.disconnect()
      }
    }
  }

  getConnectionState(): 'connecting' | 'open' | 'closing' | 'closed' {
    if (!this.ws) return 'closed'
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting'
      case WebSocket.OPEN: return 'open'
      case WebSocket.CLOSING: return 'closing'
      case WebSocket.CLOSED: return 'closed'
      default: return 'closed'
    }
  }
}

// Export singleton instance
export const wsManager = new WebSocketManager()
