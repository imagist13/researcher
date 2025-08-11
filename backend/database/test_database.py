"""
数据库功能测试脚本
Database functionality test script
"""
import os
import sys
from pathlib import Path
import asyncio
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from . import (
    init_database, 
    check_database_connection,
    ScheduledTaskDAO,
    ResearchHistoryDAO,
    TrendDataDAO,
    AnalyticsDAO
)
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database_connection():
    """测试数据库连接"""
    logger.info("Testing database connection...")
    return check_database_connection()


def test_task_operations():
    """测试定时任务操作"""
    logger.info("Testing scheduled task operations...")
    
    try:
        # 创建测试任务
        task_data = {
            "topic": "测试话题：AI发展趋势",
            "keywords": ["AI", "机器学习", "技术趋势"],
            "description": "这是一个测试任务",
            "interval_hours": 6,
            "analysis_depth": "basic",
            "source_types": ["news", "academic"],
            "report_type": "research_report",
            "report_source": "web",
            "tone": "objective"
        }
        
        # 创建任务
        task = ScheduledTaskDAO.create_task(task_data)
        logger.info(f"✅ Created task: {task.id}")
        
        # 获取任务
        retrieved_task = ScheduledTaskDAO.get_task_by_id(task.id)
        assert retrieved_task is not None, "Failed to retrieve created task"
        logger.info(f"✅ Retrieved task: {retrieved_task.topic}")
        
        # 更新任务
        update_data = {"description": "更新后的描述", "interval_hours": 12}
        updated_task = ScheduledTaskDAO.update_task(task.id, update_data)
        assert updated_task.description == "更新后的描述", "Failed to update task"
        logger.info(f"✅ Updated task description")
        
        # 获取用户任务列表
        user_tasks = ScheduledTaskDAO.get_tasks_by_user("default_user")
        assert len(user_tasks) >= 1, "Failed to get user tasks"
        logger.info(f"✅ Found {len(user_tasks)} user tasks")
        
        # 测试待执行任务查询
        pending_tasks = ScheduledTaskDAO.get_pending_tasks()
        logger.info(f"✅ Found {len(pending_tasks)} pending tasks")
        
        return task.id
        
    except Exception as e:
        logger.error(f"❌ Task operations test failed: {e}")
        raise


def test_research_history_operations(task_id: str):
    """测试研究历史操作"""
    logger.info("Testing research history operations...")
    
    try:
        # 创建测试历史记录
        history_data = {
            "task_id": task_id,
            "raw_result": "这是测试的研究结果内容...",
            "summary": "这是AI生成的摘要",
            "key_findings": ["发现1", "发现2", "发现3"],
            "key_changes": ["变化1", "变化2"],
            "sources_count": 5,
            "tokens_used": 1500,
            "trend_score": 7.5,
            "sentiment_score": 0.3,
            "status": "success"
        }
        
        # 创建历史记录
        history = ResearchHistoryDAO.create_history(history_data)
        logger.info(f"✅ Created research history: {history.id}")
        
        # 获取任务历史
        task_histories = ResearchHistoryDAO.get_history_by_task(task_id)
        assert len(task_histories) >= 1, "Failed to get task histories"
        logger.info(f"✅ Found {len(task_histories)} histories for task")
        
        # 获取最新历史
        latest_history = ResearchHistoryDAO.get_latest_history(task_id)
        assert latest_history is not None, "Failed to get latest history"
        logger.info(f"✅ Retrieved latest history: {latest_history.summary}")
        
        # 更新历史记录
        update_data = {"summary": "更新后的摘要", "trend_score": 8.0}
        updated_history = ResearchHistoryDAO.update_history(history.id, update_data)
        assert updated_history.trend_score == 8.0, "Failed to update history"
        logger.info(f"✅ Updated history trend score to {updated_history.trend_score}")
        
        return history.id
        
    except Exception as e:
        logger.error(f"❌ Research history operations test failed: {e}")
        raise


def test_trend_data_operations(task_id: str):
    """测试趋势数据操作"""
    logger.info("Testing trend data operations...")
    
    try:
        # 创建测试趋势数据
        trend_data = {
            "task_id": task_id,
            "period_start": datetime.now() - timedelta(days=1),
            "period_end": datetime.now(),
            "keyword_trends": {
                "AI": 8.5,
                "机器学习": 7.2,
                "技术趋势": 6.8
            },
            "sentiment_changes": {
                "positive": 0.6,
                "neutral": 0.3,
                "negative": 0.1
            },
            "new_topics": ["量子计算", "边缘AI"],
            "emerging_keywords": ["量子AI", "边缘计算"],
            "activity_level": 8.0,
            "change_magnitude": 6.5,
            "confidence_score": 0.85
        }
        
        # 创建趋势数据
        trend = TrendDataDAO.create_trend_data(trend_data)
        logger.info(f"✅ Created trend data: {trend.id}")
        
        # 获取任务趋势数据
        task_trends = TrendDataDAO.get_trend_data_by_task(task_id)
        assert len(task_trends) >= 1, "Failed to get task trends"
        logger.info(f"✅ Found {len(task_trends)} trend data for task")
        
        # 获取最新趋势数据
        latest_trend = TrendDataDAO.get_latest_trend_data(task_id)
        assert latest_trend is not None, "Failed to get latest trend"
        logger.info(f"✅ Retrieved latest trend: activity_level={latest_trend.activity_level}")
        
        return trend.id
        
    except Exception as e:
        logger.error(f"❌ Trend data operations test failed: {e}")
        raise


def test_analytics_operations(task_id: str):
    """测试分析统计操作"""
    logger.info("Testing analytics operations...")
    
    try:
        # 获取任务统计
        task_stats = AnalyticsDAO.get_task_statistics(task_id)
        assert "task_info" in task_stats, "Failed to get task statistics"
        logger.info(f"✅ Task statistics: {task_stats['total_executions']} executions")
        
        # 获取用户统计
        user_stats = AnalyticsDAO.get_user_statistics("default_user")
        assert "total_tasks" in user_stats, "Failed to get user statistics"
        logger.info(f"✅ User statistics: {user_stats['total_tasks']} tasks")
        
    except Exception as e:
        logger.error(f"❌ Analytics operations test failed: {e}")
        raise


def cleanup_test_data(task_id: str):
    """清理测试数据"""
    logger.info("Cleaning up test data...")
    
    try:
        # 删除测试任务（会级联删除相关数据）
        success = ScheduledTaskDAO.delete_task(task_id)
        if success:
            logger.info("✅ Test data cleaned up successfully")
        else:
            logger.warning("⚠️ Failed to clean up test data")
            
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")


def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 Starting database functionality tests...")
    
    try:
        # 初始化数据库
        logger.info("Initializing database...")
        init_database()
        
        # 测试数据库连接
        if not test_database_connection():
            raise Exception("Database connection test failed")
        
        # 测试任务操作
        task_id = test_task_operations()
        
        # 测试研究历史操作
        history_id = test_research_history_operations(task_id)
        
        # 测试趋势数据操作
        trend_id = test_trend_data_operations(task_id)
        
        # 测试分析统计操作
        test_analytics_operations(task_id)
        
        logger.info("🎉 All database tests passed successfully!")
        
        # 询问是否清理测试数据
        cleanup = os.getenv("CLEANUP_TEST_DATA", "true").lower() == "true"
        if cleanup:
            cleanup_test_data(task_id)
        
        return True
        
    except Exception as e:
        logger.error(f"💥 Database tests failed: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        sys.exit(1)
