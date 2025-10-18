import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  MessageSquare,
  FileText,
  BarChart3,
  Settings,
  ChevronLeft
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
  { icon: Users, label: 'Users', path: '/users' },
  { icon: MessageSquare, label: 'Chat Monitor', path: '/chat' },
  { icon: FileText, label: 'Content', path: '/content' },
  { icon: BarChart3, label: 'Analytics', path: '/analytics' },
  { icon: Settings, label: 'Settings', path: '/settings' },
];

export function Sidebar({ isCollapsed, onToggle }: SidebarProps) {
  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen bg-white border-r border-gray-200 transition-all duration-250 ease-in-out',
        isCollapsed ? 'w-[60px]' : 'w-[240px]'
      )}
    >
      {/* Logo Area */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-gray-200">
        {!isCollapsed && (
          <h1 className="text-lg font-semibold text-gray-900">
            WealthWarriors
          </h1>
        )}
        {!isCollapsed && <span className="text-xs text-gray-500 font-medium">Admin</span>}
      </div>

      {/* Navigation Menu */}
      <nav className="flex flex-col gap-1 p-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-150',
                  'hover:bg-gray-50 hover:text-gray-900',
                  isActive
                    ? 'bg-blue-50 text-primary border-l-4 border-primary'
                    : 'text-gray-700',
                  isCollapsed && 'justify-center'
                )
              }
              title={isCollapsed ? item.label : undefined}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {!isCollapsed && <span>{item.label}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <div className="absolute bottom-4 left-0 right-0 px-2">
        <button
          onClick={onToggle}
          className={cn(
            'flex items-center gap-3 w-full px-3 py-2 rounded-md text-sm font-medium text-gray-700',
            'hover:bg-gray-50 transition-all duration-150',
            isCollapsed && 'justify-center'
          )}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <ChevronLeft
            className={cn(
              'h-5 w-5 transition-transform duration-250',
              isCollapsed && 'rotate-180'
            )}
          />
          {!isCollapsed && <span>Collapse</span>}
        </button>

        {/* Version Number */}
        {!isCollapsed && (
          <div className="mt-2 px-3 text-xs text-gray-400">
            v1.0.0
          </div>
        )}
      </div>
    </aside>
  );
}
