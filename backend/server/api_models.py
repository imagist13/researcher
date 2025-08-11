"""
API模型定义 - 定时研究功能相关的请求和响应模型
API Models for scheduled research functionality
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# 请求模型
class CreateScheduledTaskRequest(BaseModel):
    """创建定时任务请求"""
    topic: str = Field(..., description="研究话题")
    keywords: List[str] = Field(..., description="关键词列表")
    description: Optional[str] = Field(None, description="任务描述")
    interval_hours: int = Field(24, description="执行间隔（小时）", ge=1, le=168)  # 1小时到1周
    analysis_depth: str = Field("basic", description="分析深度: basic, detailed, deep")
    source_types: List[str] = Field(["news", "academic"], description="信息源类型")
    report_type: str = Field("research_report", description="报告类型")
    report_source: str = Field("web", description="报告来源")
    tone: str = Field("objective", description="报告语调")
    query_domains: Optional[List[str]] = Field(None, description="查询域名限制")
    max_sources: int = Field(10, description="最大信息源数量", ge=1, le=50)
    language: str = Field("zh-CN", description="语言设置")
    enable_notifications: bool = Field(True, description="是否启用通知")
    notification_threshold: float = Field(7.0, description="通知阈值（趋势分数）", ge=0.0, le=10.0)


class UpdateScheduledTaskRequest(BaseModel):
    """更新定时任务请求"""
    topic: Optional[str] = None
    keywords: Optional[List[str]] = None
    description: Optional[str] = None
    interval_hours: Optional[int] = Field(None, ge=1, le=168)
    analysis_depth: Optional[str] = None
    source_types: Optional[List[str]] = None
    is_active: Optional[bool] = None
    query_domains: Optional[List[str]] = None
    max_sources: Optional[int] = Field(None, ge=1, le=50)
    enable_notifications: Optional[bool] = None
    notification_threshold: Optional[float] = Field(None, ge=0.0, le=10.0)


class TestTaskConfigRequest(BaseModel):
    """测试任务配置请求"""
    topic: str
    keywords: List[str]
    analysis_depth: str = "basic"
    source_types: List[str] = ["news"]


# 响应模型
class ScheduledTaskResponse(BaseModel):
    """定时任务响应"""
    id: str
    user_id: str
    topic: str
    keywords: List[str]
    description: Optional[str]
    interval_hours: int
    is_active: bool
    next_run: Optional[str]
    analysis_depth: str
    source_types: List[str]
    report_type: str
    report_source: str
    tone: str
    query_domains: Optional[List[str]]
    max_sources: int
    language: str
    enable_notifications: bool
    notification_threshold: float
    created_at: Optional[str]
    updated_at: Optional[str]
    last_run: Optional[str]
    total_runs: int
    success_runs: int
    failed_runs: int
    
    class Config:
        from_attributes = True


class ResearchHistoryResponse(BaseModel):
    """研究历史响应"""
    id: str
    task_id: str
    executed_at: Optional[str]
    execution_duration: Optional[float]
    status: str
    error_message: Optional[str]
    summary: Optional[str]
    key_findings: Optional[List[str]]
    key_changes: Optional[List[str]]
    sources_count: int
    tokens_used: int
    trend_score: Optional[float]
    sentiment_score: Optional[float]
    
    class Config:
        from_attributes = True


class TrendDataResponse(BaseModel):
    """趋势数据响应"""
    id: str
    task_id: str
    period_start: Optional[str]
    period_end: Optional[str]
    analysis_date: Optional[str]
    keyword_trends: Optional[Dict[str, float]]
    sentiment_changes: Optional[Dict[str, Any]]
    topic_evolution: Optional[Dict[str, Any]]
    new_topics: Optional[List[str]]
    emerging_keywords: Optional[List[str]]
    activity_level: Optional[float]
    change_magnitude: Optional[float]
    confidence_score: Optional[float]
    anomaly_detected: bool
    anomaly_description: Optional[str]
    
    class Config:
        from_attributes = True


class TaskStatisticsResponse(BaseModel):
    """任务统计响应"""
    task_info: Dict[str, Any]
    total_executions: int
    successful_executions: int
    success_rate: float
    average_trend_score: float
    latest_trend_data: Optional[Dict[str, Any]]
    uptime_days: int


class UserStatisticsResponse(BaseModel):
    """用户统计响应"""
    total_tasks: int
    active_tasks: int
    inactive_tasks: int
    total_executions: int
    successful_executions: int
    overall_success_rate: float


class SchedulerStatusResponse(BaseModel):
    """调度器状态响应"""
    running: bool
    total_jobs: int
    jobs: List[Dict[str, Any]]
    running_tasks: List[str]


class ApiResponse(BaseModel):
    """通用API响应"""
    success: bool
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int


class TaskExecutionResponse(BaseModel):
    """任务执行响应"""
    success: bool
    task_id: str
    execution_time: float
    summary: str
    key_changes: List[str]
    trend_score: float
    sources_count: int
    error: Optional[str] = None


class TestConfigResponse(BaseModel):
    """测试配置响应"""
    success: bool
    query_generated: str
    sources_found: int
    research_preview: str
    error: Optional[str] = None
