# NeutronRAG 集成指南

## 📋 概述

本项目已集成 NeutronRAG 系统，为多智能体系统提供 RAG（检索增强生成）能力。

### 特点
- ✅ **无侵入集成**：不修改 NeutronRAG-main 的任何内容
- ✅ **适配层设计**：通过适配器模式调用 NeutronRAG
- ✅ **向后兼容**：可以选择启用或禁用 RAG
- ✅ **延迟初始化**：只在需要时才加载 RAG 组件
- ✅ **多种 RAG 模式**：支持 Vector RAG、Graph RAG、Hybrid RAG
- ✅ **降级策略**：RAG 失败时自动降级到普通 LLM

---

## 🏗️ 架构设计

```
多智能体系统
├── agents/
│   └── conversation_agent.py     # 对话智能体（已集成 RAG）
├── rag/                           # 🆕 RAG 适配层
│   ├── __init__.py
│   ├── neutron_rag_adapter.py    # NeutronRAG 适配器
│   └── knowledge_manager.py      # 知识库管理器
├── knowledge_base/                # 🆕 营养知识库
│   ├── nutrition/                 # 营养学基础
│   ├── foods/                     # 食物数据
│   ├── health_goals/              # 健康目标指南
│   ├── diseases/                  # 疾病饮食
│   ├── recipes/                   # 健康食谱
│   └── supplements/               # 营养补充剂
└── NeutronRAG-main/               # 原始 NeutronRAG 系统（不修改）
    └── NeutronRAG-main/
        └── backend/
```

---

## 🚀 快速开始

### 1. 检查 NeutronRAG 依赖

确保 NeutronRAG-main 的依赖已安装：

```bash
# 查看 NeutronRAG 依赖
cat NeutronRAG-main/NeutronRAG-main/requirements.txt

# 安装关键依赖（如果未安装）
pip install pymilvus==2.3.6
pip install llama-index==0.10.10
pip install sentence-transformers==3.1.0
```

### 2. 配置 Agent 启用 RAG

在 `config/agent_config.yaml` 或代码中启用 RAG：

```python
from agents.conversation_agent import ConversationAgent

# 创建启用 RAG 的对话智能体
agent_config = {
    'use_rag': True,  # 🔑 启用 RAG
    'rag_config': {
        'llm_model': 'glm-4-flash',
        'rag_mode': 'vector',  # vector, graph, hybrid
        'vector_db': 'MilvusDB',
        'graph_db': 'nebulagraph',
        'space_name': 'nutrition_kb'  # 知识库空间名称
    }
}

conversation_agent = ConversationAgent(
    agent_id="conversation",
    config=agent_config
)
```

### 3. 准备知识库

#### 方式1：生成示例知识库（快速测试）

```python
from rag.knowledge_manager import NutritionKnowledgeManager

# 创建知识库管理器
km = NutritionKnowledgeManager()

# 生成示例知识文档
km.generate_sample_knowledge()

# 查看统计
print(km.get_statistics())
```

#### 方式2：手动添加知识文档

在 `knowledge_base/` 目录下创建 Markdown 文档：

```markdown
# knowledge_base/nutrition/protein.md

# 蛋白质营养指南

## 定义
蛋白质是由氨基酸组成的大分子...

## 推荐摄入量
- 成年人：1.0-1.2g/kg体重/天
- 运动人群：1.4-2.0g/kg体重/天
...
```

### 4. 索引知识库到 NeutronRAG

```python
from rag.neutron_rag_adapter import NeutronRAGAdapter
from rag.knowledge_manager import NutritionKnowledgeManager

# 创建 RAG 适配器
rag_adapter = NeutronRAGAdapter(
    rag_mode='vector',
    space_name='nutrition_kb'
)

# 初始化
rag_adapter.initialize()

# 创建知识库管理器
km = NutritionKnowledgeManager()

# 索引知识库
km.index_to_neutron_rag(rag_adapter)
```

### 5. 测试 RAG 功能

```python
# 直接使用 ConversationAgent 测试
result = conversation_agent.execute({
    'user_id': 1001,
    'session_id': 'test_session',
    'message': '减脂期间蛋白质怎么吃？'
})

print(result['data']['response'])
```

---

## ⚙️ 配置说明

### RAG 模式选择

| 模式 | 说明 | 适用场景 | 性能 |
|------|------|---------|------|
| **vector** | 向量检索 | 开放式问答、相似度搜索 | 快 ⚡ |
| **graph** | 图检索 | 复杂关系推理、多跳查询 | 中 |
| **hybrid** | 混合检索 | 结合两者优势 | 慢 |

### 配置参数详解

