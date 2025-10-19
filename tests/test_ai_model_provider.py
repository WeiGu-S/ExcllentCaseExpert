"""
AI 模型提供商测试模块

测试 AI 模型提供商的基本功能，包括工厂模式、重试机制等。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from openai import APIError, APIConnectionError, RateLimitError

from core.ai_model_provider import (
    AIModelProvider,
    OpenAIProvider,
    QwenProvider,
    DeepseekProvider,
    CustomProvider,
    AIModelFactory
)
from utils.exceptions import AIAnalysisException


class TestAIModelFactory:
    """测试 AI 模型工厂类"""
    
    def test_create_openai_provider(self):
        """测试创建 OpenAI 提供商"""
        provider = AIModelFactory.create_provider(
            provider_name="openai",
            api_key="test_key",
            base_url="https://api.openai.com/v1",
            model_name="gpt-4o-mini"
        )
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == "test_key"
        assert provider.model_name == "gpt-4o-mini"
    
    def test_create_qwen_provider(self):
        """测试创建 Qwen 提供商"""
        provider = AIModelFactory.create_provider(
            provider_name="qwen",
            api_key="test_key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_name="qwen-turbo"
        )
        
        assert isinstance(provider, QwenProvider)
        assert provider.api_key == "test_key"
        assert provider.model_name == "qwen-turbo"
    
    def test_create_deepseek_provider(self):
        """测试创建 Deepseek 提供商"""
        provider = AIModelFactory.create_provider(
            provider_name="deepseek",
            api_key="test_key",
            base_url="https://api.deepseek.com/v1",
            model_name="deepseek-chat"
        )
        
        assert isinstance(provider, DeepseekProvider)
        assert provider.api_key == "test_key"
        assert provider.model_name == "deepseek-chat"
    
    def test_create_custom_provider(self):
        """测试创建自定义提供商"""
        provider = AIModelFactory.create_provider(
            provider_name="custom",
            api_key="test_key",
            base_url="https://custom.api.com/v1",
            model_name="custom-model"
        )
        
        assert isinstance(provider, CustomProvider)
        assert provider.api_key == "test_key"
        assert provider.model_name == "custom-model"
    
    def test_create_unsupported_provider(self):
        """测试创建不支持的提供商"""
        with pytest.raises(AIAnalysisException) as exc_info:
            AIModelFactory.create_provider(
                provider_name="unsupported",
                api_key="test_key",
                base_url="https://test.com",
                model_name="test-model"
            )
        
        assert "不支持的 AI 提供商" in str(exc_info.value)
    
    def test_get_supported_providers(self):
        """测试获取支持的提供商列表"""
        providers = AIModelFactory.get_supported_providers()
        
        assert "openai" in providers
        assert "qwen" in providers
        assert "deepseek" in providers
        assert "custom" in providers


class TestOpenAIProvider:
    """测试 OpenAI 提供商"""
    
    @patch('core.ai_model_provider.OpenAI')
    def test_chat_success(self, mock_openai_class):
        """测试成功的聊天请求"""
        # 模拟 OpenAI 客户端
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # 模拟响应
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "测试响应内容"
        mock_client.chat.completions.create.return_value = mock_response
        
        # 创建提供商并调用
        provider = OpenAIProvider(
            api_key="test_key",
            model_name="gpt-4o-mini"
        )
        result = provider.chat("测试提示词")
        
        assert result == "测试响应内容"
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('core.ai_model_provider.OpenAI')
    @patch('core.ai_model_provider.time.sleep')  # Mock sleep to speed up test
    def test_chat_with_retry(self, mock_sleep, mock_openai_class):
        """测试重试机制"""
        # 模拟 OpenAI 客户端
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # 第一次失败，第二次成功
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "成功响应"
        
        # Create a proper APIConnectionError
        connection_error = APIConnectionError(request=MagicMock())
        mock_client.chat.completions.create.side_effect = [
            connection_error,
            mock_response
        ]
        
        # 创建提供商并调用
        provider = OpenAIProvider(
            api_key="test_key",
            model_name="gpt-4o-mini",
            max_retries=2
        )
        result = provider.chat("测试提示词")
        
        assert result == "成功响应"
        assert mock_client.chat.completions.create.call_count == 2
        mock_sleep.assert_called_once()  # Should have slept once between retries


class TestCustomProvider:
    """测试自定义提供商"""
    
    @patch('core.ai_model_provider.requests.post')
    def test_chat_success(self, mock_post):
        """测试成功的聊天请求"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "自定义响应内容"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # 创建提供商并调用
        provider = CustomProvider(
            api_key="test_key",
            base_url="https://custom.api.com/v1",
            model_name="custom-model"
        )
        result = provider.chat("测试提示词")
        
        assert result == "自定义响应内容"
        mock_post.assert_called_once()
    
    @patch('core.ai_model_provider.requests.post')
    def test_chat_auth_error(self, mock_post):
        """测试认证错误"""
        # 模拟 401 响应
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        # 创建提供商并调用
        provider = CustomProvider(
            api_key="invalid_key",
            base_url="https://custom.api.com/v1",
            model_name="custom-model"
        )
        
        with pytest.raises(AIAnalysisException) as exc_info:
            provider.chat("测试提示词")
        
        assert "API 认证失败" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
