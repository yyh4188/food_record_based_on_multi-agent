"""
营养分析智能体
基于GLM-4大模型分析食物营养并提供健康建议
"""

from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .base_agent import BaseAgent
from utils.glm4_client import get_glm4_client
import json


class NutritionAnalyzerAgent(BaseAgent):
    """营养分析智能体"""
    
    def __init__(self, agent_id: str = "nutrition_analyzer", config: Dict[str, Any] = None):
        """初始化营养分析智能体"""
        super().__init__(agent_id, config or {})
        
        # 初始化LLM客户端
        try:
            self.llm_client = get_glm4_client()
            self.use_llm = True
            self.logger.info(f"✅ GLM-4客户端初始化成功（营养分析）")
        except Exception as e:
            self.logger.warning(f"⚠️ LLM客户端初始化失败，将使用规则分析: {e}")
            self.llm_client = None
            self.use_llm = False
        
        # 营养标准
        self.daily_standards = {
            'calories': 2000,  # 每日推荐热量
            'protein': 60,  # 蛋白质(g)
            'carbohydrate': 300,  # 碳水化合物(g)
            'fat': 60,  # 脂肪(g)
            'fiber': 25,  # 纤维(g)
        }
        
        # 健康评分权重
        self.health_weights = {
            'calorie_balance': 0.3,
            'nutrient_balance': 0.3,
            'food_diversity': 0.2,
            'healthy_choices': 0.2
        }
        
        self.logger.info("营养分析智能体初始化完成")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理营养分析任务
        
        Args:
            input_data: {
                'food_data': Dict,  # 食物营养数据
                'user_profile': Dict,  # 用户资料（可选）
                'daily_intake': List[Dict],  # 当天已摄入食物（可选）
            }
            
        Returns:
            营养分析结果
        """
        food_data = input_data.get('food_data', {})
        user_profile = input_data.get('user_profile', {})
        daily_intake = input_data.get('daily_intake', [])
        
        # 如果启用了LLM，使用大模型分析
        if self.use_llm and self.llm_client:
            try:
                return self._analyze_with_llm(food_data, user_profile, daily_intake)
            except Exception as e:
                self.logger.error(f"LLM分析失败，使用规则系统: {e}")
        
        # 降级到规则系统
        # 1. 分析单个食物营养
        nutrition_analysis = self._analyze_single_food(food_data)
        
        # 2. 计算每日摄入总量
        daily_total = self._calculate_daily_total(daily_intake, food_data)
        
        # 3. 评估营养平衡
        balance_score = self._evaluate_nutrition_balance(daily_total)
        
        # 4. 生成健康建议
        recommendations = self._generate_recommendations(
            food_data, daily_total, user_profile
        )
        
        # 5. 计算健康评分
        health_score = self._calculate_health_score(
            food_data, daily_total, balance_score
        )
        
        return {
            'nutrition_analysis': nutrition_analysis,
            'daily_total': daily_total,
            'balance_score': balance_score,
            'health_score': health_score,
            'recommendations': recommendations,
            'analysis_method': 'mindspore_nutrition_model'
        }
    
    def _analyze_with_llm(self, food_data: Dict[str, Any], user_profile: Dict[str, Any], daily_intake: List[Dict]) -> Dict[str, Any]:
        """使用GLM-4进行营养分析"""
        # 计算每日总摄入
        daily_total = self._calculate_daily_total(daily_intake, food_data)
        
        prompt = f"""请作为营养师分析以下情况：

当前食物营养：
- 食物名称: {food_data.get('foodName', '未知')}
- 热量: {food_data.get('calories', 0)} kcal
- 蛋白质: {food_data.get('protein', 0)}g
- 碳水化合物: {food_data.get('carbohydrate', 0)}g
- 脂肪: {food_data.get('fat', 0)}g
- 膳食纤维: {food_data.get('fiber', 0)}g

今日总摄入:
- 总热量: {daily_total['calories']} kcal
- 蛋白质: {daily_total['protein']}g
- 碳水: {daily_total['carbohydrate']}g
- 脂肪: {daily_total['fat']}g

请提供：
1. 营养评价（50字内）
2. 3-5条健康建议
3. 健康评分（0-100）

