import { TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface MetricCardProps {
  label: string;
  value: string | number;
  change?: {
    value: number;
    direction: 'up' | 'down';
    timeframe?: string;
  };
  icon?: React.ComponentType<{ className?: string }>;
  variant?: 'default' | 'featured' | 'alert';
  onClick?: () => void;
  loading?: boolean;
}

export function MetricCard({
  label,
  value,
  change,
  icon: Icon,
  variant = 'default',
  onClick,
  loading = false,
}: MetricCardProps) {
  const isPositive = change?.direction === 'up';
  const isClickable = !!onClick;

  return (
    <div
      onClick={onClick}
      className={cn(
        'bg-white rounded-lg shadow-sm border border-gray-200 p-5 transition-all duration-200',
        'hover:shadow-md',
        isClickable && 'cursor-pointer hover:-translate-y-0.5',
        variant === 'featured' && 'border-l-4 border-l-primary',
        variant === 'alert' && 'border-l-4 border-l-danger bg-red-50'
      )}
    >
      <div className="flex items-start justify-between mb-2">
        <p className="text-sm font-medium text-gray-600">{label}</p>
        {Icon && (
          <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
            <Icon className="h-4 w-4 text-primary" />
          </div>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">
          <div className="h-8 bg-gray-200 rounded animate-pulse" />
          <div className="h-4 bg-gray-100 rounded animate-pulse w-24" />
        </div>
      ) : (
        <>
          <p className="text-3xl font-bold text-gray-900 mb-2">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>

          {change && (
            <div className="flex items-center gap-1">
              {isPositive ? (
                <TrendingUp className="h-4 w-4 text-success" />
              ) : (
                <TrendingDown className="h-4 w-4 text-danger" />
              )}
              <span
                className={cn(
                  'text-sm font-medium',
                  isPositive ? 'text-success' : 'text-danger'
                )}
              >
                {isPositive ? '+' : ''}
                {change.value}%
              </span>
              {change.timeframe && (
                <span className="text-sm text-gray-500 ml-1">
                  {change.timeframe}
                </span>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
