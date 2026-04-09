import { useState, useCallback } from 'react'
import { executeWithPayment } from '../services/x402Client'
import { useWalletStore } from '../store/walletStore'
import { api } from '../services/api'
import { useTaskStore } from '../store/taskStore'
import type { PaymentRequest } from '../types/payment'
import type { HashResponse } from '../types/task'
import toast from 'react-hot-toast'

interface ApiEnvelope<T> {
  success: boolean
  data: T
  error: string | null
}

export function useX402() {
  const { address } = useWalletStore()
  const { setActiveTaskId } = useTaskStore()
  const [loading, setLoading] = useState(false)
  const [paymentRequest, setPaymentRequest] = useState<null | {
    amount_algo: number
    is_cached: boolean
    resolve: (v: boolean) => void
  }>(null)

  const submitTask = useCallback(
    async (taskType: string, prompt: string, file?: File) => {
      if (!address) {
        toast.error('Connect your wallet first')
        return null
      }

      setLoading(true)

      try {
        // 1. Compute task hash
        const content = `${taskType}: ${prompt}`
        const hashRes = await api.post<ApiEnvelope<HashResponse>>('/api/tasks/hash', { content })
        const taskHash = hashRes.data.data.task_hash

        const formData = new FormData()
        formData.append('task_type', taskType)
        formData.append('prompt', prompt)
        if (file) formData.append('file', file)

        // 2. Execute with x402 payment flow
        const result = await executeWithPayment(
          '/api/tasks/run',
          taskHash,
          address,
          (req: PaymentRequest) =>
            new Promise<boolean>((resolve) => {
              setPaymentRequest({
                amount_algo: req.amount_algo,
                is_cached: req.is_cached,
                resolve,
              })
            }),
          formData
        )

        if (result.success && result.data) {
          const data = result.data as { task_id: string }
          setActiveTaskId(data.task_id)
        }

        return result
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Task failed'
        if (msg !== 'User cancelled payment') {
          toast.error(msg)
        }
        return null
      } finally {
        setLoading(false)
        setPaymentRequest(null)
      }
    },
    [address, setActiveTaskId]
  )

  const confirmPayment = useCallback(
    (confirmed: boolean) => {
      paymentRequest?.resolve(confirmed)
    },
    [paymentRequest]
  )

  return { submitTask, loading, paymentRequest, confirmPayment }
}
