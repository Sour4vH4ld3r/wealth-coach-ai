import { Search, Bell, User, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface HeaderProps {
  sidebarCollapsed: boolean;
}

export function Header({ sidebarCollapsed }: HeaderProps) {
  return (
    <header
      className={cn(
        'fixed top-0 right-0 z-30 h-16 bg-white border-b border-gray-200 shadow-sm transition-all duration-250',
        sidebarCollapsed ? 'left-[60px]' : 'left-[240px]'
      )}
    >
      <div className="flex h-full items-center justify-between px-6">
        {/* Left: Brand name on mobile, search on desktop */}
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold text-gray-900 md:hidden">
            WealthWarriors Admin
          </h2>

          {/* Global Search */}
          <div className="hidden md:flex items-center relative">
            <Search className="absolute left-3 h-4 w-4 text-gray-400" />
            <input
              type="search"
              placeholder="Search users, content..."
              className="w-[300px] pl-10 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-150 hover:border-gray-300"
            />
            <kbd className="absolute right-3 px-2 py-0.5 text-xs text-gray-400 border border-gray-200 rounded">
              ⌘K
            </kbd>
          </div>
        </div>

        {/* Right: Notifications and Profile */}
        <div className="flex items-center gap-4">
          {/* Search Icon (Mobile) */}
          <button
            className="md:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Search"
          >
            <Search className="h-5 w-5 text-gray-600" />
          </button>

          {/* Notifications */}
          <button
            className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5 text-gray-600" />
            <span className="absolute top-1 right-1 h-2 w-2 bg-danger rounded-full"></span>
          </button>

          {/* Profile Dropdown */}
          <button className="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 rounded-lg transition-colors">
            <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-white text-sm font-medium">
              AD
            </div>
            <span className="hidden md:block text-sm font-medium text-gray-700">
              Admin User
            </span>
            <ChevronDown className="hidden md:block h-4 w-4 text-gray-400" />
          </button>
        </div>
      </div>
    </header>
  );
}
