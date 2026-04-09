import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ShieldCheck, ShieldX, Search, ExternalLink, Loader2 } from 'lucide-react'
import { Layout } from '../components/shared/Layout'
import { useMerkleVerify } from '../hooks/useMerkleVerify'
import { shortenHash } from '../utils/formatters'

export function VerifyResult() {
  const { taskHash: paramHash } = useParams<{ taskHash: string }>()
  const navigate = useNavigate()
  const [inputHash, setInputHash] = useState(paramHash ?? '')
  const { loading, onChainProof, error, fetchProof } = useMerkleVerify()

  const handleSearch = () => {
    if (!inputHash.trim()) return
    navigate(`/verify/${inputHash.trim()}`, { replace: true })
    fetchProof(inputHash.trim())
  }

  // Auto-fetch if URL param is provided
  useState(() => {
    if (paramHash) fetchProof(paramHash)
  })

  // Parse proof data: "merkle_root|requester|price_bytes"
  const parsedProof = onChainProof?.proof_data
    ? onChainProof.proof_data.split('|')
    : null

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-blue-50 rounded-2xl mb-4">
            <ShieldCheck className="w-7 h-7 text-blue-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Verify Result</h1>
          <p className="text-sm text-gray-500">
            Enter a task hash to verify its Merkle proof from Algorand Box Storage.
          </p>
        </div>

        {/* Search */}
        <div className="flex gap-2 mb-6">
          <input
            type="text"
            value={inputHash}
            onChange={(e) => setInputHash(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Enter task hash (sha256)..."
            className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
          />
          <button
            onClick={handleSearch}
            disabled={loading || !inputHash.trim()}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-xl px-4 py-2.5 text-sm font-medium transition"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            Verify
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-2xl mb-4">
            <ShieldX className="w-5 h-5 text-red-500 shrink-0" />
            <div>
              <p className="text-sm font-medium text-red-700">Not Found</p>
              <p className="text-xs text-red-500 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* On-chain proof */}
        {onChainProof && (
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-2xl">
              <ShieldCheck className="w-6 h-6 text-green-600 shrink-0" />
              <div>
                <p className="text-sm font-semibold text-green-700">
                  Verified On-Chain
                </p>
                <p className="text-xs text-green-600 mt-0.5">
                  Merkle root found in Algorand Box Storage
                </p>
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-4">
              <div>
                <p className="text-xs text-gray-500 mb-1">Task Hash</p>
                <p className="text-sm font-mono text-gray-900 break-all">
                  {onChainProof.task_hash}
                </p>
              </div>

              {parsedProof && parsedProof[0] && (
                <div>
                  <p className="text-xs text-gray-500 mb-1">Merkle Root</p>
                  <p className="text-sm font-mono text-gray-900 break-all">
                    {parsedProof[0]}
                  </p>
                </div>
              )}

              {parsedProof && parsedProof[1] && (
                <div>
                  <p className="text-xs text-gray-500 mb-1">Original Requester</p>
                  <p className="text-sm font-mono text-gray-900">{parsedProof[1]}</p>
                </div>
              )}

              {onChainProof.cached_result && (
                <div>
                  <p className="text-xs text-gray-500 mb-1">Result Preview</p>
                  <div className="bg-gray-50 rounded-xl p-3">
                    <p className="text-sm text-gray-700 line-clamp-5">
                      {onChainProof.cached_result.result}
                    </p>
                  </div>
                  {onChainProof.cached_result.ipfs_cid && (
                    <a
                      href={`https://w3s.link/ipfs/${onChainProof.cached_result.ipfs_cid}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 mt-2"
                    >
                      View full result on IPFS{' '}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              )}

              <div className="pt-3 border-t border-gray-100">
                <p className="text-xs text-gray-400">
                  Hash:{' '}
                  <span className="font-mono">{shortenHash(onChainProof.task_hash, 16)}</span>
                  {' · '}
                  Stored in Algorand Box Storage · Tamper-proof
                </p>
              </div>
            </div>
          </div>
        )}

        {!onChainProof && !error && !loading && (
          <div className="text-center py-12 text-sm text-gray-400">
            Enter a task hash above to verify its on-chain Merkle proof.
          </div>
        )}
      </div>
    </Layout>
  )
}
