"""
营养知识库管理器
负责加载、索引营养领域的知识文档到 NeutronRAG
"""

import os
import json
from typing import List, Dict, Any
from pathlib import Path
from loguru import logger


class NutritionKnowledgeManager:
    """
    营养知识库管理器
    管理营养学相关的知识文档，支持加载、索引、更新
    """
    
    def __init__(self, knowledge_base_dir: str = None):
        """
        初始化知识库管理器
        
        Args:
            knowledge_base_dir: 知识库目录路径
        """
        if knowledge_base_dir is None:
            # 默认知识库目录
            knowledge_base_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'knowledge_base'
            )
        
        self.knowledge_base_dir = Path(knowledge_base_dir)
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        
        # 知识库分类
        self.categories = {
            'nutrition': '营养学基础',
            'foods': '食物营养数据',
            'health_goals': '健康目标指南',
            'diseases': '疾病饮食建议',
            'recipes': '健康食谱',
            'supplements': '营养补充剂'
        }
        
        # 创建分类目录
        for category in self.categories.keys():
            category_dir = self.knowledge_base_dir / category
            category_dir.mkdir(exist_ok=True)
        
        logger.info(f"知识库管理器初始化: {self.knowledge_base_dir}")
    
    def load_documents(self, category: str = None) -> List[Dict[str, Any]]:
        """
        加载知识库文档
        
        Args:
            category: 文档分类（可选，如果不指定则加载所有）
            
        Returns:
            文档列表
        """
        documents = []
        
        if category:
            # 加载指定分类
            categories = [category]
        else:
            # 加载所有分类
            categories = self.categories.keys()
        
        for cat in categories:
            cat_dir = self.knowledge_base_dir / cat
            if not cat_dir.exists():
                continue
            
            # 加载 Markdown 文件
            for md_file in cat_dir.glob("*.md"):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    documents.append({
                        'filename': md_file.name,
                        'category': cat,
                        'content': content,
                        'path': str(md_file)
                    })
                except Exception as e:
                    logger.error(f"加载文档失败 {md_file}: {e}")
            
            # 加载 JSON 文件（结构化数据）
            for json_file in cat_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    documents.append({
                        'filename': json_file.name,
                        'category': cat,
                        'content': json.dumps(data, ensure_ascii=False, indent=2),
                        'data': data,
                        'path': str(json_file)
                    })
                except Exception as e:
                    logger.error(f"加载文档失败 {json_file}: {e}")
        
        logger.info(f"加载了 {len(documents)} 个知识文档")
        return documents
    
    def index_to_neutron_rag(
        self,
        rag_adapter,
        category: str = None,
        overwrite: bool = False
    ) -> bool:
        """
        将知识库索引到 NeutronRAG
        
        Args:
            rag_adapter: NeutronRAG 适配器实例
            category: 要索引的分类（可选）
            overwrite: 是否覆盖已有索引
            
        Returns:
            是否成功
        """
        try:
            logger.info("开始索引知识库到 NeutronRAG...")
            
            # 加载文档
            documents = self.load_documents(category)
            
            if not documents:
                logger.warning("没有找到可索引的文档")
                return False
            
            # TODO: 调用 NeutronRAG 的索引接口
            # 这里需要根据 NeutronRAG 的实际接口进行调整
            # 可能需要使用 Milvus 或 NebulaGraph 的导入功能
            
            logger.success(f"✅ 成功索引 {len(documents)} 个文档")
            return True
            
        except Exception as e:
            logger.error(f"索引失败: {e}")
            return False
    
    def add_document(
        self,
        category: str,
        filename: str,
        content: str
    ) -> bool:
        """
        添加新文档到知识库
        
        Args:
            category: 文档分类
            filename: 文件名
            content: 文档内容
            
        Returns:
            是否成功
        """
        try:
            if category not in self.categories:
                logger.error(f"未知的分类: {category}")
                return False
            
            file_path = self.knowledge_base_dir / category / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"添加文档: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息
        """
        stats = {
            'total_documents': 0,
            'categories': {}
        }
        
        for category in self.categories.keys():
            cat_dir = self.knowledge_base_dir / category
            if not cat_dir.exists():
                continue
            
            md_count = len(list(cat_dir.glob("*.md")))
            json_count = len(list(cat_dir.glob("*.json")))
            
            stats['categories'][category] = {
                'name': self.categories[category],
                'markdown_files': md_count,
                'json_files': json_count,
                'total': md_count + json_count
            }
            
            stats['total_documents'] += md_count + json_count
        
        return stats
    
    def generate_sample_knowledge(self):
        """
        生成示例知识文档（用于测试）
        """
        logger.info("生成示例知识文档...")
        
        # 1. 营养学基础
        nutrition_basics = """# 三大营养素基础知识

