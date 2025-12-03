"""
日志管理工具
"""

from loguru import logger
import sys
from pathlib import Path


def setup_logger(log_file: str = "logs/multi_agent.log", level: str = "INFO"):
    """
    设置日志系统
    
    Args:
        log_file: 日志文件路径
        level: 日志级别
    """
    # 创建日志目录
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 移除默认handler
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # 添加文件输出
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=level,
        rotation="100 MB",
        retention="1 week",
        compression="zip"
    )
    
    logger.info("日志系统初始化完成")
    
    return logger
