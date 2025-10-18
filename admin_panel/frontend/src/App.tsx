import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AdminLayout } from '@/components/layouts/AdminLayout';
import { Dashboard } from '@/pages/dashboard/Dashboard';
import { Users } from '@/pages/users/Users';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AdminLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="users" element={<Users />} />
          <Route path="chat" element={<PlaceholderPage title="Chat Monitor" />} />
          <Route path="content" element={<PlaceholderPage title="Content Management" />} />
          <Route path="analytics" element={<PlaceholderPage title="Analytics" />} />
          <Route path="settings" element={<PlaceholderPage title="Settings" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

// Placeholder component for routes not yet implemented
function PlaceholderPage({ title }: { title: string }) {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">{title}</h1>
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <p className="text-gray-600">{title} interface coming soon...</p>
      </div>
    </div>
  );
}

export default App;
