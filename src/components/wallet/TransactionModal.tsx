import { motion, AnimatePresence } from 'framer-motion'
import { ExternalLink, CheckCircle, Loader2, XCircle } from 'lucide-react'
import { shortenHash } from '../../utils/formatters'

interface Props {
  open: boolean
  txId?: string
  status: 'pending' | 'confirming' | 'confirmed' | 'failed'
  onClose: () => void
}

const STATUS_CONFIG = {
  pending: { icon: Loader2, label: 'Signing transaction...', color: 'text-blue-600', spin: true },
  confirming: { icon: Loader2, label: 'Waiting for confirmation...', color: 'text-amber-600', spin: true },
  confirmed: { icon: CheckCircle, label: 'Transaction confirmed', color: 'text-green-600', spin: false },
  failed: { icon: XCircle, label: 'Transaction failed', color: 'text-red-600', spin: false },
}

export function TransactionModal({ open, txId, status, onClose }: Props) {
  const { icon: Icon, label, color, spin } = STATUS_CONFIG[status]

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white rounded-2xl shadow-xl p-8 max-w-sm w-full text-center"
          >
            <div className={`flex justify-center mb-4 ${color}`}>
              <Icon className={`w-10 h-10 ${spin ? 'animate-spin' : ''}`} />
            </div>
            <p className="text-sm font-medium text-gray-900 mb-2">{label}</p>

            {txId && (
              <div className="bg-gray-50 rounded-xl p-3 mb-4">
                <p className="text-xs text-gray-500 mb-1">Transaction ID</p>
                <p className="text-xs font-mono text-gray-700">{shortenHash(txId, 20)}</p>
              </div>
            )}

            {txId && status === 'confirmed' && (
              <a
                href={`https://testnet.explorer.perawallet.app/tx/${txId}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-1 text-xs text-blue-600 hover:text-blue-700 mb-4"
              >
                View on Algorand Explorer <ExternalLink className="w-3 h-3" />
              </a>
            )}

            {(status === 'confirmed' || status === 'failed') && (
              <button
                onClick={onClose}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium transition"
              >
                Close
              </button>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
