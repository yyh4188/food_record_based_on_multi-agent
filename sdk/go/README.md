# Multi-Agent System Go SDK

Go语言客户端SDK，用于调用多智能体系统的各项AI服务。

## 安装

```bash
go get github.com/yourusername/multi-agent-go-sdk
```

或者直接复制 `client.go` 到你的项目中。

## 快速开始

```go
package main

import (
    "fmt"
    "log"
    
    multiagent "github.com/yourusername/multi-agent-go-sdk"
)

func main() {
    // 创建客户端
    client := multiagent.NewClient("http://localhost:5000")
    
    // 健康检查
    healthy, err := client.HealthCheck()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Service healthy: %v\n", healthy)
    
    // 食物识别
    foodResp, err := client.RecognizeFood(&multiagent.FoodRecognitionRequest{
        ImagePath: "/path/to/food.jpg",
    })
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Recognized: %s (%.0f calories)\n", 
        foodResp.FoodName, 
        float64(foodResp.Calories))
}
```

## 功能示例

### 1. 食物识别

```go
client := multiagent.NewClient("http://localhost:5000")

result, err := client.RecognizeFood(&multiagent.FoodRecognitionRequest{
    ImagePath: "food.jpg",
})
if err != nil {
    log.Fatal(err)
}

fmt.Printf("食物: %s\n", result.FoodName)
fmt.Printf("热量: %d kcal\n", result.Calories)
fmt.Printf("蛋白质: %.1f g\n", result.Protein)
fmt.Printf("置信度: %.2f\n", result.Confidence)
```

### 2. 营养分析

```go
foodData := map[string]interface{}{
    "calories":     280,
    "protein":      18.0,
    "carbohydrate": 12.0,
    "fat":          18.0,
    "foodType":     "肉类",
}

analysis, err := client.AnalyzeNutrition(&multiagent.NutritionAnalysisRequest{
    FoodData: foodData,
})
if err != nil {
    log.Fatal(err)
}

fmt.Printf("营养分析: %+v\n", analysis)
```

### 3. 智能对话

```go
resp, err := client.Chat(&multiagent.ConversationRequest{
    UserID:    1,
    SessionID: "session_123",
    Message:   "我想减肥，有什么建议吗？",
})
if err != nil {
    log.Fatal(err)
}

fmt.Printf("AI回复: %s\n", resp.Response)
```

### 4. 健康目标分析

```go
req := &multiagent.HealthGoalRequest{
    GoalType: "weight_loss",
    CurrentData: map[string]interface{}{
        "value": 75,
    },
    HistoricalData: []map[string]interface{}{
        {"value": 80, "date": "2024-11-01"},
        {"value": 78, "date": "2024-11-15"},
    },
    Target: map[string]interface{}{
        "value":    70,
        "deadline": "2025-02-01",
    },
}

result, err := client.AnalyzeHealthGoal(req)
if err != nil {
    log.Fatal(err)
}

fmt.Printf("目标分析: %+v\n", result)
```

### 5. 生成饮食计划

```go
plan, err := client.GenerateMealPlan(&multiagent.MealPlanRequest{
    TargetCalories: 1800,
    Goal:           "weight_loss",
    Days:           7,
})
if err != nil {
    log.Fatal(err)
}

fmt.Printf("7天饮食计划: %+v\n", plan)
```

### 6. 个性化推荐

```go
recommendations, err := client.GetRecommendations(&multiagent.RecommendationRequest{
    UserID:             1,
    RecommendationType: "posts",
})
if err != nil {
    log.Fatal(err)
}

fmt.Printf("推荐内容: %+v\n", recommendations)
```

### 7. 综合分析（多智能体协作）

```go
result, err := client.ComprehensiveAnalysis("food.jpg", 1)
if err != nil {
    log.Fatal(err)
}

fmt.Printf("综合分析结果: %+v\n", result)
```

## 高级配置

### 设置超时时间

```go
client := multiagent.NewClient("http://localhost:5000")
client.SetTimeout(60 * time.Second) // 60秒超时
```

### 自定义HTTP客户端

```go
client := multiagent.NewClient("http://localhost:5000")
client.HTTPClient = &http.Client{
    Timeout: 30 * time.Second,
    Transport: &http.Transport{
        MaxIdleConns:       10,
        IdleConnTimeout:    90 * time.Second,
        DisableCompression: false,
    },
}
```

## 错误处理

```go
result, err := client.RecognizeFood(&multiagent.FoodRecognitionRequest{
    ImagePath: "food.jpg",
})
if err != nil {
    // 处理网络错误或API错误
    log.Printf("Error: %v\n", err)
    return
}

// 使用结果
fmt.Printf("Food: %s\n", result.FoodName)
```

## 完整示例

查看 `examples/` 目录获取更多完整示例：
- `food_recognition.go` - 食物识别示例
- `nutrition_analysis.go` - 营养分析示例
- `chatbot.go` - 聊天机器人示例
- `meal_planner.go` - 饮食计划示例

## API文档

详细API文档请参考主项目的文档：
- [API Reference](../../README.md)
- [Integration Guide](../../INTEGRATION_GUIDE.md)

## 许可证

MIT License
