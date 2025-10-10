import React from 'react';
import { cn } from '../lib/utils';

const Input = React.forwardRef(({
  className,
  type = 'text',
  error,
  ...props
}, ref) => {
  return (
    <input
      type={type}
      className={cn(
        'w-full h-11 px-4 py-2 rounded-lg',
        'bg-white bg-opacity-10 backdrop-blur-sm',
        'border border-white border-opacity-20',
        'text-white text-base',
        'placeholder-white placeholder-opacity-50',
        'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-opacity-15',
        'hover:border-opacity-30',
        'transition-all duration-200',
        'shadow-sm hover:shadow-md focus:shadow-lg',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        error && 'border-red-500 border-opacity-100 focus:ring-red-500',
        className
      )}
      ref={ref}
      {...props}
    />
  );
});

Input.displayName = 'Input';

export default Input;
