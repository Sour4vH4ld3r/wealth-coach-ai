import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { cn } from '@/lib/utils';

export function AdminLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar isCollapsed={sidebarCollapsed} onToggle={toggleSidebar} />

      {/* Header */}
      <Header sidebarCollapsed={sidebarCollapsed} />

      {/* Main Content Area */}
      <main
        className={cn(
          'pt-16 min-h-screen transition-all duration-250',
          sidebarCollapsed ? 'ml-[60px]' : 'ml-[240px]'
        )}
      >
        <div className="p-6">
          {/* Breadcrumbs can go here */}

          {/* Page Content */}
          <Outlet />
        </div>
      </main>
    </div>
  );
}