```python
rag_config = {
    # LLM 模型
    'llm_model': 'glm-4-flash',  # 使用的 LLM 模型
    
    # RAG 模式
    'rag_mode': 'vector',        # vector, graph, hybrid
    
    # 向量数据库（仅 vector/hybrid 模式需要）
    'vector_db': 'MilvusDB',     # 向量数据库类型
    
    # 图数据库（仅 graph/hybrid 模式需要）
    'graph_db': 'nebulagraph',   # 图数据库类型
    
    # 知识库空间名称
    'space_name': 'nutrition_kb'  # 不同项目使用不同空间隔离
}
```

---

## 💡 使用示例

### 示例1：基础对话（自动判断是否需要 RAG）

```python
# 创建对话智能体（启用 RAG）
agent = ConversationAgent(
    agent_id="conversation",
    config={'use_rag': True, 'rag_config': {...}}
)

# 营养问题 → 使用 RAG
response1 = agent.execute({
    'user_id': 1001,
    'session_id': 'session_001',
    'message': '高蛋白食物有哪些？'  # 触发 RAG
})

# 闲聊 → 不使用 RAG
response2 = agent.execute({
    'user_id': 1001,
    'session_id': 'session_001',
    'message': '你好'  # 不触发 RAG
})
```

### 示例2：CrewAI 集成

```python
from utils.crewai_adapter import CrewAIAgentAdapter

# 创建带 RAG 的 Agent
conversation_agent = ConversationAgent(
    agent_id="conversation",
    config={
        'use_rag': True,
        'rag_config': {
            'rag_mode': 'vector',
            'space_name': 'nutrition_kb'
        }
    }
)

# 适配到 CrewAI
crew_adapter = CrewAIAgentAdapter(
    base_agent=conversation_agent,
    role="健康饮食顾问（RAG增强）",
    goal="提供专业、准确的营养建议",
    backstory="我是一个拥有丰富营养学知识库的AI助手...",
    enable_tools=True
)

# 在 CrewAI 工作流中使用
crew = Crew(agents=[crew_adapter.crew_agent], ...)
```

### 示例3：手动调用 RAG

```python
from rag.neutron_rag_adapter import NeutronRAGAdapter

# 创建 RAG 适配器
rag = NeutronRAGAdapter(
    rag_mode='vector',
    space_name='nutrition_kb'
)

# 初始化
rag.initialize()

# 查询
answer = rag.query("减脂期间蛋白质摄入量是多少？")
print(answer)

# 获取检索结果
retrieval_results = rag.get_retrieval_results()
print("检索到的知识片段:", retrieval_results)

# 健康检查
status = rag.health_check()
print("RAG 状态:", status)
```

---

## 🔧 高级功能

### 1. 添加新知识文档

```python
from rag.knowledge_manager import NutritionKnowledgeManager

km = NutritionKnowledgeManager()

# 添加 Markdown 文档
content = """
# 增肌饮食指南

## 热量盈余
增肌需要热量盈余，建议 TDEE + 300-500 卡...

## 蛋白质摄入
1.6-2.2g/kg体重/天...
"""

km.add_document(
    category='health_goals',
    filename='增肌饮食指南.md',
    content=content
)
```

### 2. 批量生成知识文档（用 GLM-4）

```python
from utils.glm4_client import get_glm4_client

llm = get_glm4_client()
km = NutritionKnowledgeManager()

# 主题列表
topics = [
    "碳水化合物的作用和推荐摄入量",
    "脂肪的分类和健康脂肪来源",
    "维生素C的功能和食物来源",
    "高血压患者的饮食注意事项",
    # ... 更多主题
]

for topic in topics:
    prompt = f"""
请生成一份关于【{topic}】的专业营养知识文档。

要求：
1. 使用 Markdown 格式
2. 包含：定义、功能、推荐摄入量、食物来源、注意事项
3. 500-800字
4. 准确、专业、通俗易懂
"""
    
    content = llm.chat_with_retry([
        {"role": "user", "content": prompt}
    ])
    
    filename = f"{topic}.md"
    km.add_document('nutrition', filename, content)
    print(f"✅ 生成文档: {filename}")
```

### 3. 知识库统计和管理

```python
km = NutritionKnowledgeManager()

# 获取统计信息
stats = km.get_statistics()
print(f"总文档数: {stats['total_documents']}")

for category, info in stats['categories'].items():
    print(f"{info['name']}: {info['total']} 个文档")
```

### 4. 自定义 RAG 提示词

在 `NeutronRAG-main/backend/chat/chat_vectorrag.py` 中有提示词模板（不建议修改）。

如果需要自定义，可以在适配器层面处理：

