import * as React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'link';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  children: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'medium', loading = false, disabled, children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-150 ease-out disabled:opacity-50 disabled:pointer-events-none';

    const variants = {
      primary: 'bg-primary text-white hover:bg-primary-hover hover:scale-[1.02] active:scale-[0.98]',
      secondary: 'border-2 border-gray-300 text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400',
      danger: 'bg-danger text-white hover:bg-red-600 hover:scale-[1.02] active:scale-[0.98]',
      ghost: 'text-gray-700 hover:bg-gray-100',
      link: 'text-primary underline-offset-4 hover:underline',
    };

    const sizes = {
      small: 'h-8 px-3 text-xs',
      medium: 'h-10 px-4 text-sm',
      large: 'h-12 px-6 text-base',
    };

    return (
      <button
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
