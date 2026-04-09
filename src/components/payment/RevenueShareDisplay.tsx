import { DollarSign } from 'lucide-react'

interface Props {
  priceAlgo: number
  platformShare?: number
  requesterShare?: number
}

export function RevenueShareDisplay({
  priceAlgo,
  platformShare = 0.7,
  requesterShare = 0.3,
}: Props) {
  const platform = priceAlgo * platformShare
  const requester = priceAlgo * requesterShare

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <DollarSign className="w-4 h-4 text-gray-500" />
        <h3 className="text-sm font-semibold text-gray-900">Revenue Split</h3>
      </div>
      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Platform (70%)</span>
          <span className="font-medium text-gray-900">{platform.toFixed(5)} ALGO</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Original Requester (30%)</span>
          <span className="font-medium text-gray-900">{requester.toFixed(5)} ALGO</span>
        </div>
        <div className="pt-2 border-t border-gray-100 flex justify-between text-sm">
          <span className="font-medium text-gray-700">Total</span>
          <span className="font-bold text-gray-900">{priceAlgo} ALGO</span>
        </div>
      </div>
    </div>
  )
}
