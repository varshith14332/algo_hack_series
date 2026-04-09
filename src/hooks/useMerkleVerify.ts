import { useState, useCallback } from 'react'
import { algorandService } from '../services/algorand'
import { api } from '../services/api'
import type { OnChainProof } from '../types/algorand'
import type { MerkleProofStep } from '../types/algorand'

interface ApiEnvelope<T> {
  success: boolean
  data: T
  error: string | null
}

export function useMerkleVerify() {
  const [loading, setLoading] = useState(false)
  const [onChainProof, setOnChainProof] = useState<OnChainProof | null>(null)
  const [verified, setVerified] = useState<boolean | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchProof = useCallback(async (taskHash: string) => {
    setLoading(true)
    setError(null)
    setOnChainProof(null)
    setVerified(null)

    try {
      const res = await api.get<ApiEnvelope<OnChainProof>>(`/api/verify/result/${taskHash}`)
      if (res.data.success) {
        setOnChainProof(res.data.data)
      } else {
        setError(res.data.error ?? 'Result not found')
      }
    } catch {
      setError('Failed to fetch on-chain proof')
    } finally {
      setLoading(false)
    }
  }, [])

  const verifyClientSide = useCallback(
    async (leafData: string, proof: MerkleProofStep[], root: string) => {
      setLoading(true)
      try {
        const result = await algorandService.verifyMerkleProof({ leafData, proof, root })
        setVerified(result)
        return result
      } catch {
        setError('Client-side verification failed')
        return false
      } finally {
        setLoading(false)
      }
    },
    []
  )

  return { loading, onChainProof, verified, error, fetchProof, verifyClientSide }
}
