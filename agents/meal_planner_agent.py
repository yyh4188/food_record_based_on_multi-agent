"""
饮食计划智能体
基于GLM-4大模型创建个性化饮食计划
"""

from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
from .base_agent import BaseAgent
from utils.glm4_client import get_glm4_client
import random
import json


class MealPlannerAgent(BaseAgent):
    """饮食计划智能体"""
    
    def __init__(self, agent_id: str = "meal_planner", config: Dict[str, Any] = None):
        """初始化饮食计划智能体"""
        super().__init__(agent_id, config or {})
        
        # 初始化LLM客户端
        try:
            self.llm_client = get_glm4_client()
            self.use_llm = True
            self.logger.info(f"✅ GLM-4客户端初始化成功（饮食计划）")
        except Exception as e:
            self.logger.warning(f"⚠️ LLM客户端初始化失败，将使用规则生成: {e}")
            self.llm_client = None
            self.use_llm = False
        
        self.plan_days = self.config.get('plan_days', 7)
        self.meal_variety = self.config.get('meal_variety', 5)
        
        # 食谱库
        self.meal_database = self._init_meal_database()
        
        self.logger.info("饮食计划智能体初始化完成")
    
    def _init_meal_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """初始化食谱数据库"""
        return {
            'breakfast': [
                {'name': '燕麦粥 + 水煮蛋 + 牛奶', 'calories': 350, 'protein': 18, 'carbs': 45, 'fat': 10},
                {'name': '全麦面包 + 鸡蛋 + 豆浆', 'calories': 320, 'protein': 15, 'carbs': 42, 'fat': 9},
                {'name': '红薯 + 酸奶 + 坚果', 'calories': 380, 'protein': 12, 'carbs': 50, 'fat': 15},
                {'name': '杂粮粥 + 包子 + 豆浆', 'calories': 360, 'protein': 14, 'carbs': 55, 'fat': 8},
                {'name': '三明治 + 牛奶 + 水果', 'calories': 340, 'protein': 16, 'carbs': 45, 'fat': 11}
            ],
            'lunch': [
                {'name': '糙米饭 + 鸡胸肉 + 西兰花 + 豆腐', 'calories': 550, 'protein': 35, 'carbs': 65, 'fat': 12},
                {'name': '藜麦饭 + 三文鱼 + 蔬菜沙拉', 'calories': 580, 'protein': 38, 'carbs': 60, 'fat': 18},
                {'name': '荞麦面 + 牛肉 + 青菜', 'calories': 520, 'protein': 32, 'carbs': 62, 'fat': 14},
                {'name': '紫米饭 + 虾仁 + 炒时蔬', 'calories': 540, 'protein': 30, 'carbs': 68, 'fat': 10},
                {'name': '全麦意面 + 鸡肉 + 番茄', 'calories': 560, 'protein': 33, 'carbs': 70, 'fat': 13}
            ],
            'dinner': [
                {'name': '少量米饭 + 清蒸鱼 + 蔬菜', 'calories': 380, 'protein': 28, 'carbs': 35, 'fat': 12},
                {'name': '红薯 + 鸡胸肉 + 沙拉', 'calories': 350, 'protein': 30, 'carbs': 38, 'fat': 8},
                {'name': '玉米 + 豆腐 + 炒青菜', 'calories': 320, 'protein': 18, 'carbs': 42, 'fat': 10},
                {'name': '南瓜 + 虾仁 + 蒸菜', 'calories': 340, 'protein': 25, 'carbs': 40, 'fat': 9},
                {'name': '杂粮粥 + 瘦肉 + 凉拌菜', 'calories': 360, 'protein': 22, 'carbs': 45, 'fat': 11}
            ],
            'snack': [
                {'name': '苹果', 'calories': 80, 'protein': 0.5, 'carbs': 20, 'fat': 0.3},
                {'name': '香蕉', 'calories': 90, 'protein': 1, 'carbs': 23, 'fat': 0.4},
                {'name': '酸奶', 'calories': 100, 'protein': 5, 'carbs': 15, 'fat': 2.5},
                {'name': '坚果(20g)', 'calories': 120, 'protein': 5, 'carbs': 6, 'fat': 10},
                {'name': '水煮蛋', 'calories': 70, 'protein': 6, 'carbs': 1, 'fat': 5}
            ]
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理饮食计划生成任务
        
        Args:
            input_data: {
                'user_id': int,
                'target_calories': int,  # 目标卡路里
                'dietary_preferences': List[str],  # 饮食偏好（可选）
                'restrictions': List[str],  # 饮食限制（可选）
                'goal': str,  # 目标：weight_loss, muscle_gain, health_maintenance
                'days': int  # 计划天数
            }
            
        Returns:
            饮食计划
        """
        target_calories = input_data.get('target_calories', 2000)
        preferences = input_data.get('dietary_preferences', [])
        restrictions = input_data.get('restrictions', [])
        goal = input_data.get('goal', 'health_maintenance')
        days = input_data.get('days', 7)
        
        # 使用GLM-4生成饮食计划
        if self.use_llm and self.llm_client:
            try:
                return self._generate_with_llm(target_calories, preferences, restrictions, goal, days)
            except Exception as e:
                self.logger.error(f"GLM-4生成失败，使用规则系统: {e}")
        
        # 调整热量目标
        adjusted_calories = self._adjust_calories_by_goal(target_calories, goal)
        
        # 生成每日计划
        meal_plan = []
        for day in range(1, days + 1):
            daily_plan = self._generate_daily_plan(
                adjusted_calories, preferences, restrictions, goal
            )
            daily_plan['day'] = day
            daily_plan['date'] = (datetime.now() + timedelta(days=day-1)).strftime('%Y-%m-%d')
            meal_plan.append(daily_plan)
        
        # 计算营养总结
        nutrition_summary = self._calculate_plan_summary(meal_plan)
        
        # 生成购物清单
        shopping_list = self._generate_shopping_list(meal_plan)
        
        return {
            'meal_plan': meal_plan,
            'nutrition_summary': nutrition_summary,
            'shopping_list': shopping_list,
            'target_calories': adjusted_calories,
            'generation_method': 'glm4_rule_based'
        }
    
    def _adjust_calories_by_goal(self, base_calories: int, goal: str) -> int:
        """根据目标调整热量"""
        if goal == 'weight_loss':
            return int(base_calories * 0.8)  # 减少20%
        elif goal == 'muscle_gain':
            return int(base_calories * 1.15)  # 增加15%
        else:
            return base_calories
    
    def _generate_daily_plan(
        self,
        target_calories: int,
        preferences: List[str],
        restrictions: List[str],
        goal: str
    ) -> Dict[str, Any]:
        """生成单日饮食计划"""
        # 分配三餐和加餐的热量比例
        breakfast_cal = target_calories * 0.25
        lunch_cal = target_calories * 0.35
        dinner_cal = target_calories * 0.30
        snack_cal = target_calories * 0.10
        
        # 选择食谱
        breakfast = self._select_meal('breakfast', breakfast_cal, preferences, restrictions)
        lunch = self._select_meal('lunch', lunch_cal, preferences, restrictions)
        dinner = self._select_meal('dinner', dinner_cal, preferences, restrictions)
        snacks = self._select_meals('snack', snack_cal, preferences, restrictions, count=2)
        
        # 计算总营养
        total_nutrition = self._calculate_total_nutrition([breakfast, lunch, dinner] + snacks)
        
        return {
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner,
            'snacks': snacks,
            'total_nutrition': total_nutrition,
            'notes': self._generate_daily_notes(goal)
        }
    
    def _select_meal(
        self,
        meal_type: str,
        target_cal: float,
        preferences: List[str],
        restrictions: List[str]
    ) -> Dict[str, Any]:
        """选择单个餐食"""
        available_meals = self.meal_database.get(meal_type, [])
        
        # 过滤不符合要求的餐食
        filtered_meals = [
            meal for meal in available_meals
            if self._is_meal_suitable(meal, target_cal, preferences, restrictions)
        ]
        
        if not filtered_meals:
            filtered_meals = available_meals
        
        # 选择热量最接近目标的餐食
        selected = min(filtered_meals, key=lambda m: abs(m['calories'] - target_cal))
        
        return selected.copy()
    
    def _select_meals(
        self,
        meal_type: str,
        target_cal: float,
        preferences: List[str],
        restrictions: List[str],
        count: int = 2
    ) -> List[Dict[str, Any]]:
        """选择多个餐食（用于加餐）"""
        available_meals = self.meal_database.get(meal_type, [])
        
        # 随机选择
        selected = random.sample(available_meals, min(count, len(available_meals)))
        
        return [meal.copy() for meal in selected]
    
    def _is_meal_suitable(
        self,
        meal: Dict[str, Any],
        target_cal: float,
        preferences: List[str],
        restrictions: List[str]
    ) -> bool:
        """判断餐食是否符合要求"""
        # 热量不要偏差太大
        if abs(meal['calories'] - target_cal) > target_cal * 0.3:
            return False
        
        # TODO: 根据偏好和限制进行过滤
        
        return True
    
    def _calculate_total_nutrition(self, meals: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算总营养"""
        total = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0
        }
        
        for meal in meals:
            total['calories'] += meal.get('calories', 0)
            total['protein'] += meal.get('protein', 0)
            total['carbs'] += meal.get('carbs', 0)
            total['fat'] += meal.get('fat', 0)
        
        return {k: round(v, 1) for k, v in total.items()}
    
    def _calculate_plan_summary(self, meal_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算计划营养总结"""
        total_days = len(meal_plan)
        
        avg_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0
        }
        
        for day_plan in meal_plan:
            nutrition = day_plan['total_nutrition']
            for key in avg_nutrition.keys():
                avg_nutrition[key] += nutrition.get(key, 0)
        
        # 计算平均值
        for key in avg_nutrition.keys():
            avg_nutrition[key] = round(avg_nutrition[key] / total_days, 1)
        
        return {
            'average_daily_nutrition': avg_nutrition,
            'total_days': total_days,
            'variety_score': self._calculate_variety_score(meal_plan)
        }
    
    def _calculate_variety_score(self, meal_plan: List[Dict[str, Any]]) -> int:
        """计算饮食多样性评分 (0-100)"""
        # 简化计算：基于不同餐食数量
        unique_meals = set()
        
        for day_plan in meal_plan:
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                meal = day_plan.get(meal_type, {})
                if meal:
                    unique_meals.add(meal.get('name', ''))
        
        # 多样性 = (不同餐食数 / 总餐数) * 100
        total_meals = len(meal_plan) * 3
        variety_score = min(100, int((len(unique_meals) / total_meals) * 150))
        
        return variety_score
    
    def _generate_shopping_list(self, meal_plan: List[Dict[str, Any]]) -> List[str]:
        """生成购物清单"""
        # 简化版本：提取常见食材
        shopping_items = set([
            '糙米/藜麦/杂粮',
            '鸡胸肉',
            '鱼肉',
            '鸡蛋',
            '牛奶/豆浆',
            '西兰花/青菜',
            '番茄/黄瓜',
            '豆腐',
            '水果（苹果、香蕉）',
            '坚果',
            '全麦面包',
            '红薯/玉米'
        ])
        
        return sorted(list(shopping_items))
    
    def _generate_with_llm(self, target_calories: int, preferences: List[str], restrictions: List[str], goal: str, days: int) -> Dict[str, Any]:
        """使用GLM-4生成饮食计划"""
        
        # 目标描述
        goal_desc = {
            'weight_loss': '减脂减重',
            'muscle_gain': '增肌增重',
            'health_maintenance': '健康维持'
        }.get(goal, '健康维持')
        
        # 构建偏好和限制的描述
        pref_text = '、'.join(preferences) if preferences else '无特殊偏好'
        rest_text = '、'.join(restrictions) if restrictions else '无限制'
        
        # 构建提示词
        prompt = f"""请作为专业营养师，为用户制定{days}天的饮食计划。

用户信息：
- 目标热量：{target_calories} 卡路里/天
- 饮食目标：{goal_desc}
- 饮食偏好：{pref_text}
- 饮食限制：{rest_text}

请返回JSON格式，包含{days}天的计划，每天包括：
- day: 天数
- date: 日期
- breakfast: {{
    "name": "早餐名称",
    "calories": 热量,
    "protein": 蛋白质(g),
    "carbs": 碳水(g),
    "fat": 脂肪(g),
    "description": "简短描述"
  }}
- lunch: 同上
- dinner: 同上
- snacks: [加餐列表]
- total_nutrition: {{
    "calories": 总热量,
    "protein": 蛋白质(g),
    "carbs": 碳水(g),
    "fat": 脂肪(g)
  }}

只返回JSON格式，不要其他解释文字。"""

        messages = [
            {"role": "system", "content": "你是一个专业的营养师，擅长制定个性化饮食计划。"},
            {"role": "user", "content": prompt}
        ]
        
        # 调用GLM-4
        response = self.llm_client.chat_with_retry(messages, temperature=0.7)
        
        try:
            # 提取JSON内容
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            elif '{' in response:
                # 提取最外层的JSON
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
            else:
                json_str = response.strip()
            
            # 解析JSON
            result = json.loads(json_str)
            
            # 处理可能的返回格式
            if isinstance(result, dict) and 'meal_plan' in result:
                meal_plan = result['meal_plan']
            elif isinstance(result, list):
                meal_plan = result
            else:
                meal_plan = [result]
            
            # 生成购物清单
            shopping_list = self._generate_shopping_list(meal_plan)
            
            # 生成营养总结
            nutrition_summary = self._calculate_plan_summary(meal_plan)
            
            self.logger.info(f"GLM-4生成了{len(meal_plan)}天的饮食计划")
            
            # 返回结果
            return {
                'meal_plan': meal_plan,
                'nutrition_summary': nutrition_summary,
                'shopping_list': shopping_list,
                'target_calories': target_calories,
                'generation_method': 'glm4_generation'
            }
            
        except Exception as e:
            self.logger.error(f"GLM-4响应解析失败: {e}, 原始响应: {response[:100]}...")
            raise
    
    def _generate_daily_notes(self, goal: str) -> str:
        """生成每日饮食提示"""
        notes = {
            'weight_loss': "💡 减肥期间保持规律饮食，避免暴饮暴食。配合适量运动效果更佳。",
            'muscle_gain': "💪 增肌期间注意蛋白质摄入，训练后及时补充营养。保证充足睡眠。",
            'maintenance': "🥗 保持均衡饮食，适量运动，享受健康生活。"
        }
        
        return notes.get(goal, notes['maintenance'])
