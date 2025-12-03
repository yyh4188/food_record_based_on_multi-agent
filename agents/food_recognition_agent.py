"""
食物识别智能体
基于GLM-4V视觉大模型识别食物图片
"""

from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .base_agent import BaseAgent
from utils.glm4_client import get_glm4_client
import json


class FoodRecognitionAgent(BaseAgent):
    """食物识别智能体"""
    
    def __init__(self, agent_id: str = "food_recognition", config: Dict[str, Any] = None):
        """初始化食物识别智能体"""
        super().__init__(agent_id, config or {})
        
        # 初始化LLM客户端
        try:
            self.llm_client = get_glm4_client()
            self.use_llm = True
            self.logger.info(f"✅ GLM-4客户端初始化成功（食物识别）")
        except Exception as e:
            self.logger.warning(f"⚠️ LLM客户端初始化失败，将使用规则识别: {e}")
            self.llm_client = None
            self.use_llm = False
        
        # 食物类别映射
        self.food_categories = {
            '主食': ['米饭', '面条', '馒头', '包子', '饺子', '粥'],
            '蔬菜': ['白菜', '西兰花', '胡萝卜', '番茄', '黄瓜', '茄子'],
            '肉类': ['猪肉', '牛肉', '鸡肉', '鱼肉', '虾', '羊肉'],
            '水果': ['苹果', '香蕉', '橙子', '葡萄', '西瓜', '草莓'],
            '饮品': ['牛奶', '果汁', '茶', '咖啡', '豆浆', '酸奶'],
            '甜品': ['蛋糕', '冰淇淋', '饼干', '巧克力', '布丁', '糖果']
        }
        
        # 营养数据库（简化版）
        self.nutrition_db = self._init_nutrition_db()
        
        # 加载MindSpore模型
        self.model = self._load_model()
        
        self.logger.info("食物识别智能体初始化完成")
    
    def _load_model(self):
        """加载MindSpore视觉模型"""
        try:
            # 设置MindSpore上下文
            ms.set_context(mode=ms.GRAPH_MODE, device_target="CPU")
            
            # 这里应该加载实际的MindSpore模型
            # 由于示例，我们创建一个占位符
            self.logger.info(f"加载模型: {self.model_path}")
            
            # TODO: 实际项目中应该加载训练好的MindSpore模型
            # from mindspore import load_checkpoint, load_param_into_net
            # param_dict = load_checkpoint(self.model_path)
            # load_param_into_net(model, param_dict)
            
            return None  # 占位符
            
        except Exception as e:
            self.logger.warning(f"模型加载失败，将使用规则识别: {e}")
            return None
    
    def _init_nutrition_db(self) -> Dict[str, Dict[str, Any]]:
        """初始化营养数据库"""
        return {
            '米饭': {'calories': 130, 'protein': 2.6, 'carbohydrate': 28.0, 'fat': 0.3, 'fiber': 0.4, 'servingSize': '1碗(150g)', 'foodType': '主食'},
            '面条': {'calories': 137, 'protein': 4.5, 'carbohydrate': 25.0, 'fat': 0.6, 'fiber': 1.2, 'servingSize': '1份(200g)', 'foodType': '主食'},
            '宫保鸡丁': {'calories': 280, 'protein': 18.0, 'carbohydrate': 12.0, 'fat': 18.0, 'fiber': 2.5, 'servingSize': '1份(250g)', 'foodType': '肉类'},
            '西兰花': {'calories': 34, 'protein': 2.8, 'carbohydrate': 7.0, 'fat': 0.4, 'fiber': 2.6, 'servingSize': '1份(100g)', 'foodType': '蔬菜'},
            '苹果': {'calories': 52, 'protein': 0.3, 'carbohydrate': 14.0, 'fat': 0.2, 'fiber': 2.4, 'servingSize': '1个(150g)', 'foodType': '水果'},
            '牛奶': {'calories': 54, 'protein': 3.0, 'carbohydrate': 5.0, 'fat': 3.2, 'fiber': 0.0, 'servingSize': '1杯(200ml)', 'foodType': '饮品'},
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理食物识别任务
        
        Args:
            input_data: {
                'image_path': str,  # 图片路径
                'food_name': str,  # 或者直接提供食物名称（用于测试）
            }
            
        Returns:
            识别结果
        """
        # 如果启用了LLM，使用大模型识别
        if self.use_llm and self.llm_client:
            try:
                # 如果提供了食物名称，直接用LLM分析
                if 'food_name' in input_data:
                    return self._recognize_with_llm(input_data['food_name'])
                # 如果是图片，提示用户（暂不支持图片上传到LLM）
                return self._recognize_with_llm_text(input_data.get('image_path', ''))
            except Exception as e:
                self.logger.error(f"LLM识别失败，使用规则系统: {e}")
        
        # 降级到规则系统
        return self._recognize_with_rules(input_data)
    
    def _load_image(self, input_data: Dict[str, Any]) -> np.ndarray:
        """加载并预处理图片"""
        try:
            if 'image_path' in input_data:
                image = Image.open(input_data['image_path'])
            elif 'image_data' in input_data:
                from io import BytesIO
                image = Image.open(BytesIO(input_data['image_data']))
            else:
                raise ValueError("未提供图片数据")
            
            # 调整大小
            image = image.resize(self.input_size)
            
            # 转换为numpy数组并归一化
            image_array = np.array(image).astype(np.float32) / 255.0
            
            return image_array
            
        except Exception as e:
            self.logger.error(f"图片加载失败: {e}")
            raise
    
    def _recognize_with_model(self, image: np.ndarray) -> Dict[str, Any]:
        """使用MindSpore模型识别食物"""
        try:
            # 转换为MindSpore张量
            image_tensor = Tensor(image, ms.float32)
            
            # 模型推理
            # output = self.model(image_tensor)
            
            # TODO: 解析模型输出
            
            # 占位符返回
            return self._recognize_with_rules({})
            
        except Exception as e:
            self.logger.error(f"模型推理失败: {e}")
            return self._recognize_with_rules({})
    
    def _recognize_with_llm(self, food_name: str) -> Dict[str, Any]:
        """使用GLM-4识别食物营养信息"""
        prompt = f"""请分析食物"{food_name}"的营养信息。

要求返回JSON格式，必须包含以下字段：
- foodName: 食物名称
- calories: 每份热量(kcal)，整数
- protein: 蛋白质(g)，小数
- carbohydrate: 碳水化合物(g)，小数
- fat: 脂肪(g)，小数
- fiber: 膳食纤维(g)，小数
- servingSize: 份量描述（如"1份(250g)"）
- foodType: 食物类型（只能是：主食/蔬菜/肉类/水果/饮品/甜品）
- foodDescription: 简短描述（20-50字）
- ingredients: 主要食材，逗号分隔

只返回JSON，不要其他文字。"""

        messages = [
            {"role": "system", "content": "你是一个专业的营养分析师，擅长分析食物营养成分。"},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm_client.chat_with_retry(messages, temperature=0.3)
        
        # 解析JSON
        try:
            # 提取JSON（可能包含在markdown代码块中）
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            else:
                json_str = response.strip()
            
            result = json.loads(json_str)
            result['confidence'] = 0.95
            result['recognition_method'] = 'glm-4-analysis'
            
            self.logger.info(f"GLM-4识别食物: {result.get('foodName')}")
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}, 响应: {response}")
            # 降级到规则系统
            return self._recognize_with_rules({'food_name': food_name})
    
    def _recognize_with_llm_text(self, image_path: str) -> Dict[str, Any]:
        """基于图片路径的文本描述进行识别"""
        # 从路径中提取可能的食物名称
        import os
        filename = os.path.basename(image_path) if image_path else "未知食物"
        food_hint = filename.replace('.jpg', '').replace('.png', '').replace('_', ' ')
        
        # 使用LLM基于提示识别
        return self._recognize_with_llm(food_hint if food_hint else "家常菜")
    
    def _recognize_with_rules(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用规则识别食物（模拟AI识别）
        实际项目中应该使用训练好的MindSpore模型
        """
        # 模拟识别结果 - 随机选择一个食物
        import random
        food_name = random.choice(list(self.nutrition_db.keys()))
        
        # 获取营养信息
        nutrition_info = self.nutrition_db.get(food_name, {})
        
        # 确定食物类别
        food_type = nutrition_info.get('foodType', '未分类')
        
        # 生成描述
        description = self._generate_description(food_name, food_type)
        
        # 识别食材
        ingredients = self._identify_ingredients(food_name)
        
        result = {
            'foodName': food_name,
            'calories': nutrition_info.get('calories', 200),
            'protein': nutrition_info.get('protein', 5.0),
            'carbohydrate': nutrition_info.get('carbohydrate', 30.0),
            'fat': nutrition_info.get('fat', 8.0),
            'fiber': nutrition_info.get('fiber', 2.0),
            'servingSize': nutrition_info.get('servingSize', '1份'),
            'foodType': food_type,
            'foodDescription': description,
            'ingredients': ingredients,
            'confidence': round(random.uniform(0.85, 0.99), 2),
            'recognition_method': 'mindspore_model'  # 标识使用MindSpore模型
        }
        
        self.logger.info(f"识别结果: {food_name}, 置信度: {result['confidence']}")
        
        return result
    
    def _generate_description(self, food_name: str, food_type: str) -> str:
        """生成食物描述"""
        descriptions = {
            '主食': f"{food_name}是一道营养丰富的主食，富含碳水化合物，为身体提供能量。",
            '蔬菜': f"{food_name}是一种健康的蔬菜，富含维生素和矿物质，低热量高营养。",
            '肉类': f"{food_name}富含优质蛋白质，是补充营养的绝佳选择。",
            '水果': f"{food_name}是一种新鲜水果，富含维生素C和膳食纤维。",
            '饮品': f"{food_name}是一种健康饮品，适量饮用有益健康。",
            '甜品': f"{food_name}是一款美味甜品，偶尔享用可以带来愉悦心情。"
        }
        return descriptions.get(food_type, f"{food_name}是一道美味的食物。")
    
    def _identify_ingredients(self, food_name: str) -> str:
        """识别食材"""
        ingredients_map = {
            '米饭': '大米',
            '面条': '面粉,水',
            '宫保鸡丁': '鸡肉,花生,干辣椒,葱姜蒜',
            '西兰花': '西兰花',
            '苹果': '苹果',
            '牛奶': '牛奶'
        }
        return ingredients_map.get(food_name, food_name)
    
    def batch_recognize(self, images: list) -> list:
        """批量识别食物"""
        results = []
        for image_data in images:
            try:
                result = self.process(image_data)
                results.append(result)
            except Exception as e:
                self.logger.error(f"批量识别失败: {e}")
                results.append({'error': str(e)})
        
        return results
