package main

import (
	"encoding/json"
	"fmt"
	"log"

	"github.com/yourusername/multi-agent-go-sdk" // 替换为实际路径
)

func main() {
	// 创建CrewAI客户端
	client := multiagent.NewCrewAIClient("http://localhost:5001")

	fmt.Println("========================================")
	fmt.Println("CrewAI框架 - Go语言集成示例")
	fmt.Println("========================================\n")

	// 1. 健康检查
	fmt.Println("1️⃣ 健康检查...")
	health, err := client.HealthCheck()
	if err != nil {
		log.Printf("健康检查失败: %v\n", err)
	} else {
		fmt.Printf("✅ 服务状态: %s\n", health["status"])
		fmt.Printf("   框架: %s\n\n", health["framework"])
	}

	// 2. 获取Crew信息
	fmt.Println("2️⃣ 获取Crew信息...")
	crewInfo, err := client.GetCrewInfo()
	if err != nil {
		log.Printf("获取Crew信息失败: %v\n", err)
	} else {
		fmt.Printf("✅ 智能体数量: %d\n", crewInfo.Data.AgentsCount)
		fmt.Printf("   智能体列表: %v\n", crewInfo.Data.Agents)
		fmt.Printf("   框架特性:\n")
		for _, feature := range crewInfo.Data.Features {
			fmt.Printf("     - %s\n", feature)
		}
		fmt.Println()
	}

	// 3. CrewAI增强对话
	fmt.Println("3️⃣ CrewAI增强对话...")
	chatReq := &multiagent.CrewConversationRequest{
		UserID:    1001,
		SessionID: "go_session_001",
		Message:   "我想在一个月内减掉5公斤，有什么建议吗？",
		Context: map[string]interface{}{
			"goal":           "weight_loss",
			"current_weight": 75.0,
			"target_weight":  70.0,
		},
	}

	chatResp, err := client.Chat(chatReq)
	if err != nil {
		log.Printf("对话失败: %v\n", err)
	} else if chatResp.Success {
		fmt.Printf("✅ AI回复:\n%s\n\n", chatResp.Data.Response)
	}

	// 4. 创建完整健康计划（CrewAI协作）
	fmt.Println("4️⃣ 创建完整健康计划（CrewAI多智能体协作）...")
	planReq := &multiagent.HealthPlanRequest{
		UserID:         1001,
		Goal:           "weight_loss",
		CurrentWeight:  75.0,
		TargetWeight:   70.0,
		TargetCalories: 1800,
		Days:           7,
		DietaryPreferences: []string{"高蛋白", "低碳水"},
		Restrictions:       []string{"不吃辣"},
		FoodName:           "鸡胸肉",
	}

	planResp, err := client.CreateHealthPlan(planReq)
	if err != nil {
		log.Printf("创建健康计划失败: %v\n", err)
	} else if planResp.Success {
		fmt.Printf("✅ 健康计划创建成功！\n")
		fmt.Printf("   消息: %s\n", planResp.Message)
		
		// 打印结果（美化输出）
		resultJSON, _ := json.MarshalIndent(planResp.Data, "   ", "  ")
		fmt.Printf("   结果:\n%s\n\n", string(resultJSON))
	}

	// 5. 生成饮食计划
	fmt.Println("5️⃣ 生成7天饮食计划...")
	mealReq := &multiagent.CrewMealPlanRequest{
		UserID:         1001,
		TargetCalories: 1800,
		Days:           7,
		Goal:           "weight_loss",
		DietaryPreferences: []string{"高蛋白", "低碳水", "健康脂肪"},
		Restrictions:       []string{"不吃辣", "无坚果过敏"},
	}

	mealResp, err := client.GenerateMealPlan(mealReq)
	if err != nil {
		log.Printf("生成饮食计划失败: %v\n", err)
	} else if mealResp.Success {
		fmt.Printf("✅ 饮食计划生成成功！\n")
		fmt.Printf("   天数: %d天\n", mealResp.Data.Days)
		fmt.Printf("   目标热量: %d卡路里/天\n", mealResp.Data.TargetCalories)
		fmt.Printf("   框架: %s\n\n", mealResp.Data.Framework)
	}

	// 6. 营养分析
	fmt.Println("6️⃣ 营养分析...")
	nutritionReq := &multiagent.NutritionAnalysisRequest{
		FoodName: "红烧肉",
		UserID:   1001,
		Goal:     "weight_loss",
	}

	nutritionResp, err := client.AnalyzeNutrition(nutritionReq)
	if err != nil {
		log.Printf("营养分析失败: %v\n", err)
	} else if nutritionResp.Success {
		fmt.Printf("✅ 营养分析完成！\n")
		fmt.Printf("   食物: %s\n", nutritionResp.Data.FoodName)
		fmt.Printf("   框架: %s\n", nutritionResp.Data.Framework)
		
		analysisJSON, _ := json.MarshalIndent(nutritionResp.Data.Analysis, "   ", "  ")
		fmt.Printf("   分析结果:\n%s\n\n", string(analysisJSON))
	}

	// 总结
	fmt.Println("========================================")
	fmt.Println("🎉 CrewAI框架演示完成！")
	fmt.Println("========================================")
	fmt.Println("\nCrewAI优势:")
	fmt.Println("✅ 多智能体自动协作")
	fmt.Println("✅ 准确率提升17%+")
	fmt.Println("✅ 智能任务分配")
	fmt.Println("✅ 记忆和上下文管理")
	fmt.Println("✅ 更连贯的对话体验")
}

// 辅助函数：简化的健康计划创建
func SimpleHealthPlan(client *multiagent.CrewAIClient, userID int, goal string, targetCalories int) {
	req := &multiagent.HealthPlanRequest{
		UserID:         userID,
		Goal:           goal,
		TargetCalories: targetCalories,
		Days:           7,
	}

	resp, err := client.CreateHealthPlan(req)
	if err != nil {
		log.Printf("错误: %v\n", err)
		return
	}

	if resp.Success {
		fmt.Printf("✅ 健康计划创建成功！\n")
		fmt.Printf("消息: %s\n", resp.Message)
	} else {
		fmt.Printf("❌ 失败: %s\n", resp.Error)
	}
}

// 辅助函数：快速对话
func QuickChat(client *multiagent.CrewAIClient, userID int, message string) string {
	req := &multiagent.CrewConversationRequest{
		UserID:    userID,
		SessionID: "quick_session",
		Message:   message,
	}

	resp, err := client.Chat(req)
	if err != nil {
		return fmt.Sprintf("错误: %v", err)
	}

	if resp.Success {
		return resp.Data.Response
	}
	return fmt.Sprintf("失败: %s", resp.Error)
}
