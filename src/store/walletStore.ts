import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface WalletState {
  address: string | null
  balance: number
  connected: boolean
  setAddress: (address: string | null) => void
  setBalance: (balance: number) => void
  setConnected: (v: boolean) => void
  disconnect: () => void
}

export const useWalletStore = create<WalletState>()(
  persist(
    (set) => ({
      address: null,
      balance: 0,
      connected: false,
      setAddress: (address) => set({ address }),
      setBalance: (balance) => set({ balance }),
      setConnected: (connected) => set({ connected }),
      disconnect: () => set({ address: null, balance: 0, connected: false }),
    }),
    { name: 'wallet-store' }
  )
)
