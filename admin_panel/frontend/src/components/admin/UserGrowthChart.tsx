import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

// Sample data - replace with real API data
const generateData = () => {
  const data = [];
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 30);

  for (let i = 0; i < 30; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    data.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      newUsers: Math.floor(Math.random() * 100) + 50,
      totalUsers: 12000 + i * 15 + Math.floor(Math.random() * 50),
    });
  }
  return data;
};

export function UserGrowthChart() {
  const data = generateData();

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 h-80">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">User Growth</h3>
        <select className="text-sm border border-gray-200 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary">
          <option>Last 30 days</option>
          <option>Last 90 days</option>
          <option>Last year</option>
        </select>
      </div>

      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickLine={false}
            axisLine={{ stroke: '#e5e7eb' }}
          />
          <YAxis
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickLine={false}
            axisLine={{ stroke: '#e5e7eb' }}
            tickFormatter={(value) => value.toLocaleString()}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
            labelStyle={{ color: '#374151', fontWeight: 600 }}
          />
          <Legend
            wrapperStyle={{ paddingTop: '10px' }}
            iconType="circle"
          />
          <Line
            type="monotone"
            dataKey="newUsers"
            stroke="#10b981"
            strokeWidth={2}
            dot={{ fill: '#10b981', r: 3 }}
            activeDot={{ r: 5 }}
            name="New Users"
          />
          <Line
            type="monotone"
            dataKey="totalUsers"
            stroke="#2563eb"
            strokeWidth={2}
            dot={{ fill: '#2563eb', r: 3 }}
            activeDot={{ r: 5 }}
            name="Total Users"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