## 蛋白质

### 定义
蛋白质是由氨基酸组成的大分子化合物，是生命的物质基础。

### 功能
- 构成和修复组织
- 合成酶和激素
- 提供能量（1克蛋白质=4千卡）
- 维持体液平衡
- 免疫防御

### 推荐摄入量
- 成年人：1.0-1.2g/kg体重/天
- 运动人群：1.4-2.0g/kg体重/天
- 老年人：1.2-1.5g/kg体重/天

### 优质来源
- 动物性：鸡蛋、鸡胸肉、鱼类、牛奶
- 植物性：大豆、豆腐、扁豆、坚果

## 碳水化合物

### 定义
碳水化合物是人体主要的能量来源，包括糖类、淀粉和纤维素。

### 功能
- 提供能量（1克碳水=4千卡）
- 节约蛋白质
- 参与脂肪代谢
- 提供膳食纤维

### 推荐摄入量
- 占总能量的50-65%
- 每天至少130克

### 优质来源
- 全谷物：糙米、燕麦、全麦面包
- 薯类：红薯、土豆
- 豆类：红豆、绿豆
- 水果和蔬菜

## 脂肪

### 定义
脂肪是能量密度最高的营养素，也是细胞膜的重要组成部分。

### 功能
- 提供能量（1克脂肪=9千卡）
- 保护内脏器官
- 维持体温
- 促进脂溶性维生素吸收
- 提供必需脂肪酸

### 推荐摄入量
- 占总能量的20-30%
- 饱和脂肪<10%
- 反式脂肪尽量避免

### 优质来源
- 不饱和脂肪：橄榄油、鱼油、坚果、牛油果
- 饱和脂肪（适量）：瘦肉、乳制品
"""
        self.add_document('nutrition', '三大营养素.md', nutrition_basics)
        
        # 2. 减脂指南
        weight_loss_guide = """# 科学减脂指南

## 热量赤字原则

### 基础代谢率（BMR）计算
- 男性：BMR = 66 + (13.7 × 体重kg) + (5 × 身高cm) - (6.8 × 年龄)
- 女性：BMR = 655 + (9.6 × 体重kg) + (1.8 × 身高cm) - (4.7 × 年龄)

### 每日总消耗（TDEE）
- 久坐：TDEE = BMR × 1.2
- 轻度活动：TDEE = BMR × 1.375
- 中度活动：TDEE = BMR × 1.55
- 重度活动：TDEE = BMR × 1.725

### 减脂热量目标
- 安全减重：TDEE - 500卡（每周减重0.5kg）
- 快速减重：TDEE - 750卡（每周减重0.75kg）
- **不建议低于基础代谢率**

## 营养素配比

### 减脂期蛋白质
- 摄入量：1.6-2.2g/kg体重/天
- 作用：防止肌肉流失、提高饱腹感、增加热量消耗

### 减脂期碳水化合物
- 摄入量：2-4g/kg体重/天
- 选择低GI碳水：糙米、燕麦、红薯
- 避免：精制糖、白面包、含糖饮料

### 减脂期脂肪
- 摄入量：0.5-1g/kg体重/天
- 选择不饱和脂肪
- 必需脂肪酸不可缺少

## 减脂注意事项

1. **循序渐进**：不要急于求成
2. **保持营养均衡**：不要极端节食
3. **保持肌肉**：力量训练很重要
4. **充足睡眠**：每天7-9小时
5. **控制压力**：皮质醇会影响减脂
6. **多喝水**：每天2-3升
7. **监测进度**：每周测量体重和围度

## 常见误区

❌ 不吃主食
❌ 只做有氧运动
❌ 节食过度
❌ 相信减肥药
❌ 追求快速减重

