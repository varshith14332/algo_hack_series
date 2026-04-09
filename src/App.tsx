import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ErrorBoundary } from './components/shared/ErrorBoundary'
import { Marketplace } from './pages/Marketplace'
import { AgentDashboard } from './pages/AgentDashboard'
import { MyResults } from './pages/MyResults'
import { VerifyResult } from './pages/VerifyResult'
import { NotFound } from './pages/NotFound'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 2, staleTime: 10_000 },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Marketplace />} />
            <Route path="/dashboard" element={<AgentDashboard />} />
            <Route path="/results" element={<MyResults />} />
            <Route path="/verify" element={<VerifyResult />} />
            <Route path="/verify/:taskHash" element={<VerifyResult />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </ErrorBoundary>
    </QueryClientProvider>
  )
}

export default App
