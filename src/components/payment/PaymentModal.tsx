import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, Zap, CheckCircle } from 'lucide-react'
import { algoToUsd } from '../../utils/formatters'

interface Props {
  open: boolean
  amountAlgo: number
  isCached: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function PaymentModal({ open, amountAlgo, isCached, onConfirm, onCancel }: Props) {
  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="bg-white rounded-2xl shadow-xl p-8 max-w-sm w-full"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-blue-50 rounded-lg">
                <Zap className="w-5 h-5 text-blue-600" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900">Payment Required</h2>
            </div>

            {isCached && (
              <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                <CheckCircle className="w-4 h-4 text-green-600 shrink-0" />
                <span className="text-sm text-green-700 font-medium">
                  Cached result — 80% cheaper
                </span>
              </div>
            )}

            <div className="bg-gray-50 rounded-xl p-4 mb-6">
              <p className="text-sm text-gray-500 mb-1">Amount</p>
              <p className="text-3xl font-bold text-gray-900">
                {amountAlgo}{' '}
                <span className="text-lg font-normal text-gray-500">ALGO</span>
              </p>
              <p className="text-xs text-gray-400 mt-1">≈ ${algoToUsd(amountAlgo)} USD</p>
            </div>

            <div className="flex items-start gap-2 mb-6">
              <AlertCircle className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" />
              <p className="text-xs text-gray-500">
                This transaction will be signed by your Pera Wallet and verified on Algorand
                Testnet. Your result is Merkle-committed on-chain for tamper-proof integrity.
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={onCancel}
                className="flex-1 py-2.5 border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={onConfirm}
                className="flex-1 py-2.5 bg-blue-600 rounded-xl text-sm font-medium text-white hover:bg-blue-700 transition"
              >
                Sign & Pay
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
