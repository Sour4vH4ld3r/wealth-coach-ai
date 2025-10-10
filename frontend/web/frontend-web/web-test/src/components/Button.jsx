import React from 'react';
import { cn } from '../lib/utils';

const Button = React.forwardRef(({
  className,
  variant = 'default',
  size = 'default',
  children,
  disabled,
  ...props
}, ref) => {
  const baseStyles = 'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    default: 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl focus:ring-blue-500',
    secondary: 'bg-white bg-opacity-10 hover:bg-opacity-20 text-white border border-white border-opacity-30 backdrop-blur-sm hover:border-opacity-50',
    outline: 'border-2 border-blue-500 text-blue-400 hover:bg-blue-500 hover:bg-opacity-10 hover:border-blue-400 backdrop-blur-sm',
    ghost: 'hover:bg-white hover:bg-opacity-10 text-white hover:text-opacity-90 backdrop-blur-sm',
    danger: 'bg-red-600 hover:bg-red-700 text-white shadow-lg hover:shadow-xl focus:ring-red-500',
  };

  const sizes = {
    default: 'h-11 px-6 py-2 text-base',
    sm: 'h-9 px-4 text-sm',
    lg: 'h-12 px-8 text-lg',
    icon: 'h-10 w-10',
  };

  return (
    <button
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        className
      )}
      ref={ref}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
});

Button.displayName = 'Button';

export default Button;
