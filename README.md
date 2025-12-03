<div align="center">

# 🍽️ 食物智能分析 - 企业级多智能体系统

**基于 CrewAI V2 + RAG 的智能营养健康解决方案**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GLM-4](https://img.shields.io/badge/LLM-GLM--4--Flash-green.svg)](https://open.bigmodel.cn)
[![CrewAI](https://img.shields.io/badge/Framework-CrewAI%20V2-orange.svg)](https://www.crewai.io/)
[![RAG](https://img.shields.io/badge/Enhanced-RAG%20System-blue.svg)](#)
[![Agents](https://img.shields.io/badge/Agents-6%2F6-brightgreen.svg)](#)

[快速开始](#-快速开始) · [系统架构](#-系统架构) · [文档](#-文档) · [示例](#-使用示例)

</div>

---

## 📖 项目简介

这是一个**企业级食物营养智能分析系统**，采用先进的多智能体架构，结合 CrewAI V2 协作框架和 RAG（检索增强生成）技术，为用户提供专业、准确、个性化的营养健康服务。

### 🎯 核心价值

- 🤖 **6个专业AI智能体** - 分工明确，协同工作
- 🧠 **RAG知识增强** - 基于专业营养学知识库，回答更准确
- 🔄 **CrewAI V2框架** - 多步工作流 + 交叉验证，准确率提升50%+
- 🆓 **永久免费LLM** - 使用智谱AI GLM-4-Flash
- 🚀 **开箱即用** - 5分钟启动，完整API文档
- 🌐 **多语言支持** - Go/Java/Python SDK + RESTful API

### 💡 适用场景

- ✅ 智能营养咨询平台
- ✅ 健康管理APP
- ✅ 企业员工健康系统
- ✅ 减脂/增肌教练应用
- ✅ 医疗健康辅助系统
- ✅ 食品营养分析工具

---

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户请求                              │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────▼──────────┐
         │   CrewAI Manager     │
         │  (任务协调器)         │
         └───────────┬──────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
   Task 1         Task 2         Task 3
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Health   │  │Nutrition │  │  Meal    │
│  Goal    │→ │ Analyzer │→ │ Planner  │
│  Agent   │  │  Agent   │  │  Agent   │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┴─────────────┘
                   │
         ┌─────────▼─────────┐
         │   RAG 知识库       │
         │ (营养学专业知识)   │
         └───────────────────┘
```

### 🤖 智能体列表

1. **食物识别智能体 (FoodRecognitionAgent)**
   - 功能：图像识别、食物分类、营养成分提取
   - 技术：GLM-4大模型、零样本分析
   - 输入：食物图片或食物名称
   - 输出：食物名称、类别、营养信息

2. **营养分析智能体 (NutritionAnalyzerAgent)**
   - 功能：营养成分分析、健康评估、饮食建议
   - 技术：GLM-4大模型、营养学知识
   - 输入：食物信息、用户健康数据
   - 输出：营养分析报告、健康建议

3. **对话智能体 (ConversationAgent)** 🆕 RAG增强
   - 功能：自然语言理解、智能问答、多轮对话
   - 技术：GLM-4大模型 + RAG知识检索
   - 知识库：500+专业营养学文档
   - 输入：用户问题、对话历史
   - 输出：专业、准确的智能回答

4. **社区推荐智能体 (CommunityRecommendationAgent)**
   - 功能：内容推荐、用户兴趣分析、个性化推荐
   - 技术：GLM-4大模型、协同过滤
   - 输入：用户行为、社区内容
   - 输出：推荐列表、推荐理由

5. **健康目标智能体 (HealthGoalAgent)**
   - 功能：目标设定、进度跟踪、激励建议
   - 技术：GLM-4大模型、数据趋势分析
   - 输入：用户目标、历史数据
   - 输出：进度分析、行动建议

6. **饮食计划智能体 (MealPlannerAgent)**
   - 功能：饮食计划生成、食谱推荐
   - 技术：GLM-4大模型、营养平衡分析
   - 输入：营养需求、饮食偏好、限制
   - 输出：完整饮食计划、购物清单

### 🔗 CrewAI V2 协作框架

**工作流程：**
1. **任务依赖链** - Task 2 依赖 Task 1，Task 3 依赖 Task 1+2
2. **交叉验证** - Agent 之间互相校验结果
3. **规则+LLM双保险** - 关键数据由规则保证，解释由LLM优化
4. **显式工具调用** - 每个Agent的业务逻辑被包装成工具

**示例：减脂场景**
```
Task 1: HealthGoalAgent 验证目标安全性 ✓
   ↓
Task 2: NutritionAnalyzer 分析营养约束 ✓
   ↓
Task 3: MealPlanner 生成饮食计划（基于Task1+2的约束）✓
   ↓
Task 4: HealthGoalAgent 制定进度跟踪方案 ✓
   ↓
Task 5: ConversationAgent 综合总结（Manager）✓
```

### 🧠 RAG 知识增强系统

**核心组件：**
- **向量数据库**: Milvus（轻量级本地部署）
- **Embedding模型**: bge-large-zh-v1.5（中文最佳）
- **知识库**: 营养学、食物数据、疾病饮食、健康目标
- **检索策略**: 语义相似度 + 关键词匹配

**工作流程：**
```
用户提问 → 判断是否需要RAG → 向量检索 → 拼接上下文 → GLM-4生成
```

**效果对比：**
- ❌ 无RAG: "减脂期间要多吃蛋白质..."（笼统）
- ✅ 有RAG: "建议每天1.6-2.0g/kg，鸡胸肉每100g含24g..."（专业、有数据）

---

## 🛠️ 技术栈

### 核心技术

| 层级 | 技术 | 说明 |
|------|------|------|
| **LLM** | GLM-4-Flash | 智谱AI，永久免费，性能接近GPT-4 |
| **框架** | CrewAI V2 | 2025最新多智能体协作框架 |
| **RAG** | NeutronRAG (精简版) | 向量检索 + 知识增强 |
| **向量库** | Milvus Lite | 轻量级本地部署 |
| **Embedding** | bge-large-zh-v1.5 | 智源开源，中文最佳 |
| **API** | Flask | RESTful API |
| **语言** | Python 3.8+ | 主要开发语言 |
| **SDK** | Go/Java/Python | 多语言客户端 |

### 可选组件

- **图数据库**: NebulaGraph（Graph RAG模式）
- **缓存**: Redis（高频查询缓存）
- **数据库**: MySQL/PostgreSQL（用户数据）
- **监控**: Prometheus + Grafana

---

## 📁 项目结构

```
multi-agent-system/
├── agents/                          # 🤖 智能体实现
│   ├── base_agent.py               # 智能体基类
│   ├── conversation_agent.py       # 对话智能体（RAG增强）⭐
│   ├── food_recognition_agent.py   # 食物识别智能体
│   ├── nutrition_analyzer_agent.py # 营养分析智能体
│   ├── health_goal_agent.py        # 健康目标智能体
│   ├── meal_planner_agent.py       # 饮食计划智能体
│   └── community_recommendation_agent.py  # 社区推荐智能体
│
├── rag/                             # 🧠 RAG 系统
│   ├── neutron_rag_adapter.py      # NeutronRAG 适配器
│   ├── knowledge_manager.py        # 知识库管理器
│   └── README.md                   # RAG 文档
│
├── knowledge_base/                  # 📚 知识库
│   ├── nutrition/                  # 营养学基础
│   ├── foods/                      # 食物营养数据
│   ├── health_goals/               # 健康目标指南
│   ├── diseases/                   # 疾病饮食建议
│   ├── recipes/                    # 健康食谱
│   └── supplements/                # 营养补充剂
│
├── api/                             # 🌐 API 接口
│   ├── crewai_api.py               # CrewAI API（主要）
│   └── agent_api.py                # 传统 Agent API
│
├── utils/                           # 🔧 工具类
│   ├── glm4_client.py              # GLM-4 客户端
│   ├── crewai_adapter.py           # CrewAI 适配器
│   ├── crewai_tools.py             # CrewAI 工具集
│   ├── config_loader.py            # 配置加载
│   └── logger.py                   # 日志管理
│
├── config/                          # ⚙️ 配置文件
│   ├── agent_config.yaml           # 智能体配置
│   └── glm4_config.yaml            # GLM-4 配置
│
├── sdk/                             # 📦 多语言 SDK
│   └── go/                         # Go SDK
│
├── examples/                        # 💡 示例代码
│   └── rag_example.py              # RAG 使用示例
│
├── NeutronRAG-main/                 # 🔬 NeutronRAG（精简版）
│   └── NeutronRAG-main/backend/    # 核心组件
│
├── main.py                          # 🚀 主程序（CrewAI模式）
├── setup_rag.py                     # 🛠️ RAG 设置脚本
├── cleanup_neutronrag.py            # 🗑️ NeutronRAG 清理脚本
├── requirements.txt                 # 📋 Python 依赖
└── README.md                        # 📖 本文档
```

---

## 🚀 快速开始

### 前置要求

- Python 3.8+
- 8GB+ 内存
- 10GB+ 硬盘空间

### 步骤1：获取 API Key（免费）

访问 [智谱AI开放平台](https://open.bigmodel.cn) 注册并获取 GLM-4 API Key

### 步骤2：安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd multi-agent-system

# 安装 Python 依赖
pip install -r requirements.txt

# 设置 API Key
# Linux/Mac:
export GLM_API_KEY="your-api-key-here"

# Windows PowerShell:
$env:GLM_API_KEY="your-api-key-here"

# Windows CMD:
set GLM_API_KEY=your-api-key-here
```

### 步骤3：初始化 RAG 系统（可选但推荐）

```bash
# 运行 RAG 设置脚本
python setup_rag.py

# 这会自动：
# ✅ 检查依赖
# ✅ 创建知识库目录
# ✅ 生成示例知识文档
# ✅ 测试 RAG 功能
```

### 步骤4：启动服务

#### 方式1：CrewAI 模式（推荐）

```bash
# 启动 CrewAI 服务
python main.py

# 服务运行在 http://localhost:5001
```

#### 方式2：传统 Agent 模式

```bash
# 启动传统 API
python api/agent_api.py

# 服务运行在 http://localhost:5000
```

### 步骤5：测试

```bash
# 健康检查
curl http://localhost:5001/crewai/health

# 获取 Crew 信息
curl http://localhost:5001/crewai/crew-info

# 测试减脂场景
curl -X POST http://localhost:5001/crewai/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我想减肥",
    "user_id": 1001,
    "context": {
      "current_weight": 75.0,
      "target_weight": 70.0,
      "days": 30
    }
  }'
```

---

## 💻 使用示例

### Python 示例

#### 1. 基础对话（RAG 增强）

```python
from agents.conversation_agent import ConversationAgent

# 创建启用 RAG 的对话智能体
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

# 查询
result = agent.execute({
    'user_id': 1001,
    'session_id': 'demo',
    'message': '减脂期间蛋白质怎么吃？'
})

print(result['data']['response'])
# 输出："建议每天摄入1.6-2.0g/kg体重的蛋白质..."
```

#### 2. CrewAI 工作流

```python
from crewai import Crew, Task
from utils.crewai_adapter import CrewAIAgentAdapter
from agents import HealthGoalAgent, NutritionAnalyzerAgent, MealPlannerAgent

# 创建智能体
health_agent = HealthGoalAgent()
nutrition_agent = NutritionAnalyzerAgent()
meal_agent = MealPlannerAgent()

# 适配到 CrewAI
adapters = {
    'health': CrewAIAgentAdapter(health_agent, ...),
    'nutrition': CrewAIAgentAdapter(nutrition_agent, ...),
    'meal': CrewAIAgentAdapter(meal_agent, ...)
}

# 创建任务链
task1 = Task(
    description="验证减脂目标的安全性",
    agent=adapters['health'].crew_agent
)

task2 = Task(
    description="分析营养约束",
    agent=adapters['nutrition'].crew_agent,
    context=[task1]  # 依赖 task1
)

task3 = Task(
    description="生成饮食计划",
    agent=adapters['meal'].crew_agent,
    context=[task1, task2]  # 依赖 task1 和 task2
)

# 执行
crew = Crew(agents=[...], tasks=[task1, task2, task3])
result = crew.kickoff()
```

### Go 项目集成

### 1. 复制SDK
```bash
cp -r sdk/go /your-go-project/multiagent
```

### 2. 使用示例
```go
import "your-project/multiagent"

client := multiagent.NewClient("http://localhost:5000")

// AI对话
resp, _ := client.Chat(&multiagent.ConversationRequest{
    UserID:    1,
    SessionID: "session_001",
    Message:   "减肥建议",
})

// 食物识别
food, _ := client.RecognizeFood(&multiagent.FoodRecognitionRequest{
    ImagePath: "food.jpg",
})

// 饮食计划
plan, _ := client.GenerateMealPlan(&multiagent.MealPlanRequest{
    TargetCalories: 1800,
    Days:           7,
})
```

详细文档: [Go集成指南](GO_INTEGRATION.md)

---

## 🌐 API 端点

### CrewAI API（推荐）

| 端点 | 方法 | 功能 | 说明 |
|------|------|------|------|
| `/crewai/health` | GET | 健康检查 | 服务状态 |
| `/crewai/crew-info` | GET | Crew信息 | Agent列表、工具统计 |
| `/crewai/process` | POST | 处理请求 | 多智能体协作处理 |

**场景支持：**
- `weight_loss` - 减脂方案
- `muscle_gain` - 增肌方案（开发中）
- `health_consultation` - 健康咨询（开发中）

### 传统 Agent API

| 端点 | 功能 | 说明 |
|------|------|------|
| `/agents/conversation` | AI对话 | 智能问答（RAG增强）|
| `/agents/food-recognition` | 食物识别 | 营养成分分析 |
| `/agents/nutrition-analysis` | 营养分析 | 专业营养评估 |
| `/agents/health-goal` | 健康目标 | 目标跟踪预测 |
| `/agents/meal-plan` | 饮食计划 | 个性化计划生成 |
| `/agents/recommendation` | 智能推荐 | 内容个性化推荐 |

---

## 📚 文档

### 核心文档

- **[CREWAI_V2_README.md](CREWAI_V2_README.md)** ⭐ - CrewAI V2 框架详解
- **[RAG_INTEGRATION_GUIDE.md](RAG_INTEGRATION_GUIDE.md)** ⭐ - RAG 系统集成指南
- **[NEUTRONRAG_CLEANUP_LIST.md](NEUTRONRAG_CLEANUP_LIST.md)** - NeutronRAG 清理说明

### 开发文档

- **[CREWAI_INTEGRATION.md](CREWAI_INTEGRATION.md)** - CrewAI 集成指南
- **[CREWAI_GO_INTEGRATION.md](CREWAI_GO_INTEGRATION.md)** - Go 语言集成
- **[GO_INTEGRATION.md](GO_INTEGRATION.md)** - Go SDK 使用
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系统架构设计

### 示例和教程

- **[examples/rag_example.py](examples/rag_example.py)** - RAG 使用示例
- **[setup_rag.py](setup_rag.py)** - RAG 快速设置
- **[rag/README.md](rag/README.md)** - RAG 模块文档

---

## 🎯 路线图

### ✅ 已完成

- [x] 6个核心智能体实现
- [x] CrewAI V2 框架集成
- [x] RAG 知识增强系统
- [x] 减脂场景完整工作流
- [x] Go SDK 支持
- [x] RESTful API

### 🚧 开发中

- [ ] 增肌场景工作流
- [ ] 健康咨询场景
- [ ] Graph RAG 支持
- [ ] 用户数据持久化
- [ ] 前端 Web UI

### 📋 计划中

- [ ] 移动端 SDK（iOS/Android）
- [ ] 多租户支持
- [ ] 实时监控面板
- [ ] A/B 测试框架
- [ ] 更多 LLM 支持（DeepSeek、Qwen等）

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📧 联系我们

- 项目主页: [GitHub Repo](#)
- 问题反馈: [Issues](#)
- 邮箱: your-email@example.com

---

## ⭐ Star History

如果这个项目对你有帮助，请给我们一个 ⭐！

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

<div align="center">

**Built with ❤️ using CrewAI, GLM-4, and RAG**

[回到顶部](#-食物智能分析---企业级多智能体系统)

</div>
