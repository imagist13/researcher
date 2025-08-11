/**
 * 定时研究任务管理Hook
 * Scheduled Research Tasks Management Hook
 */
import { useState, useEffect, useCallback } from 'react';
import { 
  ScheduledTask, 
  CreateTaskRequest, 
  UpdateTaskRequest,
  ResearchHistoryRecord,
  TrendData,
  TaskStatistics,
  UserStatistics,
  SchedulerStatus,
  PaginatedResponse
} from '@/types/data';
import { scheduledApiService } from '@/services/scheduledApiService';

interface UseScheduledTasksOptions {
  userId?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export const useScheduledTasks = (options: UseScheduledTasksOptions = {}) => {
  const {
    userId = 'default_user',
    autoRefresh = false,
    refreshInterval = 30000, // 30秒
  } = options;

  // 状态管理
  const [tasks, setTasks] = useState<ScheduledTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userStats, setUserStats] = useState<UserStatistics | null>(null);
  const [schedulerStatus, setSchedulerStatus] = useState<SchedulerStatus | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  // 获取任务列表
  const fetchTasks = useCallback(async (activeOnly: boolean = false) => {
    try {
      setLoading(true);
      setError(null);
      const response = await scheduledApiService.getTasks(userId, activeOnly);
      setTasks(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取任务列表失败');
      console.error('Failed to fetch tasks:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // 创建新任务
  const createTask = useCallback(async (taskData: CreateTaskRequest): Promise<ScheduledTask | null> => {
    try {
      setLoading(true);
      setError(null);
      const response = await scheduledApiService.createTask(taskData);
      
      if (response.success && response.data) {
        // 添加到本地状态
        setTasks(prev => [response.data!, ...prev]);
        return response.data;
      } else {
        throw new Error(response.message || '创建任务失败');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '创建任务失败';
      setError(errorMsg);
      console.error('Failed to create task:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // 更新任务
  const updateTask = useCallback(async (
    taskId: string, 
    updateData: UpdateTaskRequest
  ): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);
      const response = await scheduledApiService.updateTask(taskId, updateData);
      
      if (response.success && response.data) {
        // 更新本地状态
        setTasks(prev => prev.map(task => 
          task.id === taskId ? response.data! : task
        ));
        return true;
      } else {
        throw new Error(response.message || '更新任务失败');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '更新任务失败';
      setError(errorMsg);
      console.error('Failed to update task:', err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // 删除任务
  const deleteTask = useCallback(async (taskId: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);
      const response = await scheduledApiService.deleteTask(taskId);
      
      if (response.success) {
        // 从本地状态移除
        setTasks(prev => prev.filter(task => task.id !== taskId));
        return true;
      } else {
        throw new Error(response.message || '删除任务失败');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '删除任务失败';
      setError(errorMsg);
      console.error('Failed to delete task:', err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // 暂停任务
  const pauseTask = useCallback(async (taskId: string): Promise<boolean> => {
    try {
      setError(null);
      const response = await scheduledApiService.pauseTask(taskId);
      
      if (response.success) {
        // 更新本地状态
        setTasks(prev => prev.map(task => 
          task.id === taskId ? { ...task, is_active: false } : task
        ));
        return true;
      } else {
        throw new Error(response.message || '暂停任务失败');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '暂停任务失败';
      setError(errorMsg);
      console.error('Failed to pause task:', err);
      return false;
    }
  }, []);

  // 恢复任务
  const resumeTask = useCallback(async (taskId: string): Promise<boolean> => {
    try {
      setError(null);
      const response = await scheduledApiService.resumeTask(taskId);
      
      if (response.success) {
        // 更新本地状态
        setTasks(prev => prev.map(task => 
          task.id === taskId ? { ...task, is_active: true } : task
        ));
        return true;
      } else {
        throw new Error(response.message || '恢复任务失败');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '恢复任务失败';
      setError(errorMsg);
      console.error('Failed to resume task:', err);
      return false;
    }
  }, []);

  // 立即触发任务
  const triggerTask = useCallback(async (taskId: string, quickMode: boolean = false): Promise<boolean> => {
    try {
      setError(null);
      const response = await scheduledApiService.triggerTask(taskId, quickMode);
      
      if (response.success) {
        return true;
      } else {
        throw new Error(response.message || '触发任务失败');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '触发任务失败';
      setError(errorMsg);
      console.error('Failed to trigger task:', err);
      return false;
    }
  }, []);

  // 获取用户统计信息
  const fetchUserStatistics = useCallback(async () => {
    try {
      const stats = await scheduledApiService.getUserStatistics(userId);
      setUserStats(stats);
    } catch (err) {
      console.error('Failed to fetch user statistics:', err);
    }
  }, [userId]);

  // 获取调度器状态
  const fetchSchedulerStatus = useCallback(async () => {
    try {
      const status = await scheduledApiService.getSchedulerStatus();
      setSchedulerStatus(status);
    } catch (err) {
      console.error('Failed to fetch scheduler status:', err);
    }
  }, []);

  // 刷新所有数据
  const refreshData = useCallback(() => {
    setRefreshKey(prev => prev + 1);
  }, []);

  // 初始加载
  useEffect(() => {
    fetchTasks();
    fetchUserStatistics();
    fetchSchedulerStatus();
  }, [fetchTasks, fetchUserStatistics, fetchSchedulerStatus, refreshKey]);

  // 自动刷新
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchTasks();
      fetchUserStatistics();
      fetchSchedulerStatus();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchTasks, fetchUserStatistics, fetchSchedulerStatus]);

  // 获取单个任务详情
  const getTask = useCallback((taskId: string): ScheduledTask | undefined => {
    return tasks.find(task => task.id === taskId);
  }, [tasks]);

  // 获取活跃任务
  const getActiveTasks = useCallback((): ScheduledTask[] => {
    return tasks.filter(task => task.is_active);
  }, [tasks]);

  // 获取非活跃任务
  const getInactiveTasks = useCallback((): ScheduledTask[] => {
    return tasks.filter(task => !task.is_active);
  }, [tasks]);

  return {
    // 状态
    tasks,
    loading,
    error,
    userStats,
    schedulerStatus,

    // 任务管理方法
    createTask,
    updateTask,
    deleteTask,
    pauseTask,
    resumeTask,
    triggerTask,

    // 数据获取方法
    fetchTasks,
    refreshData,
    getTask,
    getActiveTasks,
    getInactiveTasks,

    // 工具方法
    clearError: () => setError(null),
  };
};

// 用于获取任务历史记录的Hook
export const useTaskHistory = (taskId: string) => {
  const [history, setHistory] = useState<ResearchHistoryRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async (page: number = 1, perPage: number = 10) => {
    if (!taskId) return;

    try {
      setLoading(true);
      setError(null);
      const response = await scheduledApiService.getTaskHistory(taskId, page, perPage);
      setHistory(response.items);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '获取历史记录失败';
      setError(errorMsg);
      console.error('Failed to fetch task history:', err);
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return {
    history,
    loading,
    error,
    fetchHistory,
    clearError: () => setError(null),
  };
};

// 用于获取任务趋势数据的Hook
export const useTaskTrends = (taskId: string, days: number = 30) => {
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTrends = useCallback(async () => {
    if (!taskId) return;

    try {
      setLoading(true);
      setError(null);
      const response = await scheduledApiService.getTaskTrends(taskId, days);
      setTrends(response.items);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '获取趋势数据失败';
      setError(errorMsg);
      console.error('Failed to fetch task trends:', err);
    } finally {
      setLoading(false);
    }
  }, [taskId, days]);

  useEffect(() => {
    fetchTrends();
  }, [fetchTrends]);

  return {
    trends,
    loading,
    error,
    fetchTrends,
    clearError: () => setError(null),
  };
};

// 用于获取任务统计信息的Hook
export const useTaskStatistics = (taskId: string) => {
  const [statistics, setStatistics] = useState<TaskStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatistics = useCallback(async () => {
    if (!taskId) return;

    try {
      setLoading(true);
      setError(null);
      const stats = await scheduledApiService.getTaskStatistics(taskId);
      setStatistics(stats);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '获取统计信息失败';
      setError(errorMsg);
      console.error('Failed to fetch task statistics:', err);
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    fetchStatistics();
  }, [fetchStatistics]);

  return {
    statistics,
    loading,
    error,
    fetchStatistics,
    clearError: () => setError(null),
  };
};