返回JSON格式：
{{
  "nutrition_evaluation": "评价文字",
  "recommendations": ["建议1", "建议2", "建议3"],
  "health_score": 85,
  "balance_status": "均衡/偏高/偏低"
}}"""

        messages = [
            {"role": "system", "content": "你是一个专业的营养师，擅长分析饮食营养并提供专业建议。"},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm_client.chat_with_retry(messages, temperature=0.5)
        
        try:
            # 提取JSON
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            elif '{' in response:
                json_str = response[response.find('{'):response.rfind('}')+1]
            else:
                json_str = response.strip()
            
            llm_result = json.loads(json_str)
            
            # 组合结果
            return {
                'nutrition_analysis': {
                    'evaluation': llm_result.get('nutrition_evaluation', ''),
                    'llm_powered': True
                },
                'daily_total': daily_total,
                'balance_score': self._evaluate_nutrition_balance(daily_total),
                'health_score': llm_result.get('health_score', 75),
                'recommendations': llm_result.get('recommendations', []),
                'balance_status': llm_result.get('balance_status', '均衡'),
                'analysis_method': 'glm-4-nutrition-analysis'
            }
            
        except Exception as e:
            self.logger.error(f"LLM响应解析失败: {e}")
            # 降级到规则系统
            return self._analyze_with_rules(food_data, user_profile, daily_intake)
    
    def _analyze_with_rules(self, food_data: Dict[str, Any], user_profile: Dict[str, Any], daily_intake: List[Dict]) -> Dict[str, Any]:
        """规则系统分析（降级方案）"""
        nutrition_analysis = self._analyze_single_food(food_data)
        daily_total = self._calculate_daily_total(daily_intake, food_data)
        balance_score = self._evaluate_nutrition_balance(daily_total)
        recommendations = self._generate_recommendations(food_data, daily_total, user_profile)
        health_score = self._calculate_health_score(food_data, daily_total, balance_score)
        
        return {
            'nutrition_analysis': nutrition_analysis,
            'daily_total': daily_total,
            'balance_score': balance_score,
            'health_score': health_score,
            'recommendations': recommendations,
            'analysis_method': 'rule-based'
        }
    
    def _analyze_single_food(self, food_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析单个食物的营养成分"""
        calories = food_data.get('calories', 0)
        protein = food_data.get('protein', 0)
        carbs = food_data.get('carbohydrate', 0)
        fat = food_data.get('fat', 0)
        fiber = food_data.get('fiber', 0)
        
        # 计算营养密度
        nutrient_density = self._calculate_nutrient_density(
            calories, protein, fiber
        )
        
        # 计算三大营养素比例
        macros_ratio = self._calculate_macros_ratio(protein, carbs, fat)
        
        # 评估食物类型
        food_type = food_data.get('foodType', '未分类')
        type_evaluation = self._evaluate_food_type(food_type)
        
        return {
            'calories_per_100g': round(calories * 100 / self._get_serving_weight(food_data.get('servingSize', '')), 2),
            'nutrient_density': nutrient_density,
            'macros_ratio': macros_ratio,
            'type_evaluation': type_evaluation,
            'health_rating': self._rate_food_healthiness(food_data)
        }
    
    def _calculate_nutrient_density(self, calories: float, protein: float, fiber: float) -> str:
        """计算营养密度"""
        if calories == 0:
            return "低"
        
        density_score = (protein * 4 + fiber * 2) / calories
        
        if density_score > 0.15:
            return "高"
        elif density_score > 0.08:
            return "中"
        else:
            return "低"
    
    def _calculate_macros_ratio(self, protein: float, carbs: float, fat: float) -> Dict[str, float]:
        """计算三大营养素比例"""
        total_calories = protein * 4 + carbs * 4 + fat * 9
        
        if total_calories == 0:
            return {'protein': 0, 'carbs': 0, 'fat': 0}
        
        return {
            'protein': round((protein * 4 / total_calories) * 100, 1),
            'carbs': round((carbs * 4 / total_calories) * 100, 1),
            'fat': round((fat * 9 / total_calories) * 100, 1)
        }
    
    def _evaluate_food_type(self, food_type: str) -> str:
        """评估食物类型的健康程度"""
        evaluations = {
            '蔬菜': '优秀 - 富含维生素和矿物质',
            '水果': '优秀 - 富含维生素和抗氧化物',
            '主食': '良好 - 提供能量，建议选择全谷物',
            '肉类': '良好 - 优质蛋白来源，注意控制摄入量',
            '饮品': '一般 - 注意糖分含量',
            '甜品': '谨慎 - 高糖高脂，偶尔食用'
        }
        return evaluations.get(food_type, '中等')
    
    def _rate_food_healthiness(self, food_data: Dict[str, Any]) -> int:
        """评估食物健康等级 (1-5星)"""
        food_type = food_data.get('foodType', '')
        calories = food_data.get('calories', 0)
        fiber = food_data.get('fiber', 0)
        
        score = 3  # 默认3星
        
        # 根据食物类型调整
        if food_type in ['蔬菜', '水果']:
            score += 1
        elif food_type in ['甜品']:
            score -= 1
        
        # 根据热量调整
        if calories < 100:
            score += 0.5
        elif calories > 400:
            score -= 0.5
        
        # 根据纤维含量调整
        if fiber > 3:
            score += 0.5
        
        return max(1, min(5, int(score)))
    
    def _calculate_daily_total(self, daily_intake: List[Dict], current_food: Dict) -> Dict[str, float]:
        """计算每日总摄入量"""
        total = {
            'calories': 0,
            'protein': 0,
            'carbohydrate': 0,
            'fat': 0,
            'fiber': 0
        }
        
        # 累加已摄入食物
        for food in daily_intake:
            for nutrient in total.keys():
                total[nutrient] += food.get(nutrient, 0)
        
        # 加上当前食物
        for nutrient in total.keys():
            total[nutrient] += current_food.get(nutrient, 0)
        
        return total
    
    def _evaluate_nutrition_balance(self, daily_total: Dict[str, float]) -> Dict[str, Any]:
        """评估营养平衡"""
        balance = {}
        
        for nutrient, value in daily_total.items():
            standard = self.daily_standards.get(nutrient, 100)
            percentage = (value / standard) * 100
            
            if percentage < 80:
                status = "不足"
            elif percentage < 120:
                status = "适量"
            else:
                status = "过量"
            
            balance[nutrient] = {
                'value': round(value, 2),
                'standard': standard,
                'percentage': round(percentage, 1),
                'status': status
            }
        
        return balance
    
    def _generate_recommendations(
        self, 
        food_data: Dict[str, Any],
        daily_total: Dict[str, float],
        user_profile: Dict[str, Any]
    ) -> List[str]:
        """生成健康建议"""
        recommendations = []
        
        # 基于热量的建议
        if daily_total['calories'] > self.daily_standards['calories'] * 0.8:
            recommendations.append("今日热量摄入已接近目标，建议控制后续饮食")
        
        # 基于蛋白质的建议
        if daily_total['protein'] < self.daily_standards['protein'] * 0.5:
            recommendations.append("蛋白质摄入不足，建议补充鱼肉、豆类等优质蛋白")
        
        # 基于纤维的建议
        if daily_total['fiber'] < self.daily_standards['fiber'] * 0.5:
            recommendations.append("膳食纤维摄入不足，建议多吃蔬菜水果和全谷物")
        
        # 基于食物类型的建议
        food_type = food_data.get('foodType', '')
        if food_type == '甜品':
            recommendations.append("甜品糖分较高，建议适量食用，可搭配运动消耗")
        elif food_type == '蔬菜':
            recommendations.append("蔬菜营养丰富，继续保持这样健康的饮食习惯")
        
        # 如果没有特别建议，给出通用建议
        if not recommendations:
            recommendations.append("饮食搭配较为均衡，继续保持")
        
        return recommendations
    
    def _calculate_health_score(
        self,
        food_data: Dict[str, Any],
        daily_total: Dict[str, float],
        balance_score: Dict[str, Any]
    ) -> int:
        """计算健康评分 (0-100)"""
        score = 60  # 基础分
        
        # 营养平衡得分
        balanced_count = sum(1 for v in balance_score.values() if v['status'] == '适量')
        score += balanced_count * 5
        
        # 食物类型得分
        food_type = food_data.get('foodType', '')
        if food_type in ['蔬菜', '水果']:
            score += 10
        elif food_type == '甜品':
            score -= 5
        
        # 热量控制得分
        cal_percentage = (daily_total['calories'] / self.daily_standards['calories']) * 100
        if 80 <= cal_percentage <= 100:
            score += 10
        elif cal_percentage > 120:
            score -= 10
        
        return max(0, min(100, score))
    
    def _get_serving_weight(self, serving_size: str) -> float:
        """从份量描述中提取重量（克）"""
        import re
        match = re.search(r'(\d+)g', serving_size)
        if match:
            return float(match.group(1))
        return 100  # 默认100g
