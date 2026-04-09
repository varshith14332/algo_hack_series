import { NEW_TASK_PRICE_ALGO, CACHED_TASK_PRICE_ALGO } from '../../utils/constants'
import { algoToUsd } from '../../utils/formatters'

export function PriceBreakdown() {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">Pricing</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-700">New computation</p>
            <p className="text-xs text-gray-400">Full AI pipeline run</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-bold text-gray-900">{NEW_TASK_PRICE_ALGO} ALGO</p>
            <p className="text-xs text-gray-400">≈ ${algoToUsd(NEW_TASK_PRICE_ALGO)}</p>
          </div>
        </div>
        <div className="border-t border-gray-100" />
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-700">Cached result</p>
            <p className="text-xs text-green-600 font-medium">80% cheaper</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-bold text-gray-900">{CACHED_TASK_PRICE_ALGO} ALGO</p>
            <p className="text-xs text-gray-400">≈ ${algoToUsd(CACHED_TASK_PRICE_ALGO)}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
