"use client";

import React, { useState, useEffect, Suspense, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { useOptimizedScheduledTasks } from '@/hooks/useOptimizedScheduledTasks';
import SchedulerStatusBar from '@/components/Scheduled/SchedulerStatusBar';
import { ScheduledTask } from '@/types/data';

// 懒加载重型组件
const TaskManagement = dynamic(() => import('@/components/Scheduled/TaskManagement'), {
  loading: () => <ComponentSkeleton title="任务管理" />,
  ssr: false
});

const TrendViewer = dynamic(() => import('@/components/Scheduled/TrendViewer'), {
  loading: () => <ComponentSkeleton title="趋势分析" />,
  ssr: false
});

const TaskConfiguration = dynamic(() => import('@/components/Scheduled/TaskConfiguration'), {
  loading: () => <ComponentSkeleton title="任务配置" />,
  ssr: false
});

const AnalysisResultViewer = dynamic(() => import('@/components/Scheduled/AnalysisResultViewer'), {
  loading: () => <ComponentSkeleton title="AI分析结果" />,
  ssr: false
});

// 组件骨架屏
function ComponentSkeleton({ title }: { title: string }) {
  return (
    <div className="animate-pulse">
      <div className="mb-6">
        <div className="h-8 bg-gray-700 rounded-lg w-48 mb-2"></div>
        <div className="h-4 bg-gray-700 rounded-lg w-96"></div>
      </div>
      
      <div className="grid gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="p-6 bg-gray-800/30 rounded-lg border border-gray-700/50">
            <div className="flex justify-between items-center mb-4">
              <div className="h-6 bg-gray-600 rounded w-1/3"></div>
              <div className="flex gap-2">
                <div className="h-8 bg-gray-600 rounded w-16"></div>
                <div className="h-8 bg-gray-600 rounded w-16"></div>
              </div>
            </div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-700 rounded w-full"></div>
              <div className="h-4 bg-gray-700 rounded w-2/3"></div>
              <div className="h-4 bg-gray-700 rounded w-1/2"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ScheduledDashboard() {
  const [activeTab, setActiveTab] = useState<'tasks' | 'trends' | 'config' | 'analysis'>('tasks');
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  // 使用优化的定时任务Hook
  const {
    tasks,
    loading,
    error,
    userStats,
    schedulerStatus,
    wsConnected,
    notifications,
    createTask,
    updateTask,
    deleteTask,
    pauseTask,
    resumeTask,
    triggerTask,
    refreshData,
    clearError,
    clearNotifications,
  } = useOptimizedScheduledTasks({
    userId: 'default_user',
    autoRefresh: true,
    refreshInterval: 30000,
    enableWebSocket: true,
  });

  // 处理错误显示
  useEffect(() => {
    if (error) {
      console.error('Scheduled tasks error:', error);
    }
  }, [error]);

  // 标签页配置
  const tabs = [
    { id: 'tasks' as const, label: '任务管理', icon: '📋' },
    { id: 'trends' as const, label: '趋势分析', icon: '📈' },
    { id: 'analysis' as const, label: 'AI分析结果', icon: '🧠' },
    { id: 'config' as const, label: '新建任务', icon: '⚙️' },
  ];

  // 使用useMemo优化标签页内容渲染
  const renderActiveTabContent = useMemo(() => {
    switch (activeTab) {
      case 'tasks':
        return (
          <Suspense fallback={<ComponentSkeleton title="任务管理" />}>
            <TaskManagement
              tasks={tasks}
              loading={loading}
              onSelectTask={setSelectedTaskId}
              selectedTaskId={selectedTaskId}
              onCreateTask={createTask}
              onUpdateTask={updateTask}
              onDeleteTask={deleteTask}
              onPauseTask={pauseTask}
              onResumeTask={resumeTask}
              onTriggerTask={triggerTask}
              onRefresh={refreshData}
            />
          </Suspense>
        );
      case 'trends':
        return (
          <Suspense fallback={<ComponentSkeleton title="趋势分析" />}>
            <TrendViewer
              tasks={tasks}
              selectedTaskId={selectedTaskId}
              onSelectTask={setSelectedTaskId}
            />
          </Suspense>
        );
      case 'analysis':
        return (
          <Suspense fallback={<ComponentSkeleton title="AI分析结果" />}>
            <AnalysisResultViewer
              tasks={tasks}
              selectedTaskId={selectedTaskId}
              onSelectTask={setSelectedTaskId}
              onRefresh={refreshData}
            />
          </Suspense>
        );
      case 'config':
        return (
          <Suspense fallback={<ComponentSkeleton title="任务配置" />}>
            <TaskConfiguration
              onTaskCreated={(task: ScheduledTask) => {
                setActiveTab('tasks');
                refreshData();
              }}
              onCreateTask={createTask}
            />
          </Suspense>
        );
      default:
        return null;
    }
  }, [activeTab, tasks, loading, selectedTaskId, createTask, updateTask, deleteTask, pauseTask, resumeTask, triggerTask, refreshData]);

  return (
    <div className="container mx-auto px-4 lg:px-0 max-w-7xl">
      {/* 页面标题 */}
      <div className="mb-8">
        <h1 className="text-3xl lg:text-4xl font-bold text-white mb-4">
          📊 定时研究仪表板
        </h1>
        <p className="text-gray-300 text-lg">
          自动化话题追踪，智能趋势分析，实时掌握动态变化
        </p>
      </div>

      {/* 调度器状态栏 */}
      <SchedulerStatusBar 
        schedulerStatus={schedulerStatus}
        userStats={userStats}
        wsConnected={wsConnected}
        notifications={notifications}
        onClearNotifications={clearNotifications}
      />

      {/* 错误和提示信息 */}
      {error && (
        <div className={`mb-6 p-4 rounded-lg border ${
          error?.includes('无法连接到服务器') || error?.includes('WebSocket') 
            ? 'bg-yellow-500/20 border-yellow-500/30' 
            : 'bg-red-500/20 border-red-500/30'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className={
                error?.includes('无法连接到服务器') || error?.includes('WebSocket')
                  ? 'text-yellow-400' 
                  : 'text-red-400'
              }>
                {error?.includes('无法连接到服务器') || error?.includes('WebSocket') ? '🔌' : '⚠️'}
              </span>
              <div>
                <span className={
                  error?.includes('无法连接到服务器') || error?.includes('WebSocket')
                    ? 'text-yellow-300' 
                    : 'text-red-300'
                }>
                  {error}
                </span>
                {(error?.includes('无法连接到服务器') || error?.includes('WebSocket')) && (
                  <div className="text-xs text-yellow-200 mt-1">
                    💡 提示：请先启动后端服务，运行命令：<code className="bg-gray-800 px-1 rounded">python -m uvicorn backend.server.server:app --reload</code>
                  </div>
                )}
              </div>
            </div>
            <button
              onClick={clearError}
              className="text-gray-400 hover:text-gray-300 transition-colors ml-4"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* 未连接后端时的友好提示 */}
      {!wsConnected && !error && (
        <div className="mb-6 p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
          <div className="flex items-center gap-3">
            <span className="text-blue-400">💡</span>
            <div>
              <span className="text-blue-300">
                定时研究功能需要后端服务支持
              </span>
              <div className="text-xs text-blue-200 mt-1">
                启动后端：<code className="bg-gray-800 px-1 rounded">python -m uvicorn backend.server.server:app --reload</code>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 标签页导航 */}
      <div className="mb-8">
        <div className="flex flex-wrap gap-2 p-1 bg-gray-800/50 rounded-lg border border-gray-700/50">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-2 px-4 py-3 rounded-md font-medium transition-all duration-200
                ${activeTab === tab.id
                  ? 'bg-teal-600 text-white shadow-lg transform scale-105'
                  : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
                }
              `}
            >
              <span className="text-lg">{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 标签页内容 */}
      <div className="mb-8">
        {renderActiveTabContent}
      </div>

      {/* 加载状态 */}
      {loading && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 flex items-center gap-4">
            <div className="animate-spin w-6 h-6 border-2 border-teal-500 border-t-transparent rounded-full"></div>
            <span className="text-white">处理中...</span>
          </div>
        </div>
      )}
    </div>
  );
}
