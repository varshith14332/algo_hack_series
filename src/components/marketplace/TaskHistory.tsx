import { useTaskStore } from '../../store/taskStore'
import { StatusBadge } from '../shared/StatusBadge'
import { shortenHash, timeAgo } from '../../utils/formatters'

export function TaskHistory() {
  const { tasks } = useTaskStore()

  if (tasks.length === 0) {
    return (
      <div className="text-center py-8 text-sm text-gray-400">
        No tasks yet. Submit your first task above.
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {tasks.map((task) => (
        <div
          key={task.task_id}
          className="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-100 shadow-sm"
        >
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{task.prompt}</p>
            <p className="text-xs text-gray-400 font-mono mt-0.5">
              {shortenHash(task.task_hash)} · {timeAgo(task.created_at)}
            </p>
          </div>
          <StatusBadge status={task.status} />
        </div>
      ))}
    </div>
  )
}
