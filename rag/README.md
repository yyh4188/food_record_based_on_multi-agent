# RAG 适配层

本目录包含 NeutronRAG 与多智能体系统的适配层代码。

## 📁 文件说明

### `neutron_rag_adapter.py`
NeutronRAG 适配器，将 NeutronRAG 系统包装成简单易用的接口。

**主要类:**
- `NeutronRAGAdapter`: 主适配器类，支持 Vector RAG、Graph RAG、Hybrid RAG
- `SimplifiedRAGAdapter`: 降级适配器，当 NeutronRAG 不可用时使用

**核心功能:**
- 延迟初始化（首次使用时才加载组件）
- 自动降级（失败时回退到普通 LLM）
- 健康检查
- 检索结果追踪

### `knowledge_manager.py`
营养知识库管理器，负责管理知识文档。

**主要类:**
- `NutritionKnowledgeManager`: 知识库管理器

**核心功能:**
- 加载/添加知识文档
- 索引到 NeutronRAG
- 生成示例知识
- 知识库统计

### `__init__.py`
模块初始化文件，导出主要接口。

---

## 🚀 快速开始

### 1. 创建 RAG 适配器

```python
from rag import NeutronRAGAdapter

# 创建适配器
rag = NeutronRAGAdapter(
    llm_model='glm-4-flash',
    rag_mode='vector',  # vector, graph, hybrid
    space_name='nutrition_kb'
)

# 初始化（延迟加载）
rag.initialize()

# 查询
answer = rag.query("减脂期间蛋白质怎么吃？")
print(answer)
```

### 2. 管理知识库

```python
from rag import NutritionKnowledgeManager

# 创建管理器
km = NutritionKnowledgeManager()

# 生成示例知识
km.generate_sample_knowledge()

# 查看统计
stats = km.get_statistics()
print(f"总文档数: {stats['total_documents']}")

# 添加自定义文档
km.add_document(
    category='nutrition',
    filename='维生素.md',
    content='...'
)
```

### 3. 在 Agent 中使用

```python
from agents.conversation_agent import ConversationAgent

# 创建启用 RAG 的 Agent
agent = ConversationAgent(
    agent_id="conversation",
    config={
        'use_rag': True,
        'rag_config': {
            'rag_mode': 'vector',
            'space_name': 'nutrition_kb'
        }
    }
)

# 使用
result = agent.execute({
    'user_id': 1001,
    'session_id': 'test',
    'message': '减肥建议'
})
```

---

## 🔧 配置选项

### RAG 模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `vector` | 向量检索 | 开放式问答、语义相似搜索 |
| `graph` | 图检索 | 复杂关系推理、多跳查询 |
| `hybrid` | 混合检索 | 结合两者优势 |

### 配置参数

```python
{
    'llm_model': 'glm-4-flash',      # LLM 模型
    'rag_mode': 'vector',            # RAG 模式
    'vector_db': 'MilvusDB',         # 向量数据库
    'graph_db': 'nebulagraph',       # 图数据库
    'space_name': 'nutrition_kb',    # 知识库空间
    'use_rag': True                  # 是否启用
}
```

---

## 📚 相关文档

- **完整集成指南**: `../RAG_INTEGRATION_GUIDE.md`
- **示例代码**: `../examples/rag_example.py`
- **快速设置**: `../setup_rag.py`

---

## 🏗️ 架构说明

### 适配层设计

```
ConversationAgent
      ↓
NeutronRAGAdapter (适配层)
      ↓
NeutronRAG System (不修改)
   ├── ChatVectorRAG
   ├── ChatGraphRAG
   └── ChatUnionRAG
```

### 为什么需要适配层？

1. **解耦**: 不修改 NeutronRAG 源码，便于升级
2. **简化**: 提供统一的简单接口
3. **降级**: 自动处理异常和降级
4. **扩展**: 可以添加缓存、日志等功能

---

## ⚠️ 注意事项

1. **不要修改 NeutronRAG-main 目录**
   - 所有适配代码在 `rag/` 目录
   - NeutronRAG 作为独立模块使用

2. **延迟初始化**
   - RAG 组件只在第一次使用时初始化
   - 避免启动时的性能开销

3. **降级策略**
   - RAG 失败时自动降级到普通 LLM
   - 保证系统可用性

4. **知识库管理**
   - 定期更新知识库
   - 使用版本控制管理文档

---

## 🔍 故障排查

### 问题：导入 RAG 模块失败

**解决**:
```bash
# 确保在项目根目录
cd multi-agent-system

# 检查目录结构
ls -la rag/
```

### 问题：NeutronRAG 初始化失败

**解决**:
```bash
# 安装依赖
pip install pymilvus llama-index sentence-transformers

# 检查 NeutronRAG 目录
ls -la NeutronRAG-main/NeutronRAG-main/backend/
```

### 问题：知识库为空

**解决**:
```python
from rag import NutritionKnowledgeManager

km = NutritionKnowledgeManager()
km.generate_sample_knowledge()  # 生成示例知识
```

---

## 🤝 贡献

如果你想扩展 RAG 功能:

1. 在 `rag/` 目录下创建新模块
2. 不要修改 `NeutronRAG-main/` 的内容
3. 通过适配层添加新功能
4. 更新相关文档

---

## 📝 版本历史

- **v1.0** (2025-12-03): 初始版本，集成 NeutronRAG
  - 支持 Vector RAG、Graph RAG、Hybrid RAG
  - 知识库管理器
  - ConversationAgent 集成

---

需要帮助? 查看 `RAG_INTEGRATION_GUIDE.md` 获取详细文档。
