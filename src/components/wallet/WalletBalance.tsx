import { RefreshCw } from 'lucide-react'
import { useWallet } from '../../hooks/useWallet'
import { formatAlgo, algoToUsd, shortenAddress } from '../../utils/formatters'

export function WalletBalance() {
  const { address, balance, refreshBalance } = useWallet()

  if (!address) return null

  return (
    <div>
      <p className="text-xs text-gray-500 font-mono mb-1">{shortenAddress(address, 10)}</p>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xl font-bold text-gray-900">{formatAlgo(balance)} ALGO</p>
          <p className="text-xs text-gray-400">≈ ${algoToUsd(balance)} USD</p>
        </div>
        <button
          onClick={() => refreshBalance()}
          className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition"
          title="Refresh balance"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
