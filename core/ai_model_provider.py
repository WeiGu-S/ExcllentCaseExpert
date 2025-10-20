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
    
    def __init__(self, api_key: str, base_url: str, model_name: str, system_prompt:Optional[str]=None,
                 max_retries: int = 4, timeout: int = 120):
        """初始化模型提供商"""
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.max_retries = max_retries
        self.timeout = timeout
        self.system_prompt = system_prompt or "你是一名资深的测试架构师，擅长从需求文档中提取测试要点。"
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

class _OpenAICompatibleProvider(AIModelProvider):
    """通用的兼容 OpenAI 接口的 Provider 基类"""

    def __init__(self, api_key: str, base_url: str,
                 model_name: str, **kwargs):
        super().__init__(api_key, base_url, model_name, **kwargs)
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)

    def chat(self, prompt: str, temperature: float = 0.7,
             max_tokens: int = 2000) -> str:
        def _make_request():
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        return self._retry_with_exponential_backoff(_make_request)

class OpenAIProvider(_OpenAICompatibleProvider):
    def __init__(self, api_key: str, base_url="https://api.openai.com/v1",
                 model_name="gpt-4o-mini", **kwargs):
        super().__init__(api_key, base_url, model_name, **kwargs)


class QwenProvider(_OpenAICompatibleProvider):
    def __init__(self, api_key: str,
                 base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                 model_name="qwen-turbo", **kwargs):
        super().__init__(api_key, base_url, model_name, **kwargs)


class DeepseekProvider(_OpenAICompatibleProvider):
    def __init__(self, api_key: str,
                 base_url="https://api.deepseek.com/v1",
                 model_name="deepseek-chat", **kwargs):
        super().__init__(api_key, base_url, model_name, **kwargs)


class CustomProvider(AIModelProvider):
    """通用 HTTP API Provider"""

    def chat(self, prompt: str, temperature: float = 0.7,
             max_tokens: int = 2000) -> str:
        def _make_request():
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)

            if response.status_code == 401:
                raise AIAnalysisException("API 认证失败，请检查 API Key",
                                          provider=self.provider_name, model_name=self.model_name)
            elif response.status_code == 429:
                raise RateLimitError("API 调用频率超限")
            elif response.status_code >= 500:
                raise requests.exceptions.ConnectionError("服务器错误")
            elif response.status_code != 200:
                raise AIAnalysisException(
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    provider=self.provider_name, model_name=self.model_name
                )

            try:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except Exception as e:
                raise AIAnalysisException(
                    f"解析响应失败: {str(e)}",
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
                        base_url: Optional[str] = None, model_name: str = "",
                        **kwargs) -> AIModelProvider:
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise AIAnalysisException(f"不支持的 AI 提供商: {provider_name}",
                                      details={"supported": list(cls._providers.keys())})
        return provider_class(api_key=api_key, base_url=base_url, model_name=model_name, **kwargs)
    
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
