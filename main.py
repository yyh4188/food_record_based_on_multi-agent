#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CrewAI多智能体系统 - 真正的 CrewAI 框架集成
基于CrewAI框架 + GLM-4驱动 + 业务工具，6个智能体深度协作
"""

from loguru import logger


def main():
    """启动CrewAI API服务（真正的框架集成）"""
    logger.info("=" * 70)
    logger.info("🚀 CrewAI多智能体系统 - 真正的框架集成")
    logger.info("=" * 70)
    logger.info("框架: CrewAI (真正集成)")
    logger.info("大模型: GLM-4-Flash (永久免费)")
    logger.info("智能体: 6个协作智能体")
    logger.info("工具: 每个智能体挂载业务工具（BaseAgent.process方法）")
    logger.info("流程: 多步工作流 + 显式校验")
    logger.info("=" * 70)

    from api.crewai_api import create_crewai_app

    app = create_crewai_app()

    logger.info("\n✅ CrewAI服务已启动")
    logger.info("📍 地址: http://localhost:5001")
    logger.info("\n统一接口 (真正的多智能体协作):")
    logger.info("  POST /crewai/process")
    logger.info("       ↓")
    logger.info("  1️⃣  HealthGoalAgent: 验证目标安全性（调用业务工具）")
    logger.info("  2️⃣  NutritionAnalyzerAgent: 分析营养约束（调用业务工具）")
    logger.info("  3️⃣  MealPlannerAgent: 生成+验证饮食计划（调用业务工具）")
    logger.info("  4️⃣  HealthGoalAgent: 生成进度跟踪（调用业务工具）")
    logger.info("  5️⃣  ConversationAgent: 综合总结")
    logger.info("\n辅助接口:")
    logger.info("  GET  /crewai/health     - 健康检查")
    logger.info("  GET  /crewai/crew-info  - Crew信息（含工具统计）")
    logger.info("\n💡 这是真正的 CrewAI 框架：")
    logger.info("   ✓ 每个 Agent 都有专业工具")
    logger.info("   ✓ 多步工作流（Task 依赖）")
    logger.info("   ✓ 显式校验和约束")
    logger.info("   ✓ Agent 之间互相制约")
    logger.info("=" * 70)

    app.run(host="0.0.0.0", port=5001, debug=True)


if __name__ == "__main__":
    main()
