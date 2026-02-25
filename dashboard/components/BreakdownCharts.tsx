'use client';

import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Insight } from '@/types';
import { formatCurrency } from '@/lib/utils';

interface BreakdownChartsProps {
  insights: Insight;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function BreakdownCharts({ insights }: BreakdownChartsProps) {
  const providerData = insights.provider_analysis
    .sort((a, b) => b.discrepancy_amount - a.discrepancy_amount)
    .slice(0, 5);

  const methodData = insights.method_analysis.map(item => ({
    name: item.method.replace('_', ' ').toUpperCase(),
    value: item.discrepancy_rate,
    amount: item.discrepancy_amount,
  }));

  const countryData = insights.country_analysis.map(item => ({
    country: item.country,
    volume: item.total_volume,
    discrepancy: item.discrepancy_amount,
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Provider Breakdown */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Discrepancy by Provider</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={providerData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              type="number"
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              style={{ fontSize: '11px' }}
            />
            <YAxis
              type="category"
              dataKey="provider"
              width={80}
              style={{ fontSize: '11px' }}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload.length) return null;
                return (
                  <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                    <p className="font-semibold text-gray-900">{payload[0].payload.provider}</p>
                    <p className="text-sm text-gray-600">
                      Discrepancy: {formatCurrency(payload[0].value as number)}
                    </p>
                    <p className="text-sm text-gray-600">
                      Rate: {payload[0].payload.discrepancy_rate.toFixed(2)}%
                    </p>
                  </div>
                );
              }}
            />
            <Bar dataKey="discrepancy_amount" fill="#3b82f6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Payment Method Breakdown */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Discrepancy by Payment Method</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={methodData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {methodData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload.length) return null;
                return (
                  <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                    <p className="font-semibold text-gray-900">{payload[0].name}</p>
                    <p className="text-sm text-gray-600">
                      Rate: {payload[0].value?.toFixed(2)}%
                    </p>
                    <p className="text-sm text-gray-600">
                      Amount: {formatCurrency(payload[0].payload.amount)}
                    </p>
                  </div>
                );
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Country Breakdown */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Volume vs Discrepancy by Country</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={countryData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="country"
              style={{ fontSize: '11px' }}
            />
            <YAxis
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              style={{ fontSize: '11px' }}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload.length) return null;
                return (
                  <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                    <p className="font-semibold text-gray-900">{payload[0].payload.country}</p>
                    <p className="text-sm text-blue-600">
                      Volume: {formatCurrency(payload[0].value as number)}
                    </p>
                    <p className="text-sm text-red-600">
                      Discrepancy: {formatCurrency(payload[1].value as number)}
                    </p>
                  </div>
                );
              }}
            />
            <Legend />
            <Bar dataKey="volume" fill="#3b82f6" name="Transaction Volume" />
            <Bar dataKey="discrepancy" fill="#ef4444" name="Discrepancy" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
