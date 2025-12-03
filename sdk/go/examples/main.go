package main

import (
	"fmt"
	"log"
	"time"

	multiagent "github.com/yourusername/multi-agent-go-sdk"
)

func main() {
	// 创建客户端
	client := multiagent.NewClient("http://localhost:5000")

	// 设置超时
	client.SetTimeout(30 * time.Second)

	fmt.Println("=== 多智能体系统 Go SDK 示例 ===\n")

	// 1. 健康检查
	fmt.Println("1. 健康检查...")
	healthy, err := client.HealthCheck()
	if err != nil {
		log.Printf("健康检查失败: %v\n", err)
	} else {
		fmt.Printf("✓ 服务状态: %v\n\n", healthy)
	}

	// 2. 食物识别
	fmt.Println("2. 食物识别...")
	foodResult, err := client.RecognizeFood(&multiagent.FoodRecognitionRequest{
		ImagePath: "test_food.jpg",
	})
	if err != nil {
		log.Printf("食物识别失败: %v\n", err)
	} else {
		fmt.Printf("✓ 食物名称: %s\n", foodResult.FoodName)
		fmt.Printf("  热量: %d kcal\n", foodResult.Calories)
		fmt.Printf("  蛋白质: %.1fg\n", foodResult.Protein)
		fmt.Printf("  碳水: %.1fg\n", foodResult.Carbohydrate)
		fmt.Printf("  脂肪: %.1fg\n", foodResult.Fat)
		fmt.Printf("  置信度: %.2f\n\n", foodResult.Confidence)
	}

	// 3. 营养分析
	fmt.Println("3. 营养分析...")
	nutritionResult, err := client.AnalyzeNutrition(&multiagent.NutritionAnalysisRequest{
		FoodData: map[string]interface{}{
			"foodName":     "宫保鸡丁",
			"calories":     280,
			"protein":      18.0,
			"carbohydrate": 12.0,
			"fat":          18.0,
			"fiber":        2.5,
			"foodType":     "肉类",
		},
		DailyIntake: []map[string]interface{}{
			{
				"calories":     350,
				"protein":      15.0,
				"carbohydrate": 45.0,
				"fat":          10.0,
			},
		},
	})
	if err != nil {
		log.Printf("营养分析失败: %v\n", err)
	} else {
		fmt.Printf("✓ 营养分析完成\n")
		if analysis, ok := nutritionResult["nutrition_analysis"].(map[string]interface{}); ok {
			fmt.Printf("  营养密度: %v\n", analysis["nutrient_density"])
			fmt.Printf("  健康评分: %v\n", analysis["health_rating"])
		}
		if recs, ok := nutritionResult["recommendations"].([]interface{}); ok {
			fmt.Println("  建议:")
			for _, rec := range recs {
				fmt.Printf("    - %v\n", rec)
			}
		}
		fmt.Println()
	}

	// 4. 智能对话
	fmt.Println("4. 智能对话...")
	chatResp, err := client.Chat(&multiagent.ConversationRequest{
		UserID:    1,
		SessionID: "go-sdk-demo-001",
		Message:   "我想减肥，应该怎么做？",
	})
	if err != nil {
		log.Printf("对话失败: %v\n", err)
	} else {
		fmt.Printf("✓ AI回复:\n%s\n\n", chatResp.Response)
	}

	// 5. 健康目标分析
	fmt.Println("5. 健康目标分析...")
	goalResult, err := client.AnalyzeHealthGoal(&multiagent.HealthGoalRequest{
		GoalType: "weight_loss",
		CurrentData: map[string]interface{}{
			"value": 75.0,
		},
		HistoricalData: []map[string]interface{}{
			{"value": 80.0, "date": "2024-11-01"},
			{"value": 78.0, "date": "2024-11-15"},
			{"value": 76.0, "date": "2024-11-25"},
		},
		Target: map[string]interface{}{
			"value":    70.0,
			"deadline": "2025-02-01",
		},
	})
	if err != nil {
		log.Printf("健康目标分析失败: %v\n", err)
	} else {
		fmt.Printf("✓ 目标分析完成\n")
		if progress, ok := goalResult["progress_analysis"].(map[string]interface{}); ok {
			fmt.Printf("  完成度: %.1f%%\n", progress["completion_rate"])
			fmt.Printf("  趋势: %v\n", progress["trend"])
			fmt.Printf("  预计天数: %v\n", progress["days_to_goal"])
		}
		if recs, ok := goalResult["recommendations"].([]interface{}); ok {
			fmt.Println("  建议:")
			for _, rec := range recs {
				fmt.Printf("    - %v\n", rec)
			}
		}
		fmt.Println()
	}

	// 6. 生成饮食计划
	fmt.Println("6. 生成饮食计划...")
	mealPlan, err := client.GenerateMealPlan(&multiagent.MealPlanRequest{
		TargetCalories: 1800,
		Goal:           "weight_loss",
		Days:           3,
	})
	if err != nil {
		log.Printf("饮食计划生成失败: %v\n", err)
	} else {
		fmt.Printf("✓ 3天饮食计划生成完成\n")
		if plan, ok := mealPlan["meal_plan"].([]interface{}); ok {
			for _, dayPlan := range plan {
				if day, ok := dayPlan.(map[string]interface{}); ok {
					fmt.Printf("\n  第%v天 (%v):\n", day["day"], day["date"])
					if breakfast, ok := day["breakfast"].(map[string]interface{}); ok {
						fmt.Printf("    早餐: %v\n", breakfast["name"])
					}
					if lunch, ok := day["lunch"].(map[string]interface{}); ok {
						fmt.Printf("    午餐: %v\n", lunch["name"])
					}
					if dinner, ok := day["dinner"].(map[string]interface{}); ok {
						fmt.Printf("    晚餐: %v\n", dinner["name"])
					}
				}
			}
		}
		fmt.Println()
	}

	// 7. 获取推荐
	fmt.Println("7. 社区推荐...")
	recommendations, err := client.GetRecommendations(&multiagent.RecommendationRequest{
		UserID:             1,
		RecommendationType: "posts",
	})
	if err != nil {
		log.Printf("推荐获取失败: %v\n", err)
	} else {
		fmt.Printf("✓ 推荐获取完成\n")
		if recs, ok := recommendations["recommendations"].([]interface{}); ok {
			fmt.Printf("  推荐数量: %d\n", len(recs))
			for i, rec := range recs[:min(3, len(recs))] {
				if item, ok := rec.(map[string]interface{}); ok {
					fmt.Printf("  %d. %v (来源: %v)\n", i+1, item["title"], item["source"])
				}
			}
		}
		fmt.Println()
	}

	fmt.Println("=== 示例完成 ===")
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
