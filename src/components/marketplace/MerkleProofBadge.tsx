import { ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'

interface Props {
  merkleRoot: string
  taskId: string
}

export function MerkleProofBadge({ merkleRoot: _merkleRoot, taskId }: Props) {
  return (
    <Link
      to={`/verify/${taskId}`}
      className="inline-flex items-center gap-1.5 bg-green-50 text-green-700 border border-green-200 rounded-full px-2.5 py-0.5 text-xs font-medium hover:bg-green-100 transition"
    >
      <ShieldCheck className="w-3 h-3" />
      Merkle Verified — View Proof
    </Link>
  )
}
