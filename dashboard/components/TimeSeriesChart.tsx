'use client';

import { useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart } from 'recharts';
import { TimeSeriesData } from '@/types';
import { formatCurrency, formatDate } from '@/lib/utils';

interface TimeSeriesChartProps {
  data: TimeSeriesData[];
}

export default function TimeSeriesChart({ data }: TimeSeriesChartProps) {
  const [view, setView] = useState<'daily' | 'weekly'>('daily');

  const processedData = view === 'weekly' ? aggregateWeekly(data) : data;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">Transaction Trends</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setView('daily')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              view === 'daily'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Daily
          </button>
          <button
            onClick={() => setView('weekly')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              view === 'weekly'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Weekly
          </button>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={processedData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tickFormatter={(value) => {
              const date = new Date(value);
              return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }}
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            yAxisId="left"
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <Tooltip
            content={<CustomTooltip />}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '12px',
            }}
          />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          <Bar
            yAxisId="right"
            dataKey="transaction_volume"
            fill="#93c5fd"
            name="Transaction Volume"
            opacity={0.8}
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="transaction_amount"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ fill: '#3b82f6', r: 4 }}
            name="Transaction Amount"
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="settled_amount"
            stroke="#10b981"
            strokeWidth={2}
            dot={{ fill: '#10b981', r: 4 }}
            name="Settled Amount"
          />
        </ComposedChart>
      </ResponsiveContainer>

      <div className="mt-4 flex items-center justify-center gap-8 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          <span>Transaction Amount</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span>Settled Amount</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-300 rounded"></div>
          <span>Volume (Count)</span>
        </div>
      </div>
    </div>
  );
}

function aggregateWeekly(data: TimeSeriesData[]): TimeSeriesData[] {
  const weekMap = new Map<string, TimeSeriesData>();

  data.forEach(item => {
    const date = new Date(item.date);
    const weekStart = new Date(date);
    weekStart.setDate(date.getDate() - date.getDay());
    const weekKey = weekStart.toISOString().split('T')[0];

    const existing = weekMap.get(weekKey);
    if (existing) {
      existing.transaction_volume += item.transaction_volume;
      existing.transaction_amount += item.transaction_amount;
      existing.settled_amount += item.settled_amount;
    } else {
      weekMap.set(weekKey, { ...item, date: weekKey });
    }
  });

  return Array.from(weekMap.values()).sort((a, b) => a.date.localeCompare(b.date));
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
      <p className="font-semibold text-gray-900 mb-2">{formatDate(label)}</p>
      {payload.map((entry: any, index: number) => (
        <p key={index} className="text-sm" style={{ color: entry.color }}>
          {entry.name}: {
            entry.name === 'Transaction Volume'
              ? entry.value
              : formatCurrency(entry.value)
          }
        </p>
      ))}
    </div>
  );
}
