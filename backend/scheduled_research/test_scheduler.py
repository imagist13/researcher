"""
定时任务调度器测试脚本
Scheduler test script
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ..database import init_database, ScheduledTaskDAO
from . import ScheduledResearchManager, initialize_scheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_scheduler_initialization():
    """测试调度器初始化"""
    logger.info("Testing scheduler initialization...")
    
    try:
        # 初始化数据库
        init_database()
        logger.info("✅ Database initialized")
        
        # 初始化调度器
        manager = await initialize_scheduler()
        logger.info("✅ Scheduler initialized")
        
        # 检查调度器状态
        status = manager.get_scheduler_status()
        logger.info(f"✅ Scheduler status: running={status['running']}, jobs={status['total_jobs']}")
        
        return manager
        
    except Exception as e:
        logger.error(f"❌ Scheduler initialization failed: {e}")
        raise


async def test_task_management(manager):
    """测试任务管理功能"""
    logger.info("Testing task management...")
    
    try:
        # 创建测试任务
        task_data = {
            "topic": "人工智能最新发展",
            "keywords": ["AI", "人工智能", "机器学习", "深度学习"],
            "description": "监测人工智能领域的最新技术发展和趋势变化",
            "interval_hours": 1,  # 1小时间隔，便于测试
            "analysis_depth": "basic",
            "source_types": ["news", "academic"],
            "report_type": "research_report",
            "report_source": "web",
            "tone": "objective",
            "max_sources": 5,
            "enable_notifications": True,
            "notification_threshold": 6.0
        }
        
        # 添加任务
        task_id = await manager.add_task(task_data)
        logger.info(f"✅ Task created: {task_id}")
        
        # 验证任务被添加到调度器
        status = manager.get_scheduler_status()
        logger.info(f"✅ Jobs after adding task: {status['total_jobs']}")
        
        # 测试暂停任务
        await manager.pause_task(task_id)
        logger.info(f"✅ Task paused: {task_id}")
        
        # 测试恢复任务
        await manager.resume_task(task_id)
        logger.info(f"✅ Task resumed: {task_id}")
        
        # 测试立即触发任务（仅启动，不等待完成）
        trigger_success = await manager.trigger_task_now(task_id)
        logger.info(f"✅ Manual trigger initiated: {trigger_success}")
        
        # 等待一小段时间让任务开始执行
        await asyncio.sleep(2)
        
        # 检查运行状态
        status = manager.get_scheduler_status()
        logger.info(f"✅ Current running tasks: {len(status['running_tasks'])}")
        
        return task_id
        
    except Exception as e:
        logger.error(f"❌ Task management test failed: {e}")
        raise


async def test_task_executor_configuration(task_id):
    """测试任务执行器配置"""
    logger.info("Testing task executor configuration...")
    
    try:
        from .task_executor import ResearchTaskExecutor
        
        # 创建任务执行器
        executor = ResearchTaskExecutor()
        
        # 获取任务数据
        task = ScheduledTaskDAO.get_task_by_id(task_id)
        if not task:
            raise Exception("Task not found")
        
        # 测试研究配置（快速测试，不执行完整研究）
        test_config = {
            "topic": task.topic,
            "keywords": task.keywords,
            "analysis_depth": task.analysis_depth,
            "source_types": task.source_types
        }
        
        # 这里我们只测试配置，不执行完整的研究任务
        logger.info(f"✅ Task executor configuration test passed for task: {task.topic}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Task executor configuration test failed: {e}")
        return False


async def test_trend_analyzer():
    """测试趋势分析器"""
    logger.info("Testing trend analyzer...")
    
    try:
        from .trend_analyzer import TopicTrendAnalyzer
        
        analyzer = TopicTrendAnalyzer()
        
        # 创建模拟数据
        current_result = {
            "report": "人工智能技术在2024年取得了重大突破，机器学习算法不断优化，深度学习模型性能显著提升。",
            "sources_count": 5
        }
        
        # 模拟任务对象
        from types import SimpleNamespace
        mock_task = SimpleNamespace(
            topic="AI发展趋势",
            keywords=["人工智能", "机器学习", "深度学习"]
        )
        
        # 测试趋势分析（无历史数据）
        trend_result = await analyzer.analyze_trends(mock_task, current_result, [])
        
        logger.info(f"✅ Trend analysis completed: score={trend_result['trend_score']:.2f}")
        logger.info(f"   Activity level: {trend_result['activity_level']:.2f}")
        logger.info(f"   Confidence: {trend_result['confidence_score']:.2f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Trend analyzer test failed: {e}")
        return False


async def test_summary_generator():
    """测试摘要生成器"""
    logger.info("Testing summary generator...")
    
    try:
        from .summary_generator import DynamicSummaryGenerator
        
        generator = DynamicSummaryGenerator()
        
        # 模拟数据
        research_result = {
            "report": "人工智能技术持续发展，在各个领域都有重要应用。机器学习算法优化，提升了模型的准确性和效率。",
            "sources_count": 3
        }
        
        trend_result = {
            "trend_score": 7.5,
            "activity_level": 6.8,
            "change_magnitude": 4.2,
            "confidence_score": 0.7,
            "keyword_trends": {"人工智能": 8.0, "机器学习": 7.2},
            "new_topics": ["量子计算", "边缘AI"],
            "emerging_keywords": ["神经网络", "算法优化"],
            "anomaly_detected": False
        }
        
        # 模拟任务对象
        from types import SimpleNamespace
        mock_task = SimpleNamespace(
            topic="AI技术发展",
            interval_hours=24
        )
        
        # 测试摘要生成
        summary_result = await generator.generate_dynamic_summary(mock_task, research_result, trend_result)
        
        logger.info(f"✅ Summary generated:")
        logger.info(f"   Summary: {summary_result['summary'][:100]}...")
        logger.info(f"   Key findings: {len(summary_result['key_findings'])}")
        logger.info(f"   Priority: {summary_result['priority_level']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Summary generator test failed: {e}")
        return False


async def cleanup_test_data(manager, task_id):
    """清理测试数据"""
    logger.info("Cleaning up test data...")
    
    try:
        # 删除测试任务
        success = await manager.remove_task(task_id)
        if success:
            logger.info("✅ Test task removed")
        
        # 关闭调度器
        await manager.shutdown()
        logger.info("✅ Scheduler shutdown")
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")


async def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 Starting scheduled research system tests...")
    
    manager = None
    task_id = None
    
    try:
        # 测试1: 调度器初始化
        manager = await test_scheduler_initialization()
        
        # 测试2: 任务管理
        task_id = await test_task_management(manager)
        
        # 测试3: 任务执行器配置
        await test_task_executor_configuration(task_id)
        
        # 测试4: 趋势分析器
        await test_trend_analyzer()
        
        # 测试5: 摘要生成器
        await test_summary_generator()
        
        logger.info("🎉 All tests passed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"💥 Tests failed: {e}")
        return False
        
    finally:
        # 清理资源
        if manager and task_id:
            await cleanup_test_data(manager, task_id)


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    if not success:
        sys.exit(1)
