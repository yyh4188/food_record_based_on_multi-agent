"""
社区推荐智能体
基于GLM-4大模型提供个性化内容推荐
"""

from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .base_agent import BaseAgent
from utils.glm4_client import get_glm4_client
import random
import json


class CommunityRecommendationAgent(BaseAgent):
    """社区推荐智能体"""
    
    def __init__(self, agent_id: str = "community_recommendation", config: Dict[str, Any] = None):
        """初始化社区推荐智能体"""
        super().__init__(agent_id, config or {})
        
        # 初始化LLM客户端
        try:
            self.llm_client = get_glm4_client()
            self.use_llm = True
            self.logger.info(f"✅ GLM-4客户端初始化成功（社区推荐）")
        except Exception as e:
            self.logger.warning(f"⚠️ LLM客户端初始化失败，将使用规则推荐: {e}")
            self.llm_client = None
            self.use_llm = False
        
        self.top_k = self.config.get('top_k', 10)
        self.diversity_factor = self.config.get('diversity_factor', 0.3)
        
        self.logger.info("社区推荐智能体初始化完成")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理推荐任务
        
        Args:
            input_data: {
                'user_id': int,
                'recommendation_type': str,  # 'posts', 'users', 'foods'
                'user_history': List[Dict],  # 用户历史行为
                'context': Dict  # 上下文信息
            }
            
        Returns:
            推荐结果
        """
        user_id = input_data.get('user_id')
        rec_type = input_data.get('recommendation_type', 'posts')
        user_history = input_data.get('user_history', [])
        context = input_data.get('context', {})
        
        # 使用GLM-4生成推荐
        if self.use_llm and self.llm_client:
            try:
                return self._recommend_with_llm(user_id, rec_type, user_history, context)
            except Exception as e:
                self.logger.error(f"GLM-4推荐失败，使用规则系统: {e}")
        
        # 分析用户兴趣
        user_interests = self._analyze_user_interests(user_history)
        
        # 生成推荐列表
        if rec_type == 'posts':
            recommendations = self._recommend_posts(user_id, user_interests, context)
        elif rec_type == 'users':
            recommendations = self._recommend_users(user_id, user_interests)
        elif rec_type == 'foods':
            recommendations = self._recommend_foods(user_id, user_interests)
        else:
            recommendations = []
        
        return {
            'recommendations': recommendations,
            'user_interests': user_interests,
            'recommendation_type': rec_type,
            'count': len(recommendations),
            'algorithm': 'glm4_rule_based'
        }
    
    def _recommend_with_llm(self, user_id: int, rec_type: str, user_history: List[Dict], context: Dict) -> Dict[str, Any]:
        """使用GLM-4生成个性化推荐"""
        
        # 分析用户兴趣
        interests = self._analyze_user_interests(user_history)
        interest_text = '、'.join([f"{k}:{v}" for k, v in interests.get('food_types', {}).items()][:3])
        if not interest_text:
            interest_text = '尚无明确偏好'
        
        # 不同推荐类型的提示词
        type_desc = {
            'posts': '社区帖子',
            'users': '相似用户',
            'foods': '食物推荐'
        }.get(rec_type, '内容')
        
        # 构建提示词
        prompt = f"""请作为推荐系统，为用户推荐{type_desc}。

用户信息：
- 用户ID: {user_id}
- 兴趣偏好: {interest_text}
- 历史行为: {len(user_history)}条

请生成5-8个推荐项目，返回JSON格式：
{{
  "recommendations": [
    {{
      "id": 推荐项目ID(整数),
      "title": "标题/名称",
      "description": "描述(30-50字)",
      "reason": "推荐理由(10-30字)",
      "score": 推荐得分(0-100),
      "tags": ["标签1", "标签2"]
    }}
  ],
  "explanation": "推荐总体解释"
}}

