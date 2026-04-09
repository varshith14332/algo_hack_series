import { Toaster } from 'react-hot-toast'
import { Navbar } from './Navbar'

interface Props {
  children: React.ReactNode
}

export function Layout({ children }: Props) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
      <Toaster
        position="top-right"
        toastOptions={{
          style: { fontFamily: 'Inter, sans-serif', fontSize: '14px' },
        }}
      />
    </div>
  )
}
