"""
AI 测试要点分析模块，从需求文本中提取测试要点，使用大语言模型进行智能分析。
"""

import json
import re
from typing import Dict, Optional
from pydantic import ValidationError

from core.ai_model_provider import AIModelProvider
from utils.models import TestPointsResult, TestPoint, TestCategory, TestType, Priority
from utils.exceptions import AIAnalysisException
from utils.cache_manager import CacheManager
from utils.log_manager import get_logger


class AITestPointAnalyzer:
    """AI 测试要点分析器"""
    
    def __init__(self, model_provider: AIModelProvider, 
                 cache_manager: Optional[CacheManager] = None):
        """初始化分析器"""
        self.model_provider = model_provider
        self.cache_manager = cache_manager or CacheManager()
        self.logger = get_logger()
    
    def extract_test_points(self, requirement_text: str) -> Dict:
        """提取测试要点
        
        Args:
            requirement_text: 需求文本
            
        Returns:
            测试要点字典，格式：
            {
                "feature_name": "功能名称",
                "test_points": [
                    {
                        "id": "TP_001",
                        "category": "功能测试",
                        "description": "测试要点描述",
                        "test_type": "正向测试",
                        "priority": "P1",
                        "scenarios": ["场景1", "场景2"]
                    }
                ]
            }
            
        Raises:
            AIAnalysisException: 分析失败
        """
        if not requirement_text or not requirement_text.strip():
            raise AIAnalysisException(
                "需求文本为空",
                provider=self.model_provider.provider_name,
                model_name=self.model_provider.model_name
            )
        
        self.logger.log_operation(
            "AI_ANALYSIS_START",
            text_length=len(requirement_text),
            model=self.model_provider.model_name
        )
        
        # 检查缓存
        cached_result = self.cache_manager.get_ai_cache(
            requirement_text,
            self.model_provider.model_name
        )
        
        if cached_result:
            self.logger.info("使用缓存的 AI 分析结果")
            return cached_result
        
        # 构建 Prompt
        prompt = self._build_prompt(requirement_text)
        
        # 调用 AI 模型
        try:
            response = self.model_provider.chat(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2000
            )
        except Exception as e:
            self.logger.log_error(e, context={"operation": "AI_CHAT"})
            raise AIAnalysisException(
                f"AI 模型调用失败: {str(e)}",
                provider=self.model_provider.provider_name,
                model_name=self.model_provider.model_name
            )
        
        # 解析响应
        result = self._parse_response(response)
        
        # 验证测试要点
        if not self._validate_test_points(result):
            raise AIAnalysisException(
                "测试要点验证失败",
                provider=self.model_provider.provider_name,
                model_name=self.model_provider.model_name,
                details={"result": str(result)[:200]}
            )
        
        # 缓存结果
        self.cache_manager.set_ai_cache(
            requirement_text,
            self.model_provider.model_name,
            result
        )
        
        self.logger.log_operation(
            "AI_ANALYSIS_COMPLETE",
            test_points_count=len(result.get("test_points", []))
        )
        
        return result
    
    def _build_prompt(self, requirement_text: str) -> str:
        """构建 Prompt
        
        Args:
            requirement_text: 需求文本
            
        Returns:
            构建好的 Prompt
        """
        prompt = f"""你是一位资深的测试架构师，擅长从需求文档中提取全面的测试要点。

请分析以下需求文档，从多个维度提取测试要点：

【需求文档】
{requirement_text}

【分析要求】
1. 测试维度：功能测试、性能测试、安全测试、兼容性测试、易用性测试
2. 测试类型：正向测试、负向测试、边界测试
3. 优先级：P0(核心功能)、P1(重要功能)、P2(一般功能)、P3(次要功能)
4. 测试场景：列出具体的测试场景

【输出格式】
请以 JSON 格式输出，严格遵循以下 Schema：
{{
  "feature_name": "功能名称",
  "test_points": [
    {{
      "id": "TP_001",
      "category": "功能测试",
      "description": "测试要点描述",
      "test_type": "正向测试",
      "priority": "P0",
      "scenarios": ["场景1", "场景2"]
    }}
  ]
}}

【重要说明】
- category 必须是以下之一：功能测试、性能测试、安全测试、兼容性测试、易用性测试
- test_type 必须是以下之一：正向测试、负向测试、边界测试
- priority 必须是以下之一：P0、P1、P2、P3
- id 格式为 TP_001, TP_002 等，按顺序递增
- 请确保输出的 JSON 格式正确，可以直接解析
- 只输出 JSON，不要包含其他说明文字
"""
        return prompt
    
    def _parse_response(self, response: str) -> Dict:
        """解析 AI 响应"""
        # 尝试提取 JSON 内容
        json_str = self._extract_json(response)
        
        if not json_str:
            raise AIAnalysisException(
                "无法从响应中提取 JSON 内容",
                provider=self.model_provider.provider_name,
                model_name=self.model_provider.model_name,
                details={"response": response[:200]}
            )
        
        # 解析 JSON
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError as e:
            # 尝试修复常见的 JSON 错误
            try:
                fixed_json = self._fix_json(json_str)
                result = json.loads(fixed_json)
                self.logger.warning("JSON 格式有误，已自动修复")
            except Exception:
                raise AIAnalysisException(
                    f"JSON 解析失败: {str(e)}",
                    provider=self.model_provider.provider_name,
                    model_name=self.model_provider.model_name,
                    details={"json_str": json_str[:200]}
                )
        
        return result
    
    def _extract_json(self, text: str) -> Optional[str]:
        """从文本中提取 JSON 内容"""
        # 移除可能的 markdown 代码块标记
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # 尝试找到 JSON 对象
        # 方法1: 查找完整的 { ... } 结构
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return match.group(0)
        
        # 方法2: 如果整个文本看起来像 JSON
        text = text.strip()
        if text.startswith('{') and text.endswith('}'):
            return text
        
        return None
    
    def _fix_json(self, json_str: str) -> str:
        """尝试修复常见的 JSON 格式错误 """
        # 移除尾部逗号
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # 修复单引号为双引号
        # 注意：这个简单的替换可能在某些情况下不准确
        # json_str = json_str.replace("'", '"')
        
        return json_str
    
    def _validate_test_points(self, result: Dict) -> bool:
        """验证测试要点格式"""
        try:
            # 使用 Pydantic 模型验证
            test_points_result = TestPointsResult(**result)
            
            # 额外验证：确保至少有一个测试要点
            if not test_points_result.test_points:
                self.logger.warning("测试要点列表为空")
                return False
            
            # 验证 ID 的唯一性
            ids = [tp.id for tp in test_points_result.test_points]
            if len(ids) != len(set(ids)):
                self.logger.warning("测试要点 ID 存在重复")
                return False
            
            return True
            
        except ValidationError as e:
            self.logger.log_error(
                e,
                context={
                    "operation": "VALIDATE_TEST_POINTS",
                    "result": str(result)[:200]
                }
            )
            return False
        except Exception as e:
            self.logger.log_error(
                e,
                context={
                    "operation": "VALIDATE_TEST_POINTS",
                    "result": str(result)[:200]
                }
            )
            return False
