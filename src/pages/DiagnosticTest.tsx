import { useState, useEffect, useRef } from 'react'
import { Layout } from '../components/shared/Layout'

export function DiagnosticTest() {
  const [wsStatus, setWsStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected')
  const [messages, setMessages] = useState<string[]>([])
  const [corsTest, setCorsTest] = useState<string>('pending')
  const [backendTest, setBackendTest] = useState<string>('pending')
  const wsRef = useRef<WebSocket | null>(null)

  // Test backend health
  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => {
        setBackendTest(data.status === 'ok' ? '✅ OK' : '❌ Failed')
      })
      .catch(() => setBackendTest('❌ Failed'))
  }, [])

  // Test CORS
  useEffect(() => {
    fetch('http://localhost:8000/api/tasks/run', {
      method: 'OPTIONS',
      headers: {
        'Origin': window.location.origin,
        'Access-Control-Request-Method': 'POST',
      }
    })
      .then(res => {
        setCorsTest(res.ok ? '✅ OK' : '❌ Failed')
      })
      .catch(() => setCorsTest('❌ Failed'))
  }, [])

  // Test WebSocket
  const connectWs = () => {
    setWsStatus('connecting')
    setMessages([])
    
    const ws = new WebSocket('ws://localhost:8000/api/agents/ws/activity')
    
    ws.onopen = () => {
      setWsStatus('connected')
      setMessages(prev => [...prev, `[${new Date().toLocaleTimeString()}] ✅ Connected`])
    }
    
    ws.onmessage = (e) => {
      setMessages(prev => [...prev, `[${new Date().toLocaleTimeString()}] 📨 ${e.data}`])
    }
    
    ws.onerror = (e) => {
      setWsStatus('error')
      setMessages(prev => [...prev, `[${new Date().toLocaleTimeString()}] ❌ Error: ${e}`])
    }
    
    ws.onclose = () => {
      setWsStatus('disconnected')
      setMessages(prev => [...prev, `[${new Date().toLocaleTimeString()}] 🔌 Disconnected`])
    }
    
    wsRef.current = ws
  }

  const disconnectWs = () => {
    wsRef.current?.close()
    wsRef.current = null
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">System Diagnostics</h1>
        
        <div className="space-y-6">
          {/* Backend Health */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h2 className="text-xl font-semibold mb-4">Backend Health</h2>
            <div className="font-mono text-sm">
              Status: {backendTest}
            </div>
          </div>

          {/* CORS Test */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h2 className="text-xl font-semibold mb-4">CORS Preflight</h2>
            <div className="font-mono text-sm">
              Status: {corsTest}
            </div>
          </div>

          {/* WebSocket Test */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h2 className="text-xl font-semibold mb-4">WebSocket Connection</h2>
            
            <div className="mb-4">
              <div className="font-mono text-sm mb-2">
                Status: <span className={
                  wsStatus === 'connected' ? 'text-green-600' :
                  wsStatus === 'error' ? 'text-red-600' :
                  wsStatus === 'connecting' ? 'text-yellow-600' :
                  'text-gray-600'
                }>
                  {wsStatus.toUpperCase()}
                </span>
              </div>
              
              <div className="flex gap-2">
                <button
                  onClick={connectWs}
                  disabled={wsStatus === 'connected' || wsStatus === 'connecting'}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700"
                >
                  Connect
                </button>
                <button
                  onClick={disconnectWs}
                  disabled={wsStatus === 'disconnected'}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-red-700"
                >
                  Disconnect
                </button>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
              <div className="font-mono text-xs space-y-1">
                {messages.length === 0 ? (
                  <div className="text-gray-400">No messages yet. Click Connect to test.</div>
                ) : (
                  messages.map((msg, i) => (
                    <div key={i} className="text-gray-700">{msg}</div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Browser Info */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h2 className="text-xl font-semibold mb-4">Browser Info</h2>
            <div className="font-mono text-xs space-y-1 text-gray-700">
              <div>User Agent: {navigator.userAgent}</div>
              <div>Origin: {window.location.origin}</div>
              <div>WebSocket Support: {typeof WebSocket !== 'undefined' ? '✅ Yes' : '❌ No'}</div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
