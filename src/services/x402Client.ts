const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export interface PaymentRequest {
  amount_algo: number;
  receiver: string;
  task_hash: string;
  is_cached: boolean;
  note: string;
}

export async function executeWithPayment(
  endpoint: string,
  taskHash: string,
  walletAddress: string,
  onPaymentRequired: (req: PaymentRequest) => Promise<boolean>,
  body?: FormData
): Promise<unknown> {
  
  // Step 1 — Probe request, expect 402
  const probe = await fetch(`${BACKEND_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'X-Task-Hash': taskHash,
      'X-Wallet-Address': walletAddress,
    },
    body,
  });

  // If not 402, something else happened
  if (probe.status !== 402) {
    return probe.json();
  }

  // Step 2 — Parse the 402 payment request
  let probeData: { data: PaymentRequest };
  try {
    probeData = await probe.json();
  } catch {
    throw new Error('Invalid 402 response from server');
  }

  const paymentRequest = probeData.data;

  if (!paymentRequest?.amount_algo || !paymentRequest?.receiver) {
    throw new Error('Incomplete payment request received');
  }

  // Step 3 — Ask user to confirm payment
  const confirmed = await onPaymentRequired(paymentRequest);
  if (!confirmed) {
    throw new Error('User cancelled payment');
  }

  // Step 4 — Import algorand service and send payment
  const { algorandService } = await import('./algorand');

  let txId: string;
  try {
    txId = await algorandService.sendPayment({
      from: walletAddress,
      to: paymentRequest.receiver,
      amountAlgo: paymentRequest.amount_algo,
      note: paymentRequest.note,
    });
  } catch (err) {
    throw new Error(`Payment signing failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
  }

  // Step 5 — Wait for Algorand confirmation
  try {
    await algorandService.waitForConfirmation(txId);
  } catch {
    throw new Error(`Transaction ${txId} failed to confirm`);
  }

  // Step 6 — Retry with payment proof
  const result = await fetch(`${BACKEND_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'X-Task-Hash': taskHash,
      'X-Wallet-Address': walletAddress,
      'X-Payment-Proof': txId,
    },
    body,
  });

  return result.json();
}