```python
class CustomRAGAdapter(NeutronRAGAdapter):
    def query(self, question, history=None, **kwargs):
        # 预处理问题
        enhanced_question = f"作为营养专家，请回答：{question}"
        
        # 调用原始查询
        answer = super().query(enhanced_question, history, **kwargs)
        
        # 后处理回答
        formatted_answer = f"根据营养学知识库：\n\n{answer}"
        
        return formatted_answer
```

---

## 📊 效果对比

### 无 RAG

```
用户: "减脂期间蛋白质怎么吃？"

GLM-4: "减脂期间要多吃蛋白质，比如鸡肉、鱼肉、鸡蛋等。
蛋白质可以帮助保持肌肉，提高代谢..."

→ 回答笼统，缺乏数据支撑
```

### 有 RAG

```
用户: "减脂期间蛋白质怎么吃？"

[检索到的知识]
- 减脂期蛋白质推荐量 1.6-2.0g/kg
- 优质蛋白来源及营养成分表
- 蛋白质分散摄入的重要性

RAG 增强回答:
"减脂期间蛋白质摄入建议：

1. **摄入量**：根据您的体重，建议每天1.6-2.0g/kg体重
   （例如：70kg体重需要112-140g蛋白质）

2. **优质来源**：
   - 鸡胸肉：每100g含蛋白质24g，低脂
   - 鸡蛋：每个含6g蛋白质，生物价高
   - 三文鱼：每100g含22g蛋白质，富含Omega-3

3. **分配方式**：建议分3-4餐摄入，每餐25-35g
   运动后30分钟内补充效果最佳

4. **注意事项**：
   - 配合碳水化合物吸收更好
   - 多喝水（每天2-3升）
   - 避免一餐摄入过多"

→ 回答专业、有数据、可执行
```

---

## 🐛 故障排除

### 问题1：RAG 初始化失败

**症状**：
```
❌ NeutronRAG 适配器初始化失败: No module named 'pymilvus'
```

**解决**：
```bash
pip install pymilvus==2.3.6
```

### 问题2：Milvus 连接失败

**症状**：
```
Connection refused: localhost:19530
```

**解决**：
1. 启动 Milvus 服务（如果使用本地 Milvus）
2. 或者使用 Milvus Lite（无需额外服务）

```python
# 在 NeutronRAG 配置中使用 Milvus Lite
# 无需单独启动服务
```

### 问题3：知识库为空

**症状**：
```
检索到 0 个知识片段
```

**解决**：
1. 生成示例知识库
```python
from rag.knowledge_manager import NutritionKnowledgeManager
km = NutritionKnowledgeManager()
km.generate_sample_knowledge()
```

2. 索引知识库到 NeutronRAG
```python
km.index_to_neutron_rag(rag_adapter)
```

### 问题4：RAG 模块不可用

**症状**：
```
⚠️ RAG 模块不可用: No module named 'rag'
```

**解决**：
确保项目结构正确，`rag/` 文件夹在根目录下。

---

## 📈 性能优化

### 1. 延迟初始化

RAG 适配器默认使用延迟初始化，只在第一次查询时才初始化组件：

```python
# 创建时不初始化（快速）
rag = NeutronRAGAdapter(...)

# 第一次查询时自动初始化
answer = rag.query("...")  # 这里才初始化
```

### 2. 缓存检索结果

对于高频查询，可以添加缓存：

```python
from functools import lru_cache

class CachedRAGAdapter(NeutronRAGAdapter):
    @lru_cache(maxsize=100)
    def query(self, question, **kwargs):
        return super().query(question, **kwargs)
```

### 3. 批量查询

如果有多个问题，使用批量查询减少开销（需要 NeutronRAG 支持）。

---

## 🔐 安全注意事项

1. **知识库权限**：确保知识库目录权限正确
2. **API Key**：不要在代码中硬编码 API Key
3. **数据隐私**：用户查询可能包含敏感信息，注意日志脱敏

---

## 📚 参考资料

- **NeutronRAG 原始仓库**：`NeutronRAG-main/NeutronRAG-main/README.md`
- **Milvus 文档**：https://milvus.io/docs
- **LlamaIndex 文档**：https://docs.llamaindex.ai/
- **CrewAI 集成**：`CREWAI_V2_README.md`

---

## ✅ 下一步行动

1. **准备知识库**：使用 GLM-4 批量生成营养知识文档
2. **测试 RAG**：运行示例脚本验证功能
3. **集成到 API**：在 `api/crewai_api.py` 中启用 RAG
4. **性能调优**：根据实际使用情况优化检索策略
5. **监控效果**：对比有无 RAG 的回答质量

---

需要帮助？请查看 `rag/` 目录下的代码注释或联系开发团队。
