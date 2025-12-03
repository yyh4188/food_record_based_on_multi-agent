"""
配置加载工具
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger


def load_config(config_file: str) -> Dict[str, Any]:
    """
    加载YAML配置文件
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置字典
    """
    config_path = Path(config_file)
    
    if not config_path.exists():
        logger.warning(f"配置文件不存在: {config_file}")
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"配置文件加载成功: {config_file}")
        return config or {}
        
    except Exception as e:
        logger.error(f"配置文件加载失败: {str(e)}")
        return {}


def save_config(config: Dict[str, Any], config_file: str):
    """
    保存配置到YAML文件
    
    Args:
        config: 配置字典
        config_file: 配置文件路径
    """
    config_path = Path(config_file)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"配置文件保存成功: {config_file}")
        
    except Exception as e:
        logger.error(f"配置文件保存失败: {str(e)}")
