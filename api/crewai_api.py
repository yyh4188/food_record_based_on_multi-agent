"""
CrewAI框架专用API服务 - 真正的多智能体协作
提供基于 CrewAI + 业务工具的深度集成接口
"""

from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.food_recognition_agent import FoodRecognitionAgent
from agents.nutrition_analyzer_agent import NutritionAnalyzerAgent
from agents.health_goal_agent import HealthGoalAgent
from agents.meal_planner_agent import MealPlannerAgent
from agents.conversation_agent import ConversationAgent
from agents.community_recommendation_agent import CommunityRecommendationAgent
from utils.crewai_adapter import create_health_crew, create_weight_loss_workflow

# 创建Blueprint
crewai_bp = Blueprint('crewai', __name__, url_prefix='/crewai')

# 全局变量存储crew实例
_crew = None
_adapters = None


def init_crew():
    """初始化CrewAI Crew - 带工具集成"""
    global _crew, _adapters
    
    if _crew is None:
        logger.info("="*60)
        logger.info("🚀 正在初始化真正的 CrewAI Crew（带业务工具）...")
        logger.info("="*60)
        
        # 初始化所有智能体
        food_agent = FoodRecognitionAgent()
        nutrition_agent = NutritionAnalyzerAgent()
        health_agent = HealthGoalAgent()
        meal_agent = MealPlannerAgent()
        conversation_agent = ConversationAgent()
        recommendation_agent = CommunityRecommendationAgent()
        
        # 创建Crew（带工具）
        _crew, _adapters = create_health_crew(
            food_agent,
            nutrition_agent,
            health_agent,
            meal_agent,
            conversation_agent,
            recommendation_agent
        )
        
        logger.info("="*60)
        logger.info("✅ CrewAI Crew 初始化完成")
        logger.info(f"📊 已注册智能体: {list(_adapters.keys())}")
        logger.info("🔧 业务工具已挂载到对应智能体")
        logger.info("="*60)
    
    return _crew, _adapters


@crewai_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'CrewAI Multi-Agent System',
        'version': '2.0.0',
        'framework': 'CrewAI with Business Tools',
        'features': [
            '真正的 CrewAI 框架',
            '业务逻辑工具集成',
            '多步协作流程',
            '显式校验和约束'
        ]
    })


