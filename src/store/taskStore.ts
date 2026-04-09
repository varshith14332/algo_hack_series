import { create } from 'zustand'
import type { Task, TaskResult } from '../types/task'

interface TaskState {
  tasks: Task[]
  activeTaskId: string | null
  activeResult: TaskResult | null
  addTask: (task: Task) => void
  updateResult: (taskId: string, result: TaskResult) => void
  setActiveTaskId: (id: string | null) => void
  setActiveResult: (result: TaskResult | null) => void
  clearActive: () => void
}

export const useTaskStore = create<TaskState>((set) => ({
  tasks: [],
  activeTaskId: null,
  activeResult: null,
  addTask: (task) =>
    set((state) => ({ tasks: [task, ...state.tasks] })),
  updateResult: (taskId, result) =>
    set((state) => ({
      tasks: state.tasks.map((t) =>
        t.task_id === taskId
          ? { ...t, status: result.status, result: result.result, merkle_root: result.merkle_root, ipfs_cid: result.ipfs_cid }
          : t
      ),
      activeResult: state.activeTaskId === taskId ? result : state.activeResult,
    })),
  setActiveTaskId: (id) => set({ activeTaskId: id }),
  setActiveResult: (result) => set({ activeResult: result }),
  clearActive: () => set({ activeTaskId: null, activeResult: null }),
}))
