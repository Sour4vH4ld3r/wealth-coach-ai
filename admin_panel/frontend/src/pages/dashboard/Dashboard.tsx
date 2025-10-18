import { Users, UserCheck, MessageSquare, Activity } from 'lucide-react';
import { MetricCard } from '@/components/admin/MetricCard';
import { ActivityFeed, ActivityFeedItem } from '@/components/admin/ActivityFeedItem';
import { UserGrowthChart } from '@/components/admin/UserGrowthChart';
import { ChatActivityChart } from '@/components/admin/ChatActivityChart';

export function Dashboard() {
  // Sample activity data - replace with real API data
  const activities = [
    {
      type: 'user' as const,
      description: 'New user registered: John Doe',
      timestamp: new Date(Date.now() - 2 * 60 * 1000), // 2 mins ago
      isNew: true,
    },
    {
      type: 'chat' as const,
      description: 'Chat session completed: Jane Smith',
      timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 mins ago
    },
    {
      type: 'alert' as const,
      description: 'High error rate detected in payment gateway',
      timestamp: new Date(Date.now() - 8 * 60 * 1000), // 8 mins ago
    },
    {
      type: 'user' as const,
      description: 'New user registered: Bob Anderson',
      timestamp: new Date(Date.now() - 12 * 60 * 1000), // 12 mins ago
    },
    {
      type: 'system' as const,
      description: 'Database backup completed successfully',
      timestamp: new Date(Date.now() - 15 * 60 * 1000), // 15 mins ago
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <MetricCard
          label="Total Users"
          value={12450}
          change={{ value: 12, direction: 'up', timeframe: 'from last month' }}
          icon={Users}
          variant="featured"
          onClick={() => console.log('Navigate to users')}
        />
        <MetricCard
          label="Active Users"
          value={342}
          change={{ value: 5, direction: 'up', timeframe: 'from yesterday' }}
          icon={UserCheck}
          onClick={() => console.log('Navigate to active users')}
        />
        <MetricCard
          label="Chat Sessions"
          value={1205}
          change={{ value: 8, direction: 'up', timeframe: 'this week' }}
          icon={MessageSquare}
          onClick={() => console.log('Navigate to chat')}
        />
        <MetricCard
          label="System Health"
          value="98%"
          change={{ value: 2, direction: 'up', timeframe: 'uptime' }}
          icon={Activity}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <UserGrowthChart />
        <ChatActivityChart />
      </div>

      {/* Activity Feed */}
      <ActivityFeed>
        {activities.map((activity, index) => (
          <ActivityFeedItem
            key={index}
            type={activity.type}
            description={activity.description}
            timestamp={activity.timestamp}
            isNew={activity.isNew}
            onClick={() => console.log('Activity clicked:', activity.description)}
          />
        ))}
      </ActivityFeed>
    </div>
  );
}
