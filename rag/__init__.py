"""
RAG 模块 - 基于 NeutronRAG 的适配层
不修改 NeutronRAG-main 的任何内容，只提供适配接口
"""

from .neutron_rag_adapter import NeutronRAGAdapter
from .knowledge_manager import NutritionKnowledgeManager

__all__ = [
    'NeutronRAGAdapter',
    'NutritionKnowledgeManager'
]
