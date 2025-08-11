"use client";

import React from 'react';
import { ScheduledTask } from '@/types/data';

interface TaskListProps {
  tasks: ScheduledTask[];
  selectedTaskId: string | null;
  onSelectTask: (taskId: string | null) => void;
  onTaskAction: (action: string, taskId: string) => void;
  onEditTask: (task: ScheduledTask) => void;
  actionLoading: string | null;
  loading: boolean;
}

export default function TaskList({
  tasks,
  selectedTaskId,
  onSelectTask,
  onTaskAction,
  onEditTask,
  actionLoading,
  loading,
}: TaskListProps) {
  
  // 格式化时间
  const formatTime = (timeString?: string) => {
    if (!timeString) return '未设置';
    try {
      const date = new Date(timeString);
      if (isNaN(date.getTime())) return '格式错误';
      
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '格式错误';
    }
  };

  // 计算相对时间
  const getRelativeTime = (timeString?: string) => {
    if (!timeString) return '未知';
    try {
      const date = new Date(timeString);
      const now = new Date();
      const diffMs = date.getTime() - now.getTime();
      const diffHours = Math.round(diffMs / (1000 * 60 * 60));
      
      if (diffHours < 0) {
        return '已过期';
      } else if (diffHours < 1) {
        const diffMinutes = Math.round(diffMs / (1000 * 60));
        return diffMinutes > 0 ? `${diffMinutes}分钟后` : '即将执行';
      } else if (diffHours < 24) {
        return `${diffHours}小时后`;
      } else {
        const diffDays = Math.round(diffHours / 24);
        return `${diffDays}天后`;
      }
    } catch {
      return '未知';
    }
  };

  // 获取任务状态样式
  const getTaskStatusStyle = (task: ScheduledTask) => {
    if (!task.is_active) {
      return {
        border: 'border-gray-600/50',
        bg: 'bg-gray-800/30',
        status: { bg: 'bg-gray-500/20', text: 'text-gray-400', icon: '⏸️' }
      };
    }

    const successRate = task.total_runs > 0 ? task.success_runs / task.total_runs : 0;
    
    if (successRate >= 0.8) {
      return {
        border: 'border-green-500/30',
        bg: 'bg-green-500/10',
        status: { bg: 'bg-green-500/20', text: 'text-green-400', icon: '✅' }
      };
    } else if (successRate >= 0.5) {
      return {
        border: 'border-yellow-500/30',
        bg: 'bg-yellow-500/10',
        status: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', icon: '⚠️' }
      };
    } else {
      return {
        border: 'border-red-500/30',
        bg: 'bg-red-500/10',
        status: { bg: 'bg-red-500/20', text: 'text-red-400', icon: '❌' }
      };
    }
  };

  if (loading && tasks.length === 0) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, index) => (
          <div
            key={index}
            className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6 animate-pulse"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="h-5 bg-gray-700 rounded w-3/4 mb-3"></div>
                <div className="h-4 bg-gray-700 rounded w-1/2 mb-2"></div>
                <div className="flex gap-2">
                  <div className="h-6 bg-gray-700 rounded-full w-16"></div>
                  <div className="h-6 bg-gray-700 rounded-full w-16"></div>
                </div>
              </div>
              <div className="h-8 bg-gray-700 rounded w-20"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tasks.map((task) => {
        const styles = getTaskStatusStyle(task);
        const isSelected = selectedTaskId === task.id;
        const isActionLoading = actionLoading?.includes(task.id);

        return (
          <div
            key={task.id}
            onClick={() => onSelectTask(isSelected ? null : task.id)}
            className={`
              rounded-lg border p-6 cursor-pointer transition-all duration-200 backdrop-blur-sm
              ${styles.border} ${styles.bg}
              ${isSelected 
                ? 'ring-2 ring-teal-500/50 border-teal-500/50 bg-teal-500/10' 
                : 'hover:border-teal-500/30 hover:bg-teal-500/5'
              }
              ${isActionLoading ? 'opacity-60 pointer-events-none' : ''}
            `}
          >
            <div className="flex items-start justify-between">
              {/* 任务信息 */}
              <div className="flex-1 min-w-0">
                {/* 标题和状态 */}
                <div className="flex items-start gap-3 mb-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-white truncate">
                      {task.topic}
                    </h3>
                    {task.description && (
                      <p className="text-sm text-gray-300 mt-1 line-clamp-2">
                        {task.description}
                      </p>
                    )}
                  </div>
                  
                  {/* 状态指示器 */}
                  <div className={`
                    px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1
                    ${styles.status.bg} ${styles.status.text}
                  `}>
                    <span>{styles.status.icon}</span>
                    <span>{task.is_active ? '运行中' : '已暂停'}</span>
                  </div>
                </div>

                {/* 关键词 */}
                <div className="flex flex-wrap gap-1 mb-3">
                  {task.keywords.slice(0, 4).map((keyword, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-teal-500/20 text-teal-300 text-xs rounded-full"
                    >
                      {keyword}
                    </span>
                  ))}
                  {task.keywords.length > 4 && (
                    <span className="px-2 py-1 bg-gray-500/20 text-gray-400 text-xs rounded-full">
                      +{task.keywords.length - 4}
                    </span>
                  )}
                </div>

                {/* 执行统计 */}
                <div className="flex items-center gap-4 text-sm text-gray-400">
                  <span className="flex items-center gap-1">
                    🔄 {task.interval_hours}h间隔
                  </span>
                  <span className="flex items-center gap-1">
                    📊 {task.success_runs}/{task.total_runs} 成功
                  </span>
                  {task.next_run && (
                    <span className="flex items-center gap-1">
                      ⏰ {getRelativeTime(task.next_run)}
                    </span>
                  )}
                </div>

                {/* 时间信息 */}
                <div className="flex items-center gap-4 text-xs text-gray-500 mt-2">
                  <span>创建: {formatTime(task.created_at)}</span>
                  {task.last_run && (
                    <span>上次: {formatTime(task.last_run)}</span>
                  )}
                </div>
              </div>

              {/* 操作按钮 */}
              <div className="flex flex-col gap-2 ml-4">
                {/* 主要操作 */}
                <div className="flex gap-2">
                  {task.is_active ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onTaskAction('pause', task.id);
                      }}
                      disabled={isActionLoading}
                      className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 text-white text-xs rounded transition-colors"
                      title="暂停任务"
                    >
                      {actionLoading === `pause-${task.id}` ? '⏳' : '⏸️'}
                    </button>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onTaskAction('resume', task.id);
                      }}
                      disabled={isActionLoading}
                      className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white text-xs rounded transition-colors"
                      title="恢复任务"
                    >
                      {actionLoading === `resume-${task.id}` ? '⏳' : '▶️'}
                    </button>
                  )}

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onTaskAction('quick_trigger', task.id);
                    }}
                    disabled={isActionLoading}
                    className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white text-xs rounded transition-colors"
                    title="快速执行 (1-3分钟)"
                  >
                    {actionLoading === `quick_trigger-${task.id}` ? '⏳' : '🚀'}
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onTaskAction('trigger', task.id);
                    }}
                    disabled={isActionLoading}
                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white text-xs rounded transition-colors"
                    title="完整执行 (5-10分钟)"
                  >
                    {actionLoading === `trigger-${task.id}` ? '⏳' : '⚡'}
                  </button>
                </div>

                {/* 次要操作 */}
                <div className="flex gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onEditTask(task);
                    }}
                    disabled={isActionLoading}
                    className="px-3 py-1 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-600 text-white text-xs rounded transition-colors"
                    title="编辑任务"
                  >
                    ✏️
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onTaskAction('delete', task.id);
                    }}
                    disabled={isActionLoading}
                    className="px-3 py-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white text-xs rounded transition-colors"
                    title="删除任务"
                  >
                    {actionLoading === `delete-${task.id}` ? '⏳' : '🗑️'}
                  </button>
                </div>
              </div>
            </div>

            {/* 选中状态下的额外信息 */}
            {isSelected && (
              <div className="mt-4 pt-4 border-t border-gray-700/50">
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">分析深度:</span>
                    <p className="text-white font-medium">
                      {task.analysis_depth === 'basic' ? '基础' :
                       task.analysis_depth === 'detailed' ? '详细' : '深度'}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-400">信息源:</span>
                    <p className="text-white font-medium">
                      {task.source_types.join(', ')}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-400">最大来源:</span>
                    <p className="text-white font-medium">{task.max_sources}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">通知阈值:</span>
                    <p className="text-white font-medium">{task.notification_threshold}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
