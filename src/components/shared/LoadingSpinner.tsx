interface Props {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const SIZE_MAP = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' }

export function LoadingSpinner({ size = 'md', className = '' }: Props) {
  return (
    <div
      className={`${SIZE_MAP[size]} border-2 border-gray-200 border-t-blue-600 rounded-full animate-spin ${className}`}
    />
  )
}
