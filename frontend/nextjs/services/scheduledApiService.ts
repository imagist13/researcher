/**
 * 定时研究API服务
 * Scheduled Research API Service
 */
import { 
  ScheduledTask, 
  CreateTaskRequest, 
  UpdateTaskRequest,
  ResearchHistoryRecord,
  TrendData,
  TaskStatistics,
  UserStatistics,
  SchedulerStatus,
  TestConfigResponse,
  ApiResponse,
  PaginatedResponse
} from '@/types/data';
import { getHost } from '@/helpers/getHost';

class ScheduledApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = '';
  }

  private getApiUrl(): string {
    if (typeof window !== 'undefined') {
      const host = getHost();
      this.baseUrl = host.includes('localhost') ? 'http://localhost:8000' : `https://${host}`;
    }
    return this.baseUrl;
  }

  private async request<T = any>(
    endpoint: string, 
    options: RequestInit = {},
    retries: number = 3
  ): Promise<T> {
    const url = `${this.getApiUrl()}${endpoint}`;
    
    // 使用AbortController实现超时
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30秒超时

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      signal: controller.signal,
      ...options,
    };

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, config);
        clearTimeout(timeoutId); // 清除超时定时器
        
        if (!response.ok) {
          let errorMessage = `HTTP ${response.status}`;
          
          try {
            const errorData = await response.json();
            errorMessage = errorData.message || errorData.detail || errorMessage;
          } catch {
            const errorText = await response.text();
            errorMessage = errorText || errorMessage;
          }

          // 对于客户端错误（4xx），不进行重试
          if (response.status >= 400 && response.status < 500) {
            throw new Error(`请求错误: ${errorMessage}`);
          }

          // 对于服务器错误（5xx），进行重试
          if (attempt === retries) {
            throw new Error(`服务器错误: ${errorMessage}`);
          }
          
          // 等待后重试
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
          continue;
        }

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          return response.json();
        } else {
          return response.text() as unknown as T;
        }
      } catch (error) {
        if (attempt === retries) {
          if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error('无法连接到服务器，请检查后端服务是否启动');
          }
          throw error;
        }
        
        // 等待后重试
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
      }
    }

    throw new Error('请求失败，已达到最大重试次数');
  }

  // 任务管理API
  async createTask(taskData: CreateTaskRequest): Promise<ApiResponse<ScheduledTask>> {
    return this.request('/api/scheduled/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async getTasks(
    userId: string = 'default_user',
    activeOnly: boolean = false,
    page: number = 1,
    perPage: number = 20
  ): Promise<PaginatedResponse<ScheduledTask>> {
    const params = new URLSearchParams({
      user_id: userId,
      active_only: activeOnly.toString(),
      page: page.toString(),
      per_page: perPage.toString(),
    });

    return this.request(`/api/scheduled/tasks?${params}`);
  }

  async getTask(taskId: string): Promise<ApiResponse<ScheduledTask>> {
    return this.request(`/api/scheduled/tasks/${taskId}`);
  }

  async updateTask(
    taskId: string, 
    updateData: UpdateTaskRequest
  ): Promise<ApiResponse<ScheduledTask>> {
    return this.request(`/api/scheduled/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  async deleteTask(taskId: string): Promise<ApiResponse> {
    return this.request(`/api/scheduled/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  // 任务控制API
  async pauseTask(taskId: string): Promise<ApiResponse> {
    return this.request(`/api/scheduled/tasks/${taskId}/pause`, {
      method: 'POST',
    });
  }

  async resumeTask(taskId: string): Promise<ApiResponse> {
    return this.request(`/api/scheduled/tasks/${taskId}/resume`, {
      method: 'POST',
    });
  }

  async triggerTask(taskId: string, quickMode: boolean = false): Promise<ApiResponse> {
    const params = quickMode ? '?quick_mode=true' : '';
    return this.request(`/api/scheduled/tasks/${taskId}/trigger${params}`, {
      method: 'POST',
    });
  }

  // 历史记录和趋势API
  async getTaskHistory(
    taskId: string,
    page: number = 1,
    perPage: number = 10
  ): Promise<PaginatedResponse<ResearchHistoryRecord>> {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });

    return this.request(`/api/scheduled/tasks/${taskId}/history?${params}`);
  }

  async getTaskTrends(
    taskId: string,
    days: number = 30,
    page: number = 1,
    perPage: number = 10
  ): Promise<PaginatedResponse<TrendData>> {
    const params = new URLSearchParams({
      days: days.toString(),
      page: page.toString(),
      per_page: perPage.toString(),
    });

    return this.request(`/api/scheduled/tasks/${taskId}/trends?${params}`);
  }

  // 统计API
  async getTaskStatistics(taskId: string): Promise<TaskStatistics> {
    return this.request(`/api/scheduled/tasks/${taskId}/statistics`);
  }

  async getUserStatistics(userId: string = 'default_user'): Promise<UserStatistics> {
    return this.request(`/api/scheduled/users/${userId}/statistics`);
  }

  async getSchedulerStatus(): Promise<SchedulerStatus> {
    return this.request('/api/scheduled/scheduler/status');
  }

  // 测试和配置API
  async testTaskConfiguration(configData: {
    topic: string;
    keywords: string[];
    analysis_depth: 'basic' | 'detailed' | 'deep';
    source_types: string[];
  }): Promise<TestConfigResponse> {
    return this.request('/api/scheduled/test-config', {
      method: 'POST',
      body: JSON.stringify(configData),
    });
  }

  // 健康检查
  async healthCheck(): Promise<ApiResponse> {
    return this.request('/api/scheduled/health');
  }
}

// 导出单例实例
export const scheduledApiService = new ScheduledApiService();
export default scheduledApiService;
