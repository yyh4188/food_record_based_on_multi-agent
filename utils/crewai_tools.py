"""
CrewAI 工具集成（修复版）
把 BaseAgent 的业务逻辑包装成 CrewAI 可调用的 tools
"""

from typing import Dict, Any, Callable
from crewai_tools import tool
from loguru import logger


def create_health_goal_tools(base_agent):
    """为 HealthGoalAgent 创建工具"""
    
    def _analyze_progress_impl(input_data: Dict[str, Any]) -> Dict[str, Any]:
        """内部实现：调用 BaseAgent 的 process 方法"""
        try:
            logger.info(f"[HealthGoalTools] 调用 {base_agent.agent_id}.process()")
            result = base_agent.process(input_data)
            logger.info(f"[HealthGoalTools] 调用成功，返回结果")
            return result
        except Exception as e:
            logger.error(f"[HealthGoalTools] 调用失败: {e}")
            return {"error": str(e)}
    
    def _validate_safety_impl(current_weight: float, target_weight: float, days: int) -> Dict[str, Any]:
        """验证目标安全性（规则逻辑）"""
        try:
            weight_change = abs(target_weight - current_weight)
            daily_change = weight_change / days if days > 0 else 0
            
            safe_daily_min = 0.05
            safe_daily_max = 0.15
            
            is_safe = safe_daily_min <= daily_change <= safe_daily_max
            
            if current_weight > target_weight:
                goal_type = "减重"
                if daily_change > safe_daily_max:
                    risk_level = "高风险"
                    suggestion = f"减重速度过快！建议延长至 {int(weight_change / safe_daily_max)} 天"
                elif daily_change < safe_daily_min:
                    risk_level = "过慢"
                    suggestion = f"减重速度较慢，可适当调整"
                else:
                    risk_level = "安全"
                    suggestion = "目标设定合理"
            else:
                goal_type = "增重"
                if daily_change > safe_daily_max:
                    risk_level = "高风险"
                    suggestion = f"增重速度过快！建议延长至 {int(weight_change / safe_daily_max)} 天"
                else:
                    risk_level = "安全"
                    suggestion = "目标设定合理"
            
            logger.info(f"[HealthGoalTools] 安全验证: {risk_level}")
            return {
                "is_safe": is_safe,
                "risk_level": risk_level,
                "goal_type": goal_type,
                "daily_change_kg": round(daily_change, 3),
                "suggestion": suggestion
            }
        except Exception as e:
            logger.error(f"[HealthGoalTools] 验证失败: {e}")
            return {"error": str(e), "is_safe": False}
    
    # 创建工具（使用闭包正确捕获 base_agent）
    @tool("分析健康目标进度")
    def analyze_health_progress(input_data_str: str) -> str:
        """
        分析用户的健康目标进度
        
        参数格式（JSON字符串）:
        {
            "user_id": 用户ID,
            "goal_type": "weight_loss/muscle_gain/health_maintenance",
            "current_data": {"value": 当前值},
            "historical_data": [历史数据],
            "target": {"value": 目标值}
        }
        """
        import json
        try:
            input_data = json.loads(input_data_str)
        except:
            input_data = {"goal_type": "weight_loss", "current_data": {}, "historical_data": [], "target": {}}
        
        result = _analyze_progress_impl(input_data)
        return json.dumps(result, ensure_ascii=False)
    
    @tool("验证目标安全性")
    def validate_goal_safety(current_weight: float, target_weight: float, days: int) -> str:
        """
        验证健康目标的安全性
        
        参数:
        - current_weight: 当前体重(kg)
        - target_weight: 目标体重(kg)
        - days: 计划天数
        """
        result = _validate_safety_impl(current_weight, target_weight, days)
        import json
        return json.dumps(result, ensure_ascii=False)
    
    return [analyze_health_progress, validate_goal_safety]


