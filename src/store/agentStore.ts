import { create } from 'zustand'
import type { AgentActivity, AgentReputation } from '../types/agent'

interface AgentState {
  activities: AgentActivity[]
  reputations: AgentReputation[]
  addActivity: (activity: AgentActivity) => void
  setReputations: (reps: AgentReputation[]) => void
}

export const useAgentStore = create<AgentState>((set) => ({
  activities: [],
  reputations: [],
  addActivity: (activity) =>
    set((state) => ({
      activities: [activity, ...state.activities].slice(0, 100), // keep last 100
    })),
  setReputations: (reputations) => set({ reputations }),
}))
