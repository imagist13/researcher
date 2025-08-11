"""
数据库模块 - 定时研究功能
Database module for scheduled research functionality
"""

from .database import (
    get_database,
    init_database,
    check_database_connection,
    SessionLocal,
    engine,
    Base
)

from .models import (
    ScheduledTask,
    ResearchHistory,
    TrendData,
    TaskExecutionLog
)

from .dao import (
    ScheduledTaskDAO,
    ResearchHistoryDAO,
    TrendDataDAO,
    TaskExecutionLogDAO,
    AnalyticsDAO
)

__all__ = [
    # Database connection and configuration
    "get_database",
    "init_database", 
    "check_database_connection",
    "SessionLocal",
    "engine",
    "Base",
    
    # Data models
    "ScheduledTask",
    "ResearchHistory",
    "TrendData", 
    "TaskExecutionLog",
    
    # Data access objects
    "ScheduledTaskDAO",
    "ResearchHistoryDAO",
    "TrendDataDAO",
    "TaskExecutionLogDAO",
    "AnalyticsDAO"
]
