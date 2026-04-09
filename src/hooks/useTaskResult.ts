import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { useTaskStore } from '../store/taskStore'
import type { TaskResult } from '../types/task'

interface ApiEnvelope<T> {
  success: boolean
  data: T
}

const POLL_INTERVAL = 2000 // 2s
const DONE_STATUSES = new Set(['verified', 'failed', 'cache_hit'])

export function useTaskResult(taskId: string | null) {
  const { updateResult } = useTaskStore()

  return useQuery({
    queryKey: ['task-result', taskId],
    queryFn: async () => {
      const res = await api.get<ApiEnvelope<TaskResult>>(`/api/tasks/result/${taskId}`)
      const result = res.data.data
      if (taskId) updateResult(taskId, result)
      return result
    },
    enabled: !!taskId,
    refetchInterval: (query) => {
      const data = query.state.data
      if (!data) return POLL_INTERVAL
      return DONE_STATUSES.has(data.status) ? false : POLL_INTERVAL
    },
    staleTime: 0,
  })
}
