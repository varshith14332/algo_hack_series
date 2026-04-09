import type { MerkleProofStep } from '../types/algorand'

async function sha256hex(data: string): Promise<string> {
  const encoder = new TextEncoder()
  const buf = await crypto.subtle.digest('SHA-256', encoder.encode(data))
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
}

export async function verifyMerkleProof(
  leafData: string,
  proof: MerkleProofStep[],
  root: string
): Promise<boolean> {
  let current = await sha256hex(leafData)

  for (const step of proof) {
    if (step.position === 'right') {
      current = await sha256hex(current + step.hash)
    } else {
      current = await sha256hex(step.hash + current)
    }
  }

  return current === root
}

export async function hashContent(content: string): Promise<string> {
  return sha256hex(content)
}
