"""
CrewAI适配器 - 真正的 CrewAI 框架集成
将现有的BaseAgent智能体适配为CrewAI Agent，并挂载业务工具
"""

from typing import Dict, Any, Optional, List
from crewai import Agent, Task, Crew, Process
from langchain.llms.base import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from utils.glm4_client import GLM4Client, get_glm4_client
from utils.crewai_tools import create_agent_tools
from loguru import logger as main_logger


class GLM4LangChainWrapper(LLM):
    """将GLM4Client包装为LangChain LLM"""
    
    client: GLM4Client
    
    def __init__(self, client: GLM4Client = None):
        """初始化LangChain包装器"""
        super().__init__()
        self.client = client or get_glm4_client()
    
    @property
    def _llm_type(self) -> str:
        """返回LLM类型"""
        return "glm4"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """调用GLM-4生成回复"""
        messages = [{"role": "user", "content": prompt}]
        return self.client.chat(messages, **kwargs)


class CrewAIAgentAdapter:
    """CrewAI智能体适配器 - 带工具集成"""
    
    def __init__(self, base_agent, role: str, goal: str, backstory: str, enable_tools: bool = True):
        """
        初始化适配器
        
        Args:
            base_agent: 我们现有的BaseAgent实例
            role: 智能体角色
            goal: 智能体目标
            backstory: 智能体背景故事
            enable_tools: 是否启用业务工具（默认True）
        """
        self.base_agent = base_agent
        self.role = role
        self.goal = goal
        self.backstory = backstory
        
        # 创建LangChain包装的GLM-4客户端
        if hasattr(base_agent, 'llm_client') and base_agent.llm_client:
            self.llm = GLM4LangChainWrapper(base_agent.llm_client)
        else:
            self.llm = GLM4LangChainWrapper()
        
        # 创建业务工具（把 BaseAgent 的 process 方法暴露给 CrewAI）
        tools = []
        if enable_tools:
            tools = create_agent_tools(base_agent)
            main_logger.info(f"✅ 为 {base_agent.agent_id} 创建了 {len(tools)} 个工具")
        
        # 创建CrewAI Agent
        self.crew_agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=self.llm,
            tools=tools,  # 挂载业务工具
            verbose=True,
            allow_delegation=True,
            memory=True
        )
    
    def create_task(self, description: str, expected_output: str, context: List[Task] = None) -> Task:
        """
        创建任务
        
        Args:
            description: 任务描述
            expected_output: 期望输出
            context: 依赖的前置任务列表
            
        Returns:
            CrewAI Task实例
        """
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.crew_agent,
            context=context or []
        )


