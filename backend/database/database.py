"""
数据库连接和配置管理
Database connection and configuration management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging

logger = logging.getLogger(__name__)

# 数据库文件路径
DATABASE_PATH = os.getenv("DATABASE_PATH", "./backend/database/scheduled_research.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # SQLite特定配置
        "timeout": 20,  # 连接超时
    },
    poolclass=StaticPool,
    echo=bool(os.getenv("DEBUG_DB", False))  # 开发环境下显示SQL语句
)

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类
Base = declarative_base()

def get_database():
    """
    获取数据库会话
    Get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """
    初始化数据库，创建所有表
    Initialize database and create all tables
    """
    try:
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized successfully at {DATABASE_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def check_database_connection():
    """
    检查数据库连接是否正常
    Check if database connection is working
    """
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
