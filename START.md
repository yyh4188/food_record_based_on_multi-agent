# 快速启动指南

## 🚀 一键启动

```bash
python main.py
```

就这么简单！CrewAI多智能体系统将在 **http://localhost:5001** 启动。

## 📋 前置要求

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置GLM-4 API Key**
```bash
# Linux/Mac
export GLM_API_KEY="your-api-key"

# Windows
set GLM_API_KEY=your-api-key
```

获取API Key: https://open.bigmodel.cn （永久免费）

## 🎯 使用方式

### 1. 从Go项目调用

```go
import "github.com/yourusername/multi-agent-go-sdk"

client := multiagent.NewCrewAIClient("http://localhost:5001")

// 创建健康计划
resp, _ := client.CreateHealthPlan(&multiagent.HealthPlanRequest{
    UserID: 1001,
    Goal: "weight_loss",
    TargetCalories: 1800,
    Days: 7,
})
```

### 2. 直接HTTP调用

```bash
curl -X POST http://localhost:5001/crewai/health-plan \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1001,
    "goal": "weight_loss",
    "target_calories": 1800,
    "days": 7
  }'
```

## 🔧 可用端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/crewai/health` | GET | 健康检查 |
| `/crewai/crew-info` | GET | 获取Crew信息 |
| `/crewai/health-plan` | POST | 创建完整健康计划 |
| `/crewai/conversation` | POST | AI对话 |
| `/crewai/meal-plan` | POST | 生成饮食计划 |
| `/crewai/nutrition-analysis` | POST | 营养分析 |

## 📚 详细文档

- [CrewAI框架集成指南](CREWAI_INTEGRATION.md)
- [Go语言集成指南](CREWAI_GO_INTEGRATION.md)
- [API文档](api/README.md)

## ❓ 问题排查

**问题1: 端口被占用**
```bash
# 修改端口
# 编辑 api/crewai_api.py 最后一行
app.run(host='0.0.0.0', port=5002, debug=True)  # 改为其他端口
```

**问题2: 缺少依赖**
```bash
pip install crewai crewai-tools langchain langchain-core
```

**问题3: GLM-4 API Key未设置**
```bash
export GLM_API_KEY="your-key-here"
```

## 🎉 就是这样！

系统已完全基于CrewAI框架，提供最佳的多智能体协作体验。