def create_nutrition_tools(base_agent):
    """为 NutritionAnalyzerAgent 创建工具"""
    
    def _analyze_nutrition_impl(input_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用 BaseAgent 的 process 方法"""
        try:
            logger.info(f"[NutritionTools] 调用 {base_agent.agent_id}.process()")
            result = base_agent.process(input_data)
            logger.info(f"[NutritionTools] 调用成功")
            return result
        except Exception as e:
            logger.error(f"[NutritionTools] 调用失败: {e}")
            return {"error": str(e)}
    
    def _validate_balance_impl(daily_total: Dict[str, float]) -> Dict[str, Any]:
        """验证营养平衡（规则逻辑）"""
        try:
            standards = {
                'calories': (1200, 2500),
                'protein': (50, 150),
                'carbohydrate': (200, 400),
                'fat': (30, 100)
            }
            
            validation = {
                "is_balanced": True,
                "issues": [],
                "warnings": []
            }
            
            for nutrient, (min_val, max_val) in standards.items():
                value = daily_total.get(nutrient, 0)
                if value < min_val:
                    validation["is_balanced"] = False
                    validation["issues"].append(f"{nutrient} 过低: {value} (最低{min_val})")
                elif value > max_val:
                    validation["is_balanced"] = False
                    validation["issues"].append(f"{nutrient} 过高: {value} (最高{max_val})")
                else:
                    validation["warnings"].append(f"{nutrient} 正常: {value}")
            
            logger.info(f"[NutritionTools] 营养验证: {'平衡' if validation['is_balanced'] else '不平衡'}")
            return validation
        except Exception as e:
            logger.error(f"[NutritionTools] 验证失败: {e}")
            return {"error": str(e), "is_balanced": False}
    
    @tool("分析食物营养")
    def analyze_nutrition(input_data_str: str) -> str:
        """
        分析食物的营养成分和健康评分
        
        参数格式（JSON字符串）:
        {
            "food_data": {"name": "食物名", "calories": 热量, ...},
            "user_profile": {},
            "daily_intake": []
        }
        """
        import json
        try:
            input_data = json.loads(input_data_str)
        except:
            input_data = {"food_data": {}, "user_profile": {}, "daily_intake": []}
        
        result = _analyze_nutrition_impl(input_data)
        return json.dumps(result, ensure_ascii=False)
    
    @tool("验证营养平衡")
    def validate_nutrition_balance(calories: float, protein: float, carbohydrate: float, fat: float) -> str:
        """
        验证每日营养摄入是否平衡
        
        参数:
        - calories: 总热量
        - protein: 蛋白质(g)
        - carbohydrate: 碳水化合物(g)
        - fat: 脂肪(g)
        """
        daily_total = {
            "calories": calories,
            "protein": protein,
            "carbohydrate": carbohydrate,
            "fat": fat
        }
        result = _validate_balance_impl(daily_total)
        import json
        return json.dumps(result, ensure_ascii=False)
    
    return [analyze_nutrition, validate_nutrition_balance]


def create_meal_planner_tools(base_agent):
    """为 MealPlannerAgent 创建工具"""
    
    def _generate_plan_impl(input_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用 BaseAgent 的 process 方法"""
        try:
            logger.info(f"[MealPlannerTools] 调用 {base_agent.agent_id}.process()")
            result = base_agent.process(input_data)
            logger.info(f"[MealPlannerTools] 调用成功")
            return result
        except Exception as e:
            logger.error(f"[MealPlannerTools] 调用失败: {e}")
            return {"error": str(e)}
    
    def _validate_plan_impl(meal_plan: Dict[str, Any], target_calories: int) -> Dict[str, Any]:
        """验证饮食计划（规则逻辑）"""
        try:
            validation = {
                "is_valid": True,
                "issues": [],
                "adjustments_needed": []
            }
            
            daily_plans = meal_plan.get('daily_plans', [])
            for i, day_plan in enumerate(daily_plans):
                day_calories = day_plan.get('total_calories', 0)
                calorie_diff = abs(day_calories - target_calories)
                calorie_tolerance = target_calories * 0.1
                
                if calorie_diff > calorie_tolerance:
                    validation["is_valid"] = False
                    validation["issues"].append(
                        f"第{i+1}天热量偏差: {day_calories} vs 目标{target_calories}"
                    )
            
            logger.info(f"[MealPlannerTools] 计划验证: {'通过' if validation['is_valid'] else '不通过'}")
            return validation
        except Exception as e:
            logger.error(f"[MealPlannerTools] 验证失败: {e}")
            return {"error": str(e), "is_valid": False}
    
    @tool("生成饮食计划")
    def generate_meal_plan(input_data_str: str) -> str:
        """
        生成个性化饮食计划
        
        参数格式（JSON字符串）:
        {
            "user_id": 用户ID,
            "target_calories": 目标卡路里,
            "dietary_preferences": ["偏好1", "偏好2"],
            "restrictions": ["限制1"],
            "goal": "weight_loss",
            "days": 7
        }
        """
        import json
        try:
            input_data = json.loads(input_data_str)
        except:
            input_data = {"target_calories": 2000, "days": 7, "goal": "health_maintenance"}
        
        result = _generate_plan_impl(input_data)
        return json.dumps(result, ensure_ascii=False)
    
    @tool("验证饮食计划合理性")
    def validate_meal_plan(meal_plan_str: str, target_calories: int) -> str:
        """
        验证生成的饮食计划是否符合约束
        
        参数:
        - meal_plan_str: 饮食计划（JSON字符串）
        - target_calories: 目标卡路里
        """
        import json
        try:
            meal_plan = json.loads(meal_plan_str)
        except:
            meal_plan = {"daily_plans": []}
        
        result = _validate_plan_impl(meal_plan, target_calories)
        return json.dumps(result, ensure_ascii=False)
    
    return [generate_meal_plan, validate_meal_plan]


def create_agent_tools(agent):
    """
    根据智能体类型创建对应的工具（修复版）
    
    Args:
        agent: BaseAgent 实例
    
    Returns:
        tools 列表
    """
    agent_id = agent.agent_id
    
    logger.info(f"🔧 为智能体 {agent_id} 创建工具...")
    
    if 'health' in agent_id or 'goal' in agent_id:
        tools = create_health_goal_tools(agent)
        logger.info(f"✅ {agent_id} 获得 {len(tools)} 个工具: {[t.name for t in tools]}")
        return tools
    elif 'nutrition' in agent_id or 'analyzer' in agent_id:
        tools = create_nutrition_tools(agent)
        logger.info(f"✅ {agent_id} 获得 {len(tools)} 个工具: {[t.name for t in tools]}")
        return tools
    elif 'meal' in agent_id or 'planner' in agent_id:
        tools = create_meal_planner_tools(agent)
        logger.info(f"✅ {agent_id} 获得 {len(tools)} 个工具: {[t.name for t in tools]}")
        return tools
    else:
        logger.info(f"ℹ️ {agent_id} 不需要工具（协调者或其他角色）")
        return []
