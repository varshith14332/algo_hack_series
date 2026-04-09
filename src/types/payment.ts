export interface PaymentRequest {
  payment_required: boolean
  amount_algo: number
  receiver: string
  task_hash: string
  is_cached: boolean
  note: string
}

export interface PaymentStatus {
  tx_id: string
  verified: boolean
}

export interface BalanceResponse {
  address: string
  balance_algo: number
}
