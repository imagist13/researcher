"""
数据库初始化脚本
Database initialization script
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .database import init_database, check_database_connection
from .models import ScheduledTask, ResearchHistory, TrendData, TaskExecutionLog
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_data():
    """创建示例数据（仅用于开发和测试）"""
    from .dao import ScheduledTaskDAO
    from datetime import datetime, timedelta
    
    try:
        # 创建示例定时任务
        sample_task_data = {
            "topic": "人工智能技术发展动态",
            "keywords": ["人工智能", "AI技术", "机器学习", "深度学习", "技术趋势"],
            "description": "追踪人工智能领域的最新技术发展和行业动态",
            "interval_hours": 24,
            "analysis_depth": "detailed",
            "source_types": ["news", "academic", "industry_reports"],
            "report_type": "research_report",
            "report_source": "web",
            "tone": "objective",
            "max_sources": 15,
            "language": "zh-CN",
            "enable_notifications": True,
            "notification_threshold": 7.0
        }
        
        task = ScheduledTaskDAO.create_task(sample_task_data)
        logger.info(f"Created sample task: {task.id} - {task.topic}")
        
        # 创建另一个示例任务
        sample_task_data_2 = {
            "topic": "区块链技术与加密货币市场",
            "keywords": ["区块链", "比特币", "以太坊", "DeFi", "NFT", "Web3"],
            "description": "监控区块链技术发展和加密货币市场变化",
            "interval_hours": 12,
            "analysis_depth": "basic",
            "source_types": ["news", "social_media", "financial_reports"],
            "report_type": "research_report",
            "report_source": "web",
            "tone": "analytical",
            "max_sources": 10,
            "language": "zh-CN",
            "enable_notifications": True,
            "notification_threshold": 6.5
        }
        
        task2 = ScheduledTaskDAO.create_task(sample_task_data_2)
        logger.info(f"Created sample task: {task2.id} - {task2.topic}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        return False


def main():
    """主函数：初始化数据库"""
    logger.info("Starting database initialization...")
    
    try:
        # 检查数据库连接
        logger.info("Checking database connection...")
        if not check_database_connection():
            logger.error("Database connection failed!")
            return False
        
        # 初始化数据库表
        logger.info("Creating database tables...")
        init_database()
        logger.info("Database tables created successfully!")
        
        # 询问是否创建示例数据
        create_samples = os.getenv("CREATE_SAMPLE_DATA", "false").lower() == "true"
        if create_samples:
            logger.info("Creating sample data...")
            if create_sample_data():
                logger.info("Sample data created successfully!")
            else:
                logger.warning("Failed to create sample data, but database initialization completed.")
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
