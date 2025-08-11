"use client";

import React, { useState } from 'react';
import { ScheduledTask } from '@/types/data';
import { useTaskHistory, useTaskStatistics } from '@/hooks/useScheduledTasks';

interface TaskStatusCardProps {
  task: ScheduledTask | null;
  onEditTask: (task: ScheduledTask) => void;
  onTaskAction: (action: string, taskId: string) => void;
  actionLoading: string | null;
}

export default function TaskStatusCard({
  task,
  onEditTask,
  onTaskAction,
  actionLoading,
}: TaskStatusCardProps) {
  const [activeTab, setActiveTab] = useState<'info' | 'history' | 'stats'>('info');

  // 获取任务历史和统计
  const { history, loading: historyLoading } = useTaskHistory(task?.id || '');
  const { statistics, loading: statsLoading } = useTaskStatistics(task?.id || '');

  if (!task) {
    return (
      <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 p-6 backdrop-blur-sm">
        <div className="text-center py-8">
          <div className="text-4xl mb-4">📋</div>
          <h3 className="text-lg font-semibold text-white mb-2">选择一个任务</h3>
          <p className="text-gray-400">
            点击左侧任务列表中的任务查看详细信息
          </p>
        </div>
      </div>
    );
  }

  // 格式化时间
  const formatTime = (timeString?: string) => {
    if (!timeString) return '未知';
    try {
      return new Date(timeString).toLocaleString('zh-CN');
    } catch {
      return '格式错误';
    }
  };

  // 计算成功率
  const successRate = task.total_runs > 0 ? (task.success_runs / task.total_runs) * 100 : 0;

  // 获取状态颜色
  const getStatusColor = () => {
    if (!task.is_active) return 'text-gray-400';
    if (successRate >= 80) return 'text-green-400';
    if (successRate >= 50) return 'text-yellow-400';
    return 'text-red-400';
  };

  const isActionLoading = actionLoading?.includes(task.id);

  return (
    <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 backdrop-blur-sm overflow-hidden">
      {/* 任务标题 */}
      <div className="p-6 border-b border-gray-700/50">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <h3 className="text-xl font-bold text-white truncate">
              {task.topic}
            </h3>
            {task.description && (
              <p className="text-gray-300 mt-1 text-sm">
                {task.description}
              </p>
            )}
          </div>
          
          {/* 状态指示器 */}
          <div className={`
            px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2
            ${task.is_active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}
          `}>
            <div className={`w-2 h-2 rounded-full ${
              task.is_active ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
            }`}></div>
            {task.is_active ? '运行中' : '已暂停'}
          </div>
        </div>

        {/* 快速操作按钮 */}
        <div className="flex gap-2">
          {task.is_active ? (
            <button
              onClick={() => onTaskAction('pause', task.id)}
              disabled={isActionLoading}
              className="flex items-center gap-2 px-3 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 text-white text-sm rounded transition-colors"
            >
              {actionLoading === `pause-${task.id}` ? '⏳' : '⏸️'}
              暂停
            </button>
          ) : (
            <button
              onClick={() => onTaskAction('resume', task.id)}
              disabled={isActionLoading}
              className="flex items-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white text-sm rounded transition-colors"
            >
              {actionLoading === `resume-${task.id}` ? '⏳' : '▶️'}
              恢复
            </button>
          )}

          <button
            onClick={() => onTaskAction('trigger', task.id)}
            disabled={isActionLoading}
            className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white text-sm rounded transition-colors"
          >
            {actionLoading === `trigger-${task.id}` ? '⏳' : '⚡'}
            立即执行
          </button>

          <button
            onClick={() => onEditTask(task)}
            disabled={isActionLoading}
            className="flex items-center gap-2 px-3 py-2 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-600 text-white text-sm rounded transition-colors"
          >
            ✏️ 编辑
          </button>
        </div>
      </div>

      {/* 标签页导航 */}
      <div className="flex border-b border-gray-700/50">
        {[
          { key: 'info', label: '基本信息', icon: 'ℹ️' },
          { key: 'history', label: '执行历史', icon: '📋' },
          { key: 'stats', label: '统计数据', icon: '📊' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`
              flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors
              ${activeTab === tab.key
                ? 'bg-teal-600/20 text-teal-400 border-b-2 border-teal-500'
                : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
              }
            `}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* 标签页内容 */}
      <div className="p-6">
        {activeTab === 'info' && (
          <div className="space-y-4">
            {/* 基本配置 */}
            <div>
              <h4 className="text-sm font-semibold text-gray-300 mb-3">任务配置</h4>
              <div className="grid grid-cols-1 gap-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">执行间隔:</span>
                  <span className="text-white">{task.interval_hours} 小时</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">分析深度:</span>
                  <span className="text-white">
                    {task.analysis_depth === 'basic' ? '基础' :
                     task.analysis_depth === 'detailed' ? '详细' : '深度'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">报告类型:</span>
                  <span className={`font-medium ${
                    task.report_type === 'deep' ? 'text-purple-400' : 
                    task.report_type === 'detailed_report' ? 'text-blue-400' : 
                    'text-white'
                  }`}>
                    {task.report_type === 'deep' ? '🌟 深度研究' :
                     task.report_type === 'detailed_report' ? '📊 详细报告' :
                     task.report_type === 'research_report' ? '📝 研究报告' :
                     task.report_type === 'outline_report' ? '📋 大纲报告' :
                     task.report_type === 'subtopic_report' ? '🔍 子主题报告' :
                     task.report_type}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">信息源:</span>
                  <span className="text-white">{task.source_types.join(', ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">最大来源数:</span>
                  <span className="text-white">{task.max_sources}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">语言:</span>
                  <span className="text-white">{task.language}</span>
                </div>
              </div>
            </div>

            {/* 关键词 */}
            <div>
              <h4 className="text-sm font-semibold text-gray-300 mb-3">关键词</h4>
              <div className="flex flex-wrap gap-2">
                {task.keywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-teal-500/20 text-teal-300 text-xs rounded-full"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>

            {/* 时间信息 */}
            <div>
              <h4 className="text-sm font-semibold text-gray-300 mb-3">时间信息</h4>
              <div className="grid grid-cols-1 gap-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">创建时间:</span>
                  <span className="text-white">{formatTime(task.created_at)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">更新时间:</span>
                  <span className="text-white">{formatTime(task.updated_at)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">上次执行:</span>
                  <span className="text-white">{formatTime(task.last_run)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">下次执行:</span>
                  <span className="text-white">{formatTime(task.next_run)}</span>
                </div>
              </div>
            </div>

            {/* 通知设置 */}
            <div>
              <h4 className="text-sm font-semibold text-gray-300 mb-3">通知设置</h4>
              <div className="grid grid-cols-1 gap-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">启用通知:</span>
                  <span className={task.enable_notifications ? 'text-green-400' : 'text-red-400'}>
                    {task.enable_notifications ? '是' : '否'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">通知阈值:</span>
                  <span className="text-white">{task.notification_threshold}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-gray-300">最近执行记录</h4>
            
            {historyLoading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, index) => (
                  <div key={index} className="animate-pulse">
                    <div className="h-4 bg-gray-700 rounded w-full mb-2"></div>
                    <div className="h-3 bg-gray-700 rounded w-3/4"></div>
                  </div>
                ))}
              </div>
            ) : history.length > 0 ? (
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {history.map((record) => (
                  <div
                    key={record.id}
                    className="p-3 bg-gray-700/30 rounded-lg border border-gray-600/50"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-sm text-gray-300">
                        {formatTime(record.executed_at)}
                      </span>
                      <span className={`
                        px-2 py-1 rounded text-xs
                        ${record.status === 'success' ? 'bg-green-500/20 text-green-400' :
                          record.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                          'bg-yellow-500/20 text-yellow-400'
                        }
                      `}>
                        {record.status === 'success' ? '成功' :
                         record.status === 'failed' ? '失败' : '部分'}
                      </span>
                    </div>
                    
                    {record.summary && (
                      <p className="text-xs text-gray-400 line-clamp-2 mb-2">
                        {record.summary}
                      </p>
                    )}
                    
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>⏱️ {record.execution_duration?.toFixed(1)}s</span>
                      <span>📚 {record.sources_count} 来源</span>
                      {record.trend_score && (
                        <span>📈 {record.trend_score.toFixed(1)}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <div className="text-2xl mb-2">📋</div>
                <p className="text-gray-400 text-sm">暂无执行记录</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'stats' && (
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-gray-300">统计概览</h4>
            
            {statsLoading ? (
              <div className="space-y-4">
                {[...Array(4)].map((_, index) => (
                  <div key={index} className="animate-pulse">
                    <div className="h-4 bg-gray-700 rounded w-full mb-2"></div>
                    <div className="h-6 bg-gray-700 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {/* 执行统计 */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-gray-700/30 rounded-lg">
                    <div className="text-2xl font-bold text-white">
                      {task.total_runs}
                    </div>
                    <div className="text-xs text-gray-400">总执行次数</div>
                  </div>
                  <div className="text-center p-3 bg-gray-700/30 rounded-lg">
                    <div className={`text-2xl font-bold ${getStatusColor()}`}>
                      {successRate.toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-400">成功率</div>
                  </div>
                </div>

                {/* 详细统计 */}
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">成功执行:</span>
                    <span className="text-green-400">{task.success_runs}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">失败执行:</span>
                    <span className="text-red-400">{task.failed_runs}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">运行天数:</span>
                    <span className="text-white">
                      {statistics?.uptime_days || 0} 天
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">平均趋势分数:</span>
                    <span className="text-white">
                      {statistics?.average_trend_score?.toFixed(1) || '0.0'}
                    </span>
                  </div>
                </div>

                {/* 趋势图表占位符 */}
                <div className="mt-4 p-4 bg-gray-700/30 rounded-lg text-center">
                  <div className="text-lg mb-2">📈</div>
                  <p className="text-gray-400 text-sm">
                    趋势图表功能即将推出
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
