import { Wallet } from 'lucide-react'
import { useWallet } from '../../hooks/useWallet'

interface Props {
  children: React.ReactNode
}

export function WalletGuard({ children }: Props) {
  const { connected, connectWallet } = useWallet()

  if (!connected) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-6">
        <div className="p-5 bg-blue-50 rounded-2xl">
          <Wallet className="w-10 h-10 text-blue-600" />
        </div>
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Connect Your Wallet</h2>
          <p className="text-sm text-gray-500 max-w-xs">
            Connect your Algorand wallet via Pera Wallet to access the marketplace.
          </p>
        </div>
        <button
          onClick={connectWallet}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-6 py-3 text-sm font-medium transition"
        >
          <Wallet className="w-4 h-4" />
          Connect Pera Wallet
        </button>
      </div>
    )
  }

  return <>{children}</>
}
