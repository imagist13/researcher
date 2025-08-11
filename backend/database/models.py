"""
数据模型定义
Data models for scheduled research functionality
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, Float, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid

from .database import Base


class ScheduledTask(Base):
    """
    定时研究任务模型
    Scheduled research task model
    """
    __tablename__ = "scheduled_tasks"

    # 基础字段
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, default="default_user")  # 用户ID，未来扩展用户系统时使用
    
    # 任务配置
    topic = Column(String(500), nullable=False)  # 研究话题
    keywords = Column(JSON, nullable=False)  # 关键词列表，存储为JSON
    description = Column(Text, nullable=True)  # 任务描述
    
    # 调度配置
    interval_hours = Column(Integer, nullable=False, default=24)  # 执行间隔（小时）
    is_active = Column(Boolean, default=True)  # 是否激活
    next_run = Column(DateTime, nullable=False)  # 下次执行时间
    
    # 研究配置
    analysis_depth = Column(String(20), nullable=False, default="basic")  # 分析深度: basic, detailed, deep
    source_types = Column(JSON, nullable=False)  # 信息源类型列表
    report_type = Column(String(50), nullable=False, default="research_report")  # 报告类型
    report_source = Column(String(50), nullable=False, default="web")  # 报告来源
    tone = Column(String(20), nullable=False, default="objective")  # 报告语调
    
    # 高级配置
    query_domains = Column(JSON, nullable=True)  # 查询域名限制
    max_sources = Column(Integer, default=10)  # 最大信息源数量
    language = Column(String(10), default="zh-CN")  # 语言设置
    
    # 通知配置
    enable_notifications = Column(Boolean, default=True)  # 是否启用通知
    notification_threshold = Column(Float, default=0.0)  # 通知阈值（趋势变化分数）
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_run = Column(DateTime, nullable=True)  # 上次执行时间
    
    # 状态统计
    total_runs = Column(Integer, default=0)  # 总执行次数
    success_runs = Column(Integer, default=0)  # 成功执行次数
    failed_runs = Column(Integer, default=0)  # 失败执行次数
    
    # 关联关系
    research_histories = relationship("ResearchHistory", back_populates="task", cascade="all, delete-orphan")
    trend_data = relationship("TrendData", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ScheduledTask(id={self.id}, topic={self.topic}, active={self.is_active})>"

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "topic": self.topic,
            "keywords": self.keywords,
            "description": self.description,
            "interval_hours": self.interval_hours,
            "is_active": self.is_active,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "analysis_depth": self.analysis_depth,
            "source_types": self.source_types,
            "report_type": self.report_type,
            "report_source": self.report_source,
            "tone": self.tone,
            "query_domains": self.query_domains,
            "max_sources": self.max_sources,
            "language": self.language,
            "enable_notifications": self.enable_notifications,
            "notification_threshold": self.notification_threshold,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "total_runs": self.total_runs,
            "success_runs": self.success_runs,
            "failed_runs": self.failed_runs,
        }

    def update_next_run(self):
        """更新下次执行时间"""
        self.next_run = datetime.now() + timedelta(hours=self.interval_hours)

    def should_run(self) -> bool:
        """检查是否应该执行"""
        return self.is_active and self.next_run and datetime.now() >= self.next_run


class ResearchHistory(Base):
    """
    研究历史记录模型
    Research history model
    """
    __tablename__ = "research_histories"

    # 基础字段
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("scheduled_tasks.id"), nullable=False)
    
    # 执行信息
    executed_at = Column(DateTime, default=func.now())
    execution_duration = Column(Float, nullable=True)  # 执行时长（秒）
    status = Column(String(20), nullable=False, default="success")  # success, failed, partial
    error_message = Column(Text, nullable=True)  # 错误信息
    
    # 研究结果
    raw_result = Column(Text, nullable=True)  # 原始研究结果
    summary = Column(Text, nullable=True)  # AI生成的摘要
    key_findings = Column(JSON, nullable=True)  # 关键发现列表
    key_changes = Column(JSON, nullable=True)  # 相比上次的关键变化
    
    # 统计信息
    sources_count = Column(Integer, default=0)  # 使用的信息源数量
    tokens_used = Column(Integer, default=0)  # 使用的token数量
    trend_score = Column(Float, nullable=True)  # 趋势变化分数 (0-10)
    sentiment_score = Column(Float, nullable=True)  # 情感分数 (-1 to 1)
    
    # 元数据
    research_config = Column(JSON, nullable=True)  # 研究配置快照
    sources_used = Column(JSON, nullable=True)  # 使用的信息源列表
    
    # 关联关系
    task = relationship("ScheduledTask", back_populates="research_histories")

    def __repr__(self):
        return f"<ResearchHistory(id={self.id}, task_id={self.task_id}, status={self.status})>"

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "execution_duration": self.execution_duration,
            "status": self.status,
            "error_message": self.error_message,
            "raw_result": self.raw_result,
            "summary": self.summary,
            "key_findings": self.key_findings,
            "key_changes": self.key_changes,
            "sources_count": self.sources_count,
            "tokens_used": self.tokens_used,
            "trend_score": self.trend_score,
            "sentiment_score": self.sentiment_score,
            "research_config": self.research_config,
            "sources_used": self.sources_used,
        }


class TrendData(Base):
    """
    趋势分析数据模型
    Trend analysis data model
    """
    __tablename__ = "trend_data"

    # 基础字段
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("scheduled_tasks.id"), nullable=False)
    
    # 时间周期
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    analysis_date = Column(DateTime, default=func.now())
    
    # 趋势分析
    keyword_trends = Column(JSON, nullable=True)  # 关键词趋势变化 {keyword: trend_score}
    sentiment_changes = Column(JSON, nullable=True)  # 情感变化 {period: sentiment_score}
    topic_evolution = Column(JSON, nullable=True)  # 话题演变数据
    
    # 新发现
    new_topics = Column(JSON, nullable=True)  # 新出现的相关话题
    emerging_keywords = Column(JSON, nullable=True)  # 新兴关键词
    trending_sources = Column(JSON, nullable=True)  # 热门信息源
    
    # 统计指标
    activity_level = Column(Float, nullable=True)  # 活跃度分数 (0-10)
    change_magnitude = Column(Float, nullable=True)  # 变化幅度 (0-10)
    confidence_score = Column(Float, nullable=True)  # 置信度分数 (0-1)
    
    # 对比分析
    comparison_data = Column(JSON, nullable=True)  # 与历史数据的对比分析
    anomaly_detected = Column(Boolean, default=False)  # 是否检测到异常
    anomaly_description = Column(Text, nullable=True)  # 异常描述
    
    # 关联关系
    task = relationship("ScheduledTask", back_populates="trend_data")

    def __repr__(self):
        return f"<TrendData(id={self.id}, task_id={self.task_id}, period={self.period_start}-{self.period_end})>"

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "analysis_date": self.analysis_date.isoformat() if self.analysis_date else None,
            "keyword_trends": self.keyword_trends,
            "sentiment_changes": self.sentiment_changes,
            "topic_evolution": self.topic_evolution,
            "new_topics": self.new_topics,
            "emerging_keywords": self.emerging_keywords,
            "trending_sources": self.trending_sources,
            "activity_level": self.activity_level,
            "change_magnitude": self.change_magnitude,
            "confidence_score": self.confidence_score,
            "comparison_data": self.comparison_data,
            "anomaly_detected": self.anomaly_detected,
            "anomaly_description": self.anomaly_description,
        }


class TaskExecutionLog(Base):
    """
    任务执行日志模型
    Task execution log model
    """
    __tablename__ = "task_execution_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("scheduled_tasks.id"), nullable=False)
    
    # 执行信息
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)  # running, completed, failed, cancelled
    
    # 执行详情
    execution_step = Column(String(100), nullable=True)  # 当前执行步骤
    progress_percentage = Column(Float, default=0.0)  # 执行进度百分比
    log_messages = Column(JSON, nullable=True)  # 日志消息列表
    
    # 资源使用
    memory_usage = Column(Float, nullable=True)  # 内存使用量(MB)
    cpu_usage = Column(Float, nullable=True)  # CPU使用率
    api_calls_made = Column(Integer, default=0)  # API调用次数
    
    def __repr__(self):
        return f"<TaskExecutionLog(id={self.id}, task_id={self.task_id}, status={self.status})>"

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "execution_step": self.execution_step,
            "progress_percentage": self.progress_percentage,
            "log_messages": self.log_messages,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage,
            "api_calls_made": self.api_calls_made,
        }
