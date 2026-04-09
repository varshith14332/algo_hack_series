export interface AlgorandAccount {
  address: string
  amount: number
  'min-balance': number
}

export interface MerkleProofStep {
  hash: string
  position: 'left' | 'right'
}

export interface OnChainProof {
  task_hash: string
  on_chain: boolean
  proof_data: string
  cached_result: CachedResult | null
}

export interface CachedResult {
  result: string
  merkle_root: string
  ipfs_cid: string
  requester: string
  task_hash: string
}
