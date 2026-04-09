import type { TaskStatus } from '../../types/task'

const CONFIG: Record<TaskStatus, { label: string; className: string }> = {
  pending: { label: 'Pending', className: 'bg-gray-100 text-gray-600 border-gray-200' },
  processing: { label: 'Processing', className: 'bg-blue-50 text-blue-700 border-blue-200' },
  verified: { label: 'Verified', className: 'bg-green-50 text-green-700 border-green-200' },
  failed: { label: 'Failed', className: 'bg-red-50 text-red-700 border-red-200' },
  cache_hit: { label: 'Cached', className: 'bg-purple-50 text-purple-700 border-purple-200' },
}

interface Props {
  status: TaskStatus
}

export function StatusBadge({ status }: Props) {
  const { label, className } = CONFIG[status]
  return (
    <span className={`inline-flex items-center border rounded-full px-2.5 py-0.5 text-xs font-medium ${className}`}>
      {label}
    </span>
  )
}
