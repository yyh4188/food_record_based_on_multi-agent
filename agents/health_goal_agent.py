"""
健康目标智能体
基于GLM-4大模型跟踪和预测用户健康目标
"""

from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
from .base_agent import BaseAgent
from utils.glm4_client import get_glm4_client


class HealthGoalAgent(BaseAgent):
    """健康目标智能体"""
    
    def __init__(self, agent_id: str = "health_goal", config: Dict[str, Any] = None):
        """初始化健康目标智能体"""
        super().__init__(agent_id, config or {})
        
        # 初始化LLM客户端
        try:
            self.llm_client = get_glm4_client()
            self.use_llm = True
            self.logger.info(f"✅ GLM-4客户端初始化成功（健康目标）")
        except Exception as e:
            self.logger.warning(f"⚠️ LLM客户端初始化失败，将使用规则分析: {e}")
            self.llm_client = None
            self.use_llm = False
        
        self.prediction_days = self.config.get('prediction_days', 7)
        self.alert_threshold = self.config.get('alert_threshold', 0.8)
        
        self.logger.info("健康目标智能体初始化完成")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理健康目标任务
        
        Args:
            input_data: {
                'user_id': int,
                'goal_type': str,  # 'weight_loss', 'muscle_gain', 'health_maintenance'
                'current_data': Dict,  # 当前数据
                'historical_data': List[Dict],  # 历史数据
                'target': Dict  # 目标设定
            }
            
        Returns:
            分析结果和建议
        """
        goal_type = input_data.get('goal_type', 'health_maintenance')
        current_data = input_data.get('current_data', {})
        historical_data = input_data.get('historical_data', [])
        target = input_data.get('target', {})
        
        # 1. 分析当前进度
        progress_analysis = self._analyze_progress(
            current_data, historical_data, target
        )
        
        # 2. 预测未来趋势
        prediction = self._predict_trend(historical_data, self.prediction_days)
        
        # 3. 生成行动建议
        recommendations = self._generate_action_plan(
            goal_type, progress_analysis, prediction, target
        )
        
        # 4. 设置提醒和激励
        alerts = self._generate_alerts(progress_analysis, target)
        
        return {
            'progress_analysis': progress_analysis,
            'prediction': prediction,
            'recommendations': recommendations,
            'alerts': alerts,
            'analysis_method': 'glm4_rule_based'
        }
    
    def _analyze_progress(
        self,
        current_data: Dict[str, Any],
        historical_data: List[Dict],
        target: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析目标进度"""
        if not historical_data:
            return {
                'completion_rate': 0,
                'trend': 'insufficient_data',
                'days_to_goal': None
            }
        
        # 计算完成度
        current_value = current_data.get('value', 0)
        target_value = target.get('value', 0)
        initial_value = historical_data[0].get('value', current_value)
        
        if target_value == initial_value:
            completion_rate = 100
        else:
            completion_rate = min(100, max(0,
                ((current_value - initial_value) / (target_value - initial_value)) * 100
            ))
        
        # 分析趋势
        trend = self._calculate_trend(historical_data)
        
        # 预估达成天数
        days_to_goal = self._estimate_days_to_goal(
            current_value, target_value, trend
        )
        
        return {
            'completion_rate': round(completion_rate, 1),
            'current_value': current_value,
            'target_value': target_value,
            'trend': trend,
            'days_to_goal': days_to_goal,
            'on_track': self._is_on_track(completion_rate, historical_data, target)
        }
    
    def _calculate_trend(self, historical_data: List[Dict]) -> str:
        """计算趋势"""
        if len(historical_data) < 2:
            return 'stable'
        
        recent_values = [d.get('value', 0) for d in historical_data[-7:]]
        
        if len(recent_values) < 2:
            return 'stable'
        
        # 简单线性趋势
        avg_change = (recent_values[-1] - recent_values[0]) / len(recent_values)
        
        if avg_change > 0.1:
            return 'improving'
        elif avg_change < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _estimate_days_to_goal(
        self,
        current: float,
        target: float,
        trend: str
    ) -> int:
        """估算达成目标所需天数"""
        if trend == 'stable' or current == target:
            return None
        
        # 简化估算
        difference = abs(target - current)
        daily_progress = 0.5  # 假设每天进步0.5单位
        
        if trend == 'improving':
            daily_progress *= 1.2
        elif trend == 'declining':
            daily_progress *= 0.8
        
        days = int(difference / daily_progress) if daily_progress > 0 else None
        
        return max(1, days) if days else None
    
    def _is_on_track(
        self,
        completion_rate: float,
        historical_data: List[Dict],
        target: Dict[str, Any]
    ) -> bool:
        """判断是否按计划进行"""
        if not historical_data or not target.get('deadline'):
            return True
        
        # 计算应该完成的进度
        start_date = datetime.fromisoformat(historical_data[0].get('date', datetime.now().isoformat()))
        target_date = datetime.fromisoformat(target.get('deadline', (datetime.now() + timedelta(days=30)).isoformat()))
        current_date = datetime.now()
        
        total_days = (target_date - start_date).days
        elapsed_days = (current_date - start_date).days
        
        if total_days <= 0:
            return completion_rate >= 100
        
        expected_rate = (elapsed_days / total_days) * 100
        
        return completion_rate >= expected_rate * 0.9  # 允许10%的偏差
    
    def _predict_trend(
        self,
        historical_data: List[Dict],
        days: int
    ) -> Dict[str, Any]:
        """预测未来趋势"""
        # TODO: 使用GLM-4大模型进行智能预测
        
        if not historical_data:
            return {'predictions': [], 'confidence': 0}
        
        # 简单线性预测
        recent_values = [d.get('value', 0) for d in historical_data[-7:]]
        avg_value = sum(recent_values) / len(recent_values)
        trend = self._calculate_trend(historical_data)
        
        daily_change = 0.3 if trend == 'improving' else (-0.2 if trend == 'declining' else 0)
        
        predictions = []
        for i in range(1, days + 1):
            predicted_value = avg_value + (daily_change * i)
            predictions.append({
                'day': i,
                'value': round(predicted_value, 2),
                'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            })
        
        return {
            'predictions': predictions,
            'confidence': 0.75,
            'trend': trend
        }
    
    def _generate_action_plan(
        self,
        goal_type: str,
        progress: Dict[str, Any],
        prediction: Dict[str, Any],
        target: Dict[str, Any]
    ) -> List[str]:
        """生成行动建议"""
        recommendations = []
        
        # 根据目标类型给出建议
        if goal_type == 'weight_loss':
            if progress.get('trend') == 'declining':
                recommendations.append("⚠️ 体重呈上升趋势，建议调整饮食和增加运动")
            elif progress.get('trend') == 'stable':
                recommendations.append("💡 进度平稳，建议增加运动强度以加快进度")
            else:
                recommendations.append("✅ 减重进展良好，继续保持！")
            
            recommendations.append("🥗 建议每日热量摄入减少300-500卡")
            recommendations.append("🏃 建议每天进行40-60分钟有氧运动")
        
        elif goal_type == 'muscle_gain':
            recommendations.append("💪 建议增加蛋白质摄入，每kg体重1.6-2.2g")
            recommendations.append("🏋️ 建议每周进行3-4次力量训练")
            recommendations.append("😴 保证充足睡眠，肌肉在休息时生长")
        
        else:  # health_maintenance
            recommendations.append("🥗 保持均衡饮食，多样化食材")
            recommendations.append("🏃 每周至少150分钟中等强度运动")
            recommendations.append("💧 保证充足水分摄入")
        
        # 根据进度给出建议
        if not progress.get('on_track'):
            recommendations.append("⏰ 目前进度落后，建议调整计划或延长期限")
        
        return recommendations
    
    def _generate_alerts(
        self,
        progress: Dict[str, Any],
        target: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成提醒和激励"""
        alerts = []
        
        completion_rate = progress.get('completion_rate', 0)
        
        # 里程碑提醒
        if completion_rate >= 25 and completion_rate < 30:
            alerts.append({
                'type': 'milestone',
                'message': '🎉 恭喜达成25%进度！继续加油！'
            })
        elif completion_rate >= 50 and completion_rate < 55:
            alerts.append({
                'type': 'milestone',
                'message': '🎊 已完成一半！坚持就是胜利！'
            })
        elif completion_rate >= 75 and completion_rate < 80:
            alerts.append({
                'type': 'milestone',
                'message': '🌟 75%进度达成！距离目标越来越近！'
            })
        elif completion_rate >= 100:
            alerts.append({
                'type': 'achievement',
                'message': '🏆 目标达成！恭喜您完成健康目标！'
            })
        
        # 进度警告
        if not progress.get('on_track'):
            alerts.append({
                'type': 'warning',
                'message': '⚠️ 进度落后，建议调整计划'
            })
        
        return alerts
