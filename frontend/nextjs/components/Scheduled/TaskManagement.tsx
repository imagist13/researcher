"use client";

import React, { useState, useMemo } from 'react';
import { ScheduledTask, CreateTaskRequest, UpdateTaskRequest } from '@/types/data';
import TaskList from './TaskList';
import TaskStatusCard from './TaskStatusCard';
import TaskEditModal from './TaskEditModal';
import { useToast, ToastContainer } from './Toast';

interface TaskManagementProps {
  tasks: ScheduledTask[];
  loading: boolean;
  selectedTaskId: string | null;
  onSelectTask: (taskId: string | null) => void;
  onCreateTask: (taskData: CreateTaskRequest) => Promise<ScheduledTask | null>;
  onUpdateTask: (taskId: string, updateData: UpdateTaskRequest) => Promise<boolean>;
  onDeleteTask: (taskId: string) => Promise<boolean>;
  onPauseTask: (taskId: string) => Promise<boolean>;
  onResumeTask: (taskId: string) => Promise<boolean>;
  onTriggerTask: (taskId: string, quickMode?: boolean) => Promise<boolean>;
  onRefresh: () => void;
}

export default function TaskManagement({
  tasks,
  loading,
  selectedTaskId,
  onSelectTask,
  onCreateTask,
  onUpdateTask,
  onDeleteTask,
  onPauseTask,
  onResumeTask,
  onTriggerTask,
  onRefresh,
}: TaskManagementProps) {
  const [filter, setFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [editingTask, setEditingTask] = useState<ScheduledTask | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const { toasts, showToast, removeToast } = useToast();

  // 过滤和搜索任务
  const filteredTasks = useMemo(() => {
    let filtered = tasks;

    // 按状态过滤
    if (filter === 'active') {
      filtered = filtered.filter(task => task.is_active);
    } else if (filter === 'inactive') {
      filtered = filtered.filter(task => !task.is_active);
    }

    // 搜索过滤
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(task => 
        task.topic.toLowerCase().includes(query) ||
        task.keywords.some(keyword => keyword.toLowerCase().includes(query)) ||
        (task.description && task.description.toLowerCase().includes(query))
      );
    }

    return filtered.sort((a, b) => {
      // 先按活跃状态排序，再按创建时间排序
      if (a.is_active !== b.is_active) {
        return a.is_active ? -1 : 1;
      }
      return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
    });
  }, [tasks, filter, searchQuery]);

  // 选中的任务
  const selectedTask = selectedTaskId ? tasks.find(task => task.id === selectedTaskId) : null;

  // 执行任务操作
  const handleTaskAction = async (action: string, taskId: string) => {
    setActionLoading(`${action}-${taskId}`);
    
    try {
      let success = false;
      
      switch (action) {
        case 'pause':
          success = await onPauseTask(taskId);
          if (success) {
            showToast('任务已暂停', 'success');
          } else {
            showToast('暂停任务失败', 'error');
          }
          break;
        case 'resume':
          success = await onResumeTask(taskId);
          if (success) {
            showToast('任务已恢复', 'success');
          } else {
            showToast('恢复任务失败', 'error');
          }
          break;
        case 'trigger':
          success = await onTriggerTask(taskId);
          if (success) {
            showToast('任务已触发执行', 'success');
          } else {
            showToast('触发任务失败', 'error');
          }
          break;
        case 'quick_trigger':
          // 快速触发模式
          success = await onTriggerTask(taskId, true);
          if (success) {
            showToast('任务已快速触发执行', 'success');
          } else {
            showToast('快速触发任务失败', 'error');
          }
          break;
        case 'delete':
          if (confirm('确定要删除这个任务吗？此操作不可撤销。')) {
            success = await onDeleteTask(taskId);
            if (success) {
              showToast('任务已删除', 'success');
              if (selectedTaskId === taskId) {
                onSelectTask(null);
              }
            } else {
              showToast('删除任务失败', 'error');
            }
          }
          break;
      }

      if (success) {
        // 操作成功后刷新数据
        onRefresh();
      }
    } finally {
      setActionLoading(null);
    }
  };

  // 编辑任务
  const handleEditTask = (task: ScheduledTask) => {
    setEditingTask(task);
  };

  // 保存编辑
  const handleSaveEdit = async (updateData: UpdateTaskRequest) => {
    if (!editingTask) return;

    const success = await onUpdateTask(editingTask.id, updateData);
    if (success) {
      showToast('任务已更新', 'success');
      setEditingTask(null);
      onRefresh();
    } else {
      showToast('更新任务失败', 'error');
    }
  };

  return (
    <div className="space-y-6">
      {/* 标题和操作栏 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">任务管理</h2>
          <p className="text-gray-300">
            管理您的定时研究任务，监控执行状态和结果
          </p>
        </div>
        
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
        >
          <span className={`text-lg ${loading ? 'animate-spin' : ''}`}>🔄</span>
          刷新
        </button>
      </div>

      {/* 搜索和过滤栏 */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* 搜索框 */}
        <div className="flex-1">
          <div className="relative">
            <input
              type="text"
              placeholder="搜索任务（话题、关键词、描述）..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-lg text-white placeholder-gray-400 focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 focus:outline-none transition-all"
            />
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              🔍
            </div>
          </div>
        </div>

        {/* 状态过滤 */}
        <div className="flex bg-gray-800/50 rounded-lg border border-gray-700/50 p-1">
          {[
            { key: 'all', label: '全部', count: tasks.length },
            { key: 'active', label: '活跃', count: tasks.filter(t => t.is_active).length },
            { key: 'inactive', label: '暂停', count: tasks.filter(t => !t.is_active).length },
          ].map((option) => (
            <button
              key={option.key}
              onClick={() => setFilter(option.key as any)}
              className={`
                px-4 py-2 rounded-md text-sm font-medium transition-all duration-200
                ${filter === option.key
                  ? 'bg-teal-600 text-white shadow-lg'
                  : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
                }
              `}
            >
              {option.label}
              <span className="ml-1 text-xs opacity-75">({option.count})</span>
            </button>
          ))}
        </div>
      </div>

      {/* 主要内容区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 任务列表 */}
        <div className="lg:col-span-2">
          <TaskList
            tasks={filteredTasks}
            selectedTaskId={selectedTaskId}
            onSelectTask={onSelectTask}
            onTaskAction={handleTaskAction}
            onEditTask={handleEditTask}
            actionLoading={actionLoading}
            loading={loading}
          />
        </div>

        {/* 任务详情卡片 */}
        <div className="lg:col-span-1">
          <TaskStatusCard
            task={selectedTask || null}
            onEditTask={handleEditTask}
            onTaskAction={handleTaskAction}
            actionLoading={actionLoading}
          />
        </div>
      </div>

      {/* 编辑任务模态框 */}
      {editingTask && (
        <TaskEditModal
          task={editingTask}
          onSave={handleSaveEdit}
          onCancel={() => setEditingTask(null)}
        />
      )}

      {/* 空状态 */}
      {!loading && tasks.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📋</div>
          <h3 className="text-xl font-semibold text-white mb-2">暂无任务</h3>
          <p className="text-gray-400 mb-6">
            开始创建您的第一个定时研究任务
          </p>
          <button
            onClick={() => {/* 切换到配置标签页的逻辑将在父组件中处理 */}}
            className="px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-medium transition-colors"
          >
            创建任务
          </button>
        </div>
      )}

      {/* 搜索无结果 */}
      {!loading && tasks.length > 0 && filteredTasks.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-white mb-2">未找到匹配的任务</h3>
          <p className="text-gray-400 mb-6">
            尝试调整搜索条件或过滤器
          </p>
          <button
            onClick={() => {
              setSearchQuery('');
              setFilter('all');
            }}
            className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
          >
            清除筛选
          </button>
        </div>
      )}

      {/* Toast通知 */}
      <ToastContainer toasts={toasts} onRemoveToast={removeToast} />
    </div>
  );
}
