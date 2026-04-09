export type TaskType = 'summarize' | 'extract' | 'analyze'

export type TaskStatus =
  | 'pending'
  | 'processing'
  | 'verified'
  | 'failed'
  | 'cache_hit'

export interface Task {
  task_id: string
  task_hash: string
  task_type: TaskType
  prompt: string
  status: TaskStatus
  result?: string
  merkle_root?: string
  ipfs_cid?: string
  verification_score?: number
  similarity_score?: number
  from_cache: boolean
  price_algo: number
  created_at: string
}

export interface TaskResult {
  task_id: string
  status: TaskStatus
  result?: string
  merkle_root?: string
  ipfs_cid?: string
  verification_score?: number
  similarity_score?: number
  from_cache: boolean
  error?: string
}

export interface HashResponse {
  task_hash: string
  is_cached: boolean
  semantic_match: SemanticMatch | null
}

export interface SemanticMatch {
  task_hash: string
  score: number
  metadata: Record<string, string>
}
