import { UserPlus, MessageSquare, Settings, AlertTriangle, User } from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

export type ActivityType = 'user' | 'chat' | 'system' | 'alert' | 'admin';

export interface ActivityFeedItemProps {
  type: ActivityType;
  description: string;
  timestamp: Date | string;
  onClick?: () => void;
  isNew?: boolean;
}

const activityConfig = {
  user: {
    icon: UserPlus,
    color: 'text-success',
    bgColor: 'bg-success/10',
  },
  chat: {
    icon: MessageSquare,
    color: 'text-primary',
    bgColor: 'bg-primary/10',
  },
  system: {
    icon: Settings,
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
  },
  alert: {
    icon: AlertTriangle,
    color: 'text-warning',
    bgColor: 'bg-warning/10',
  },
  admin: {
    icon: User,
    color: 'text-info',
    bgColor: 'bg-info/10',
  },
};

export function ActivityFeedItem({
  type,
  description,
  timestamp,
  onClick,
  isNew = false,
}: ActivityFeedItemProps) {
  const config = activityConfig[type];
  const Icon = config.icon;

  const formattedTime =
    timestamp instanceof Date
      ? formatDistanceToNow(timestamp, { addSuffix: true })
      : timestamp;

  return (
    <div
      onClick={onClick}
      className={cn(
        'flex items-center justify-between py-3 px-2 -mx-2 rounded-lg transition-all duration-150',
        'border-b border-gray-100 last:border-0',
        onClick && 'cursor-pointer hover:bg-gray-50',
        isNew && 'animate-[fadeIn_300ms_ease-out] bg-blue-50/50'
      )}
    >
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <div className={cn('h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0', config.bgColor)}>
          <Icon className={cn('h-4 w-4', config.color)} />
        </div>
        <p className="text-sm text-gray-700 truncate">{description}</p>
      </div>
      <span className="text-xs text-gray-500 ml-3 flex-shrink-0">{formattedTime}</span>
    </div>
  );
}

// Pulse animation for new items (add to index.css if not using Tailwind's built-in)
export function ActivityFeed({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
        <button className="text-sm text-primary hover:text-primary-hover font-medium transition-colors">
          View All →
        </button>
      </div>
      <div className="space-y-0">{children}</div>
    </div>
  );
}
