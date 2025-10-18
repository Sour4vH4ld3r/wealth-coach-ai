import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

// Sample data - replace with real API data
const generateData = () => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  return days.map((day) => ({
    day,
    sessions: Math.floor(Math.random() * 150) + 50,
    messages: Math.floor(Math.random() * 500) + 200,
  }));
};

export function ChatActivityChart() {
  const data = generateData();

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 h-80">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Chat Activity</h3>
        <select className="text-sm border border-gray-200 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary">
          <option>Last 7 days</option>
          <option>Last 30 days</option>
          <option>Last 90 days</option>
        </select>
      </div>

      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
          <XAxis
            dataKey="day"
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickLine={false}
            axisLine={{ stroke: '#e5e7eb' }}
          />
          <YAxis
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickLine={false}
            axisLine={{ stroke: '#e5e7eb' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
            labelStyle={{ color: '#374151', fontWeight: 600 }}
            cursor={{ fill: 'rgba(37, 99, 235, 0.05)' }}
          />
          <Legend
            wrapperStyle={{ paddingTop: '10px' }}
            iconType="circle"
          />
          <Bar
            dataKey="sessions"
            fill="#2563eb"
            radius={[4, 4, 0, 0]}
            name="Chat Sessions"
            maxBarSize={60}
          />
          <Bar
            dataKey="messages"
            fill="#10b981"
            radius={[4, 4, 0, 0]}
            name="Total Messages"
            maxBarSize={60}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
