import { useState, useEffect, useCallback, useMemo } from 'react';
import { useScheduledTasks } from './useScheduledTasks';
import { useScheduledWebSocket } from './useScheduledWebSocket';
import { ScheduledTask, ScheduledResultMessage, CreateTaskRequest, UpdateTaskRequest } from '@/types/data';

interface UseOptimizedScheduledTasksOptions {
  userId: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
  enableWebSocket?: boolean;
}

interface UseOptimizedScheduledTasksReturn {
  // 任务数据
  tasks: ScheduledTask[];
  loading: boolean;
  error: string | null;
  userStats: any;
  schedulerStatus: any;
  
  // WebSocket状态
  wsConnected: boolean;
  notifications: ScheduledResultMessage[];
  
  // 操作方法
  createTask: (task: CreateTaskRequest) => Promise<ScheduledTask | null>;
  updateTask: (taskId: string, updates: UpdateTaskRequest) => Promise<boolean>;
  deleteTask: (taskId: string) => Promise<boolean>;
  pauseTask: (taskId: string) => Promise<boolean>;
  resumeTask: (taskId: string) => Promise<boolean>;
  triggerTask: (taskId: string, quickMode?: boolean) => Promise<boolean>;
  refreshData: () => void;
  clearError: () => void;
  clearNotifications: () => void;
}

/**
 * 优化的定时任务Hook，包含性能优化和错误处理
 */
export function useOptimizedScheduledTasks({
  userId,
  autoRefresh = true,
  refreshInterval = 30000,
  enableWebSocket = true,
}: UseOptimizedScheduledTasksOptions): UseOptimizedScheduledTasksReturn {
  const [notifications, setNotifications] = useState<ScheduledResultMessage[]>([]);
  const [wsError, setWsError] = useState<string | null>(null);

  // 使用原有的定时任务Hook
  const {
    tasks,
    loading,
    error,
    userStats,
    schedulerStatus,
    createTask,
    updateTask,
    deleteTask,
    pauseTask,
    resumeTask,
    triggerTask,
    refreshData,
    clearError,
  } = useScheduledTasks({
    userId,
    autoRefresh,
    refreshInterval,
  });

  // WebSocket连接处理
  const handleScheduledResult = useCallback((message: ScheduledResultMessage) => {
    console.log('📊 Received scheduled result:', message);
    setNotifications(prev => {
      // 避免重复通知 - 使用时间戳作为唯一标识
      const messageKey = `${message.task_id}_${message.timestamp || Date.now()}`;
      const exists = prev.some(n => `${n.task_id}_${n.timestamp || 0}` === messageKey);
      if (exists) return prev;
      
      // 保留最近10条通知
      return [message, ...prev.slice(0, 9)];
    });
    
    // 刷新数据（使用防抖）
    debouncedRefresh();
  }, []);

  // 防抖刷新函数
  const debouncedRefresh = useMemo(() => {
    let timeoutId: NodeJS.Timeout;
    return () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        refreshData();
      }, 1000);
    };
  }, [refreshData]);

  // WebSocket Hook
  const {
    isConnected: wsConnected,
    error: wsSocketError,
  } = useScheduledWebSocket({
    onScheduledResult: handleScheduledResult,
    autoConnect: enableWebSocket,
    onError: (error: Event) => {
      setWsError(error.toString());
    },
  });

  // 合并WebSocket错误
  useEffect(() => {
    if (wsSocketError) {
      setWsError(wsSocketError);
    }
  }, [wsSocketError]);

  // 清除通知
  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // 合并错误信息
  const combinedError = error || wsError;

  // 清除所有错误
  const clearAllErrors = useCallback(() => {
    clearError();
    setWsError(null);
  }, [clearError]);

  return {
    // 任务数据
    tasks,
    loading,
    error: combinedError,
    userStats,
    schedulerStatus,
    
    // WebSocket状态
    wsConnected,
    notifications,
    
    // 操作方法
    createTask,
    updateTask,
    deleteTask,
    pauseTask,
    resumeTask,
    triggerTask,
    refreshData,
    clearError: clearAllErrors,
    clearNotifications,
  };
}

export default useOptimizedScheduledTasks;
