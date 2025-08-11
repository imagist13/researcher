export interface BaseData {
  type: string;
}

export interface BasicData extends BaseData {
  type: 'basic';
  content: string;
}

export interface LanggraphButtonData extends BaseData {
  type: 'langgraphButton';
  link: string;
}

export interface DifferencesData extends BaseData {
  type: 'differences';
  content: string;
  output: string;
}

export interface QuestionData extends BaseData {
  type: 'question';
  content: string;
}

export interface ChatData extends BaseData {
  type: 'chat';
  content: string;
}

export interface ErrorData extends BaseData {
  type: 'error';
  content: string;
  output: string;
}

export type Data = BasicData | LanggraphButtonData | DifferencesData | QuestionData | ChatData | ErrorData;

export interface ChatBoxSettings {
  report_type: string;
  report_source: string;
  tone: string;
  domains: string[];
  defaultReportType: string;
  mcp_enabled: boolean;
  mcp_configs: MCPConfig[];
}

export interface MCPConfig {
  name: string;
  command: string;
  args: string[];
  env: Record<string, string>;
}

export interface Domain {
  value: string;
}

export interface ResearchHistoryItem {
  id: string;
  question: string;
  answer: string;
  timestamp: number;
  orderedData: Data[];
}

// 定时研究相关类型定义
export interface ScheduledTask {
  id: string;
  user_id: string;
  topic: string;
  keywords: string[];
  description?: string;
  interval_hours: number;
  is_active: boolean;
  next_run?: string;
  analysis_depth: 'basic' | 'detailed' | 'deep';
  source_types: string[];
  report_type: string;
  report_source: string;
  tone: string;
  query_domains?: string[];
  max_sources: number;
  language: string;
  enable_notifications: boolean;
  notification_threshold: number;
  created_at?: string;
  updated_at?: string;
  last_run?: string;
  total_runs: number;
  success_runs: number;
  failed_runs: number;
}

export interface ResearchHistoryRecord {
  id: string;
  task_id: string;
  executed_at: string;
  execution_duration?: number;
  status: 'success' | 'failed' | 'partial';
  error_message?: string;
  raw_result?: string;
  summary?: string;
  key_findings?: string[];
  key_changes?: string[];
  sources_count: number;
  tokens_used: number;
  trend_score?: number;
  sentiment_score?: number;
  research_config?: Record<string, any>;
  sources_used?: Record<string, any>[];
}

export interface TrendData {
  id: string;
  task_id: string;
  period_start?: string;
  period_end?: string;
  analysis_date?: string;
  keyword_trends?: Record<string, number>;
  sentiment_changes?: Record<string, any>;
  topic_evolution?: Record<string, any>;
  new_topics?: string[];
  emerging_keywords?: string[];
  activity_level?: number;
  change_magnitude?: number;
  confidence_score?: number;
  anomaly_detected: boolean;
  anomaly_description?: string;
}

export interface TaskStatistics {
  task_info: Record<string, any>;
  total_executions: number;
  successful_executions: number;
  success_rate: number;
  average_trend_score: number;
  latest_trend_data?: Record<string, any>;
  uptime_days: number;
}

export interface UserStatistics {
  total_tasks: number;
  active_tasks: number;
  inactive_tasks: number;
  total_executions: number;
  successful_executions: number;
  overall_success_rate: number;
}

export interface SchedulerStatus {
  running: boolean;
  total_jobs: number;
  jobs: Array<Record<string, any>>;
  running_tasks: string[];
}

export interface CreateTaskRequest {
  topic: string;
  keywords: string[];
  description?: string;
  interval_hours: number;
  analysis_depth: 'basic' | 'detailed' | 'deep';
  source_types: string[];
  report_type?: string;
  report_source?: string;
  tone?: string;
  query_domains?: string[];
  max_sources?: number;
  language?: string;
  enable_notifications?: boolean;
  notification_threshold?: number;
}

export interface UpdateTaskRequest {
  topic?: string;
  keywords?: string[];
  description?: string;
  interval_hours?: number;
  analysis_depth?: 'basic' | 'detailed' | 'deep';
  source_types?: string[];
  is_active?: boolean;
  query_domains?: string[];
  max_sources?: number;
  enable_notifications?: boolean;
  notification_threshold?: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface TaskExecutionResponse {
  success: boolean;
  task_id: string;
  execution_time: number;
  summary: string;
  key_changes: string[];
  trend_score: number;
  sources_count: number;
  error?: string;
}

export interface TestConfigResponse {
  success: boolean;
  query_generated: string;
  sources_found: number;
  research_preview: string;
  error?: string;
}

// WebSocket消息类型
export interface ScheduledResultMessage {
  type: 'scheduled_result';
  task_id: string;
  topic: string;
  timestamp: string;
  summary: string;
  key_changes: string[];
  trend_score: number;
  sources_count: number;
} 