def create_health_crew(
    food_agent,
    nutrition_agent,
    health_agent,
    meal_agent,
    conversation_agent,
    recommendation_agent
):
    """
    创建健康饮食Crew - 真正的 CrewAI 集成
    
    Args:
        各个智能体实例
        
    Returns:
        配置好的Crew实例和适配器字典
    """
    
    # 适配各个智能体（启用工具）
    food_adapter = CrewAIAgentAdapter(
        food_agent,
        role="食物识别专家",
        goal="准确识别食物并提取营养成分信息",
        backstory="拥有丰富经验的食品营养分析师，精通各类食材的营养特性。可以调用专业工具进行食物识别。",
        enable_tools=True
    )
    
    nutrition_adapter = CrewAIAgentAdapter(
        nutrition_agent,
        role="营养分析师",
        goal="分析食物营养价值并提供专业健康建议，验证营养平衡",
        backstory="注册营养师，专注于个性化营养方案制定。拥有营养分析工具和验证工具。",
        enable_tools=True
    )
    
    health_adapter = CrewAIAgentAdapter(
        health_agent,
        role="健康目标教练",
        goal="跟踪用户健康目标进度、验证目标安全性并提供激励建议",
        backstory="资深健康管理顾问，帮助数千人达成健康目标。能够评估目标的合理性和安全性。",
        enable_tools=True
    )
    
    meal_adapter = CrewAIAgentAdapter(
        meal_agent,
        role="饮食计划设计师",
        goal="设计科学合理的个性化饮食计划，并验证计划的合理性",
        backstory="创意营养餐设计师，擅长平衡美味与健康。可以生成饮食计划并自我验证。",
        enable_tools=True
    )
    
    conversation_adapter = CrewAIAgentAdapter(
        conversation_agent,
        role="健康咨询总协调",
        goal="理解用户需求，协调各专家团队，提供综合解决方案",
        backstory="温暖亲切的健康顾问，善于倾听和沟通。负责协调团队中其他专家的工作。",
        enable_tools=False  # 协调者不需要工具，主要负责沟通
    )
    
    recommendation_adapter = CrewAIAgentAdapter(
        recommendation_agent,
        role="社区内容推荐专家",
        goal="为用户推荐相关的健康内容和社区资源",
        backstory="熟悉各类健康资讯，善于发现优质内容",
        enable_tools=False
    )
    
    # 创建Crew（使用分层流程，由 conversation 作为 manager）
    crew = Crew(
        agents=[
            conversation_adapter.crew_agent,  # Manager 放第一位
            health_adapter.crew_agent,
            nutrition_adapter.crew_agent,
            meal_adapter.crew_agent,
            food_adapter.crew_agent,
            recommendation_adapter.crew_agent
        ],
        process=Process.hierarchical,  # 分层管理
        manager_agent=conversation_adapter.crew_agent,  # 指定 manager
        verbose=True,
        memory=True,  # 启用记忆功能
        embedder={
            "provider": "huggingface",
            "config": {
                "model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        }
    )
    
    return crew, {
        'food': food_adapter,
        'nutrition': nutrition_adapter,
        'health': health_adapter,
        'meal': meal_adapter,
        'conversation': conversation_adapter,
        'recommendation': recommendation_adapter
    }


def create_weight_loss_workflow(crew: Crew, adapters: Dict, user_input: Dict[str, Any]) -> List[Task]:
    """
    创建减脂场景的多步工作流
    这是真正的 CrewAI 多智能体协作，带显式校验
    
    Args:
        crew: Crew实例
        adapters: 智能体适配器字典
        user_input: 用户输入 {
            'user_id', 'current_weight', 'target_weight', 
            'days', 'target_calories', 'dietary_preferences', 'restrictions'
        }
    
    Returns:
        任务列表（按依赖顺序）
    """
    
    main_logger.info("🚀 创建减脂工作流 - 多智能体协作模式")
    
    # Task 1: 健康目标安全性验证（第一步，必须先验证）
    task1_goal_safety = adapters['health'].create_task(
        description=f"""
        验证减脂目标的安全性：
        - 当前体重: {user_input.get('current_weight')} kg
        - 目标体重: {user_input.get('target_weight')} kg
        - 计划天数: {user_input.get('days')} 天
        
        使用 "验证目标安全性" 工具进行评估。
        如果目标不安全，必须给出调整建议。
        """,
        expected_output="目标安全性评估报告，包括是否安全、风险等级、建议"
    )
    
    # Task 2: 营养约束分析（基于目标）
    task2_nutrition_constraints = adapters['nutrition'].create_task(
        description=f"""
        基于用户的减脂目标，分析营养约束：
        - 目标热量: {user_input.get('target_calories')} kcal/天
        - 用户偏好: {user_input.get('dietary_preferences', [])}
        - 饮食限制: {user_input.get('restrictions', [])}
        
        使用 "验证营养平衡" 工具检查这个热量和营养配比是否合理。
        如果Task 1显示目标不安全，需要调整热量建议。
        """,
        expected_output="营养约束报告，包括每日各营养素的范围要求",
        context=[task1_goal_safety]
    )
    
    # Task 3: 生成饮食计划（基于前两步的约束）
    task3_meal_plan = adapters['meal'].create_task(
        description=f"""
        根据前面两步的安全验证和营养约束，生成 {user_input.get('days')} 天的饮食计划：
        - 目标热量: 参考Task 2的调整建议
        - 营养分配: 符合Task 2的营养约束
        - 用户偏好: {user_input.get('dietary_preferences', [])}
        - 饮食限制: {user_input.get('restrictions', [])}
        
        使用 "生成饮食计划" 工具创建计划。
        生成后，必须使用 "验证饮食计划合理性" 工具进行自检。
        如果验证不通过，需要调整计划。
        """,
        expected_output="经过验证的完整饮食计划，包括每日三餐、加餐、总营养",
        context=[task1_goal_safety, task2_nutrition_constraints]
    )
    
    # Task 4: 健康目标进度跟踪（生成后续指导）
    task4_progress_tracking = adapters['health'].create_task(
        description=f"""
        基于最终确定的饮食计划，生成健康目标跟踪方案：
        - 用户ID: {user_input.get('user_id')}
        - 目标类型: weight_loss
        - 当前数据: 体重 {user_input.get('current_weight')} kg
        - 目标: 体重 {user_input.get('target_weight')} kg
        
        使用 "分析健康目标进度" 工具生成跟踪方案。
        提供里程碑、检查点、激励建议。
        """,
        expected_output="健康目标跟踪方案，包括里程碑、检查频率、预期进度",
        context=[task3_meal_plan]
    )
    
    # Task 5: 综合解决方案（由协调者总结）
    task5_final_summary = adapters['conversation'].create_task(
        description=f"""
        综合前面4个专家的工作成果，为用户提供完整的减脂方案：
        1. 目标安全性评估（Task 1）
        2. 营养约束（Task 2）
        3. 饮食计划（Task 3）
        4. 进度跟踪方案（Task 4）
        
        用友好、专业的语言解释：
        - 这个减脂计划是否安全
        - 每天应该吃什么
        - 如何跟踪进度
        - 注意事项和建议
        """,
        expected_output="用户友好的完整减脂方案，包含所有关键信息和温馨提示",
        context=[task1_goal_safety, task2_nutrition_constraints, task3_meal_plan, task4_progress_tracking]
    )
    
    return [
        task1_goal_safety,
        task2_nutrition_constraints,
        task3_meal_plan,
        task4_progress_tracking,
        task5_final_summary
    ]
