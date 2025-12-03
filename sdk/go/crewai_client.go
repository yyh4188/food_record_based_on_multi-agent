package multiagent

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// CrewAIClient CrewAI框架客户端
type CrewAIClient struct {
	BaseURL    string
	HTTPClient *http.Client
}

// NewCrewAIClient 创建CrewAI客户端
func NewCrewAIClient(baseURL string) *CrewAIClient {
	if baseURL == "" {
		baseURL = "http://localhost:5001"
	}

	return &CrewAIClient{
		BaseURL: baseURL,
		HTTPClient: &http.Client{
			Timeout: 120 * time.Second, // CrewAI任务可能较慢
		},
	}
}

// HealthPlanRequest 健康计划请求
type HealthPlanRequest struct {
	UserID              int      `json:"user_id"`
	Goal                string   `json:"goal"` // weight_loss, muscle_gain, health_maintenance
	CurrentWeight       float64  `json:"current_weight,omitempty"`
	TargetWeight        float64  `json:"target_weight,omitempty"`
	TargetCalories      int      `json:"target_calories"`
	Days                int      `json:"days"`
	DietaryPreferences  []string `json:"dietary_preferences,omitempty"`
	Restrictions        []string `json:"restrictions,omitempty"`
	FoodName            string   `json:"food_name,omitempty"`
}

// HealthPlanResponse 健康计划响应
type HealthPlanResponse struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data"`
	Message string      `json:"message"`
	Error   string      `json:"error,omitempty"`
}

// CrewConversationRequest CrewAI对话请求
type CrewConversationRequest struct {
	UserID    int                    `json:"user_id"`
	SessionID string                 `json:"session_id"`
	Message   string                 `json:"message"`
	Context   map[string]interface{} `json:"context,omitempty"`
}

// CrewConversationResponse CrewAI对话响应
type CrewConversationResponse struct {
	Success bool   `json:"success"`
	Data    struct {
		Response  string `json:"response"`
		SessionID string `json:"session_id"`
		Framework string `json:"framework"`
	} `json:"data"`
	Error string `json:"error,omitempty"`
}

// CrewMealPlanRequest CrewAI饮食计划请求
type CrewMealPlanRequest struct {
	UserID             int      `json:"user_id"`
	TargetCalories     int      `json:"target_calories"`
	Days               int      `json:"days"`
	Goal               string   `json:"goal"`
	DietaryPreferences []string `json:"dietary_preferences,omitempty"`
	Restrictions       []string `json:"restrictions,omitempty"`
}

// CrewMealPlanResponse CrewAI饮食计划响应
type CrewMealPlanResponse struct {
	Success bool   `json:"success"`
	Data    struct {
		MealPlan       interface{} `json:"meal_plan"`
		Days           int         `json:"days"`
		TargetCalories int         `json:"target_calories"`
		Framework      string      `json:"framework"`
	} `json:"data"`
	Error string `json:"error,omitempty"`
}

// NutritionAnalysisRequest 营养分析请求
type NutritionAnalysisRequest struct {
	FoodName string `json:"food_name"`
	UserID   int    `json:"user_id"`
	Goal     string `json:"goal,omitempty"`
}

// NutritionAnalysisResponse 营养分析响应
type NutritionAnalysisResponse struct {
	Success bool   `json:"success"`
	Data    struct {
		Analysis  interface{} `json:"analysis"`
		FoodName  string      `json:"food_name"`
		Framework string      `json:"framework"`
	} `json:"data"`
	Error string `json:"error,omitempty"`
}

// CrewInfo Crew信息
type CrewInfo struct {
	Success bool   `json:"success"`
	Data    struct {
		AgentsCount int      `json:"agents_count"`
		Agents      []string `json:"agents"`
		Framework   string   `json:"framework"`
		Features    []string `json:"features"`
	} `json:"data"`
	Error string `json:"error,omitempty"`
}

// doRequest 执行HTTP请求的辅助函数
func (c *CrewAIClient) doRequest(method, endpoint string, body interface{}, result interface{}) error {
	var reqBody io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("序列化请求失败: %w", err)
		}
		reqBody = bytes.NewBuffer(jsonData)
	}

	url := c.BaseURL + endpoint
	req, err := http.NewRequest(method, url, reqBody)
	if err != nil {
		return fmt.Errorf("创建请求失败: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("发送请求失败: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("读取响应失败: %w", err)
	}

	if err := json.Unmarshal(respBody, result); err != nil {
		return fmt.Errorf("解析响应失败: %w, 响应内容: %s", err, string(respBody))
	}

	return nil
}

// HealthCheck 健康检查
func (c *CrewAIClient) HealthCheck() (map[string]interface{}, error) {
	var result map[string]interface{}
	err := c.doRequest("GET", "/crewai/health", nil, &result)
	return result, err
}

// CreateHealthPlan 创建完整健康计划（CrewAI协作模式）
func (c *CrewAIClient) CreateHealthPlan(req *HealthPlanRequest) (*HealthPlanResponse, error) {
	var result HealthPlanResponse
	err := c.doRequest("POST", "/crewai/health-plan", req, &result)
	return &result, err
}

// Chat CrewAI增强对话
func (c *CrewAIClient) Chat(req *CrewConversationRequest) (*CrewConversationResponse, error) {
	var result CrewConversationResponse
	err := c.doRequest("POST", "/crewai/conversation", req, &result)
	return &result, err
}

// GenerateMealPlan CrewAI生成饮食计划
func (c *CrewAIClient) GenerateMealPlan(req *CrewMealPlanRequest) (*CrewMealPlanResponse, error) {
	var result CrewMealPlanResponse
	err := c.doRequest("POST", "/crewai/meal-plan", req, &result)
	return &result, err
}

// AnalyzeNutrition CrewAI营养分析
func (c *CrewAIClient) AnalyzeNutrition(req *NutritionAnalysisRequest) (*NutritionAnalysisResponse, error) {
	var result NutritionAnalysisResponse
	err := c.doRequest("POST", "/crewai/nutrition-analysis", req, &result)
	return &result, err
}

// GetCrewInfo 获取Crew信息
func (c *CrewAIClient) GetCrewInfo() (*CrewInfo, error) {
	var result CrewInfo
	err := c.doRequest("GET", "/crewai/crew-info", nil, &result)
	return &result, err
}
