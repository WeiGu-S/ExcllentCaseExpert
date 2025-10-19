"""
AI 测试要点分析器测试
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from core.ai_test_point_analyzer import AITestPointAnalyzer
from core.ai_model_provider import AIModelProvider
from utils.cache_manager import CacheManager
from utils.exceptions import AIAnalysisException


class TestAITestPointAnalyzer:
    """测试 AI 测试要点分析器"""
    
    @pytest.fixture
    def mock_provider(self):
        """创建模拟的 AI 提供商"""
        provider = Mock(spec=AIModelProvider)
        provider.provider_name = "test_provider"
        provider.model_name = "test_model"
        return provider
    
    @pytest.fixture
    def mock_cache_manager(self, tmp_path):
        """创建模拟的缓存管理器"""
        cache_dir = tmp_path / "cache"
        return CacheManager(cache_dir=str(cache_dir))
    
    @pytest.fixture
    def analyzer(self, mock_provider, mock_cache_manager):
        """创建分析器实例"""
        return AITestPointAnalyzer(mock_provider, mock_cache_manager)
    
    @pytest.fixture
    def sample_requirement(self):
        """示例需求文本"""
        return """
        用户登录功能需求：
        1. 用户可以使用用户名和密码登录系统
        2. 登录失败3次后账号锁定30分钟
        3. 支持记住密码功能
        4. 登录成功后跳转到首页
        """
    
    @pytest.fixture
    def sample_ai_response(self):
        """示例 AI 响应"""
        return json.dumps({
            "feature_name": "用户登录",
            "test_points": [
                {
                    "id": "TP_001",
                    "category": "功能测试",
                    "description": "验证用户名密码登录",
                    "test_type": "正向测试",
                    "priority": "P0",
                    "scenarios": ["正确的用户名和密码", "登录成功跳转"]
                },
                {
                    "id": "TP_002",
                    "category": "安全测试",
                    "description": "验证账号锁定机制",
                    "test_type": "负向测试",
                    "priority": "P1",
                    "scenarios": ["连续3次错误密码", "账号锁定30分钟"]
                }
            ]
        }, ensure_ascii=False)
    
    def test_extract_test_points_success(self, analyzer, mock_provider, 
                                        sample_requirement, sample_ai_response):
        """测试成功提取测试要点"""
        mock_provider.chat.return_value = sample_ai_response
        
        result = analyzer.extract_test_points(sample_requirement)
        
        assert result["feature_name"] == "用户登录"
        assert len(result["test_points"]) == 2
        assert result["test_points"][0]["id"] == "TP_001"
        assert result["test_points"][0]["priority"] == "P0"
        mock_provider.chat.assert_called_once()
    
    def test_extract_test_points_with_cache(self, analyzer, mock_provider,
                                           sample_requirement, sample_ai_response):
        """测试缓存机制"""
        mock_provider.chat.return_value = sample_ai_response
        
        # 第一次调用
        result1 = analyzer.extract_test_points(sample_requirement)
        
        # 第二次调用应该使用缓存
        result2 = analyzer.extract_test_points(sample_requirement)
        
        assert result1 == result2
        # 只调用一次 AI
        assert mock_provider.chat.call_count == 1
    
    def test_extract_test_points_empty_text(self, analyzer):
        """测试空文本输入"""
        with pytest.raises(AIAnalysisException) as exc_info:
            analyzer.extract_test_points("")
        
        assert "需求文本为空" in str(exc_info.value)
    
    def test_extract_test_points_ai_failure(self, analyzer, mock_provider,
                                           sample_requirement):
        """测试 AI 调用失败"""
        mock_provider.chat.side_effect = Exception("API 调用失败")
        
        with pytest.raises(AIAnalysisException) as exc_info:
            analyzer.extract_test_points(sample_requirement)
        
        assert "AI 模型调用失败" in str(exc_info.value)
    
    def test_parse_response_with_markdown(self, analyzer):
        """测试解析带 markdown 标记的响应"""
        response = """```json
        {
            "feature_name": "测试功能",
            "test_points": [
                {
                    "id": "TP_001",
                    "category": "功能测试",
                    "description": "测试描述",
                    "test_type": "正向测试",
                    "priority": "P1",
                    "scenarios": ["场景1"]
                }
            ]
        }
        ```"""
        
        result = analyzer._parse_response(response)
        
        assert result["feature_name"] == "测试功能"
        assert len(result["test_points"]) == 1
    
    def test_parse_response_invalid_json(self, analyzer):
        """测试解析无效 JSON"""
        response = "这不是一个有效的 JSON"
        
        with pytest.raises(AIAnalysisException) as exc_info:
            analyzer._parse_response(response)
        
        assert "无法从响应中提取 JSON 内容" in str(exc_info.value)
    
    def test_validate_test_points_success(self, analyzer):
        """测试验证成功的测试要点"""
        result = {
            "feature_name": "测试功能",
            "test_points": [
                {
                    "id": "TP_001",
                    "category": "功能测试",
                    "description": "测试描述",
                    "test_type": "正向测试",
                    "priority": "P1",
                    "scenarios": ["场景1"]
                }
            ]
        }
        
        assert analyzer._validate_test_points(result) is True
    
    def test_validate_test_points_empty_list(self, analyzer):
        """测试空测试要点列表"""
        result = {
            "feature_name": "测试功能",
            "test_points": []
        }
        
        assert analyzer._validate_test_points(result) is False
    
    def test_validate_test_points_duplicate_ids(self, analyzer):
        """测试重复的测试要点 ID"""
        result = {
            "feature_name": "测试功能",
            "test_points": [
                {
                    "id": "TP_001",
                    "category": "功能测试",
                    "description": "测试描述1",
                    "test_type": "正向测试",
                    "priority": "P1",
                    "scenarios": ["场景1"]
                },
                {
                    "id": "TP_001",  # 重复的 ID
                    "category": "功能测试",
                    "description": "测试描述2",
                    "test_type": "正向测试",
                    "priority": "P1",
                    "scenarios": ["场景2"]
                }
            ]
        }
        
        assert analyzer._validate_test_points(result) is False
    
    def test_build_prompt(self, analyzer, sample_requirement):
        """测试 Prompt 构建"""
        prompt = analyzer._build_prompt(sample_requirement)
        
        assert sample_requirement in prompt
        assert "功能测试" in prompt
        assert "正向测试" in prompt
        assert "P0" in prompt
        assert "JSON" in prompt
    
    def test_extract_json_from_text(self, analyzer):
        """测试从文本中提取 JSON"""
        text = """这是一些说明文字
        {
            "key": "value",
            "nested": {
                "data": "test"
            }
        }
        还有一些其他文字"""
        
        json_str = analyzer._extract_json(text)
        
        assert json_str is not None
        assert json_str.startswith('{')
        assert json_str.endswith('}')
        
        # 验证可以解析
        parsed = json.loads(json_str)
        assert parsed["key"] == "value"
    
    def test_fix_json_trailing_comma(self, analyzer):
        """测试修复尾部逗号"""
        bad_json = '{"key": "value",}'
        fixed = analyzer._fix_json(bad_json)
        
        # 应该能够解析
        parsed = json.loads(fixed)
        assert parsed["key"] == "value"
