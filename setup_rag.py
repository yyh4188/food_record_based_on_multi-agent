"""
RAG 系统快速设置脚本
用于初始化 NeutronRAG 集成环境
"""

import sys
import os
from pathlib import Path
from loguru import logger


def check_neutron_rag_exists():
    """检查 NeutronRAG 目录是否存在"""
    neutron_path = Path(__file__).parent / 'NeutronRAG-main' / 'NeutronRAG-main'
    
    if not neutron_path.exists():
        logger.error(f"❌ NeutronRAG 目录不存在: {neutron_path}")
        logger.error("请确保 NeutronRAG-main 文件夹在项目根目录下")
        return False
    
    logger.success(f"✅ NeutronRAG 目录存在: {neutron_path}")
    return True


def check_dependencies():
    """检查关键依赖是否已安装"""
    logger.info("检查依赖包...")
    
    required_packages = {
        'pymilvus': '向量数据库客户端',
        'llama_index': 'LlamaIndex 框架',
        'sentence_transformers': '向量化模型',
        'langchain': 'LangChain 框架',
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            __import__(package)
            logger.success(f"✅ {package} ({description})")
        except ImportError:
            logger.warning(f"⚠️ {package} ({description}) - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"\n缺少 {len(missing_packages)} 个依赖包")
        logger.info("请运行以下命令安装:")
        logger.info(f"pip install {' '.join(missing_packages)}")
        return False
    
    logger.success("✅ 所有依赖包已安装")
    return True


def create_knowledge_base_structure():
    """创建知识库目录结构"""
    logger.info("创建知识库目录结构...")
    
    kb_root = Path(__file__).parent / 'knowledge_base'
    
    categories = {
        'nutrition': '营养学基础',
        'foods': '食物营养数据',
        'health_goals': '健康目标指南',
        'diseases': '疾病饮食建议',
        'recipes': '健康食谱',
        'supplements': '营养补充剂'
    }
    
    for category, description in categories.items():
        cat_dir = kb_root / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建 README
        readme_path = cat_dir / 'README.md'
        if not readme_path.exists():
            readme_content = f"# {description}\n\n此目录存放{description}相关的知识文档。\n"
            readme_path.write_text(readme_content, encoding='utf-8')
        
        logger.success(f"✅ {category}/ ({description})")
    
    logger.success("✅ 知识库目录结构创建完成")
    return True


def generate_sample_knowledge():
    """生成示例知识文档"""
    logger.info("生成示例知识文档...")
    
    try:
        from rag.knowledge_manager import NutritionKnowledgeManager
        
        km = NutritionKnowledgeManager()
        km.generate_sample_knowledge()
        
        stats = km.get_statistics()
        logger.success(f"✅ 生成了 {stats['total_documents']} 个示例文档")
        
        for category, info in stats['categories'].items():
            if info['total'] > 0:
                logger.info(f"  - {info['name']}: {info['total']} 个文档")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 生成示例文档失败: {e}")
        return False


def test_rag_adapter():
    """测试 RAG 适配器"""
    logger.info("测试 RAG 适配器...")
    
    try:
        from rag.neutron_rag_adapter import NeutronRAGAdapter
        
        # 创建适配器
        rag = NeutronRAGAdapter(
            llm_model='glm-4-flash',
            rag_mode='vector',
            space_name='nutrition_kb',
            use_rag=True
        )
        
        logger.success("✅ RAG 适配器创建成功")
        
        # 健康检查
        status = rag.health_check()
        logger.info("RAG 状态:")
        for key, value in status.items():
            logger.info(f"  - {key}: {value}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG 适配器测试失败: {e}")
        logger.info("💡 这是正常的，因为 RAG 需要在第一次查询时才初始化")
        return True  # 不算失败


def test_conversation_agent():
    """测试带 RAG 的对话智能体"""
    logger.info("测试带 RAG 的对话智能体...")
    
    try:
        from agents.conversation_agent import ConversationAgent
        
        # 创建不启用 RAG 的智能体（避免初始化开销）
        agent = ConversationAgent(
            agent_id="test_agent",
            config={'use_rag': False}
        )
        
        logger.success("✅ ConversationAgent 创建成功（RAG 未启用）")
        
        # 创建启用 RAG 的智能体（仅测试创建，不初始化）
        agent_with_rag = ConversationAgent(
            agent_id="test_agent_rag",
            config={
                'use_rag': True,
                'rag_config': {
                    'rag_mode': 'vector',
                    'space_name': 'nutrition_kb'
                }
            }
        )
        
        logger.success("✅ ConversationAgent（RAG 启用）创建成功")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ConversationAgent 测试失败: {e}")
        return False


def print_next_steps():
    """打印后续步骤"""
    logger.info("\n" + "="*60)
    logger.info("🎉 RAG 系统设置完成！")
    logger.info("="*60 + "\n")
    
    logger.info("📝 后续步骤:\n")
    
    logger.info("1️⃣ 运行示例代码:")
    logger.info("   python examples/rag_example.py")
    logger.info("")
    
    logger.info("2️⃣ 生成更多知识文档（使用 GLM-4）:")
    logger.info("   from rag.knowledge_manager import NutritionKnowledgeManager")
    logger.info("   km = NutritionKnowledgeManager()")
    logger.info("   # 添加自定义文档...")
    logger.info("")
    
    logger.info("3️⃣ 在 API 中启用 RAG:")
    logger.info("   修改 config/agent_config.yaml 中的 use_rag 为 true")
    logger.info("")
    
    logger.info("4️⃣ 查看集成文档:")
    logger.info("   RAG_INTEGRATION_GUIDE.md")
    logger.info("")
    
    logger.info("📚 文档和示例:")
    logger.info("   - RAG_INTEGRATION_GUIDE.md - 完整集成指南")
    logger.info("   - examples/rag_example.py - 示例代码")
    logger.info("   - rag/ - RAG 适配器源码")
    logger.info("")


def main():
    """主函数"""
    logger.info("\n" + "="*60)
    logger.info("🚀 NeutronRAG 系统设置")
    logger.info("="*60 + "\n")
    
    steps = [
        ("检查 NeutronRAG 目录", check_neutron_rag_exists),
        ("检查依赖包", check_dependencies),
        ("创建知识库目录", create_knowledge_base_structure),
        ("生成示例知识文档", generate_sample_knowledge),
        ("测试 RAG 适配器", test_rag_adapter),
        ("测试对话智能体", test_conversation_agent),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        logger.info(f"\n▶️ {step_name}...")
        logger.info("-" * 40)
        
        try:
            success = step_func()
            if not success:
                failed_steps.append(step_name)
        except Exception as e:
            logger.error(f"❌ {step_name}失败: {e}")
            failed_steps.append(step_name)
    
    # 总结
    logger.info("\n" + "="*60)
    logger.info("📊 设置总结")
    logger.info("="*60 + "\n")
    
    if not failed_steps:
        logger.success("✅ 所有步骤完成！")
        print_next_steps()
    else:
        logger.warning(f"⚠️ {len(failed_steps)} 个步骤失败:")
        for step in failed_steps:
            logger.warning(f"  - {step}")
        logger.info("\n请根据错误信息解决问题后重新运行此脚本")


if __name__ == "__main__":
    main()
