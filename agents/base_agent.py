"""
智能体基类
所有智能体都需要继承此基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from loguru import logger
import time


class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        """
        初始化智能体
        
        Args:
            agent_id: 智能体唯一标识
            config: 智能体配置
        """
        self.agent_id = agent_id
        self.config = config
        self.enabled = config.get('enabled', True)
        self.priority = config.get('priority', 5)
        self.status = 'idle'  # idle, busy, error
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_time': 0.0,
            'average_time': 0.0
        }
        
        # 初始化日志
        self.logger = logger.bind(agent=self.agent_id)
        self.logger.info(f"智能体 {self.agent_id} 初始化完成")
        
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理任务的核心方法（需要子类实现）
        
        Args:
            input_data: 输入数据
            
        Returns:
            处理结果
        """
        pass
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务（带状态管理和统计）
        
        Args:
            input_data: 输入数据
            
        Returns:
            执行结果
        """
        if not self.enabled:
            return {
                'success': False,
                'error': f'智能体 {self.agent_id} 未启用'
            }
        
        self.status = 'busy'
        self.stats['total_requests'] += 1
        start_time = time.time()
        
        try:
            self.logger.info(f"开始处理任务: {input_data.get('task_type', 'unknown')}")
            
            # 调用子类实现的处理方法
            result = self.process(input_data)
            
            # 更新统计信息
            elapsed_time = time.time() - start_time
            self.stats['successful_requests'] += 1
            self.stats['total_time'] += elapsed_time
            self.stats['average_time'] = self.stats['total_time'] / self.stats['total_requests']
            
            self.logger.info(f"任务处理完成，耗时: {elapsed_time:.2f}秒")
            
            self.status = 'idle'
            return {
                'success': True,
                'agent_id': self.agent_id,
                'data': result,
                'execution_time': elapsed_time
            }
            
        except Exception as e:
            # 处理错误
            elapsed_time = time.time() - start_time
            self.stats['failed_requests'] += 1
            self.status = 'error'
            
            self.logger.error(f"任务处理失败: {str(e)}")
            
            return {
                'success': False,
                'agent_id': self.agent_id,
                'error': str(e),
                'execution_time': elapsed_time
            }
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            'agent_id': self.agent_id,
            'status': self.status,
            'enabled': self.enabled,
            'priority': self.priority,
            'stats': self.stats
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_time': 0.0,
            'average_time': 0.0
        }
        self.logger.info("统计信息已重置")
    
    def enable(self):
        """启用智能体"""
        self.enabled = True
        self.logger.info("智能体已启用")
    
    def disable(self):
        """禁用智能体"""
        self.enabled = False
        self.logger.info("智能体已禁用")
