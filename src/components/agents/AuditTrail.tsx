import { motion } from 'framer-motion';

export interface AuditEntry {
  event: string;
  agent?: string;
  timestamp: string;
  cost_algo?: number;
  merkle_root?: string;
  from_cache?: boolean;
  reputation_score?: number;
  [key: string]: unknown;
}

interface Props {
  entries: AuditEntry[];
  loading?: boolean;
}

const EVENT_COLORS: Record<string, string> = {
  master_agent_initialized: 'bg-blue-500',
  service_discovered: 'bg-purple-500',
  subtask_completed: 'bg-green-500',
  cache_hit: 'bg-teal-500',
  authorization_failed: 'bg-red-500',
  reputation_updated: 'bg-amber-500',
};

function formatEventName(event: string): string {
  return event
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function formatTimestamp(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return timestamp;
  }
}

export function AuditTrail({ entries, loading = false }: Props) {
  if (loading && entries.length === 0) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map(i => (
          <div key={i} className="flex gap-3 animate-pulse">
            <div className="w-2 h-2 bg-gray-300 rounded-full mt-2" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4" />
              <div className="h-3 bg-gray-100 rounded w-1/2" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400 text-sm">
        No audit trail entries yet
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {entries.map((entry, index) => {
        const dotColor = EVENT_COLORS[entry.event] || 'bg-gray-400';

        return (
          <motion.div
            key={`${entry.event}-${index}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="flex gap-3"
          >
            {/* Timeline dot */}
            <div className="flex flex-col items-center">
              <div className={`w-2 h-2 rounded-full ${dotColor} mt-2`} />
              {index < entries.length - 1 && (
                <div className="w-px h-full bg-gray-200 mt-1" />
              )}
            </div>

            {/* Content */}
            <div className="flex-1 pb-4">
              <div className="text-sm font-medium text-gray-900">
                {formatEventName(entry.event)}
              </div>
              
              <div className="text-xs text-gray-500 mt-0.5">
                {formatTimestamp(entry.timestamp)}
              </div>

              {/* Badges */}
              <div className="flex flex-wrap gap-2 mt-2">
                {entry.cost_algo !== undefined && (
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-50 text-red-700 border border-red-200">
                    −{entry.cost_algo} ALGO
                  </span>
                )}

                {entry.from_cache && (
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-50 text-green-700 border border-green-200">
                    cached
                  </span>
                )}

                {entry.reputation_score !== undefined && (
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
                    Score → {entry.reputation_score}
                  </span>
                )}
              </div>

              {/* Merkle root link */}
              {entry.merkle_root && (
                <div className="mt-2">
                  <a
                    href={`https://testnet.algoexplorer.io/tx/${entry.merkle_root}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-mono text-blue-600 hover:text-blue-700 hover:underline"
                  >
                    {entry.merkle_root.slice(0, 12)}...
                  </a>
                </div>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
