"""
NeutronRAG 适配器
将 NeutronRAG 系统适配到多智能体项目中
"""

import sys
import os
from typing import Dict, Any, List, Optional
from loguru import logger

# 添加 NeutronRAG 路径到 Python 路径
NEUTRON_RAG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'NeutronRAG-main',
    'NeutronRAG-main',
    'backend'
)

if NEUTRON_RAG_PATH not in sys.path:
    sys.path.insert(0, NEUTRON_RAG_PATH)


class NeutronRAGAdapter:
    """
    NeutronRAG 适配器
    封装 NeutronRAG 的功能，提供简化的接口给多智能体系统使用
    """
    
    def __init__(
        self,
        llm_model: str = "glm-4-flash",
        rag_mode: str = "vector",  # vector, graph, hybrid
        vector_db: str = "MilvusDB",
        graph_db: str = "nebulagraph",
        space_name: str = "nutrition_kb",
        use_rag: bool = True
    ):
        """
        初始化 NeutronRAG 适配器
        
        Args:
            llm_model: LLM 模型名称
            rag_mode: RAG 模式 (vector/graph/hybrid)
            vector_db: 向量数据库类型
            graph_db: 图数据库类型
            space_name: 知识库空间名称
            use_rag: 是否启用 RAG
        """
        self.llm_model = llm_model
        self.rag_mode = rag_mode
        self.vector_db_type = vector_db
        self.graph_db_type = graph_db
        self.space_name = space_name
        self.use_rag = use_rag
        
        # 延迟加载 NeutronRAG 组件
        self.llm = None
        self.chat_engine = None
        self.vector_db = None
        self.graph_db = None
        
        self._initialized = False
        
        logger.info(f"NeutronRAG 适配器创建: mode={rag_mode}, model={llm_model}")
    
    def initialize(self):
        """
        延迟初始化 NeutronRAG 组件
        只在第一次使用时初始化，避免启动时加载过多资源
        """
        if self._initialized:
            return
        
        try:
            logger.info("正在初始化 NeutronRAG 组件...")
            
            # 导入 NeutronRAG 模块
            from llmragenv.LLM.llm_factory import ClientFactory
            from chat.chat_vectorrag import ChatVectorRAG
            from chat.chat_graphrag import ChatGraphRAG
            from chat.chat_unionrag import ChatUnionRAG
            from chat.chat_withoutrag import ChatWithoutRAG
            
            # 初始化 LLM 客户端
            # 这里需要根据你的 LLM 配置调整
            # NeutronRAG 支持多种 LLM，我们使用 GLM-4
            self.llm = self._create_llm_client()
            
            # 根据模式创建对应的 Chat 引擎
            if not self.use_rag:
                self.chat_engine = ChatWithoutRAG(self.llm)
                logger.info("RAG 模式: Without RAG")
                
            elif self.rag_mode.lower() == "vector":
                # 初始化向量数据库
                from database.vector.Milvus.milvus import MilvusDB
                self.vector_db = MilvusDB(
                    self.space_name,
                    dim=1024,  # embedding 维度
                    overwrite=False,
                    store=True,
                    retriever=True
                )
                self.chat_engine = ChatVectorRAG(self.llm, self.vector_db)
                logger.info("RAG 模式: Vector RAG")
                
            elif self.rag_mode.lower() == "graph":
                # 初始化图数据库
                from database.graph.graph_dbfactory import GraphDBFactory
                self.graph_db = GraphDBFactory(self.graph_db_type).get_graphdb(
                    space_name=self.space_name
                )
                self.chat_engine = ChatGraphRAG(self.llm, self.graph_db)
                logger.info("RAG 模式: Graph RAG")
                
            elif self.rag_mode.lower() == "hybrid":
                # 混合 RAG（需要同时初始化向量和图数据库）
                from database.vector.Milvus.milvus import MilvusDB
                from database.graph.graph_dbfactory import GraphDBFactory
                
                self.vector_db = MilvusDB(
                    self.space_name,
                    dim=1024,
                    overwrite=False,
                    store=True,
                    retriever=True
                )
                self.graph_db = GraphDBFactory(self.graph_db_type).get_graphdb(
                    space_name=self.space_name
                )
                self.chat_engine = ChatUnionRAG(self.llm)
                logger.info("RAG 模式: Hybrid RAG")
                
            else:
                raise ValueError(f"不支持的 RAG 模式: {self.rag_mode}")
            
            self._initialized = True
            logger.success("✅ NeutronRAG 初始化成功")
            
        except Exception as e:
            logger.error(f"❌ NeutronRAG 初始化失败: {e}")
            logger.warning("将使用降级模式（不使用 RAG）")
            self.use_rag = False
            self._initialized = False
            raise
    
    def _create_llm_client(self):
        """
        创建 LLM 客户端
        这里需要根据你的 GLM-4 配置进行适配
        """
        try:
            # 方式1: 使用 NeutronRAG 的 LLM Factory
            from llmragenv.LLM.llm_factory import ClientFactory
            
            # 尝试使用你已有的 GLM-4 客户端
            # NeutronRAG 支持多种 LLM，需要看配置
            llm_client = ClientFactory.get_client(
                llm_name=self.llm_model,
                llm_backend="openai"  # 或者 "llama_index"
            )
            
            return llm_client
            
        except Exception as e:
            logger.warning(f"无法使用 NeutronRAG 的 LLM Factory: {e}")
            logger.info("尝试使用自定义 GLM-4 客户端")
            
            # 方式2: 使用你自己的 GLM-4 客户端
            from utils.glm4_client import get_glm4_client
            return self._wrap_glm4_client(get_glm4_client())
    
    def _wrap_glm4_client(self, glm4_client):
        """
        将你的 GLM-4 客户端包装成 NeutronRAG 兼容的接口
        """
        from llmragenv.LLM.llm_base import LLMBase
        
        class GLM4Wrapper(LLMBase):
            """GLM-4 客户端适配器"""
            
            def __init__(self, glm4_client):
                self.client = glm4_client
            
            def chat_with_ai(self, prompt: str) -> str:
                """调用 LLM 生成回复"""
                try:
                    messages = [{"role": "user", "content": prompt}]
                    response = self.client.chat_with_retry(
                        messages=messages,
                        temperature=0.7,
                        max_tokens=2048
                    )
                    return response
                except Exception as e:
                    logger.error(f"GLM-4 调用失败: {e}")
                    return f"抱歉，生成回复时出现错误: {str(e)}"
            
            def chat_with_ai_stream(self, prompt: str, history=None):
                """流式生成（如果支持）"""
                # 如果 GLM-4 支持流式，在这里实现
                # 否则直接返回完整结果
                result = self.chat_with_ai(prompt)
                yield result
        
        return GLM4Wrapper(glm4_client)
    
    def query(
        self,
        question: str,
        history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """
        查询接口 - 使用 RAG 增强的问答
        
        Args:
            question: 用户问题
            history: 对话历史 (可选)
            **kwargs: 其他参数
            
        Returns:
            回答字符串
        """
        # 确保已初始化
        if not self._initialized:
            self.initialize()
        
        try:
            # 调用 NeutronRAG 的 chat 接口
            answer = self.chat_engine.chat_without_stream(question)
            
            logger.info(f"RAG 查询成功: {question[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"RAG 查询失败: {e}")
            return f"抱歉，查询知识库时出现错误: {str(e)}"
    
    def get_retrieval_results(self) -> List[str]:
        """
        获取检索到的知识片段
        
        Returns:
            检索结果列表
        """
        if not self._initialized:
            return []
        
        try:
            # 获取检索结果（用于调试或展示）
            results = self.chat_engine.retrieval_result()
            return results if results else []
        except Exception as e:
            logger.error(f"获取检索结果失败: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态信息
        """
        status = {
            "initialized": self._initialized,
            "rag_mode": self.rag_mode,
            "use_rag": self.use_rag,
            "llm_model": self.llm_model,
            "vector_db": self.vector_db_type if self.vector_db else None,
            "graph_db": self.graph_db_type if self.graph_db else None,
            "space_name": self.space_name
        }
        
        # 检查组件状态
        if self._initialized:
            try:
                # 简单测试查询
                test_result = self.query("测试连接")
                status["status"] = "healthy"
                status["test_query"] = "success"
            except Exception as e:
                status["status"] = "unhealthy"
                status["error"] = str(e)
        else:
            status["status"] = "not_initialized"
        
        return status


class SimplifiedRAGAdapter:
    """
    简化版 RAG 适配器
    如果 NeutronRAG 初始化失败，使用这个简化版本作为降级方案
    """
    
    def __init__(self):
        self.use_rag = False
        logger.warning("使用简化版 RAG 适配器（降级模式）")
    
    def initialize(self):
        """空实现"""
        pass
    
    def query(self, question: str, history=None, **kwargs) -> str:
        """
        简单回复（不使用 RAG）
        """
        return "抱歉，RAG 系统当前不可用。请稍后再试。"
    
    def get_retrieval_results(self) -> List[str]:
        """空实现"""
        return []
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "degraded",
            "use_rag": False,
            "message": "RAG 系统未启用（降级模式）"
        }
