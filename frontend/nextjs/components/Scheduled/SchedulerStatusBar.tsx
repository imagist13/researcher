"use client";

import React, { useState } from 'react';
import { UserStatistics, SchedulerStatus, ScheduledResultMessage } from '@/types/data';

interface SchedulerStatusBarProps {
  schedulerStatus: SchedulerStatus | null;
  userStats: UserStatistics | null;
  wsConnected: boolean;
  notifications: ScheduledResultMessage[];
  onClearNotifications: () => void;
}

export default function SchedulerStatusBar({
  schedulerStatus,
  userStats,
  wsConnected,
  notifications,
  onClearNotifications,
}: SchedulerStatusBarProps) {
  const [showNotifications, setShowNotifications] = useState(false);

  return (
    <div className="mb-6 space-y-4">
      {/* 主状态栏 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 调度器状态 */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700/50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-300 mb-1">调度器状态</h3>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${
                  schedulerStatus?.running ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`}></div>
                <span className={`text-sm font-semibold ${
                  schedulerStatus?.running ? 'text-green-400' : 'text-red-400'
                }`}>
                  {schedulerStatus?.running ? '运行中' : '已停止'}
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-1">
                {schedulerStatus?.total_jobs || 0} 个任务
              </p>
            </div>
            <div className="text-2xl">⚙️</div>
          </div>
        </div>

        {/* WebSocket连接状态 */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700/50 p-4">
          <div className="flex items-center justify-between">
            <div className="min-w-0 flex-1">
              <h3 className="text-sm font-medium text-gray-300 mb-1">实时连接</h3>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${
                  wsConnected ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'
                }`}></div>
                <span className={`text-sm font-semibold ${
                  wsConnected ? 'text-green-400' : 'text-yellow-400'
                }`}>
                  {wsConnected ? '已连接' : '等待后端'}
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-1">
                {wsConnected ? 'WebSocket 正常' : '需要启动后端服务'}
              </p>
            </div>
            <div className="text-2xl flex-shrink-0">
              {wsConnected ? '📡' : '⏳'}
            </div>
          </div>
        </div>

        {/* 活跃任务数 */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700/50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-300 mb-1">活跃任务</h3>
              <p className="text-xl font-bold text-teal-400">
                {userStats?.active_tasks || 0}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                共 {userStats?.total_tasks || 0} 个任务
              </p>
            </div>
            <div className="text-2xl">📋</div>
          </div>
        </div>

        {/* 执行统计 */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700/50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-300 mb-1">成功率</h3>
              <p className="text-xl font-bold text-green-400">
                {userStats?.overall_success_rate 
                  ? `${(userStats.overall_success_rate * 100).toFixed(1)}%`
                  : '0%'
                }
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {userStats?.successful_executions || 0} / {userStats?.total_executions || 0} 次
              </p>
            </div>
            <div className="text-2xl">📊</div>
          </div>
        </div>
      </div>

      {/* 通知面板 */}
      {notifications.length > 0 && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700/50 p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-300 flex items-center gap-2">
              <span className="text-lg">🔔</span>
              最新研究结果 ({notifications.length})
            </h3>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="text-xs text-teal-400 hover:text-teal-300 transition-colors"
              >
                {showNotifications ? '收起' : '展开'}
              </button>
              <button
                onClick={onClearNotifications}
                className="text-xs text-gray-400 hover:text-gray-300 transition-colors"
              >
                清空
              </button>
            </div>
          </div>

          {showNotifications && (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {notifications.map((notification, index) => (
                <div
                  key={`${notification.task_id}-${notification.timestamp}-${index}`}
                  className="bg-gray-700/50 rounded-md p-3 border border-gray-600/50"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-white truncate">
                        {notification.topic}
                      </h4>
                      <p className="text-xs text-gray-300 mt-1 line-clamp-2">
                        {notification.summary}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                        <span>📈 趋势: {notification.trend_score.toFixed(1)}</span>
                        <span>📚 来源: {notification.sources_count}</span>
                        <span>🕒 {new Date(notification.timestamp).toLocaleString('zh-CN', {
                          month: '2-digit',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}</span>
                      </div>
                    </div>
                    <div className={`
                      px-2 py-1 rounded text-xs font-medium
                      ${notification.trend_score >= 7 ? 'bg-green-500/20 text-green-400' :
                        notification.trend_score >= 5 ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-gray-500/20 text-gray-400'
                      }
                    `}>
                      {notification.trend_score >= 7 ? '🔥 热门' :
                       notification.trend_score >= 5 ? '📊 一般' :
                       '📉 冷门'
                      }
                    </div>
                  </div>
                  
                  {notification.key_changes.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-600/50">
                      <p className="text-xs text-gray-400 mb-1">关键变化:</p>
                      <div className="flex flex-wrap gap-1">
                        {notification.key_changes.slice(0, 3).map((change, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-teal-500/20 text-teal-300 text-xs rounded"
                          >
                            {change}
                          </span>
                        ))}
                        {notification.key_changes.length > 3 && (
                          <span className="text-xs text-gray-400">
                            +{notification.key_changes.length - 3} 更多
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 正在运行的任务 */}
      {schedulerStatus?.running_tasks && schedulerStatus.running_tasks.length > 0 && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
            <h3 className="text-sm font-medium text-yellow-400">
              正在执行的任务 ({schedulerStatus.running_tasks.length})
            </h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {schedulerStatus.running_tasks.map((taskId, index) => (
              <span
                key={`running-${taskId}-${index}`}
                className="px-2 py-1 bg-yellow-500/20 text-yellow-300 text-xs rounded"
              >
                {taskId.substring(0, 8)}...
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
