"use client";

import React, { useMemo, useState, useCallback } from 'react';
import { ScheduledTask } from '@/types/data';

interface VirtualizedTaskListProps {
  tasks: ScheduledTask[];
  selectedTaskId: string | null;
  onSelectTask: (taskId: string) => void;
  onEditTask: (taskId: string) => void;
  onDeleteTask: (taskId: string) => void;
  onPauseTask: (taskId: string) => void;
  onResumeTask: (taskId: string) => void;
  onTriggerTask: (taskId: string) => void;
  itemHeight?: number;
  maxVisibleItems?: number;
}

interface TaskItemProps {
  task: ScheduledTask;
  isSelected: boolean;
  onSelect: () => void;
  onEdit: () => void;
  onDelete: () => void;
  onPause: () => void;
  onResume: () => void;
  onTrigger: () => void;
}

// 优化的任务项组件
const TaskItem = React.memo<TaskItemProps>(({
  task,
  isSelected,
  onSelect,
  onEdit,
  onDelete,
  onPause,
  onResume,
  onTrigger,
}) => {
  const statusColors = {
    active: 'text-green-400 bg-green-500/20',
    paused: 'text-yellow-400 bg-yellow-500/20',
    error: 'text-red-400 bg-red-500/20',
    completed: 'text-blue-400 bg-blue-500/20',
  };

  const statusIcons = {
    active: '🟢',
    paused: '⏸️',
    error: '🔴',
    completed: '✅',
  };

  return (
    <div
      className={`
        p-4 rounded-lg border transition-all duration-200 cursor-pointer
        ${isSelected 
          ? 'bg-teal-500/20 border-teal-500/50 shadow-lg' 
          : 'bg-gray-800/30 border-gray-700/50 hover:bg-gray-800/50 hover:border-gray-600/50'
        }
      `}
      onClick={onSelect}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-lg">{task.is_active ? '🟢' : '⏸️'}</span>
          <div>
            <h3 className="font-semibold text-white text-lg truncate max-w-[300px]">
              {task.topic}
            </h3>
            <p className="text-sm text-gray-400 mt-1">
              {task.description || '无描述'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <span className={`
            px-2 py-1 rounded-full text-xs font-medium
            ${task.is_active ? 'text-green-400 bg-green-500/20' : 'text-gray-400 bg-gray-500/20'}
          `}>
            {task.is_active ? '运行中' : '已暂停'}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-400">
        <div className="flex items-center gap-4">
          <span>📅 每{task.interval_hours}小时</span>
          {task.next_run && (
            <span>⏰ {new Date(task.next_run).toLocaleString('zh-CN')}</span>
          )}
        </div>
        
        <div className="flex items-center gap-1">
          {task.is_active && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onPause();
              }}
              className="p-1 text-yellow-400 hover:text-yellow-300 transition-colors"
              title="暂停任务"
            >
              ⏸️
            </button>
          )}
          
          {!task.is_active && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onResume();
              }}
              className="p-1 text-green-400 hover:text-green-300 transition-colors"
              title="恢复任务"
            >
              ▶️
            </button>
          )}
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              onTrigger();
            }}
            className="p-1 text-blue-400 hover:text-blue-300 transition-colors"
            title="立即执行"
          >
            🚀
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit();
            }}
            className="p-1 text-gray-400 hover:text-gray-300 transition-colors"
            title="编辑任务"
          >
            ✏️
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className="p-1 text-red-400 hover:text-red-300 transition-colors"
            title="删除任务"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
  );
});

TaskItem.displayName = 'TaskItem';

export default function VirtualizedTaskList({
  tasks,
  selectedTaskId,
  onSelectTask,
  onEditTask,
  onDeleteTask,
  onPauseTask,
  onResumeTask,
  onTriggerTask,
  itemHeight = 120,
  maxVisibleItems = 10,
}: VirtualizedTaskListProps) {
  const [scrollTop, setScrollTop] = useState(0);

  // 计算可见项目范围
  const visibleRange = useMemo(() => {
    const containerHeight = maxVisibleItems * itemHeight;
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      tasks.length
    );
    
    return { startIndex: Math.max(0, startIndex), endIndex };
  }, [scrollTop, itemHeight, maxVisibleItems, tasks.length]);

  // 可见任务项
  const visibleTasks = useMemo(() => {
    return tasks.slice(visibleRange.startIndex, visibleRange.endIndex);
  }, [tasks, visibleRange]);

  // 滚动处理
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  // 任务操作回调
  const createTaskHandlers = useCallback((taskId: string) => ({
    onSelect: () => onSelectTask(taskId),
    onEdit: () => onEditTask(taskId),
    onDelete: () => onDeleteTask(taskId),
    onPause: () => onPauseTask(taskId),
    onResume: () => onResumeTask(taskId),
    onTrigger: () => onTriggerTask(taskId),
  }), [onSelectTask, onEditTask, onDeleteTask, onPauseTask, onResumeTask, onTriggerTask]);

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800/50 flex items-center justify-center">
          <span className="text-2xl">📋</span>
        </div>
        <h3 className="text-lg font-medium text-gray-300 mb-2">暂无任务</h3>
        <p className="text-gray-400">创建您的第一个定时研究任务</p>
      </div>
    );
  }

  const totalHeight = tasks.length * itemHeight;
  const containerHeight = Math.min(maxVisibleItems * itemHeight, totalHeight);

  return (
    <div className="space-y-4">
      {/* 任务统计 */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-400">
          共 {tasks.length} 个任务
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span>🟢 活跃: {tasks.filter(t => t.is_active).length}</span>
          <span>⏸️ 暂停: {tasks.filter(t => !t.is_active).length}</span>
          <span>📊 总计: {tasks.length}</span>
        </div>
      </div>

      {/* 虚拟化列表容器 */}
      <div
        className="relative overflow-auto border border-gray-700/50 rounded-lg"
        style={{ height: containerHeight }}
        onScroll={handleScroll}
      >
        {/* 总高度占位符 */}
        <div style={{ height: totalHeight, position: 'relative' }}>
          {/* 可见项目 */}
          <div
            style={{
              position: 'absolute',
              top: visibleRange.startIndex * itemHeight,
              width: '100%',
            }}
          >
            <div className="space-y-3 p-3">
              {visibleTasks.map((task, index) => {
                const taskHandlers = createTaskHandlers(task.id);
                return (
                  <TaskItem
                    key={task.id}
                    task={task}
                    isSelected={selectedTaskId === task.id}
                    {...taskHandlers}
                  />
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
