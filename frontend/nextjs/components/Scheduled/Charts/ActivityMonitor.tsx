"use client";

import React, { useState, useEffect } from 'react';
import { ScheduledTask, ResearchHistoryRecord } from '@/types/data';

interface ActivityMonitorProps {
  tasks: ScheduledTask[];
  recentExecutions: ResearchHistoryRecord[];
  onTaskSelect?: (taskId: string) => void;
}

export default function ActivityMonitor({
  tasks,
  recentExecutions,
  onTaskSelect,
}: ActivityMonitorProps) {
  const [filter, setFilter] = useState<'all' | 'today' | 'week'>('today');
  const [selectedCategory, setSelectedCategory] = useState<'executions' | 'tasks'>('executions');

  // 过滤最近执行记录
  const filteredExecutions = React.useMemo(() => {
    if (!recentExecutions) return [];
    
    const now = new Date();
    const startDate = new Date();
    
    switch (filter) {
      case 'today':
        startDate.setHours(0, 0, 0, 0);
        break;
      case 'week':
        startDate.setDate(now.getDate() - 7);
        break;
      default:
        return recentExecutions.slice(0, 50); // 最近50条
    }
    
    return recentExecutions.filter(execution => {
      if (!execution.executed_at) return false;
      const executionDate = new Date(execution.executed_at);
      return executionDate >= startDate;
    });
  }, [recentExecutions, filter]);

  // 活跃任务统计
  const activeTasksStats = React.useMemo(() => {
    const activeTasks = tasks.filter(task => task.is_active);
    const now = new Date();
    
    const comingSoon = activeTasks.filter(task => {
      if (!task.next_run) return false;
      const nextRun = new Date(task.next_run);
      const timeDiff = nextRun.getTime() - now.getTime();
      return timeDiff > 0 && timeDiff <= 60 * 60 * 1000; // 1小时内
    });

    const overdue = activeTasks.filter(task => {
      if (!task.next_run) return false;
      const nextRun = new Date(task.next_run);
      return nextRun.getTime() < now.getTime();
    });

    return {
      total: activeTasks.length,
      comingSoon: comingSoon.length,
      overdue: overdue.length,
      normal: activeTasks.length - comingSoon.length - overdue.length
    };
  }, [tasks]);

  // 执行状态统计
  const executionStats = React.useMemo(() => {
    const successful = filteredExecutions.filter(e => e.status === 'success').length;
    const failed = filteredExecutions.filter(e => e.status === 'failed').length;
    const partial = filteredExecutions.filter(e => e.status === 'partial').length;
    
    return {
      total: filteredExecutions.length,
      successful,
      failed,
      partial,
      successRate: filteredExecutions.length > 0 ? (successful / filteredExecutions.length) * 100 : 0
    };
  }, [filteredExecutions]);

  // 格式化时间
  const formatTime = (timeString?: string) => {
    if (!timeString) return '未知';
    const date = new Date(timeString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;
    return date.toLocaleDateString('zh-CN');
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-400 bg-green-500/20';
      case 'failed': return 'text-red-400 bg-red-500/20';
      case 'partial': return 'text-yellow-400 bg-yellow-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  return (
    <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 backdrop-blur-sm">
      {/* 标题和控制 */}
      <div className="p-6 border-b border-gray-700/50">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">实时活动监控</h3>
            <p className="text-sm text-gray-400">
              监控任务执行状态和系统活动
            </p>
          </div>
          
          <div className="flex gap-2">
            {/* 分类选择 */}
            <div className="flex gap-1 bg-gray-700/50 rounded-lg p-1">
              <button
                onClick={() => setSelectedCategory('executions')}
                className={`
                  px-3 py-1 rounded-md text-sm font-medium transition-all duration-200
                  ${selectedCategory === 'executions'
                    ? 'bg-teal-600 text-white'
                    : 'text-gray-300 hover:text-white'
                  }
                `}
              >
                执行记录
              </button>
              <button
                onClick={() => setSelectedCategory('tasks')}
                className={`
                  px-3 py-1 rounded-md text-sm font-medium transition-all duration-200
                  ${selectedCategory === 'tasks'
                    ? 'bg-teal-600 text-white'
                    : 'text-gray-300 hover:text-white'
                  }
                `}
              >
                任务状态
              </button>
            </div>
            
            {/* 时间过滤 */}
            {selectedCategory === 'executions' && (
              <div className="flex gap-1 bg-gray-700/50 rounded-lg p-1">
                {[
                  { key: 'today', label: '今天' },
                  { key: 'week', label: '本周' },
                  { key: 'all', label: '全部' }
                ].map(option => (
                  <button
                    key={option.key}
                    onClick={() => setFilter(option.key as any)}
                    className={`
                      px-3 py-1 rounded-md text-sm font-medium transition-all duration-200
                      ${filter === option.key
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-300 hover:text-white'
                      }
                    `}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 统计概览 */}
      <div className="p-6 border-b border-gray-700/50">
        {selectedCategory === 'executions' ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{executionStats.total}</div>
              <div className="text-sm text-gray-400">总执行次数</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">{executionStats.successful}</div>
              <div className="text-sm text-gray-400">成功执行</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-400">{executionStats.failed}</div>
              <div className="text-sm text-gray-400">执行失败</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">
                {executionStats.successRate.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-400">成功率</div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{activeTasksStats.total}</div>
              <div className="text-sm text-gray-400">活跃任务</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-400">{activeTasksStats.comingSoon}</div>
              <div className="text-sm text-gray-400">即将执行</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-400">{activeTasksStats.overdue}</div>
              <div className="text-sm text-gray-400">执行超时</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">{activeTasksStats.normal}</div>
              <div className="text-sm text-gray-400">正常等待</div>
            </div>
          </div>
        )}
      </div>

      {/* 活动列表 */}
      <div className="p-6">
        {selectedCategory === 'executions' ? (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filteredExecutions.length > 0 ? (
              filteredExecutions.map((execution) => (
                <div
                  key={execution.id}
                  className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-700/30 transition-all duration-200"
                >
                  {/* 状态指示器 */}
                  <div className={`
                    w-3 h-3 rounded-full flex-shrink-0
                    ${execution.status === 'success' ? 'bg-green-500' :
                      execution.status === 'failed' ? 'bg-red-500' :
                      'bg-yellow-500'
                    }
                  `}></div>
                  
                  {/* 执行信息 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-white truncate">
                        任务 {execution.task_id.substring(0, 8)}...
                      </span>
                      <span className={`
                        px-2 py-1 text-xs rounded-full
                        ${getStatusColor(execution.status)}
                      `}>
                        {execution.status === 'success' ? '成功' :
                         execution.status === 'failed' ? '失败' : '部分'}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span>{formatTime(execution.executed_at)}</span>
                      <span>⏱️ {execution.execution_duration?.toFixed(1)}s</span>
                      <span>📚 {execution.sources_count} 来源</span>
                      {execution.trend_score && (
                        <span>📈 {execution.trend_score.toFixed(1)}</span>
                      )}
                    </div>
                  </div>
                  
                  {/* 查看按钮 */}
                  {onTaskSelect && (
                    <button
                      onClick={() => onTaskSelect(execution.task_id)}
                      className="flex-shrink-0 px-3 py-1 text-xs text-teal-400 hover:text-teal-300 transition-colors"
                    >
                      查看
                    </button>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">📋</div>
                <p className="text-gray-400">暂无执行记录</p>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {tasks.filter(task => task.is_active).length > 0 ? (
              tasks.filter(task => task.is_active).map((task) => {
                const now = new Date();
                const nextRun = task.next_run ? new Date(task.next_run) : null;
                const isComingSoon = nextRun && (nextRun.getTime() - now.getTime()) <= 60 * 60 * 1000;
                const isOverdue = nextRun && nextRun.getTime() < now.getTime();
                
                return (
                  <div
                    key={task.id}
                    className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-700/30 transition-all duration-200 cursor-pointer"
                    onClick={() => onTaskSelect?.(task.id)}
                  >
                    {/* 状态指示器 */}
                    <div className={`
                      w-3 h-3 rounded-full flex-shrink-0
                      ${isOverdue ? 'bg-red-500 animate-pulse' :
                        isComingSoon ? 'bg-yellow-500 animate-pulse' :
                        'bg-green-500'
                      }
                    `}></div>
                    
                    {/* 任务信息 */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-white truncate">
                          {task.topic}
                        </span>
                        {isOverdue && (
                          <span className="px-2 py-1 text-xs rounded-full bg-red-500/20 text-red-400">
                            超时
                          </span>
                        )}
                        {isComingSoon && (
                          <span className="px-2 py-1 text-xs rounded-full bg-yellow-500/20 text-yellow-400">
                            即将执行
                          </span>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        <span>⏰ {task.interval_hours}h间隔</span>
                        <span>📊 {task.success_runs}/{task.total_runs}</span>
                        {nextRun && (
                          <span>下次: {formatTime(task.next_run)}</span>
                        )}
                      </div>
                    </div>
                    
                    {/* 成功率指示器 */}
                    <div className="flex-shrink-0 text-right">
                      <div className="text-sm font-medium text-white">
                        {task.total_runs > 0 ? 
                          `${((task.success_runs / task.total_runs) * 100).toFixed(0)}%` : 
                          '新任务'
                        }
                      </div>
                      <div className="text-xs text-gray-400">成功率</div>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">💤</div>
                <p className="text-gray-400">暂无活跃任务</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
