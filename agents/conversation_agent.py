"""
对话智能体
基于最新大语言模型提供智能对话功能
支持: DeepSeek-V3, Qwen2.5, GLM-4, Gemini 2.0等
"""

from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .base_agent import BaseAgent
from utils.glm4_client import get_glm4_client


class ConversationAgent(BaseAgent):
    """对话智能体"""
    
    def __init__(self, agent_id: str = "conversation", config: Dict[str, Any] = None):
        """初始化对话智能体"""
        super().__init__(agent_id, config or {})
        
        self.max_history = self.config.get('max_history', 10)
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 2048)
        self.system_prompt = self.config.get(
            'system_prompt',
            "你是一个专业的健康饮食助手，名叫'食刻AI助手'。你擅长提供营养建议、饮食计划、减肥指导等服务。请用友好、专业的语气回答问题。"
        )
        
        # 初始化LLM客户端
        try:
            self.llm_client = get_glm4_client()
            self.use_llm = True
            self.logger.info(f"✅ LLM客户端初始化成功")
        except Exception as e:
            self.logger.warning(f"⚠️ LLM客户端初始化失败，将使用规则回复: {e}")
            self.llm_client = None
            self.use_llm = False
        
        # 对话历史存储（实际应该用数据库）
        self.conversation_history = {}
        
        # 知识库（作为后备）
        self.knowledge_base = self._init_knowledge_base()
        
        self.logger.info("对话智能体初始化完成")
    
    def _init_knowledge_base(self) -> Dict[str, List[str]]:
        """初始化知识库"""
        return {
            '营养': [
                '均衡饮食应包含蛋白质、碳水化合物、脂肪、维生素和矿物质',
                '每天应摄入足够的蔬菜水果，建议至少5种不同颜色',
                '优质蛋白来源包括鱼类、鸡肉、豆类和坚果'
            ],
            '减肥': [
                '健康减肥的关键是控制热量摄入和增加运动消耗',
                '不建议过度节食，应保证基础代谢所需热量',
                '减肥期间也要保证营养均衡，避免营养不良'
            ],
            '运动': [
                '成年人每周应进行至少150分钟中等强度有氧运动',
                '运动前后应适当补充能量，运动后30分钟内补充蛋白质效果最好',
                '力量训练有助于增加肌肉量，提高基础代谢率'
            ],
            '健康饮食': [
                '多吃全谷物、蔬菜水果，少吃加工食品',
                '控制盐、糖、油的摄入量',
                '保持规律饮食，不要暴饮暴食'
            ]
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理对话任务
        
        Args:
            input_data: {
                'user_id': int,
                'session_id': str,
                'message': str,
                'context': Dict (可选)
            }
            
        Returns:
            对话响应
        """
        user_id = input_data.get('user_id')
        session_id = input_data.get('session_id')
        user_message = input_data.get('message', '')
        context = input_data.get('context', {})
        
        # 获取对话历史
        history = self._get_conversation_history(session_id)
        
        # 使用MindSpore NLP模型生成回复
        response = self._generate_response(
            user_message, history, context
        )
        
        # 更新对话历史
        self._update_conversation_history(
            session_id, user_message, response
        )
        
        return {
            'response': response,
            'session_id': session_id,
            'conversation_turns': len(history) + 1,
            'generation_method': 'mindspore_nlp_model'
        }
    
    def _get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """获取对话历史"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        return self.conversation_history[session_id][-self.max_history:]
    
    def _update_conversation_history(
        self,
        session_id: str,
        user_message: str,
        ai_response: str
    ):
        """更新对话历史"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append({
            'role': 'user',
            'content': user_message
        })
        self.conversation_history[session_id].append({
            'role': 'assistant',
            'content': ai_response
        })
    
    def _generate_llm_response(
        self,
        user_message: str,
        history: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> str:
        """使用GLM-4大模型生成回复"""
        # 构建消息列表
        messages = []
        
        # 系统提示
        messages.append({
            "role": "system",
            "content": self.system_prompt
        })
        
        # 添加历史对话（保持上下文）
        for msg in history:
            messages.append(msg)
        
        # 当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # 调用GLM-4
        response = self.llm_client.chat_with_retry(
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response
    
    def _generate_response(
        self,
        user_message: str,
        history: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> str:
        """
        生成回复
        优先使用大语言模型，降级到规则系统
        """
        # 如果启用了LLM，使用大语言模型
        if self.use_llm and self.llm_client:
            try:
                return self._generate_llm_response(user_message, history, context)
            except Exception as e:
                self.logger.error(f"LLM生成失败，使用规则回复: {e}")
                # 降级到规则系统
        
        # 规则系统（后备方案）
        message_lower = user_message.lower()
        
        # 关键词匹配
        if '热量' in user_message or '卡路里' in user_message:
            return self._get_calorie_advice(context)
        elif '减肥' in user_message or '瘦身' in user_message:
            return self._get_weight_loss_advice()
        elif '营养' in user_message:
            return self._get_nutrition_advice()
        elif '运动' in user_message or '锻炼' in user_message:
            return self._get_exercise_advice()
        elif '食谱' in user_message or '吃什么' in user_message:
            return self._get_meal_suggestion()
        elif any(word in user_message for word in ['你好', 'hello', 'hi', '您好']):
            return self._get_greeting()
        else:
            return self._get_default_response(user_message)
    
    def _get_calorie_advice(self, context: Dict[str, Any]) -> str:
        """热量相关建议"""
        return ("关于卡路里管理，我有以下建议：\n\n"
                "1️⃣ 成年人每天需要约2000-2500卡路里\n"
                "2️⃣ 减肥期间可适当减少500卡路里摄入\n"
                "3️⃣ 均衡饮食很重要，不要过度节食\n"
                "4️⃣ 配合适量运动效果更好\n\n"
                "您可以告诉我您的具体情况，我会给出更个性化的建议。")
    
    def _get_weight_loss_advice(self) -> str:
        """减肥建议"""
        return ("关于健康减肥，我的建议是：\n\n"
                "🥗 饮食方面：\n"
                "- 控制总热量摄入，但不要节食\n"
                "- 多吃蔬菜水果和优质蛋白\n"
                "- 少吃高糖高脂肪食物\n"
                "- 规律饮食，不要暴饮暴食\n\n"
                "🏃 运动方面：\n"
                "- 每天至少30分钟有氧运动\n"
                "- 结合力量训练增加肌肉\n"
                "- 保持充足睡眠，规律作息\n\n"
                "健康减肥需要时间，建议每周减重0.5-1kg为宜。")
    
    def _get_nutrition_advice(self) -> str:
        """营养建议"""
        return ("均衡营养对健康很重要：\n\n"
                "🥩 蛋白质：鸡蛋、鱼肉、豆类\n"
                "🍚 碳水化合物：全谷物、糙米、燕麦\n"
                "🥑 健康脂肪：坚果、橄榄油、深海鱼\n"
                "🥬 维生素矿物质：新鲜蔬菜水果\n"
                "💧 水分：每天2000ml左右\n\n"
                "建议每餐包含多种食材，保证营养多样性。")
    
    def _get_exercise_advice(self) -> str:
        """运动建议"""
        return ("关于运动建议：\n\n"
                "💪 运动频率：\n"
                "- 每周至少150分钟中等强度运动\n"
                "- 或75分钟高强度运动\n\n"
                "🏋️ 运动类型：\n"
                "- 有氧运动：跑步、游泳、骑行\n"
                "- 力量训练：器械训练、自重训练\n"
                "- 柔韧性：瑜伽、拉伸\n\n"
                "⚠️ 注意事项：\n"
                "- 运动前后适当补充能量\n"
                "- 循序渐进，避免运动损伤\n"
                "- 保持规律，坚持最重要")
    
    def _get_meal_suggestion(self) -> str:
        """饮食建议"""
        return ("健康饮食搭配建议：\n\n"
                "🌅 早餐：\n"
                "全麦面包 + 鸡蛋 + 牛奶 + 水果\n\n"
                "🌞 午餐：\n"
                "糙米饭 + 鸡胸肉/鱼肉 + 蔬菜 + 豆腐\n\n"
                "🌙 晚餐：\n"
                "少量主食 + 瘦肉 + 大量蔬菜\n\n"
                "🍎 加餐：\n"
                "坚果、酸奶、水果\n\n"
                "记住：多样化、适量、规律是健康饮食的关键！")
    
    def _get_greeting(self) -> str:
        """问候语"""
        return ("您好！我是食刻AI助手 🍽️\n\n"
                "我可以帮您：\n"
                "🔍 识别食物营养成分\n"
                "📊 分析饮食健康状况\n"
                "💡 提供饮食和运动建议\n"
                "📅 制定个性化饮食计划\n\n"
                "请告诉我您想了解什么？")
    
    def _get_default_response(self, user_message: str) -> str:
        """默认回复"""
        return ("感谢您的提问！作为健康饮食助手，我主要可以帮助您：\n\n"
                "• 食物营养分析\n"
                "• 饮食健康建议\n"
                "• 减肥和增肌指导\n"
                "• 运动与饮食搭配\n\n"
                "您可以询问关于营养、减肥、运动等方面的问题，"
                "我会尽力为您提供专业的建议。")
    
    def clear_history(self, session_id: str):
        """清除对话历史"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
            self.logger.info(f"已清除会话 {session_id} 的历史记录")
