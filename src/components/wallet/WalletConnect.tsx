import { Wallet, LogOut, ChevronDown } from 'lucide-react'
import { useState } from 'react'
import { useWallet } from '../../hooks/useWallet'
import { WalletBalance } from './WalletBalance'
import { shortenAddress } from '../../utils/formatters'

export function WalletConnect() {
  const { address, connected, connectWallet, disconnectWallet } = useWallet()
  const [open, setOpen] = useState(false)

  if (!connected || !address) {
    return (
      <button
        onClick={connectWallet}
        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-4 py-2 text-sm font-medium transition"
      >
        <Wallet className="w-4 h-4" />
        Connect Wallet
      </button>
    )
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 border border-gray-200 rounded-xl px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
      >
        <div className="w-2 h-2 bg-green-500 rounded-full" />
        {shortenAddress(address)}
        <ChevronDown className="w-3 h-3" />
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-2xl border border-gray-100 shadow-lg p-4 z-50">
          <WalletBalance />
          <div className="mt-4 pt-3 border-t border-gray-100">
            <button
              onClick={() => { disconnectWallet(); setOpen(false) }}
              className="flex items-center gap-2 text-sm text-red-600 hover:text-red-700 font-medium"
            >
              <LogOut className="w-4 h-4" />
              Disconnect
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
