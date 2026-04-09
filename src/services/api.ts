import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000'

export const api = axios.create({
  baseURL: BACKEND_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    // Passthrough 402 so x402Client can handle it
    if (err.response?.status === 402) return Promise.reject(err)
    console.error('API error:', err.response?.data?.error ?? err.message)
    return Promise.reject(err)
  }
)
