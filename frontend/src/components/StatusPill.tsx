import { Loader, CircleCheck, CircleX } from 'lucide-react'
import { cn } from '@/lib/utils'

type StatusPillState = 'initializing' | 'processing' | 'succeeded' | 'failed'

interface StatusPillProps {
  state: StatusPillState
  label: string
}

const statusConfig: Record<
  StatusPillState,
  {
    color: string
    bgColor: string
    Icon: typeof Loader
  }
> = {
  initializing: {
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    Icon: Loader
  },
  processing: {
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    Icon: Loader
  },
  succeeded: {
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    Icon: CircleCheck
  },
  failed: {
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    Icon: CircleX
  }
}

export function StatusPill({
  state,
  label
}: StatusPillProps): React.JSX.Element {
  const config = statusConfig[state]
  const Icon = config.Icon
  const isLoading = state === 'initializing' || state === 'processing'

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium',
        config.bgColor,
        config.color
      )}
    >
      <Icon
        className={cn('h-4 w-4', isLoading && 'animate-spin')}
        aria-hidden="true"
      />
      <span>{label}</span>
    </div>
  )
}
