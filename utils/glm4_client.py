"""
智谱AI GLM-4客户端
专门用于调用GLM-4-Flash（永久免费大模型）
"""

import os
import requests
from typing import List, Dict, Any, Optional
from loguru import logger
import time


class GLM4Client:
    """智谱AI GLM-4大模型客户端
    
    用于调用智谱AI提供的GLM-4-Flash模型，永久免费。
    支持聊天完成，自带重试机制。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化GLM-4客户端
        
        Args:
            config: GLM-4配置字典
        """
        self.config = config
        self.provider_config = config.get('glm', {})
        
        # 从环境变量或配置文件获取API密钥
        self.api_key = os.getenv('GLM_API_KEY') or self.provider_config.get('api_key')
        
        if not self.api_key:
            logger.warning("⚠️ 未设置GLM API Key，请访问 https://open.bigmodel.cn 获取")
        
        self.api_base = self.provider_config.get('api_base')
        self.models = self.provider_config.get('models', {})
        self.temperature = self.provider_config.get('temperature', 0.7)
        self.max_tokens = self.provider_config.get('max_tokens', 4096)
        
        logger.info(f"✅ GLM-4客户端初始化成功 - 使用永久免费的GLM-4-Flash")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        GLM-4聊天接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            model: 模型名称（默认使用glm-4-flash）
            temperature: 温度参数（0-1，控制创造性）
            max_tokens: 最大输出token数
            
        Returns:
            模型回复文本
        """
        url = f"{self.api_base}/chat/completions"
        
        payload = {
            "model": model or self.models.get('flash', 'glm-4-flash'),
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            "top_p": self.provider_config.get('top_p', 0.9),
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            logger.debug(f"调用GLM-4 API: {model or 'glm-4-flash'}")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            logger.debug(f"GLM-4响应成功，长度: {len(content)}")
            return content
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"GLM API HTTP错误: {e.response.status_code}"
            if e.response.text:
                error_msg += f" - {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"GLM API调用失败: {e}")
            raise
    
    def chat_with_retry(
        self,
        messages: List[Dict[str, str]],
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        带重试的聊天接口
        
        Args:
            messages: 消息列表
            max_retries: 最大重试次数
            **kwargs: 其他参数
            
        Returns:
            模型回复
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return self.chat(messages, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    logger.warning(f"API调用失败，{wait_time}秒后重试 ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
        
        raise Exception(f"API调用失败，已重试{max_retries}次: {last_error}")


def get_glm4_client(config_path: str = None) -> GLM4Client:
    """
    获取GLM-4客户端实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        GLM-4客户端实例
    """
    import yaml
    
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config',
            'glm4_config.yaml'
        )
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return GLM4Client(config)


# 使用示例
if __name__ == '__main__':
    # 创建客户端
    client = get_glm4_client()
    
    # 简单对话测试
    messages = [
        {"role": "system", "content": "你是一个专业的健康饮食助手"},
        {"role": "user", "content": "减肥期间应该吃什么？"}
    ]
    
    print("测试GLM-4-Flash...")
    response = client.chat(messages)
    print(f"回复: {response}")