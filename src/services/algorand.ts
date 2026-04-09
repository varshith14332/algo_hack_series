import algosdk from 'algosdk'
import { PeraWalletConnect } from '@perawallet/connect'
import type { MerkleProofStep } from '../types/algorand'

const peraWallet = new PeraWalletConnect()

const algodClient = new algosdk.Algodv2(
  '',
  import.meta.env.VITE_ALGORAND_NODE_URL ?? 'https://testnet-api.algonode.cloud',
  ''
)

export const algorandService = {
  peraWallet,

  async connect(): Promise<string[]> {
    const accounts = await peraWallet.connect()
    peraWallet.connector?.on('disconnect', () => {
      peraWallet.disconnect()
    })
    return accounts
  },

  async reconnect(): Promise<string[]> {
    return await peraWallet.reconnectSession()
  },

  async disconnect(): Promise<void> {
    await peraWallet.disconnect()
  },

  async getBalance(address: string): Promise<number> {
    const info = await algodClient.accountInformation(address).do()
    return Number(info.amount) / 1_000_000
  },

  async sendPayment(params: {
    from: string
    to: string
    amountAlgo: number
    note: string
  }): Promise<string> {
    const suggestedParams = await algodClient.getTransactionParams().do()
    const noteBytes = new TextEncoder().encode(params.note)

    const txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
      from: params.from,
      to: params.to,
      amount: Math.round(params.amountAlgo * 1_000_000),
      note: noteBytes,
      suggestedParams,
    })

    const singleTxnGroups = [{ txn, signers: [params.from] }]
    const signedTxns = await peraWallet.signTransaction([singleTxnGroups])
    const { txId } = await algodClient.sendRawTransaction(signedTxns).do()
    return txId as string
  },

  async waitForConfirmation(txId: string, rounds = 10): Promise<void> {
    await algosdk.waitForConfirmation(algodClient, txId, rounds)
  },

  async verifyMerkleProof(params: {
    leafData: string
    proof: MerkleProofStep[]
    root: string
  }): Promise<boolean> {
    const { leafData, proof, root } = params
    const encoder = new TextEncoder()

    async function sha256hex(data: string): Promise<string> {
      const buf = await crypto.subtle.digest('SHA-256', encoder.encode(data))
      return Array.from(new Uint8Array(buf))
        .map((b) => b.toString(16).padStart(2, '0'))
        .join('')
    }

    let current = await sha256hex(leafData)

    for (const step of proof) {
      if (step.position === 'right') {
        current = await sha256hex(current + step.hash)
      } else {
        current = await sha256hex(step.hash + current)
      }
    }

    return current === root
  },
}