只返回JSON格式，不要其他解释文字。"""

        messages = [
            {"role": "system", "content": "你是一个专业的个性化推荐系统。"},
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
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
            else:
                json_str = response.strip()
            
            # 解析JSON
            result = json.loads(json_str)
            recommendations = result.get('recommendations', [])
            
            self.logger.info(f"GLM-4生成了{len(recommendations)}条{type_desc}推荐")
            
            # 返回结果
            return {
                'recommendations': recommendations,
                'user_interests': interests,
                'recommendation_type': rec_type,
                'count': len(recommendations),
                'algorithm': 'glm4_personalized',
                'explanation': result.get('explanation', 'GLM-4个性化推荐')
            }
            
        except Exception as e:
            self.logger.error(f"GLM-4响应解析失败: {e}, 原始响应: {response[:100]}...")
            raise
    
    def _analyze_user_interests(self, user_history: List[Dict]) -> Dict[str, Any]:
        """分析用户兴趣"""
        interests = {
            'food_types': {},
            'topics': {},
            'interaction_patterns': {}
        }
        
        for item in user_history:
            # 统计食物类型偏好
            if 'food_type' in item:
                food_type = item['food_type']
                interests['food_types'][food_type] = \
                    interests['food_types'].get(food_type, 0) + 1
            
            # 统计话题偏好
            if 'topics' in item:
                for topic in item['topics']:
                    interests['topics'][topic] = \
                        interests['topics'].get(topic, 0) + 1
        
        return interests
    
    def _recommend_posts(
        self,
        user_id: int,
        user_interests: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """推荐社区帖子"""
        # TODO: 使用GLM-4大模型推荐
        # 这里使用模拟数据
        
        recommended_posts = []
        
        # 基于协同过滤的推荐
        similar_users_posts = self._get_similar_users_posts(user_id)
        
        # 基于内容的推荐
        content_based_posts = self._get_content_based_posts(user_interests)
        
        # 热门推荐
        trending_posts = self._get_trending_posts()
        
        # 融合多种推荐策略
        all_posts = similar_users_posts + content_based_posts + trending_posts
        
        # 去重和排序
        unique_posts = {post['id']: post for post in all_posts}
        recommended_posts = list(unique_posts.values())[:self.top_k]
        
        return recommended_posts
    
    def _get_similar_users_posts(self, user_id: int) -> List[Dict[str, Any]]:
        """获取相似用户的帖子"""
        # 模拟推荐
        return [
            {
                'id': i,
                'title': f'美食分享 {i}',
                'food_type': random.choice(['主食', '蔬菜', '肉类', '水果']),
                'score': random.uniform(0.7, 0.95),
                'source': 'collaborative_filtering'
            }
            for i in range(1, 4)
        ]
    
    def _get_content_based_posts(self, user_interests: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于内容的推荐"""
        # 根据用户兴趣推荐相似内容
        return [
            {
                'id': i + 10,
                'title': f'推荐菜谱 {i}',
                'food_type': random.choice(list(user_interests.get('food_types', {}).keys()) or ['主食']),
                'score': random.uniform(0.65, 0.90),
                'source': 'content_based'
            }
            for i in range(1, 4)
        ]
    
    def _get_trending_posts(self) -> List[Dict[str, Any]]:
        """获取热门帖子"""
        return [
            {
                'id': i + 20,
                'title': f'热门美食 {i}',
                'food_type': random.choice(['主食', '蔬菜', '肉类', '水果']),
                'score': random.uniform(0.80, 0.98),
                'source': 'trending'
            }
            for i in range(1, 3)
        ]
    
    def _recommend_users(self, user_id: int, user_interests: Dict[str, Any]) -> List[Dict[str, Any]]:
        """推荐相似用户"""
        # 模拟推荐
        return [
            {
                'id': i,
                'username': f'美食达人{i}',
                'similarity_score': random.uniform(0.7, 0.95),
                'common_interests': random.randint(3, 10)
            }
            for i in range(1, 6)
        ]
    
    def _recommend_foods(self, user_id: int, user_interests: Dict[str, Any]) -> List[Dict[str, Any]]:
        """推荐食物"""
        food_types = user_interests.get('food_types', {})
        preferred_type = max(food_types.items(), key=lambda x: x[1])[0] if food_types else '主食'
        
        return [
            {
                'id': i,
                'name': f'{preferred_type}推荐{i}',
                'food_type': preferred_type,
                'recommendation_score': random.uniform(0.75, 0.95),
                'reason': f'基于您对{preferred_type}的偏好'
            }
            for i in range(1, 6)
        ]
