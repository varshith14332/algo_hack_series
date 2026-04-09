import { useCallback, useEffect } from 'react'
import { algorandService } from '../services/algorand'
import { useWalletStore } from '../store/walletStore'
import toast from 'react-hot-toast'

export function useWallet() {
  const { address, balance, connected, setAddress, setBalance, setConnected, disconnect } =
    useWalletStore()

  useEffect(() => {
    // Attempt to reconnect saved session on mount
    if (!connected) {
      algorandService
        .reconnect()
        .then((accounts) => {
          if (accounts.length > 0) {
            setAddress(accounts[0])
            setConnected(true)
            refreshBalance(accounts[0])
          }
        })
        .catch(() => {
          // No saved session — silent fail
        })
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const refreshBalance = useCallback(
    async (addr?: string) => {
      const target = addr ?? address
      if (!target) return
      try {
        const bal = await algorandService.getBalance(target)
        setBalance(bal)
      } catch {
        // Network error — keep existing balance
      }
    },
    [address, setBalance]
  )

  const connectWallet = useCallback(async () => {
    try {
      const accounts = await algorandService.connect()
      if (accounts.length === 0) {
        toast.error('No accounts found in Pera Wallet')
        return
      }
      setAddress(accounts[0])
      setConnected(true)
      await refreshBalance(accounts[0])
      toast.success('Wallet connected')
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to connect wallet'
      toast.error(msg)
    }
  }, [setAddress, setConnected, refreshBalance])

  const disconnectWallet = useCallback(async () => {
    try {
      await algorandService.disconnect()
    } catch {
      // Ignore disconnect errors
    } finally {
      disconnect()
      toast.success('Wallet disconnected')
    }
  }, [disconnect])

  return { address, balance, connected, connectWallet, disconnectWallet, refreshBalance }
}
