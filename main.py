import logging
from pathlib import Path
from config_manager import ConfigManager

# 初始化配置管理器
config = ConfigManager()

# Create logs directory if it doesn't exist
logs_dir = Path(config.get('paths.logs', './logs'))
logs_dir.mkdir(exist_ok=True)

# Configure logging based on config
log_level = getattr(logging, config.get('logging.level', 'INFO').upper())
verbose = config.get('logging.verbose', False)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # File handler for general application logs
        logging.FileHandler(logs_dir / 'app.log'),
        # Stream handler for console output
        logging.StreamHandler()
    ]
)

# Set module-specific log levels from config
fonttools_level = getattr(logging, config.get('logging.modules.fontTools', 'WARNING').upper())
logging.getLogger('fontTools').setLevel(fonttools_level)
logging.getLogger('fontTools.subset').setLevel(fonttools_level)
logging.getLogger('fontTools.ttLib').setLevel(fonttools_level)

transformers_level = getattr(logging, config.get('logging.modules.transformers', 'WARNING').upper())
logging.getLogger('transformers').setLevel(transformers_level)

# Create logger instance
logger = logging.getLogger(__name__)

# 显示配置信息
logger.info(f"使用配置文件：{config.config_path}")
logger.info(f"日志级别：{config.get('logging.level', 'INFO')}")
logger.info(f"详细模式：{verbose}")

from backend.server.server import app

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
