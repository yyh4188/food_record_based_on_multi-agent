# 食物智能分析 - 多智能体系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GLM-4](https://img.shields.io/badge/LLM-GLM--4--Flash-green.svg)](https://open.bigmodel.cn)
[![Agents](https://img.shields.io/badge/Agents-6%2F6%20Using%20GLM--4-brightgreen.svg)](#)

## 概述

基于**智谱AI GLM-4-Flash**（永久免费大模型）的多智能体系统，为各类应用（Go、Java、Python等）提供：
- 🤖 AI智能对话
- 🍔 食物识别分析  
- 💊 营养健康建议
- 📊 健康目标跟踪
- 🍱 个性化饮食计划
- 📝 社区内容推荐

## 特点

✅ **永久免费** - 使用GLM-4-Flash，无使用限制  
✅ **6个AI智能体** - 全部使用大模型，真正的AI能力  
✅ **CrewAI框架** - 2025年最新智能体协作框架，提升准确性  
✅ **性能强大** - 接近GPT-4的中文能力  
✅ **独立部署** - 通用的微服务架构  
✅ **多语言支持** - Go SDK + RESTful API  
✅ **开箱即用** - 5分钟启动

## 系统架构

### 智能体列表

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

3. **对话智能体 (ConversationAgent)**
   - 功能：自然语言理解、智能问答、多轮对话
   - 技术：GLM-4大模型、上下文管理
   - 输入：用户问题、对话历史
   - 输出：智能回答、建议

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

### 协调器 (MultiAgentCoordinator)

- 功能：任务分配、智能体协作、结果聚合
- 机制：基于优先级的任务调度、智能体间通信
- 特点：支持并行处理、动态负载均衡

## 技术栈

- **大语言模型**: 智谱AI GLM-4-Flash (永久免费)
- **服务端语言**: Python 3.8+
- **API框架**: Flask (RESTful API)
- **通信协议**: HTTP/HTTPS, gRPC（可选）
- **数据库**: 独立配置（可选，用于智能体数据存储）
- **缓存**: Redis（可选）
- **客户端支持**: Go, Java, Python, JavaScript等

## 目录结构

```
multi-agent-system/
├── agents/                    # 智能体实现
│   ├── base_agent.py         # 智能体基类
│   ├── food_recognition_agent.py
│   ├── nutrition_analyzer_agent.py
│   ├── conversation_agent.py
│   ├── community_recommendation_agent.py
│   ├── health_goal_agent.py
│   └── meal_planner_agent.py
├── coordinators/             # 协调器
│   └── multi_agent_coordinator.py
├── models/                   # 模型相关(可选)
│   ├── vision_models/       # 视觉模型
│   ├── nlp_models/          # NLP模型
│   └── recommendation_models/ # 推荐模型
├── config/                   # 配置文件
│   ├── agent_config.yaml    # 智能体配置
│   └── glm4_config.yaml     # GLM-4模型配置
├── utils/                    # 工具类
│   ├── glm4_client.py       # GLM-4模型客户端
│   ├── data_processor.py    # 数据处理
│   ├── logger.py            # 日志管理
│   └── config_loader.py     # 配置加载
├── tests/                    # 测试文件
├── api/                      # API接口
│   └── agent_api.py         # 智能体API服务
└── requirements.txt          # Python依赖

```

## 快速开始（3步）

### 1. 获取免费API Key
访问 https://open.bigmodel.cn 注册获取GLM-4 API Key（永久免费）

### 2. 配置并安装
```bash
cd multi-agent-system
pip install -r requirements.txt

# 设置API Key
export GLM_API_KEY="your-api-key"  # Linux/Mac
# 或 Windows: set GLM_API_KEY=your-api-key
```

### 3. 启动CrewAI服务
```bash
python main.py
# CrewAI服务运行在 http://localhost:5001
```

测试：
```bash
# 健康检查
curl http://localhost:5001/crewai/health

# 获取Crew信息
curl http://localhost:5001/crewai/crew-info
```

## Go项目集成

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

## 主要功能

| API端点 | 功能 | 说明 |
|---------|------|------|
| `/agents/conversation` | AI对话 | 智能问答、健康建议 |
| `/agents/food-recognition` | 食物识别 | 营养成分分析 |
| `/agents/nutrition-analysis` | 营养分析 | 专业营养评估 |
| `/agents/health-goal` | 健康目标 | 目标跟踪预测 |
| `/agents/meal-plan` | 饮食计划 | 个性化计划生成 |
| `/agents/recommendation` | 智能推荐 | 内容个性化推荐 |

## 文档

- **[CREWAI_INTEGRATION.md](CREWAI_INTEGRATION.md)** - CrewAI框架集成指南（Python）
- **[CREWAI_GO_INTEGRATION.md](CREWAI_GO_INTEGRATION.md)** - CrewAI框架Go语言集成（新）⭐
- **[MULTI_AGENT_DEMO.md](MULTI_AGENT_DEMO.md)** - 多智能体协作演示
- **[LLM_SETUP.md](LLM_SETUP.md)** - GLM-4配置详细说明
- **[GO_INTEGRATION.md](GO_INTEGRATION.md)** - Go语言集成指南
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - 生产环境部署
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系统架构

## 许可证

MIT License
