import { algorandService } from './algorand'
import type { PaymentRequest } from '../types/payment'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000'

export interface X402Result {
  success: boolean
  data: unknown
  error?: string
}

export async function executeWithPayment(
  endpoint: string,
  taskHash: string,
  walletAddress: string,
  onPaymentRequired: (req: PaymentRequest) => Promise<boolean>,
  body?: FormData
): Promise<X402Result> {
  // Step 1: Probe — expect 402
  const probe = await fetch(`${BACKEND_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'X-Task-Hash': taskHash,
      'X-Wallet-Address': walletAddress,
    },
    body,
  })

  if (probe.status !== 402) {
    return probe.json() as Promise<X402Result>
  }

  const probeData = await probe.json() as { data: PaymentRequest }
  const paymentRequest = probeData.data

  // Step 2: Show confirmation modal
  const confirmed = await onPaymentRequired(paymentRequest)
  if (!confirmed) {
    throw new Error('User cancelled payment')
  }

  // Step 3: Build and sign transaction via Pera Wallet
  const txId = await algorandService.sendPayment({
    from: walletAddress,
    to: paymentRequest.receiver,
    amountAlgo: paymentRequest.amount_algo,
    note: paymentRequest.note,
  })

  // Step 4: Wait for confirmation on-chain
  await algorandService.waitForConfirmation(txId)

  // Step 5: Retry with payment proof
  const result = await fetch(`${BACKEND_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'X-Task-Hash': taskHash,
      'X-Wallet-Address': walletAddress,
      'X-Payment-Proof': txId,
    },
    body,
  })

  return result.json() as Promise<X402Result>
}