@crewai_bp.route('/process', methods=['POST'])
def process_request():
    """
    统一处理接口 - 真正的 CrewAI 多智能体协作
    
    请求体:
    {
        "message": "我想减肥，帮我制定一个健康计划",
        "user_id": 1001,
        "context": {
            "current_weight": 75.0,
            "target_weight": 70.0,
            "days": 30,
            "target_calories": 1800,
            "dietary_preferences": ["高蛋白", "低碳水"],
            "restrictions": ["不吃辣"]
        }
    }
    
    内部流程：
    1. HealthGoalAgent: 验证目标安全性
    2. NutritionAnalyzerAgent: 分析营养约束
    3. MealPlannerAgent: 生成并自验证饮食计划
    4. HealthGoalAgent: 生成进度跟踪方案
    5. ConversationAgent: 综合总结
    
    各智能体会调用自己的业务工具（BaseAgent.process方法）
    """
    try:
        data = request.get_json()
        
        # 验证必需字段
        if 'message' not in data and 'context' not in data:
            return jsonify({
                'success': False,
                'error': '缺少message或context字段'
            }), 400
        
        user_message = data.get('message', '')
        user_id = data.get('user_id', 0)
        context = data.get('context', {})
        
        # 初始化Crew
        crew, adapters = init_crew()
        
        logger.info("="*60)
        logger.info(f"📥 收到用户请求")
        logger.info(f"👤 用户ID: {user_id}")
        logger.info(f"💬 消息: {user_message}")
        logger.info(f"📋 上下文: {context}")
        logger.info("="*60)
        
        # 判断场景类型（这里演示减脂场景）
        goal_type = context.get('goal_type', 'weight_loss')
        
        if goal_type == 'weight_loss' or (context.get('current_weight') and context.get('target_weight')):
            # 减脂场景：使用完整的多步工作流
            logger.info("🎯 场景识别: 减脂健康计划")
            logger.info("🔄 启动多步协作流程...")
            
            # 准备输入数据
            workflow_input = {
                'user_id': user_id,
                'current_weight': context.get('current_weight', 75),
                'target_weight': context.get('target_weight', 70),
                'days': context.get('days', 30),
                'target_calories': context.get('target_calories', 1800),
                'dietary_preferences': context.get('dietary_preferences', []),
                'restrictions': context.get('restrictions', [])
            }
            
            # 创建多步工作流
            tasks = create_weight_loss_workflow(crew, adapters, workflow_input)
            
            logger.info(f"📝 创建了 {len(tasks)} 个协作任务")
            for i, task in enumerate(tasks, 1):
                logger.info(f"   Task {i}: {task.description[:50]}...")
            
            # 执行Crew（CrewAI 会按依赖顺序执行各个 Task）
            crew.tasks = tasks
            logger.info("⚡ 开始执行 CrewAI 工作流...")
            result = crew.kickoff()
            logger.info("✅ 工作流执行完成")
            
            return jsonify({
                'success': True,
                'data': {
                    'response': str(result),
                    'user_id': user_id,
                    'scenario': 'weight_loss',
                    'tasks_executed': len(tasks),
                    'coordinated_agents': list(adapters.keys()),
                    'workflow_type': 'multi_step_validation'
                },
                'message': 'CrewAI多智能体协作完成（带业务工具和显式校验）'
            })
        
        else:
            # 其他场景：使用简化流程
            logger.info("🎯 场景识别: 通用咨询")
            
            from crewai import Task
            
            main_task = Task(
                description=f"""
                用户请求: {user_message}
                用户ID: {user_id}
                上下文信息: {context}
                
                请理解用户需求，协调相关智能体完成任务。
                """,
                expected_output="完整的智能响应",
                agent=adapters['conversation'].crew_agent
            )
            
            crew.tasks = [main_task]
            result = crew.kickoff()
            
            return jsonify({
                'success': True,
                'data': {
                    'response': str(result),
                    'user_id': user_id,
                    'scenario': 'general',
                    'coordinated_agents': list(adapters.keys())
                },
                'message': 'CrewAI协作完成'
            })
        
    except Exception as e:
        logger.error(f"❌ CrewAI处理失败: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@crewai_bp.route('/crew-info', methods=['GET'])
def crew_info():
    """获取Crew信息"""
    try:
        crew, adapters = init_crew()
        
        # 统计每个智能体的工具数量
        agent_tools = {}
        for name, adapter in adapters.items():
            tools_count = len(adapter.crew_agent.tools) if hasattr(adapter.crew_agent, 'tools') else 0
            agent_tools[name] = {
                'role': adapter.role,
                'tools_count': tools_count,
                'has_tools': tools_count > 0
            }
        
        return jsonify({
            'success': True,
            'data': {
                'agents_count': len(adapters),
                'agents': list(adapters.keys()),
                'agent_details': agent_tools,
                'framework': 'CrewAI',
                'features': [
                    '真正的 CrewAI 框架',
                    '业务逻辑工具集成',
                    '角色明确的智能体',
                    '自动任务协调',
                    '记忆和上下文管理',
                    '分层管理流程（hierarchical）',
                    '智能体间委托',
                    '显式工具调用',
                    '多步工作流',
                    '交叉校验'
                ]
            }
        })
    except Exception as e:
        logger.error(f"获取Crew信息失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# 创建独立的Flask应用
def create_crewai_app():
    """创建CrewAI专用Flask应用"""
    app = Flask(__name__)
    CORS(app)
    
    # 注册Blueprint
    app.register_blueprint(crewai_bp)
    
    return app


if __name__ == '__main__':
    app = create_crewai_app()
    logger.info("="*60)
    logger.info("🚀 启动 CrewAI 服务（真正的框架集成）")
    logger.info("="*60)
    app.run(host='0.0.0.0', port=5001, debug=True)
