"use client";

import React, { useState, useEffect, Suspense } from 'react';
import dynamic from 'next/dynamic';
import { ScheduledTask, TrendData, ResearchHistoryRecord } from '@/types/data';
import { useTaskTrends, useTaskHistory } from '@/hooks/useScheduledTasks';

// 懒加载图表组件
const TrendChart = dynamic(() => import('./Charts/TrendChart'), {
  loading: () => <ChartSkeleton />,
  ssr: false
});

const KeywordTrendsChart = dynamic(() => import('./Charts/KeywordTrendsChart'), {
  loading: () => <ChartSkeleton />,
  ssr: false
});

const ActivityMonitor = dynamic(() => import('./Charts/ActivityMonitor'), {
  loading: () => <ChartSkeleton />,
  ssr: false
});

// 图表骨架屏
function ChartSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="p-6 bg-gray-800/30 rounded-lg border border-gray-700/50">
        <div className="h-6 bg-gray-600 rounded w-1/3 mb-4"></div>
        <div className="h-64 bg-gray-700 rounded"></div>
        <div className="flex justify-between mt-4">
          <div className="h-4 bg-gray-600 rounded w-16"></div>
          <div className="h-4 bg-gray-600 rounded w-16"></div>
        </div>
      </div>
    </div>
  );
}

interface TrendViewerProps {
  tasks: ScheduledTask[];
  selectedTaskId: string | null;
  onSelectTask: (taskId: string | null) => void;
}

export default function TrendViewer({
  tasks,
  selectedTaskId,
  onSelectTask,
}: TrendViewerProps) {
  const [selectedMetric, setSelectedMetric] = useState<'trend_score' | 'activity_level' | 'change_magnitude'>('trend_score');
  const [activeTab, setActiveTab] = useState<'overview' | 'trends' | 'keywords' | 'activity'>('overview');

  // 获取选中任务的趋势数据
  const { trends, loading: trendsLoading } = useTaskTrends(selectedTaskId || '', 30);
  const { history, loading: historyLoading } = useTaskHistory(selectedTaskId || '');

  // 选中的任务
  const selectedTask = selectedTaskId ? tasks.find(task => task.id === selectedTaskId) : null;

  // 获取所有任务的最近执行记录
  const allRecentExecutions = React.useMemo(() => {
    // 这里应该从所有任务的历史记录中获取，暂时使用当前任务的历史
    return history.slice(0, 20);
  }, [history]);

  // 标签页配置
  const tabs = [
    { id: 'overview', label: '总览', icon: '📊', description: '整体趋势概览' },
    { id: 'trends', label: '趋势图表', icon: '📈', description: '详细趋势分析' },
    { id: 'keywords', label: '关键词热度', icon: '🔍', description: '关键词变化分析' },
    { id: 'activity', label: '实时活动', icon: '⚡', description: '任务执行监控' },
  ];

  return (
    <div className="space-y-6">
      {/* 标题和任务选择 */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">趋势分析</h2>
          <p className="text-gray-300">
            分析话题发展趋势，追踪关键词热度变化和异常检测
          </p>
        </div>
        
        {/* 任务选择器 */}
        <div className="flex flex-col sm:flex-row gap-4">
          <select
            value={selectedTaskId || ''}
            onChange={(e) => onSelectTask(e.target.value || null)}
            className="px-4 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
          >
            <option value="">选择任务进行分析</option>
            {tasks.map((task) => (
              <option key={task.id} value={task.id}>
                {task.topic} ({task.total_runs} 次执行)
              </option>
            ))}
          </select>
        </div>
      </div>

      {!selectedTaskId ? (
        /* 未选择任务的状态 */
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 任务概览 */}
          <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6 backdrop-blur-sm">
            <h3 className="text-lg font-semibold text-white mb-4">任务概览</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{tasks.length}</div>
                  <div className="text-sm text-gray-400">总任务数</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">
                    {tasks.filter(t => t.is_active).length}
                  </div>
                  <div className="text-sm text-gray-400">活跃任务</div>
                </div>
              </div>
              
              <div className="space-y-2">
                {tasks.slice(0, 3).map((task) => (
                  <div
                    key={task.id}
                    onClick={() => onSelectTask(task.id)}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-700/30 cursor-pointer transition-all"
                  >
                    <span className="font-medium text-white truncate">{task.topic}</span>
                    <span className="text-sm text-gray-400">{task.total_runs} 次</span>
                  </div>
                ))}
                {tasks.length > 3 && (
                  <div className="text-center text-sm text-gray-400 pt-2">
                    还有 {tasks.length - 3} 个任务...
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 系统活动 */}
          <ActivityMonitor
            tasks={tasks}
            recentExecutions={allRecentExecutions}
            onTaskSelect={onSelectTask}
          />
        </div>
      ) : (
        /* 选中任务的分析界面 */
        <div className="space-y-6">
          {/* 任务信息卡片 */}
          {selectedTask && (
            <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6 backdrop-blur-sm">
              <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">{selectedTask.topic}</h3>
                  <div className="flex flex-wrap gap-4 text-sm text-gray-400">
                    <span>🔄 {selectedTask.interval_hours}小时间隔</span>
                    <span>📊 {selectedTask.success_runs}/{selectedTask.total_runs} 成功</span>
                    <span>📈 {selectedTask.analysis_depth} 分析</span>
                    <span className={selectedTask.is_active ? 'text-green-400' : 'text-red-400'}>
                      {selectedTask.is_active ? '✅ 活跃' : '⏸️ 暂停'}
                    </span>
                  </div>
                </div>
                <div className="flex gap-2">
                  {selectedTask.keywords.slice(0, 3).map((keyword, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-teal-500/20 text-teal-300 text-xs rounded-full"
                    >
                      {keyword}
                    </span>
                  ))}
                  {selectedTask.keywords.length > 3 && (
                    <span className="px-2 py-1 bg-gray-500/20 text-gray-400 text-xs rounded-full">
                      +{selectedTask.keywords.length - 3}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* 标签页导航 */}
          <div className="flex flex-wrap gap-2 p-1 bg-gray-800/50 rounded-lg border border-gray-700/50">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`
                  flex items-center gap-2 px-4 py-3 rounded-md font-medium transition-all duration-200
                  ${activeTab === tab.id
                    ? 'bg-teal-600 text-white shadow-lg transform scale-105'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
                  }
                `}
                title={tab.description}
              >
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>

          {/* 标签页内容 */}
          <div>
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <TrendChart
                  trendData={trends}
                  selectedMetric={selectedMetric}
                  onMetricChange={setSelectedMetric}
                />
                <KeywordTrendsChart
                  trendData={trends}
                  maxKeywords={8}
                />
              </div>
            )}

            {activeTab === 'trends' && (
              <TrendChart
                trendData={trends}
                selectedMetric={selectedMetric}
                onMetricChange={setSelectedMetric}
              />
            )}

            {activeTab === 'keywords' && (
              <KeywordTrendsChart
                trendData={trends}
                maxKeywords={15}
              />
            )}

            {activeTab === 'activity' && (
              <ActivityMonitor
                tasks={tasks}
                recentExecutions={allRecentExecutions}
                onTaskSelect={onSelectTask}
              />
            )}
          </div>

          {/* 数据加载状态 */}
          {(trendsLoading || historyLoading) && (
            <div className="flex items-center justify-center py-8">
              <div className="flex items-center gap-3 text-gray-400">
                <div className="animate-spin w-6 h-6 border-2 border-teal-500 border-t-transparent rounded-full"></div>
                <span>加载趋势数据中...</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
