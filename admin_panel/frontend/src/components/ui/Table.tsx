import { cn } from '@/lib/utils';

export interface TableProps {
  children: React.ReactNode;
  className?: string;
}

export function Table({ children, className }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className={cn('w-full border-collapse', className)}>
        {children}
      </table>
    </div>
  );
}

export interface TableHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export function TableHeader({ children, className }: TableHeaderProps) {
  return (
    <thead className={cn('bg-gray-50 border-b border-gray-200', className)}>
      {children}
    </thead>
  );
}

export interface TableBodyProps {
  children: React.ReactNode;
  className?: string;
}

export function TableBody({ children, className }: TableBodyProps) {
  return <tbody className={className}>{children}</tbody>;
}

export interface TableRowProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export function TableRow({ children, className, onClick }: TableRowProps) {
  return (
    <tr
      onClick={onClick}
      className={cn(
        'border-b border-gray-100 last:border-0',
        onClick && 'cursor-pointer hover:bg-gray-50',
        className
      )}
    >
      {children}
    </tr>
  );
}

export interface TableHeadProps {
  children: React.ReactNode;
  className?: string;
  sortable?: boolean;
  onSort?: () => void;
}

export function TableHead({ children, className, sortable, onSort }: TableHeadProps) {
  return (
    <th
      onClick={sortable ? onSort : undefined}
      className={cn(
        'px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider',
        sortable && 'cursor-pointer hover:text-gray-900 select-none',
        className
      )}
    >
      {children}
    </th>
  );
}

export interface TableCellProps {
  children: React.ReactNode;
  className?: string;
}

export function TableCell({ children, className }: TableCellProps) {
  return (
    <td className={cn('px-4 py-3 text-sm text-gray-700', className)}>
      {children}
    </td>
  );
}
