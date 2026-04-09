import { Link, useLocation } from 'react-router-dom'
import { Brain, LayoutDashboard, FileText, ShieldCheck } from 'lucide-react'
import { WalletConnect } from '../wallet/WalletConnect'

const NAV_ITEMS = [
  { to: '/', label: 'Marketplace', icon: Brain },
  { to: '/dashboard', label: 'Agents', icon: LayoutDashboard },
  { to: '/results', label: 'My Results', icon: FileText },
  { to: '/verify', label: 'Verify', icon: ShieldCheck },
]

export function Navbar() {
  const { pathname } = useLocation()

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-gray-900">NeuralLedger</span>
          </Link>

          {/* Nav links */}
          <div className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition ${
                  pathname === to
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            ))}
          </div>

          <WalletConnect />
        </div>
      </div>
    </nav>
  )
}
