"""
提供统一的 AI 模型调用接口，支持多种 AI 提供商（OpenAI、Qwen、Deepseek 等）
"""

import time
import requests
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from openai import APITimeoutError

from utils.exceptions import AIAnalysisException


class AIModelProvider(ABC):
    """AI 模型提供商抽象基类"""
    
    def __init__(self, api_key: str, base_url: str, model_name: str,
                 max_retries: int = 4, timeout: int = 30):
        """初始化模型提供商"""
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.max_retries = max_retries
        self.timeout = timeout
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
    
    @abstractmethod
    def chat(self, prompt: str, temperature: float = 0.7, 
             max_tokens: int = 2000) -> str:
        """发送聊天请求"""
        pass
    
    def _retry_with_exponential_backoff(self, func, *args, **kwargs) -> Any:
        """使用指数退避策略重试函数调用"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except AIAnalysisException:
                # 自定义异常直接抛出，不重试
                raise
            except (APIConnectionError, APITimeoutError, requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError) as e:
                # 网络错误，可以重试
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避: 1s, 2s, 4s, 8s
                    time.sleep(wait_time)
                    continue
            except RateLimitError as e:
                # 限流错误，等待后重试
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** (attempt + 1)  # 更长的等待时间
                    time.sleep(wait_time)
                    continue
            except APIError as e:
                # API 错误，通常不应重试
                raise AIAnalysisException(
                    f"API 调用失败: {str(e)}",
                    provider=self.provider_name,
                    model_name=self.model_name,
                    details={"error_type": type(e).__name__}
                )
            except Exception as e:
                # 其他未知错误
                raise AIAnalysisException(
                    f"未知错误: {str(e)}",
                    provider=self.provider_name,
                    model_name=self.model_name,
                    details={"error_type": type(e).__name__}
                )
        
        # 重试次数耗尽
        raise AIAnalysisException(
            f"重试 {self.max_retries} 次后仍然失败: {str(last_exception)}",
            provider=self.provider_name,
            model_name=self.model_name,
            details={"last_error": str(last_exception)}
        )


class OpenAIProvider(AIModelProvider):
    """使用官方 openai 库调用 OpenAI API。"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1",
                 model_name: str = "gpt-4o-mini", max_retries: int = 4,
                 timeout: int = 30):
        """初始化 OpenAI 提供商"""
        super().__init__(api_key, base_url, model_name, max_retries, timeout)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )
    
    def chat(self, prompt: str, temperature: float = 0.7,
             max_tokens: int = 2000) -> str:
        """发送聊天请求到 OpenAI"""
        def _make_request():
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一位资深的测试架构师，擅长从需求文档中提取全面的测试要点。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        return self._retry_with_exponential_backoff(_make_request)


class QwenProvider(AIModelProvider):
    """使用兼容 OpenAI 的接口调用通义千问 API。"""
    
    def __init__(self, api_key: str, 
                 base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
                 model_name: str = "qwen-turbo", max_retries: int = 4,
                 timeout: int = 30):
        """初始化 Qwen 提供商"""
        super().__init__(api_key, base_url, model_name, max_retries, timeout)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )
    
    def chat(self, prompt: str, temperature: float = 0.7,
             max_tokens: int = 2000) -> str:
        """发送聊天请求到通义千问"""
        def _make_request():
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一位资深的测试架构师，擅长从需求文档中提取全面的测试要点。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        return self._retry_with_exponential_backoff(_make_request)


class DeepseekProvider(AIModelProvider):
    """使用兼容 OpenAI 的接口调用 Deepseek API。"""
    
    def __init__(self, api_key: str,
                 base_url: str = "https://api.deepseek.com/v1",
                 model_name: str = "deepseek-chat", max_retries: int = 4,
                 timeout: int = 30):
        """初始化 Deepseek """
        super().__init__(api_key, base_url, model_name, max_retries, timeout)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )
    
    def chat(self, prompt: str, temperature: float = 0.7,
             max_tokens: int = 2000) -> str:
        """发送聊天请求到 Deepseek"""
        def _make_request():
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一位资深的测试架构师，擅长从需求文档中提取全面的测试要点。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        return self._retry_with_exponential_backoff(_make_request)


class CustomProvider(AIModelProvider):
    """使用通用 HTTP 请求调用自定义 API，支持任何兼容 OpenAI 格式的 API。"""
    
    def __init__(self, api_key: str, base_url: str, model_name: str,
                 max_retries: int = 4, timeout: int = 30):
        """初始化自定义提供商"""
        super().__init__(api_key, base_url, model_name, max_retries, timeout)
    
    def chat(self, prompt: str, temperature: float = 0.7,
             max_tokens: int = 2000) -> str:
        """发送聊天请求到自定义 API"""
        def _make_request():
            # 构建请求
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "你是一位资深的测试架构师，擅长从需求文档中提取全面的测试要点。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # 发送请求
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            # 检查响应状态
            if response.status_code == 401:
                # 认证错误不应重试，直接抛出
                raise AIAnalysisException(
                    "API 认证失败，请检查 API Key 是否正确",
                    provider=self.provider_name,
                    model_name=self.model_name,
                    details={"status_code": response.status_code}
                )
            elif response.status_code == 429:
                # 限流错误，可以重试
                raise RateLimitError("API 调用频率超限")
            elif response.status_code >= 500:
                # 服务器错误，可以重试
                raise requests.exceptions.ConnectionError("服务器错误")
            elif response.status_code != 200:
                # 其他错误不应重试
                raise AIAnalysisException(
                    f"API 返回错误状态码: {response.status_code}",
                    provider=self.provider_name,
                    model_name=self.model_name,
                    details={"status_code": response.status_code}
                )
            
            # 解析响应
            try:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as e:
                raise AIAnalysisException(
                    f"API 响应格式错误: {str(e)}",
                    provider=self.provider_name,
                    model_name=self.model_name,
                    details={"response": response.text[:200]}
                )
        
        return self._retry_with_exponential_backoff(_make_request)


class AIModelFactory:
    """AI 模型工厂类,负责根据配置创建对应的 AI 模型提供商实例。"""
    
    # 注册的提供商类
    _providers: Dict[str, type] = {
        "openai": OpenAIProvider,
        "qwen": QwenProvider,
        "deepseek": DeepseekProvider,
        "custom": CustomProvider
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, api_key: str,
                       base_url: str, model_name: str,
                       max_retries: int = 4, timeout: int = 30) -> AIModelProvider:
        """创建 AI 模型提供商实例"""
        provider_class = cls._providers.get(provider_name.lower())
        
        if not provider_class:
            raise AIAnalysisException(
                f"不支持的 AI 提供商: {provider_name}",
                provider=provider_name,
                details={
                    "supported_providers": list(cls._providers.keys())
                }
            )
        
        try:
            return provider_class(
                api_key=api_key,
                base_url=base_url,
                model_name=model_name,
                max_retries=max_retries,
                timeout=timeout
            )
        except Exception as e:
            raise AIAnalysisException(
                f"创建 AI 提供商实例失败: {str(e)}",
                provider=provider_name,
                model_name=model_name,
                details={"error": str(e)}
            )
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """注册新的提供商类"""
        if not issubclass(provider_class, AIModelProvider):
            raise ValueError(
                f"{provider_class.__name__} 必须继承 AIModelProvider"
            )
        
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """获取支持的提供商列表"""
        return list(cls._providers.keys())
