import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

interface MetricState {
  orders: number;
  revenue: number;
}

interface OutcomeVisualizationProps {
  beforeState: MetricState;
  afterState: MetricState;
  executionLogs: string[];
  simulationId: string;
}

const TypewriterLog: React.FC<{ logs: string[] }> = ({ logs }) => {
  const [displayedLogs, setDisplayedLogs] = useState<string[]>([]);
  const [currentLogIndex, setCurrentLogIndex] = useState(0);
  const [currentCharIndex, setCurrentCharIndex] = useState(0);

  useEffect(() => {
    if (currentLogIndex < logs.length) {
      const currentLog = logs[currentLogIndex];
      const timer = setTimeout(() => {
        if (currentCharIndex < currentLog.length) {
          setCurrentCharIndex((prev) => prev + 1);
        } else {
          setDisplayedLogs((prev) => [...prev, currentLog]);
          setCurrentLogIndex((prev) => prev + 1);
          setCurrentCharIndex(0);
        }
      }, 30); // Typing speed

      return () => clearTimeout(timer);
    }
  }, [currentLogIndex, currentCharIndex, logs]);

  return (
    <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm h-48 overflow-y-auto">
      {displayedLogs.map((log, index) => (
        <div key={index} className="mb-1">{`> ${log}`}</div>
      ))}
      {currentLogIndex < logs.length && (
        <div>{`> ${logs[currentLogIndex].substring(0, currentCharIndex)}`}</div>
      )}
    </div>
  );
};

const OutcomeVisualization: React.FC<OutcomeVisualizationProps> = ({
  beforeState,
  afterState,
  executionLogs,
  simulationId
}) => {
  const revenueImprovement = ((afterState.revenue - beforeState.revenue) / beforeState.revenue) * 100;
  
  const chartData = [
    {
      name: 'Orders',
      Before: beforeState.orders,
      After: afterState.orders,
    },
    {
      name: 'Revenue',
      Before: beforeState.revenue,
      After: afterState.revenue,
    }
  ];

  return (
    <div className="flex flex-col gap-6 p-6 w-full bg-white dark:bg-gray-800 rounded-xl shadow-lg">
      
      {/* Breadcrumb */}
      <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 overflow-x-auto whitespace-nowrap">
        <span>Input</span>
        <span className="mx-2">→</span>
        <span>Insights</span>
        <span className="mx-2">→</span>
        <span>Impact</span>
        <span className="mx-2">→</span>
        <span>Action</span>
        <span className="mx-2">→</span>
        <span className="font-semibold text-blue-600 dark:text-blue-400">Simulation ({simulationId})</span>
        <span className="mx-2">→</span>
        <span>Result</span>
      </div>

      {/* Projected Impact Banner */}
      <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4 flex justify-between items-center">
        <div>
          <h3 className="text-lg font-bold text-blue-800 dark:text-blue-300">Projected Impact</h3>
          <p className="text-sm text-blue-600 dark:text-blue-400">Simulation indicates significant improvements.</p>
        </div>
        <div className="text-2xl font-extrabold text-green-600 dark:text-green-400">
          +{revenueImprovement.toFixed(1)}% Revenue
        </div>
      </div>

      {/* Split Panel */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Before State */}
        <div className="border-2 border-red-400 dark:border-red-600 rounded-xl p-6 bg-red-50 dark:bg-red-900/10">
          <h3 className="text-xl font-bold text-red-800 dark:text-red-400 mb-4">Before State</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
              <div className="text-sm text-gray-500 dark:text-gray-400">Orders</div>
              <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">{beforeState.orders.toLocaleString()}</div>
            </div>
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
              <div className="text-sm text-gray-500 dark:text-gray-400">Revenue</div>
              <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">${beforeState.revenue.toLocaleString()}</div>
            </div>
          </div>
        </div>

        {/* After State */}
        <div className="border-2 border-green-400 dark:border-green-600 rounded-xl p-6 bg-green-50 dark:bg-green-900/10">
          <h3 className="text-xl font-bold text-green-800 dark:text-green-400 mb-4">After State</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
              <div className="text-sm text-gray-500 dark:text-gray-400">Orders</div>
              <div className="flex items-center">
                <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">{afterState.orders.toLocaleString()}</div>
                <span className="ml-2 text-green-500">↑</span>
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
              <div className="text-sm text-gray-500 dark:text-gray-400">Revenue</div>
              <div className="flex items-center">
                <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">${afterState.revenue.toLocaleString()}</div>
                <span className="ml-2 text-green-500">↑</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart */}
        <div className="bg-white dark:bg-gray-800 p-4 border border-gray-200 dark:border-gray-700 rounded-xl h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis dataKey="name" />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              <Bar dataKey="Before" fill="#ef4444" radius={[4, 4, 0, 0]} />
              <Bar dataKey="After" fill="#22c55e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Execution Log */}
        <div className="flex flex-col">
          <h4 className="text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2">Simulation Execution Log</h4>
          <TypewriterLog logs={executionLogs} />
        </div>
      </div>

    </div>
  );
};

export default OutcomeVisualization;