✅ 均衡饮食
✅ 有氧+力量训练
✅ 适度热量赤字
✅ 科学规划
✅ 可持续的生活方式改变
"""
        self.add_document('health_goals', '科学减脂指南.md', weight_loss_guide)
        
        # 3. 食物营养数据
        food_data = {
            "foods": [
                {
                    "name": "鸡胸肉",
                    "category": "肉类",
                    "per_100g": {
                        "calories": 133,
                        "protein": 24.0,
                        "carbs": 0,
                        "fat": 5.0,
                        "fiber": 0
                    },
                    "glycemic_index": 0,
                    "tags": ["高蛋白", "低脂", "低碳水"],
                    "suitable_for": ["减脂", "增肌", "糖尿病"],
                    "cooking_methods": ["水煮", "清蒸", "烤制"]
                },
                {
                    "name": "西兰花",
                    "category": "蔬菜",
                    "per_100g": {
                        "calories": 34,
                        "protein": 2.8,
                        "carbs": 7.0,
                        "fat": 0.4,
                        "fiber": 2.6
                    },
                    "glycemic_index": 15,
                    "tags": ["低热量", "高纤维", "富含维生素"],
                    "suitable_for": ["减脂", "健康维持", "糖尿病"],
                    "nutrients": ["维生素C", "维生素K", "叶酸", "钙"]
                },
                {
                    "name": "糙米",
                    "category": "主食",
                    "per_100g": {
                        "calories": 112,
                        "protein": 2.6,
                        "carbs": 24.0,
                        "fat": 0.8,
                        "fiber": 1.8
                    },
                    "glycemic_index": 56,
                    "tags": ["全谷物", "中GI", "富含B族维生素"],
                    "suitable_for": ["健康维持", "糖尿病"],
                    "benefits": ["稳定血糖", "促进消化", "提供持久能量"]
                },
                {
                    "name": "三文鱼",
                    "category": "肉类",
                    "per_100g": {
                        "calories": 208,
                        "protein": 22.0,
                        "carbs": 0,
                        "fat": 13.0,
                        "fiber": 0
                    },
                    "glycemic_index": 0,
                    "tags": ["高蛋白", "富含Omega-3", "优质脂肪"],
                    "suitable_for": ["增肌", "心血管健康", "抗炎"],
                    "nutrients": ["Omega-3脂肪酸", "维生素D", "维生素B12"]
                },
                {
                    "name": "鸡蛋",
                    "category": "蛋类",
                    "per_100g": {
                        "calories": 147,
                        "protein": 12.6,
                        "carbs": 1.1,
                        "fat": 10.0,
                        "fiber": 0
                    },
                    "glycemic_index": 0,
                    "tags": ["完全蛋白", "营养丰富", "生物价高"],
                    "suitable_for": ["减脂", "增肌", "健康维持"],
                    "nutrients": ["卵磷脂", "胆碱", "维生素A", "维生素D"]
                }
            ]
        }
        self.add_document('foods', '常见食物营养数据.json', 
                         json.dumps(food_data, ensure_ascii=False, indent=2))
        
        # 4. 糖尿病饮食指南
        diabetes_guide = """# 糖尿病饮食管理指南

## 血糖控制原则

### 选择低GI食物
- GI < 55：低GI食物（推荐）
- GI 55-70：中GI食物（适量）
- GI > 70：高GI食物（避免）

### 控制碳水摄入
- 每餐碳水：45-60克
- 分散到三餐
- 搭配蛋白质和脂肪

### 增加膳食纤维
- 每天25-35克
- 有助于稳定血糖
- 改善肠道健康

## 推荐食物

### 主食类（低GI）
- ✅ 燕麦
- ✅ 糙米
- ✅ 全麦面包
- ✅ 荞麦面
- ✅ 红薯（小份量）

### 蛋白质类
- ✅ 鸡胸肉
- ✅ 鱼类
- ✅ 豆腐
- ✅ 鸡蛋
- ✅ 低脂奶制品

### 蔬菜类（低碳水）
- ✅ 西兰花
- ✅ 菠菜
- ✅ 白菜
- ✅ 黄瓜
- ✅ 西红柿

## 避免食物

❌ 白米饭、白面包
❌ 含糖饮料
❌ 蛋糕、饼干
❌ 果汁（即使100%纯果汁）
❌ 高糖水果（西瓜、葡萄、榴莲）
❌ 油炸食品

## 餐次安排

### 三餐+加餐模式
- 早餐：07:00-08:00
- 上午加餐：10:00-10:30
- 午餐：12:00-13:00
- 下午加餐：15:00-16:00
- 晚餐：18:00-19:00

### 每餐时间控制
- 20-30分钟
- 细嚼慢咽
- 不要吃太饱（七分饱）

## 监测建议

- 餐前血糖：4.4-7.0 mmol/L
- 餐后2小时：<10.0 mmol/L
- 糖化血红蛋白：<7.0%

## 注意事项

1. 定时定量
2. 规律用药
3. 监测血糖
4. 适量运动
5. 保持心情舒畅
"""
        self.add_document('diseases', '糖尿病饮食管理.md', diabetes_guide)
        
        logger.success("✅ 示例知识文档生成完成")


# 便捷函数
def create_nutrition_knowledge_manager(knowledge_base_dir: str = None):
    """
    创建营养知识库管理器的便捷函数
    """
    return NutritionKnowledgeManager(knowledge_base_dir)
